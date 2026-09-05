---
title: "实战：Linux USB Gadget（configfs）与 usbip"
layer: 枝干/主机侧与实现
doc-path: 60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md
---
# 实战：Linux USB Gadget（configfs）与 usbip

> 🌳 知识树位置: 树干 → 枝干[主机侧与实现] → 叶
> ⬆️ 父节点: [04-libusb与用户态访问](04-libusb与用户态访问.md)
> 工具与官方文档缓存索引: [../80-参考资料/README.md](../80-参考资料/README.md)

Linux 有两条"让 USB 工作起来"的路：一是把带 UDC（USB Device Controller，USB 设备控制器）的板子变成真 USB 设备（configfs gadget）；二是用 usbip 把 USB 设备通过网络搬到另一台机器（USB over IP）。本文给两条路的完整可执行脚本与踩坑清单。原理背景见 [02-操作系统USB支持](02-操作系统USB支持.md) 与 [04-libusb与用户态访问](04-libusb与用户态访问.md)。

## 一、configfs gadget：把开发板变成 USB 设备

内核要求（主流发行版内核已带）：`CONFIG_USB_CONFIGFS` + 各功能模块 `CONFIG_USB_CONFIGFS_F_HID`、`CONFIG_USB_F_ACM`（CDC-ACM）等；UDC 驱动随芯片（树莓派 Zero/4 用 `dwc2`，需在 `config.txt` 加 `dtoverlay=dwc2`；其他板以各自文档为准）。

模型：在 configfs（内核配置文件系统）里"搭积木"——设备级属性 + functions（功能）+ configs（配置）+ 符号链接绑定，最后写 UDC 名触发枚举。整个过程完全镜像描述符结构（[../10-树干-USB核心/07-描述符详解.md](../10-树干-USB核心/07-描述符详解.md)）。

configfs 目录树与描述符的对应关系：

```
/sys/kernel/config/usb_gadget/g1/
├── idVendor / idProduct / bcdUSB / bcdDevice   ← 设备描述符字段
├── bDeviceClass / bDeviceSubClass / bDeviceProtocol
├── strings/0x409/{serialnumber,manufacturer,product}  ← 字符串描述符
├── functions/                   ← 功能（= 接口群 + 类驱动行为）
│   ├── hid.usb0/  {protocol, subclass, report_length, report_desc}
│   └── acm.usb0/
├── configs/c.1/                 ← 一个目录 = 一个配置描述符
│   ├── MaxPower / bmAttributes / strings/0x409/configuration
│   └── hid.usb0@ → ../../../functions/hid.usb0   ← 符号链接 = 把接口装进配置
└── UDC                          ← 写入控制器名 = 开始枚举
```

对应说明：一个 gadget 目录对应一个设备；`configs/` 下每个子目录对应一个配置描述符；往配置里做多少个功能符号链接，配置描述符里就有多少组接口（复合设备由此而来）。

### 完整脚本：HID 键盘 + CDC 串口复合 gadget

在**板子**上以 root 执行（树莓派 Zero/4、BeagleBone 等带 device 口的板验证过同套路）：

```bash
#!/bin/bash
# gadget_hid_cdc.sh —— HID 键盘 + CDC-ACM 复合 gadget
set -e

# [1] 加载复合 gadget 框架（自动带出 configfs 挂载点）
modprobe libcomposite

# [2] 进入 gadget 配置目录，新建一个 gadget "g1"
cd /sys/kernel/config/usb_gadget
mkdir -p g1
cd g1

# [3] 设备描述符级属性：VID/PID/版本/USB 版本
echo 0x1d6b > idVendor      # Linux Foundation（测试用；量产换自己的 VID）
echo 0x0104 > idProduct     # Multifunction Composite Gadget 约定值
echo 0x0100 > bcdDevice     # 设备版本号 v1.00
echo 0x0200 > bcdUSB        # USB 2.0

# [4] 字符串描述符（语言 0x0409 = 英语美国）
mkdir -p strings/0x409
echo "fedcba9876543210" > strings/0x409/serialnumber  # 序列号：Windows 对 CDC 复合设备要求非空
echo "USBTree Lab"       > strings/0x409/manufacturer
echo "Gadget HID+CDC"    > strings/0x409/product

# [5] HID 功能：写报告描述符（标准 Boot 键盘，63 字节）必须在绑 UDC 前完成
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol        # 键盘协议
echo 1 > functions/hid.usb0/subclass        # Boot 子类（可进 BIOS）
echo 8 > functions/hid.usb0/report_length   # Input 报告 8 字节
# 63 字节 Boot 键盘报告描述符（与《HID 键盘详解》逐字节一致）
printf '\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x01\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0' > functions/hid.usb0/report_desc

# [6] CDC-ACM 功能：无需额外配置，节点出现在绑定后（/dev/ttyGS0）
mkdir -p functions/acm.usb0

# [7] 配置 c.1：功率与配置字符串
mkdir -p configs/c.1/strings/0x409
echo 250  > configs/c.1/MaxPower                    # mA
echo 0x80 > configs/c.1/bmAttributes                # bit7 必须为 1（总线供电）
echo "HID+CDC Config" > configs/c.1/strings/0x409/configuration

# [8] 把功能链接进配置——这一步才决定配置描述符里有什么接口
ln -s functions/hid.usb0 configs/c.1/
ln -s functions/acm.usb0 configs/c.1/

# [9] 绑定 UDC：写入控制器名，主机立刻开始枚举
UDC=$(ls /sys/class/udc | head -n1)         # 例如 20980000.usb / musb-hdrc.0 / ci_hdrc.0
echo "使用 UDC: $UDC"
echo "$UDC" > UDC

echo "gadget 已上线。设备侧串口节点: /dev/ttyGS0"
```

拆绑与清理（改描述符前必须先下线）：

```bash
cd /sys/kernel/config/usb_gadget/g1
echo "" > UDC                        # 解绑控制器，主机侧设备消失
rm configs/c.1/hid.usb0 configs/c.1/acm.usb0
rmdir functions/hid.usb0 functions/acm.usb0
cd /sys/kernel/config/usb_gadget && rmdir g1
```

### 主机侧验证

主机插上 OTG 线后：

```bash
dmesg | tail
# [ 5432.10] usb 1-1.2: new full-speed USB device number 6 using xhci_hcd
# [ 5432.35] usb 1-1.2: New USB device found, idVendor=1d6b, idProduct=0104
# [ 5432.40] cdc_acm 1-1.2:1.0: ttyACM0: USB ACM device
# [ 5432.45] hid-generic 1-1.2:1.2: hiddev0,hidraw2: USB HID v1.11 Keyboard
lsusb                                        # 应看到 1d6b:0104 复合设备
lsusb -v -d 1d6b:0104 | grep -E "bInterfaceClass|iProduct"
```

功能验证：主机端 `sudo cat /dev/hidraw2 | hexdump -C`（等按键），板子端发 HID 报告 `printf '\0\0\x08\0\0\0\0\0' > /dev/hidg0`（0x08=E 键按下，8 字节 Boot 键盘报告；先发 `\0\0\0\0\0\0\0\0` 抬起）；串口则板子 `echo hi > /dev/ttyGS0`、主机 `cat /dev/ttyACM0` 能收到。抓包核对用 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)。

### 其他功能一句话

- **MSD（大容量存储）**：`functions/mass_storage.usb0`，`echo /path/file.img > functions/mass_storage.usb0/lun.0/file`，镜像文件当 U 盘。
- **UAC2 声卡**：`functions/uac2.usb0`，板子变 USB 声卡，参数（采样率/声道）在其子目录配置。
- **网络类**：`functions/ecm.usb0`（Linux/macOS 网卡）、`rndis.usb0`（Windows 老式 RNDIS 网卡），常与 ECM 链接进同一配置做全平台兼容。

### 旧式 g_hid/g_serial 模块与 configfs 的关系

`g_hid`、`g_serial`、`g_mass_storage`、`g_multi` 等是"预打包" gadget 模块：modprobe 时用模块参数固定功能组合，方便但僵硬（换功能要重编内核或改参数重启）。configfs 与它们**共用同一批底层 function 驱动**（f_hid、f_acm…），只是把组合权从编译期挪到运行期。两者互斥：同一 UDC 同时只能服务一个 gadget，`lsmod | grep g_` 有旧模块时先 `rmmod` 再玩 configfs。

## 二、usbip：把 USB 设备搬过网线

usbip（USB over IP）由内核模块 + `usbip` 工具组成：服务端把本地设备的 URB 封装成 TCP（端口 3240）发往客户端，客户端的虚拟主机控制器（vhci）把 URB 还原给本地 USB 栈——客户端类驱动看到的与插了真设备完全一样。

### 服务端（Linux，设备插在这台机器）

```bash
# [1] 加载服务端内核模块
sudo modprobe usbip_host

# [2] 列出本地设备，拿到 busid（形如 1-1.2）
usbip list -l
#  - busid 1-1.2 (1d6b:0104) USBTree Lab :: Gadget HID+CDC (…)

# [3] 把设备标记为可导出
sudo usbip bind --busid=1-1.2

# [4] 启动服务守护进程（监听 TCP 3240；新版本发现流程另用 UDP 3240）
sudo usbipd -D
```

### 客户端 A：Linux

```bash
sudo modprobe vhci_hcd                    # 虚拟主机控制器
usbip list --remote=192.168.1.10          # 看服务端导出的设备
sudo usbip attach --remote=192.168.1.10 --busid=1-1.2
usbip port                                # 查看已 attach 的端口
lsusb                                     # 设备已出现在本地
sudo usbip detach --port=00               # 用完解绑
```

### 客户端 B：Windows

Windows 侧最成熟的是 **usbipd-win**（微软推荐、用于 WSL2 直通），它把 **Windows 当服务端**：

```powershell
winget install usbipd
usbipd list                                # 找到 busid，如 2-3
usbipd bind --busid 2-3                    # 注册共享
usbipd attach --wsl --busid 2-3            # 附给 WSL；WSL 内 lsusb 可见
```

而"Windows 作为 usbip 客户端去连 Linux 服务端"需用第三方 usbip-win 项目（驱动需测试签名，稳定性以项目 README 为准）。**注意方向**：usbipd-win 是服务器；usbip-win 是客户端，两者不要混淆。

### 延迟与安全注意

| 事项 | 说明 |
|---|---|
| 延迟 | 每个 URB 一次网络往返（RTT），bulk 吞吐 ≈ 缓冲大小/RTT；同步传输、HID 等低频设备无感，摄像头/音频（等时传输）体验差 |
| 加密/认证 | usbip 协议**明文且无认证**：仅限可信局域网或 VPN 内使用，跨公网务必套 WireGuard/SSH 隧道 |
| 独占性 | 同一设备同一时刻只能 attach 给一个客户端 |
| 防火墙 | 服务端放行 **TCP 3240**（新版本发现机制还需 UDP 3240） |

## 三、与 QEMU usb-host 透传对比

QEMU 直通命令示例：`qemu-system-x86_64 -device qemu-xhci -device usb-host,vendorid=0xcafe,productid=0x4004`。

| 维度 | configfs gadget | usbip | QEMU usb-host |
|---|---|---|---|
| 本质 | 板子硬件真实扮演 USB 设备 | 原始 URB 过网络，客户端类驱动照常工作 | 宿主进程代理真设备给虚拟机控制器 |
| 需要 | 带 UDC 的开发板 | 真实设备 + 两台机器 | 真实设备 + 宿主机 + 虚拟机 |
| 平台 | Linux（板端） | 服务端 Linux 为主，客户端 Linux 稳、Windows 看项目 | Linux 宿主最佳，Windows 宿主受限 |
| 延迟 | 无 | 每 URB 一次网络 RTT | 很小（本机进程间） |
| 加密 | — | 无（自建隧道） | 无（本机） |
| 典型场景 | 固件/协议实验、自制外设 | 远程共享加密狗、WSL2 直通 | 驱动开发在 VM 内复现 |

## 四、常见坑速查

| 坑 | 现象 | 处置 |
|---|---|---|
| UDC 名不对 | `echo xxx > UDC` 报 No such device | `ls /sys/class/udc` 看真实名；无输出说明 UDC 驱动没加载（dwc2/ci_hdrc 等）或无 device 口 |
| UDC 被占用 | 写 UDC 报 Device or resource busy | 已有 g_hid 等旧模块或 g1 已绑定：`rmmod g_*`，或先 `echo "" > UDC` 再改配置 |
| 改描述符不生效 | report_desc/idProduct 写了没变化 | 必须**先解绑 UDC 再改**，改完重写 UDC；HID 报告描述符只允许在绑定前写入 |
| Windows 不认 gadget | 设备管理器感叹号/枚举失败 | Windows 校验苛刻：序列号字符串不能空、复合设备必须 IAD、bmAttributes bit7 必须为 1；先在 Linux 用 `lsusb -v` 比对全量描述符 |
| 主机识别成单接口 | CDC 只出了半个接口 | IAD 缺失或 `idVendor` 用了 Windows 有内嵌驱动的值；换 0x1d6b:0x0104 组合先跑通 |
| usbip attach 失败 | `usbip: error: unable to attach` | 服务端没 bind / usbipd 没跑 / 防火墙拦 3240；`nc -vz <ip> 3240` 先探端口 |
| USB 设备 attach 后 "Device busy" | 客户端内核驱动抢先绑定 | 属正常：设备已被本地类驱动接管；要用户态访问参考 [04-libusb与用户态访问](04-libusb与用户态访问.md) |

## 相关节点

- [04-libusb与用户态访问](04-libusb与用户态访问.md)：usbip 客户端拿到"本地设备"后怎么访问
- [02-操作系统USB支持](02-操作系统USB支持.md)：gadget 与 vhci 在内核中的位置
- [../10-树干-USB核心/08-枚举流程与标准请求.md](../10-树干-USB核心/08-枚举流程与标准请求.md)：写 UDC 那一刻触发的完整枚举
- [../20-枝干-设备类协议/CDC-通信设备类/01-虚拟串口ACM.md](../20-枝干-设备类协议/CDC-通信设备类/01-虚拟串口ACM.md)：本例 acm.usb0 的协议依据
- [../20-枝干-设备类协议/HID-人机接口设备/05-键盘详解.md](../20-枝干-设备类协议/HID-人机接口设备/05-键盘详解.md)：脚本里 63 字节报告描述符的逐行解释
