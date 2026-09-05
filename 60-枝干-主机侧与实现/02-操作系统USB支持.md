---
title: "操作系统 USB 支持"
layer: 枝干/主机侧与实现
doc-path: 60-枝干-主机侧与实现/02-操作系统USB支持.md
---
# 操作系统 USB 支持

> 🌿 知识树位置: 树干 → 枝干[主机侧与实现] → 叶
> ⬆️ 返回: [../10-树干-USB核心/02-体系架构与分层模型.md](../10-树干-USB核心/02-体系架构与分层模型.md)

三大桌面系统 + Android 的 USB 子系统各成体系，但都遵循同一分层骨架（见 [01-主机控制器栈全景](01-主机控制器栈全景.md)）。本文按"当前主流做法"梳理各平台的关键组件、驱动绑定机制与工具链。

## 一、Windows

### 1.1 驱动模型演进

| 阶段 | 栈形态 | 关键组件 | 备注 |
|---|---|---|---|
| XP~7 | WDM USB 2.0 栈 | `usbport.sys`（USB 核心）+ `usbuhci.sys`/`usbohci.sys`/`usbehci.sys` + `usbhub.sys` | 每类 HCI 一个微端口驱动，minidriver 模式 |
| 8 起 | 原生 USB 3.0 栈 | `usbxhci.sys` + **UCX(USB Host Controller Extension, `ucx01000.sys`)** + `usbhub3.sys` | UCX 是 HCI 无关的控制器扩展层，厂商控制器驱动只需对接 UCX；微软从 Win8 开始内置 xHCI 支持 |
| 10 起 | 用户态框架 WinUSB 成熟 | `winusb.sys`（内核）+ `winusb.dll`（用户态 API） | 不写内核驱动即可访问自定义设备的首选；设备侧配合 MS OS 描述符(WCID/MS OS 2.0)可免 INF 自动绑定 |
| 10 起 | USB 双角色与 Type-C 框架 | 双角色控制器栈(URS) + USB 连接器管理(UCM) + UCSI 客户端 | 面向 SoC 平台的 OTG/双角色支持；UCSI(USB Type-C Connector System Software Interface) 用于对接 EC/Retimer 中的 Type-C 管理器 |

当前主流做法：自定义设备一律走 **WinUSB（用户态）**；厂商需要自家内核功能时用 **KMDF** 写驱动；仅做配置/采集则完全不动内核。

### 1.2 设备安装与驱动绑定规则

Windows 的 PnP 管理器按"硬件 ID(Hardware ID) → 兼容 ID(Compatible ID)"顺序匹配驱动：

- **硬件 ID** 示例：`USB\VID_1234&PID_5678&REV_0100`（设备级）、复合设备每个接口额外生成 `USB\VID_1234&PID_5678&MI_00`；
- **兼容 ID** 按接口类收窄：`USB\Class_03&SubClass_01&Prot_01` → `USB\Class_03` → `USB\`。标准类（HID/Mass Storage/打印机/Win10+ 的 CDC-ACM）由此自动命中内置驱动（`hidusb.sys`、`usbstor.sys`、`usbprint.sys`、`usbser.sys`）；
- 复合设备由 `usbccgp.sys` 按 IAD/接口拆分成多个子设备分别安装——**缺少 IAD 的 CDC 复合设备在 Windows 上常绑定失败（代码 10）**，这是设备固件问题而非系统问题；
- INF 文件的核心段：`[Manufacturer]`/`[Models]`（匹配行）+ `Install` 段（`AddReg` 指定服务、`CopyFiles` 部署文件）。Win10+ 自定义设备更推荐设备端实现 **MS OS 2.0 描述符**（BOS 中的 Platform Capability），声明 compatibleID="WINUSB"，实现**零 INF** 绑定。

### 1.3 设备管理器错误码速查

| 代码 | 含义 | 常见原因与排查方向 |
|---|---|---|
| 10 | 此设备无法启动(CM_PROB_FAILED_START) | 驱动与设备/描述符不匹配（典型：CDC 无 IAD、接口数与 INF 不符）、固件在配置后挂起、驱动启动路径失败 |
| 28 | 未安装该设备的驱动程序 | 没有任何 INF 匹配：VID/PID 写错、兼容 ID 覆盖不到、驱动未签名导致被策略拦 |
| 43 | Windows 已停止这个设备因为它报告了问题 | 驱动报告致命错误/设备行为异常（枚举后协议级失败）；坏固件、供电不稳时常见 |
| 1 | 设备配置不正确 | INF 中配置与实际硬件不符 |
| 19 | 注册表信息损坏/冲突 | 上层/下层过滤器堆积，卸载驱动+删设备后重装 |
| 22 | 设备被禁用 | 用户或策略禁用（组策略设备安装限制的典型表现，见 [70/04](../70-枝干-调试测试与安全/04-USB安全与BadUSB.md)） |
| 45 | 设备未连接 | 幽灵设备残留，重新插拔即消 |

查看真实问题码：`设备管理器 → 属性 → 常规/事件`，或 PowerShell：`Get-PnpDevice -InstanceId "USB\VID_1234*" | Format-List Problem,FriendlyName`。

### 1.4 WDF 写 USB 驱动要点

- **KMDF**(Kernel-Mode Driver Framework)：内核 USB 驱动的标准框架。核心对象：`WDFUSBDEVICE` / `WDFUSBINTERFACE` / `WDFUSBPIPE`；同步/异步读写在 `WDF_REQUEST_SEND_OPTIONS` 之上封装；**连续读取器(Continuous Reader)** 是中断端点的惯用法，预分配缓冲避免高频分配。
- **UMDF 2.x**(User-Mode Driver Framework)：用户态驱动，底层经 WinUSB 通道访问设备；稳定性好、崩溃不影响内核，吞吐要求不高时优先选它。
- 通用建议：中断端点走连续读取器；bulk 用队列并行深度控制背压；控制传输直接用框架的 USB Target API；调试用 WPP 追踪 + `!wdfkd` 调试器扩展。

### 1.5 工具链

| 工具 | 用途 | 备注 |
|---|---|---|
| PnPUtil | `pnputil /enum-devices /connected`、导出/导入驱动、禁用设备 | 命令行批量管理首选 |
| USBView | 树形展示全部控制器/集线器/设备与描述符 | WDK 附带，有开源等价 GUI |
| UsbTreeView (Uwe Sieber) | USBView 增强版：显示速度、电源、能力、重枚举 | 免费单文件，实战利器 |
| Wireshark + USBPcap | 软件层抓包（Message Analyzer 已退役，官方建议改用 Wireshark 生态） | 详见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](../70-枝干-调试测试与安全/01-协议分析仪与抓包.md) |

## 二、Linux

### 2.1 内核组件地图

```
usbcore (USB 核心: usb_devices、hub 事件、驱动匹配)
 ├─ 主机侧: xhci-hcd / ehci-hcd / ohci-hcd / uhci-hcd (HCD 层)
 ├─ 集线器驱动 hub.ko（kmalloc 探测、端口电源管理）
 ├─ 类驱动: usb-storage.ko / usbhid.ko / cdc-acm.ko / cdc_ether.ko / uvcvideo.ko ...
 ├─ 设备侧(gadget): libcomposite.ko + 各 function 驱动
 └─ 用户态接口: usbfs (/dev/bus/usb/BB/DD) + /sys/bus/usb
```

- **usbcore**：设备生命周期（attach/configure/detach）、URB 提交、驱动绑定、带宽仲裁。
- **usbfs**：每个设备一个节点 `/dev/bus/usb/<bus>/<dev>`，是 libusb 的后端；高吞吐场景注意 `usbfs_memory_mb` 内存上限（见 [04-libusb与用户态访问](04-libusb与用户态访问.md)）。
- **sysfs**：`/sys/bus/usb/devices/` 下的 `1-2.1` 形式节点暴露全部描述符字段（`idVendor`、`bcdDevice`、`bMaxPower`…），shell 脚本即读。

### 2.2 udev 规则：权限与命名

```
# /etc/udev/rules.d/99-mydevice.rules
# 1) 放开串口权限并固定别名（ATTRS 逐级回溯到 USB 设备节点）
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", \
  MODE="0666", SYMLINK+="my_serial"

# 2) 通用：让 plugdev 组可访问指定 USB 设备
SUBSYSTEM=="usb", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", \
  MODE="0660", GROUP="plugdev"

# 3) 禁止某设备被 sudo 之外的用户访问（安全场景，见 70/04）
SUBSYSTEM=="usb", ATTRS{idVendor}=="0781", MODE="0000"
```

操作命令：

```bash
udevadm info --attribute-walk -n /dev/ttyUSB0   # 查完整属性链，写规则的依据
sudo udevadm control --reload-rules && sudo udevadm trigger
```

匹配原则：`SUBSYSTEM` 选事件类型，`ATTRS{}`（带 S）向父设备回溯；写完用 `udevadm test` 演练。

### 2.3 驱动绑定与解绑

```bash
# 查看当前绑定
lsusb -t                          # 树形：驱动名、速度、带宽占用
readlink /sys/bus/usb/devices/1-2/driver   # -> ../../../../../../bus/usb/drivers/usb-storage

# 手动解绑/换绑（免重插）
echo 1-2 | sudo tee /sys/bus/usb/devices/1-2/driver/unbind
echo 1-2 | sudo tee /sys/bus/usb/drivers/usbserial/bind

# 为已有驱动追加新 VID/PID（无需改代码重编译）
echo "1234 5678" | sudo tee /sys/bus/usb/drivers/usb-storage/new_id
```

### 2.4 Gadget 栈：Linux 变身 USB 设备

设备侧（UDC 模式）当前主流用 **configfs + libcomposite** 动态构造复合设备。示例：HID 鼠标 + CDC-ACM 串口。

```bash
sudo modprobe libcomposite
cd /sys/kernel/config/usb_gadget
mkdir g1 && cd g1

echo 0x1d6b > idVendor            # Linux Foundation
echo 0x0104 > idProduct           # Multifunction Composite Gadget
echo 0x0200 > bcdUSB              # USB 2.0
mkdir -p strings/0x409
echo "Demo Corp" > strings/0x409/manufacturer
echo "HID+CDC Demo" > strings/0x409/product
mkdir -p configs/c.1/strings/0x409
echo "hid+acm" > configs/c.1/strings/0x409/configuration
echo 100 > configs/c.1/MaxPower   # 单位 2mA → 200mA

# 功能 1：HID 鼠标
mkdir functions/hid.usb0
echo 1 > functions/hid.usb0/protocol      # 1=鼠标
echo 1 > functions/hid.usb0/subclass      # 1=Boot
echo 8 > functions/hid.usb0/report_length
printf '\x05\x01\x09\x02\xa1\x01\x05\x09\x19\x01\x29\x03\x15\x00\x25\x01\x95\x03\x75\x01\x81\x02\x95\x01\x75\x05\x81\x01\x05\x01\x09\x30\x09\x31\x15\x81\x25\x7f\x75\x08\x95\x02\x81\x06\xc0\xc0' \
  > functions/hid.usb0/report_desc

# 功能 2：CDC-ACM 虚拟串口
mkdir functions/acm.usb1

ln -s functions/hid.usb0 configs/c.1/
ln -s functions/acm.usb1 configs/c.1/

UDC=$(ls /sys/class/udc | head -1)
echo "$UDC" > UDC                 # 绑定控制器，开始枚举
```

构造出来的设备在主机端即表现为"复合设备"：一个 `/dev/ttyGS0`（gadget 侧）+ 主机侧出 HID 和串口两个接口。USB/IP 与 embedded 应用大量依赖此栈。

### 2.5 USB/IP：跨机器透传

- 内核模块 `usbip-core.ko` + 服务端 `usbip-host.ko`，用户态 `usbip` 工具；Linux 侧 `usbipd` 守护进程共享设备，远端 `usbip attach` 后设备像本地一样出现。
- **usbipd-win**：Windows 上的服务端实现，主要用于 **WSL2 的 USB 设备直通**（Windows 共享 → WSL 内 `usbip attach`），是当前最常用的跨系统透传方案。

## 三、macOS

| 层面 | 说明 |
|---|---|
| 框架 | **IOKit** 的 `IOUSBHostFamily`（IOUSBHostDevice/IOUSBHostInterface），取代旧 IOUSBFamily；驱动开发走 **DriverKit (DEXT)**，内核扩展(kext)已被逐步淘汰 |
| 描述符查看 | `system_profiler SPUSBDataType`、`ioreg -p IOUSB -l`、图形化 IORegistryExplorer（Xcode 工具） |
| 沙盒权限 | 沙盒 App 访问 USB 需 entitlement：`com.apple.security.device.usb`；配合 usage description 说明 |
| 驱动绑定 | 系统按 IOKit 匹配字典(IOProviderMergeProperties/ personalities)绑定；自定义设备可用 DriverKit 的 `USBDriverKit` 或直接由 App 经 IOKit 访问 |
| 权限弹出 | 新版 macOS 对新增 USB 设备（尤其摄像头/音频）会请求用户授权 |

## 四、Android

- **USB Host API**（自 Android 3.1）：`UsbManager` 枚举设备 → 请求权限（`requestPermission` + 广播接收）→ `UsbDeviceConnection` 上做 `controlTransfer`/`bulkTransfer`，接口粒度经 `UsbInterface`/`UsbEndpoint`。
- 声明式匹配：manifest 中 intent-filter `android.hardware.usb.action.USB_DEVICE_ATTACHED` + `res/xml/device_filter.xml`（vendor-id/product-id），插入即启动应用。
- **OTG(On-The-Go)**：手机当主机需要 A-A 转接线（OTG 线），设备侧由手机供 VBUS；USB4/Type-C 时代由 DRP 角色切换承担（见 [../30-枝干-接口与供电/](../30-枝干-接口与供电/) 相关章节）。
- 无 root 的调试通道：adb 本身就是一个 USB 接口上的私有协议，是"USB 复用"的典型案例。

## 五、四平台能力对照

| 能力 | Windows | Linux | macOS | Android |
|---|---|---|---|---|
| 免驱动用户态访问 | WinUSB / libusb | usbfs / libusb | IOKit / libusb | UsbDeviceConnection |
| 热插拔通知 | WM_DEVICECHANGE / CFG 注册 | udev / netlink | IOKit 通知 | 广播 ACTION_USB_DEVICE_* |
| 设备侧(gadget) | 有限（WCID 之外的制造商栈少） | 完整（configfs） | 极少 | 部分设备可开 |
| 抓包 | USBPcap | usbmon | 无原生（见 70/01） | 无原生（root+内核补丁/硬件） |

## 相关节点

- [01-主机控制器栈全景](01-主机控制器栈全景.md)：各平台共享的硬件契约
- [03-设备端固件栈](03-设备端固件栈.md)：设备侧如何配合枚举与复合设备
- [04-libusb与用户态访问](04-libusb与用户态访问.md)：跨平台用户态访问统一抽象
- [../70-枝干-调试测试与安全/04-USB安全与BadUSB.md](../70-枝干-调试测试与安全/04-USB安全与BadUSB.md)：平台侧的设备准入管控
- [../10-树干-USB核心/08-枚举流程与标准请求.md](../10-树干-USB核心/08-枚举流程与标准请求.md)：OS 枚举时执行的标准请求序列
