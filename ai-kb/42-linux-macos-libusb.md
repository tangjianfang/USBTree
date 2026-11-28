---
id: 42-linux-macos-libusb
title: "libusb 用户态访问、Linux Gadget/usbip、macOS 与 Linux 主机开发"
topic: host/linux-macos
level: 进阶
keywords: ["libusb", "libusb_control_transfer", "libusb_bulk_transfer", "async transfer", "hidapi", "Zadig", "usbfs", "udev", "Linux gadget", "configfs", "FunctionFS", "usbip", "usbmon", "IOKit", "DriverKit"]
sources:
  - path: "60-枝干-主机侧与实现/04-libusb与用户态访问.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/04-libusb与用户态访问.md"
  - path: "60-枝干-主机侧与实现/06-实战-libusb主机程序.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/06-实战-libusb主机程序.md"
  - path: "60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md"
  - path: "60-枝干-主机侧与实现/09-macOS与Linux主机开发.md"
    url: "https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/09-macOS与Linux主机开发.md"
spec_refs: ["libusb 1.0 API", "Linux kernel USB documentation"]
related: ["40-host-controller-os", "41-windows-driver", "43-device-firmware"]
usbtree_commit: 03306ba
generated: 2026-11-28
---

# libusb 用户态访问、Linux Gadget/usbip、macOS 与 Linux 主机开发

> 层级 进阶 · 主题 `host/linux-macos` · 相关：[主机控制器栈与操作系统 USB 支持](40-host-controller-os.md)、[Windows USB 驱动开发：选型、WinUSB、KMDF/UMDF、调试](41-windows-driver.md)、[设备端固件栈与 TinyUSB 实战](43-device-firmware.md)

## 核心事实 Key Facts

> 由维护者整理并与规范核对；与下方 USBTree 原文冲突时以本节为准。

- libusb 同步 API：libusb_init → libusb_open_device_with_vid_pid → libusb_detach_kernel_driver（Linux）→ libusb_claim_interface → libusb_control_transfer / libusb_bulk_transfer / libusb_interrupt_transfer → libusb_release_interface → libusb_close → libusb_exit。异步：libusb_alloc_transfer + libusb_submit_transfer + libusb_handle_events。
- Windows 上 libusb 需设备绑定 WinUSB（Zadig、INF 或 MS OS 2.0）；不能访问被 hidclass 占用的 HID 接口——HID 用 hidapi。
- Linux 权限：udev 规则 `SUBSYSTEM=="usb", ATTR{idVendor}=="xxxx", MODE="0666"`；hidraw 节点 `KERNEL=="hidraw*"`。
- Gadget configfs：/sys/kernel/config/usb_gadget/<g>/ 下建 idVendor/idProduct/strings/configs/functions（hid.usb0、acm.usb0、ncm.usb0、mass_storage.usb0、ffs.*），最后把 UDC 名写入 UDC 文件绑定。

## 原文：04-libusb与用户态访问

> Source: [60-枝干-主机侧与实现/04-libusb与用户态访问.md](https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/04-libusb与用户态访问.md)

大多数自定义 USB 设备并不需要内核驱动：现代操作系统都提供用户态通道（WinUSB / usbfs / IOKit），而 **libusb 1.0** 把三条路统一成一个 API。本文给出完整的编程模型、生态选型与实战坑位。

### 一、为什么用户态直接访问

| 内核驱动路线 | 用户态路线 |
|---|---|
| 需要签名/安装 INF，跨平台各写一份 | 一个二进制跨三大平台 |
| 崩溃蓝屏/内核 oops | 崩溃只是进程退出 |
| 开发迭代慢 | printf 直接调试 |
| 独占：内核类驱动先绑走，用户拿不到 | 控制绑定关系，接口归属清晰 |

用户态的限制也要清楚：拿不到同步传输的硬件级优先保证之外的特殊调度、无法参与内核即插即用语义（比如伪装成键盘需要 HID 类驱动解析报告的场景除外——libusb 可以裸发报告但系统级"键盘"语义由 HID 栈实现）、高吞吐时受用户态轮询与内存上限约束。

### 二、libusb 1.0 编程模型（C）

完整生命周期：`init → 枚举设备 → 读描述符 → open → claim_interface → 传输 → release → close → exit`。

```c
#include <libusb-1.0/libusb.h>
#include <stdio.h>

int main(void) {
    libusb_context *ctx = NULL;
    libusb_init(&ctx);                                /* 1. 初始化库 */

    libusb_device **list;
    ssize_t n = libusb_get_device_list(ctx, &list);   /* 2. 枚举所有设备 */
    for (ssize_t i = 0; i < n; i++) {
        struct libusb_device_descriptor d;
        libusb_get_device_descriptor(list[i], &d);    /* 3. 读设备描述符(18B) */
        printf("%04x:%04x bus=%03d addr=%03d\n",
               d.idVendor, d.idProduct,
               libusb_get_bus_number(list[i]),
               libusb_get_device_address(list[i]));
    }
    libusb_free_device_list(list, 1);

    /* 4. 打开目标设备（也常先 get_device_list 逐个比对再 libusb_open） */
    libusb_device_handle *h =
        libusb_open_device_with_vid_pid(ctx, 0x1234, 0x5678);
    if (!h) { libusb_exit(ctx); return 1; }

    libusb_set_auto_detach_kernel_driver(h, 1);       /* 5. 内核驱动自动分离 */
    if (libusb_claim_interface(h, 0) != 0) {          /* 6. 声明接口 0 */
        fprintf(stderr, "claim 失败：接口被内核驱动占用？\n");
        return 1;
    }

    unsigned char buf[512]; int done = 0;
    /* 7a. 同步 bulk 读：EP 0x81，超时 1000ms */
    int rc = libusb_bulk_transfer(h, 0x81, buf, sizeof buf, &done, 1000);
    if (rc == 0) printf("bulk: %d bytes\n", done);

    /* 7b. 同步中断读：EP 0x83 */
    rc = libusb_interrupt_transfer(h, 0x83, buf, 64, &done, 1000);

    /* 7c. 同步控制传输：GET_DESCRIPTOR(设备描述符, 前 18 字节) */
    rc = libusb_control_transfer(h,
            0x80,           /* bmRequestType: IN | 标准 | 设备 */
            0x06,           /* GET_DESCRIPTOR */
            0x0100,         /* wValue: type=DEVICE */
            0x0000,         /* wIndex */
            buf, 18, 1000);

    libusb_release_interface(h, 0);                   /* 8. 释放 */
    libusb_close(h);                                  /* 9. */
    libusb_exit(ctx);
    return 0;
}
```

编译：`gcc main.c -o demo $(pkg-config --cflags --libs libusb-1.0)`

#### 异步传输（高吞吐必须）

同步 API 每次传输阻塞一个线程；异步模型 = **分配 transfer → 填充 → submit → 事件循环 → 回调**，可挂起几十上百个 transfer 保持 USB 管道满载。

```c
static void LIBUSB_CALL on_done(struct libusb_transfer *t) {
    if (t->status == LIBUSB_TRANSFER_COMPLETED)
        printf("%d bytes\n", t->actual_length);
    else
        fprintf(stderr, "status=%d\n", t->status);
    libusb_free_transfer(t);          /* 生产中通常重新 fill+submit */
}

void submit_read(libusb_device_handle *h, libusb_context *ctx) {
    struct libusb_transfer *t = libusb_alloc_transfer(0);
    unsigned char *buf = malloc(512);
    libusb_fill_bulk_transfer(t, h, 0x81, buf, 512, on_done, NULL, 2000);
    libusb_submit_transfer(t);

    while (1)
        libusb_handle_events_completed(ctx, NULL);   /* 驱动事件循环 */
}
```

吞吐经验：同时 submit 多个传输（常见 8~64 个）× 大缓冲，比单传输循环快一个数量级。

#### 热插拔（hotplug）

```c
static int LIBUSB_CALL hot_cb(libusb_context *ctx, libusb_device *dev,
                              libusb_hotplug_event ev, void *user) {
    /* ev == LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED / _DEVICE_LEFT */
    return 0;   /* 返回 0 继续，非 0 注销回调 */
}

libusb_hotplug_register_callback(ctx,
    LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED | LIBUSB_HOTPLUG_EVENT_DEVICE_LEFT,
    0, 0x1234, 0x5678, LIBUSB_HOTPLUG_MATCH_ANY, hot_cb, NULL, &handle);

while (1) libusb_handle_events(ctx);   /* 热插拔回调在事件线程触发 */
```

注意 `libusb_has_capability(LIBUSB_CAP_HAS_HOTPLUG)` 先行探测——老 Windows 后端可能不支持。

### 三、各平台内核后端

| 平台 | libusb 后端 | 底层通道 | 备注 |
|---|---|---|---|
| Linux | usbfs 后端 | `/dev/bus/usb/BB/DD` | 受 `usbfs_memory_mb` 限制（默认 16MB，高吞吐需调大：`usbcore.usbfs_memory_mb=1024` 或运行时 echo） |
| Windows | **WinUSB** 后端（默认） | `winusb.sys` | 设备需绑定 WinUSB 驱动（WCID/Zadig）；部分老功能（如同步传输的某些选项）受限 |
| Windows | **libusbK** 后端 | `libusbK.sys`（KMDF） | 功能更全（含同步传输），Zadig 中可手动选择 |
| Windows | usbDk（可选） | 驱动过滤 | 允许**不替换**原驱动并行访问，适合厂商驱动共存场景 |
| macOS | Darwin 后端 | IOKit | 首次访问会触发系统授权弹窗 |

#### claim / detach 内核驱动

Linux 上标准类驱动（`usb-storage`、`usbhid` 等）会在设备出现时自动绑定，接口被占用后 `claim_interface` 返回 `LIBUSB_ERROR_BUSY`：

```c
/* 方式一：自动分离（推荐） */
libusb_set_auto_detach_kernel_driver(h, 1);

/* 方式二：显式分离（需权限，Windows/macOS 返回不支持错误） */
if (libusb_kernel_driver_active(h, 0) == 1)
    libusb_detach_kernel_driver(h, 0);
```

取舍：分离 `usb-storage` 后该设备不再有块设备节点，进程退出时应重绑或拔插恢复。

### 四、Python 生态与选型

| 库 | 定位 | 后端/依赖 | 何时选 |
|---|---|---|---|
| **pyusb** | libusb 1.0 的 Python 封装 | 需系统 libusb | 通用设备：bulk/control/interrupt 一把梭 |
| **hidapi**（`hid` 包） | 专用跨平台 HID 库 | Windows: hid.dll；Linux: hidraw；macOS: IOHidManager；另有 libusb 后端 | **HID 设备首选**：自动处理报告协议、免分离内核 HID 驱动 |
| pyserial | CDC-ACM/FTDI/CH340 串口 | OS 串口栈 | 虚拟串口场景，别用 libusb 自己解析 |
| libusb C + ctypes | 直呼原生 API | — | 需要 hotplug/异步等 pyusb 未覆盖能力 |

```python
# pyusb 快速示例
import usb.core
dev = usb.core.find(idVendor=0x1234, idProduct=0x5678)
dev.set_configuration()
print(dev.write(0x01, b'hello', 1000))       # EP1 OUT bulk
print(bytes(dev.read(0x81, 512, 1000)))      # EP1 IN bulk

# hidapi 快速示例（HID 设备推荐）
import hid
h = hid.device(0x1234, 0x5678); h.open()
print(h.read(64, timeout_ms=1000))
```

推荐组合：HID → hidapi；虚拟串口 → pyserial；其余自定义协议 → pyusb/libusb。

### 五、USB/IP 与设备透传方案

| 方案 | 组成 | 典型场景 |
|---|---|---|
| **usbip** | Linux 内核模块 + `usbip` 工具；Windows 客户端有 usbip-win 项目 | 远程设备透传：实验室加密狗共享给多台机器（同一时刻独占） |
| **usbipd-win** | Windows 服务端 | **WSL2 USB 直通**：Windows 共享 → WSL 内 attach，Linux 工具链直接访问 |
| **usbredir** | spice 协议组件，配合 QEMU `usb-redir` chardev | 虚拟机远程 USB（SPICE 远程桌面内重定向本机设备） |
| QEMU usb-host | `-device usb-host,vendorid=0x1234,productid=0x5678` | 本机设备直通进 VM（Linux 宿主效果最好） |
| 商用方案 | VirtualHere 等 | 网络摄像头/加密狗跨平台共享，免自建 |

排查透传问题时记住：usbip/usbredir 都是把**原始 URB 级流量**搬过网线，主机端类驱动行为不变，抓包在两端语义一致。

### 六、调试组合拳

```bash
lsusb                        # 一行一设备：VID:PID
lsusb -v -d 1234:5678        # 全量描述符树形解析（枚举问题先看这个）
lsusb -t                     # 树形：速度/驱动/带宽
usbhid-dump -a 1:2           # 转储 HID 报告描述符与原始报告(usbutils)
udevadm info -q all -n /dev/bus/usb/001/005   # sysfs 全属性
```

Windows 侧等价物：UsbTreeView（见 [02-操作系统USB支持](40-host-controller-os.md)），配合 Wireshark+USBPcap（见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](50-debug-troubleshooting.md)）。

### 七、常见坑速查

| 坑 | 现象 | 处置 |
|---|---|---|
| 超时设 0 | `*_transfer` 永久阻塞 | 明确给 1000~5000ms；异步用 transfer 自身超时 |
| 接口不可 claim | `LIBUSB_ERROR_BUSY` | 内核驱动占用：auto-detach / `new_id` 换驱动 / 卸载模块 |
| Linux usbfs 内存上限 | 大吞吐提交报 `LIBUSB_ERROR_NO_MEM` | 调大 `usbfs_memory_mb`（sysfs 或内核参数） |
| Windows 驱动不匹配 | `LIBUSB_ERROR_NOT_SUPPORTED` | 用 Zadig 给该 VID/PID 安装 WinUSB/libusbK |
| Zadig 风险 | 原厂驱动被覆盖，官方软件失效 | Zadig 是**全局替换**该设备的驱动绑定：认准 VID/PID/描述串再点；恢复靠卸载设备勾选"删除驱动"后重装原厂包；绝不应用于键鼠/存储等系统依赖设备 |
| 配置未设置 | 传输报 `LIBUSB_ERROR_NOT_FOUND` | 先 `set_configuration(1)` |
| macOS 首次访问无响应 | 数据全 NAK | 系统弹窗未确认；到"系统设置→隐私与安全性"允许 |

## 原文：06-实战-libusb主机程序

> Source: [60-枝干-主机侧与实现/06-实战-libusb主机程序.md](https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/06-实战-libusb主机程序.md)

> 工具与官方文档缓存索引: [../80-参考资料/README.md](92-spec-references.md)

本文从零写一个能跑的 [libusb](https://libusb.info) 1.0 主机程序：环境准备 → 单文件完整示例（约 120 行，逐段讲解）→ 异步传输 → 热插拔 → Python 对照 → 错误码速查。编程模型总览见 [04-libusb与用户态访问](42-linux-macos-libusb.md)，本文全部是可照抄的实战代码。

- 依赖版本：libusb ≥ 1.0.23（示例只用到 1.0.16 时代稳定 API，最新版以官方 API 文档 [github.com/libusb/libusb](https://github.com/libusb/libusb) 为准）
- 设备端配套：任意提供批量（Bulk）IN/OUT 端点的自定义设备；可直接用 [05-实战-TinyUSB设备固件](43-device-firmware.md) 的思路扩展一个 vendor 接口来配对测试

### 一、环境搭建：各平台驱动与权限

libusb 在各平台走不同内核后端，**设备侧的驱动绑定决定了程序能不能打开设备**：

| 平台 | 要求 | 说明 |
|---|---|---|
| Linux | udev 规则放权限 | 不装任何驱动；内核类驱动可用 auto-detach 绕开 |
| Windows | 设备须绑定 WinUSB/libusbK 驱动 | 两条路线：Zadig 手动替换，或设备固件自带 MS OS 描述符免驱 |
| macOS | 无需任何驱动 | 首次访问触发系统授权弹窗，允许即可 |

#### Windows：Zadig 替换 vs MS OS 描述符免驱

| 维度 | Zadig 手动替换 | MS OS 描述符（免驱） |
|---|---|---|
| 原理 | 工具把设备的驱动绑定改成 WinUSB/libusbK | 固件在描述符层面声明 `CompatibleID = "WINUSB"`，Windows 自动装 WinUSB |
| 操作 | 插上设备 → 选 VID/PID → 目标驱动选 WinUSB → Install Device | 固件实现 MS OS 1.0 字符串（索引 0xEE）或 MS OS 2.0 描述符（挂在 BOS 上，Win8.1+） |
| 风险 | **全局替换**该设备的驱动：原厂软件可能失效；绝不用于键鼠/存储等系统依赖设备 | 无侵入，随固件走；但需要改固件描述符 |
| 适用 | 调试期临时设备、二手模块 | 量产产品标准做法 |

结论：**自己开发固件，直接做 MS OS 描述符；调试别人的设备，用 Zadig 认准 VID/PID/描述串再点**。

#### Linux：udev 规则

非 root 用户访问设备需要 udev（userspace dev）授权。新建 `/etc/udev/rules.d/99-usbtree.rules`：

```
# VID=cafe PID=4004：放开读写权限
SUBSYSTEM=="usb", ATTRS{idVendor}=="cafe", ATTRS{idProduct}=="4004", MODE="0666"
```

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
# 重插设备生效；查询设备节点: udevadm info -n /dev/bus/usb/001/005
```

### 二、完整示例：bulk_demo.c（单文件约 120 行）

功能：查找设备 → 打开并声明接口 → 同步批量写+读（回环）→ 控制传输读设备描述符 + 发厂商自定义请求 → 释放退出。

```c
/* bulk_demo.c —— libusb 1.0 跨平台示例
 * 平台: Linux / Windows(需 WinUSB 驱动) / macOS；依赖: libusb >= 1.0.16
 * 编译: gcc bulk_demo.c -o bulk_demo $(pkg-config --cflags --libs libusb-1.0)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "libusb.h"

#define VENDOR_ID  0xCAFE
#define PRODUCT_ID 0x4004
#define EP_OUT     0x02      // 批量 OUT 端点地址（与固件描述符一致）
#define EP_IN      0x82      // 批量 IN
#define IFACE      0         // 接口号

/* 出错即打印可读错误名并退出 */
static void check(int rc, const char *what) {
    if (rc != LIBUSB_SUCCESS) {
        fprintf(stderr, "%s 失败: %s (%d)\n", what, libusb_error_name(rc), rc);
        exit(1);
    }
}

int main(void) {
    libusb_context *ctx = NULL;
    libusb_device_handle *h = NULL;
    int rc;

    /* 1. 初始化库（也可用 libusb_init_context 附带日志选项，>=1.0.27） */
    rc = libusb_init(&ctx);
    check(rc, "libusb_init");
    libusb_set_option(ctx, LIBUSB_OPTION_LOG_LEVEL, LIBUSB_LOG_LEVEL_WARNING);

    /* 2. 按 VID/PID 查找：内部遍历设备列表、读设备描述符比对 */
    h = libusb_open_device_with_vid_pid(ctx, VENDOR_ID, PRODUCT_ID);
    if (!h) {
        fprintf(stderr, "未找到 %04x:%04x；检查插接/驱动绑定(Windows)/udev 权限(Linux)\n",
                VENDOR_ID, PRODUCT_ID);
        libusb_exit(ctx);
        return 1;
    }

    /* 3. 配置与接口：进配置 1，分离内核驱动，声明接口 */
    int cfg = 0;
    libusb_get_configuration(h, &cfg);
    if (cfg != 1)
        check(libusb_set_configuration(h, 1), "set_configuration");

    libusb_set_auto_detach_kernel_driver(h, 1);   /* Linux 下自动解绑类驱动，其余平台无害 */
    check(libusb_claim_interface(h, IFACE), "claim_interface");

    /* 4. 同步批量写 + 读（设备固件需把收到数据原样回发） */
    unsigned char wr[64], rd[64];
    int transferred = 0;
    for (int i = 0; i < 64; i++) wr[i] = (unsigned char)i;

    rc = libusb_bulk_transfer(h, EP_OUT, wr, sizeof wr, &transferred, 2000);
    check(rc, "bulk OUT");
    printf("bulk OUT %d 字节\n", transferred);

    memset(rd, 0, sizeof rd);
    rc = libusb_bulk_transfer(h, EP_IN, rd, sizeof rd, &transferred, 2000);
    check(rc, "bulk IN");
    printf("bulk IN  %d 字节, rd[0]=0x%02X\n", transferred, rd[0]);

    /* 5a. 控制传输：标准请求 GET_DESCRIPTOR 读设备描述符 18 字节
     * bmRequestType=0x80: 方向IN | 标准请求 | 接收方设备 */
    unsigned char desc[18];
    rc = libusb_control_transfer(h, 0x80, 0x06, 0x0100, 0x0000,
                                 desc, sizeof desc, 1000);
    check(rc, "GET_DESCRIPTOR");
    printf("设备描述符: bcdUSB=%04x VID=%04x PID=%04x\n",
           desc[0] | (desc[1] << 8),
           desc[8] | (desc[9] << 8), desc[10] | (desc[11] << 8));

    /* 5b. 控制传输：厂商自定义 OUT 请求（bRequest 与固件约定，标准请求占用 0x00~0x0C）
     * bmRequestType=0x40: 方向OUT | 厂商请求 | 接收方设备 */
    unsigned char payload[4] = { 0xA1, 0xB2, 0xC3, 0xD4 };
    rc = libusb_control_transfer(h, 0x40, 0xB0,   /* 厂商命令号 0xB0 仅为示例 */
                                 0x0001, 0x0000,  /* wValue/wIndex 自定义语义 */
                                 payload, sizeof payload, 1000);
    check(rc, "vendor control OUT");
    printf("厂商控制请求已发送: %d 字节\n", rc);

    /* 6. 释放退出（顺序：release → close → exit） */
    libusb_release_interface(h, IFACE);
    libusb_close(h);
    libusb_exit(ctx);
    return 0;
}
```

#### 逐段讲解

1. **init（步骤 1）**：`libusb_context` 是会话句柄；多线程程序可共享一个 ctx，或每线程独立 ctx。日志级别建议先 WARNING，排查时临时开 LIBUSB_LOG_LEVEL_DEBUG 看每次 URB（USB Request Block，USB 请求块）的内核调用。
2. **查找（步骤 2）**：`libusb_open_device_with_vid_pid` 是便捷函数；需要按"接口类/序列号/多设备遍历"筛选时，改用 `libusb_get_device_list` + `libusb_get_device_descriptor` 逐个比对后 `libusb_open`（模式见 [04-libusb与用户态访问](42-linux-macos-libusb.md)）。
3. **配置与接口（步骤 3）**：`set_configuration` 必须在 claim 之前；`claim_interface` 是独占声明，被内核类驱动占用时返回 `LIBUSB_ERROR_BUSY`。`set_auto_detach_kernel_driver` 只在 Linux 生效，Windows 上调用返回 0 但不做事。
4. **同步传输（步骤 4）**：`libusb_bulk_transfer` 阻塞直到完成/超时/出错；超时给 2000ms，**不要传 0**（表示无限等待）。`transferred` 指示实际字节数，短包（小于申请长度）不算错误。
5. **控制传输（步骤 5a/5b）**：`libusb_control_transfer` 把 bmRequestType/bRequest/wValue/wIndex/wLength 五元组一次传参，IN 请求返回收到的字节数、OUT 请求返回已发字节数；它不需要先 claim 接口（走端点 0）。
6. **清理（步骤 6）**：漏掉 release/close 在进程退出时通常无害，但常驻进程必须成对释放，否则接口被自己占用。

### 三、异步传输骨架

同步 API 一线一传；要打满带宽需要"多 transfer 在飞 + 事件循环"：

```c
/* async_demo.c 骨架 —— 连续批量 IN：提交 N 个 transfer，回调里重新入队
 * 依赖: libusb >= 1.0.16；编译同 bulk_demo.c
 */
#include "libusb.h"
#include <stdio.h>
#include <stdlib.h>

#define QUEUE_DEPTH 16          /* 同时在飞的传输数 */
#define BUF_SIZE    16384       /* 单缓冲越大越省中断 */

static int pending = 0;

static void LIBUSB_CALL on_bulk_in(struct libusb_transfer *t) {
    pending--;
    if (t->status == LIBUSB_TRANSFER_COMPLETED) {
        /* 处理 t->actual_length 字节数据（t->buffer）…… */
        libusb_fill_bulk_transfer(t, t->dev_handle, t->endpoint, t->buffer,
                                  BUF_SIZE, on_bulk_in, t->user_data, 5000);
        if (libusb_submit_transfer(t) == 0) pending++;   /* 复用 transfer 再次入队 */
        return;
    }
    /* 错误/拔出：释放缓冲并停止 */
    free(t->buffer);
    libusb_free_transfer(t);
}

void run(libusb_device_handle *h, libusb_context *ctx) {
    for (int i = 0; i < QUEUE_DEPTH; i++) {
        struct libusb_transfer *t = libusb_alloc_transfer(0);
        unsigned char *buf = malloc(BUF_SIZE);            /* 生命周期归回调管 */
        libusb_fill_bulk_transfer(t, h, 0x82, buf, BUF_SIZE,
                                  on_bulk_in, NULL, 5000);
        libusb_submit_transfer(t);
        pending++;
    }
    while (pending > 0)
        libusb_handle_events_completed(ctx, NULL);        /* 阻塞式事件循环 */
}
```

经验值：`QUEUE_DEPTH × BUF_SIZE` 决定吞吐上限；Linux 上单次提交超过 usbfs 限制会报 `LIBUSB_ERROR_NO_MEM`，处置见 [04-libusb与用户态访问](42-linux-macos-libusb.md)。

### 四、热插拔：到达即打开

```c
/* hotplug_demo.c 骨架 —— 插入设备自动打开并 claim
 * 依赖: libusb >= 1.0.16，且后端支持 LIBUSB_CAP_HAS_HOTPLUG（先探测）
 */
#include "libusb.h"
#include <stdio.h>

static int LIBUSB_CALL on_hotplug(libusb_context *ctx, libusb_device *dev,
                                  libusb_hotplug_event event, void *user_data) {
    libusb_device_handle *h = NULL;
    if (libusb_open(dev, &h) != 0) return 0;          /* 打不开就放过 */
    libusb_set_auto_detach_kernel_driver(h, 1);
    if (libusb_claim_interface(h, 0) == 0) {
        printf("设备到达并已占用接口 0\n");
        /* 交给工作线程做传输；此处演示直接持有 */
    } else {
        libusb_close(h);
    }
    return 0;   /* 返回 0 继续监听，非 0 注销本回调 */
}

int main(void) {
    libusb_context *ctx = NULL;
    libusb_init(&ctx);
    if (!libusb_has_capability(LIBUSB_CAP_HAS_HOTPLUG)) {
        fprintf(stderr, "此后端不支持热插拔，退化为轮询设备列表\n");
        return 1;
    }
    libusb_hotplug_callback_handle ch;
    libusb_hotplug_register_callback(ctx,
        LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED | LIBUSB_HOTPLUG_EVENT_DEVICE_LEFT,
        0,                        /* flags：1.0.27+ 可用 LIBUSB_HOTPLUG_NO_FLAGS */
        0xCAFE, 0x4004,           /* VID/PID 过滤；LIBUSB_HOTPLUG_MATCH_ANY 匹配任意 */
        LIBUSB_HOTPLUG_MATCH_ANY, /* 设备类过滤 */
        on_hotplug, NULL, &ch);

    while (1)
        libusb_handle_events(ctx);   /* 回调在此事件循环内被调用 */
}
```

注意：回调运行在 `libusb_handle_events` 所在线程，回调里**不要**做阻塞传输，先保存句柄交给工作线程。

### 五、Python 对照版（pyusb，约 20 行）

```python
# pyusb_demo.py —— 与 bulk_demo.c 等价的 pyusb（libusb 1.0 的 Python 封装）版本
# 依赖: pip install pyusb；系统需有 libusb(Linux 自带 / Windows 可用 libusb 官方发行包)
import usb.core
import usb.util

dev = usb.core.find(idVendor=0xCAFE, idProduct=0x4004)
if dev is None:
    raise SystemExit("设备未找到")

dev.set_configuration()                       # 默认配置 1
if dev.is_kernel_driver_active(0):            # Linux 必要，Windows 可跳过
    dev.detach_kernel_driver(0)

print(dev.write(0x02, bytes(range(64)), 2000))   # 批量 OUT: 返回写入字节数
print(bytes(dev.read(0x82, 64, 2000)))           # 批量 IN
print(dev.ctrl_transfer(0x80, 0x06, 0x0100, 0, 18))  # 控制传输: 读设备描述符
usb.util.dispose_resources(dev)               # 释放接口与资源
```

HID 设备建议直接用 hidapi（`pip install hid`），免分离内核 HID 驱动，选型对照见 [04-libusb与用户态访问](42-linux-macos-libusb.md)。

### 六、错误码速查表

| 错误码 | 值 | 典型原因 | 处置 |
|---|---|---|---|
| `LIBUSB_SUCCESS` | 0 | — | — |
| `LIBUSB_ERROR_IO` | -1 |
>  对抗抽查（evolve #34）：错误码数值与 libusb master `libusb.h` 枚举逐一比对一致（IO=-1/ACCESS=-3/NO_DEVICE=-4/NOT_FOUND=-5/BUSY=-6/TIMEOUT=-7/OVERFLOW=-8/PIPE=-9/NO_MEM=-11/NOT_SUPPORTED=-12）。
 线缆差/设备死机/后端底层错误 | 重试；换线换口；抓包定位（见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](50-debug-troubleshooting.md)） |
| `LIBUSB_ERROR_ACCESS` | -3 | Linux 权限不足；Windows 句柄被占 | 补 udev 规则或 sudo；关闭占用该设备的其他程序 |
| `LIBUSB_ERROR_NO_DEVICE` | -4 | 传输中途设备被拔出 | 释放句柄，回热插拔逻辑重新等设备 |
| `LIBUSB_ERROR_NOT_FOUND` | -5 | 端点/接口不存在，或配置未设置 | 核对端点地址与描述符；先 `set_configuration` |
| `LIBUSB_ERROR_BUSY` | -6 | 接口被内核驱动占用 | auto-detach、卸载驱动模块或换接口号 |
| `LIBUSB_ERROR_TIMEOUT` | -7 | 设备对请求持续 NAK（固件没收/没发） | 查固件端点处理；加大超时；抓包看是否 IN/OUT 停等 |
| `LIBUSB_ERROR_PIPE` | -9 | 端点返回 STALL（halted） | `libusb_clear_halt(h, ep)` 恢复；检查固件为何 stall |
| `LIBUSB_ERROR_OVERFLOW` | -8 | 数据比缓冲大（设备发超） | 加大缓冲或核对端点包大小 |
| `LIBUSB_ERROR_NO_MEM` | -11 | Linux usbfs 内存上限（默认 16MB） | 调大 `usbcore.usbfs_memory_mb`（见 [04-libusb与用户态访问](42-linux-macos-libusb.md)） |
| `LIBUSB_ERROR_NOT_SUPPORTED` | -12 | 平台不支持该调用（如 Windows 调 detach_kernel_driver） | 代码里按平台跳过，不当作致命错误 |

通用打印：`libusb_error_name(rc)` 给出符号名，`libusb_strerror(rc)` 给出人话描述。

### 七、编译与安装命令

```bash
# Linux (Debian/Ubuntu)
sudo apt install libusb-1.0-0-dev pkg-config
gcc bulk_demo.c -o bulk_demo $(pkg-config --cflags --libs libusb-1.0)

# macOS
brew install libusb          # 命令同上

# MSYS2 (Windows)
pacman -S mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-libusb
gcc bulk_demo.c -o bulk_demo.exe $(pkg-config --cflags --libs libusb-1.0)

# Windows + vcpkg (CMake 工程)
vcpkg install libusb:x64-windows
# 在 CMake 中 find_package 链接的目标名以 vcpkg 安装完成时打印的 usage 提示为准
```

## 原文：07-实战-LinuxGadget与usbip

> Source: [60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md](https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md)

> 工具与官方文档缓存索引: [../80-参考资料/README.md](92-spec-references.md)

Linux 有两条"让 USB 工作起来"的路：一是把带 UDC（USB Device Controller，USB 设备控制器）的板子变成真 USB 设备（configfs gadget）；二是用 usbip 把 USB 设备通过网络搬到另一台机器（USB over IP）。本文给两条路的完整可执行脚本与踩坑清单。原理背景见 [02-操作系统USB支持](40-host-controller-os.md) 与 [04-libusb与用户态访问](42-linux-macos-libusb.md)。

### 一、configfs gadget：把开发板变成 USB 设备

内核要求（主流发行版内核已带）：`CONFIG_USB_CONFIGFS` + 各功能模块 `CONFIG_USB_CONFIGFS_F_HID`、`CONFIG_USB_F_ACM`（CDC-ACM）等；UDC 驱动随芯片（树莓派 Zero/4 用 `dwc2`，需在 `config.txt` 加 `dtoverlay=dwc2`；其他板以各自文档为准）。

模型：在 configfs（内核配置文件系统）里"搭积木"——设备级属性 + functions（功能）+ configs（配置）+ 符号链接绑定，最后写 UDC 名触发枚举。整个过程完全镜像描述符结构（[../10-树干-USB核心/07-描述符详解.md](06-descriptors.md)）。

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

#### 完整脚本：HID 键盘 + CDC 串口复合 gadget

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

#### 主机侧验证

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

功能验证：主机端 `sudo cat /dev/hidraw2 | hexdump -C`（等按键），板子端发 HID 报告 `printf '\0\0\x08\0\0\0\0\0' > /dev/hidg0`（0x08=E 键按下，8 字节 Boot 键盘报告；先发 `\0\0\0\0\0\0\0\0` 抬起）；串口则板子 `echo hi > /dev/ttyGS0`、主机 `cat /dev/ttyACM0` 能收到。抓包核对用 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](50-debug-troubleshooting.md)。

#### 其他功能一句话

- **MSD（大容量存储）**：`functions/mass_storage.usb0`，`echo /path/file.img > functions/mass_storage.usb0/lun.0/file`，镜像文件当 U 盘。
- **UAC2 声卡**：`functions/uac2.usb0`，板子变 USB 声卡，参数（采样率/声道）在其子目录配置。
- **网络类**：`functions/ecm.usb0`（Linux/macOS 网卡）、`rndis.usb0`（Windows 老式 RNDIS 网卡），常与 ECM 链接进同一配置做全平台兼容。

#### 旧式 g_hid/g_serial 模块与 configfs 的关系

`g_hid`、`g_serial`、`g_mass_storage`、`g_multi` 等是"预打包" gadget 模块：modprobe 时用模块参数固定功能组合，方便但僵硬（换功能要重编内核或改参数重启）。configfs 与它们**共用同一批底层 function 驱动**（f_hid、f_acm…），只是把组合权从编译期挪到运行期。两者互斥：同一 UDC 同时只能服务一个 gadget，`lsmod | grep g_` 有旧模块时先 `rmmod` 再玩 configfs。

### 二、usbip：把 USB 设备搬过网线

usbip（USB over IP）由内核模块 + `usbip` 工具组成：服务端把本地设备的 URB 封装成 TCP（端口 3240）发往客户端，客户端的虚拟主机控制器（vhci）把 URB 还原给本地 USB 栈——客户端类驱动看到的与插了真设备完全一样。

#### 服务端（Linux，设备插在这台机器）

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

#### 客户端 A：Linux

```bash
sudo modprobe vhci_hcd                    # 虚拟主机控制器
usbip list --remote=192.168.1.10          # 看服务端导出的设备
sudo usbip attach --remote=192.168.1.10 --busid=1-1.2
usbip port                                # 查看已 attach 的端口
lsusb                                     # 设备已出现在本地
sudo usbip detach --port=00               # 用完解绑
```

#### 客户端 B：Windows

Windows 侧最成熟的是 **usbipd-win**（微软推荐、用于 WSL2 直通），它把 **Windows 当服务端**：

```powershell
winget install usbipd
usbipd list                                # 找到 busid，如 2-3
usbipd bind --busid 2-3                    # 注册共享
usbipd attach --wsl --busid 2-3            # 附给 WSL；WSL 内 lsusb 可见
```

而"Windows 作为 usbip 客户端去连 Linux 服务端"需用第三方 usbip-win 项目（驱动需测试签名，稳定性以项目 README 为准）。**注意方向**：usbipd-win 是服务器；usbip-win 是客户端，两者不要混淆。

#### 延迟与安全注意

| 事项 | 说明 |
|---|---|
| 延迟 | 每个 URB 一次网络往返（RTT），bulk 吞吐 ≈ 缓冲大小/RTT；同步传输、HID 等低频设备无感，摄像头/音频（等时传输）体验差 |
| 加密/认证 | usbip 协议**明文且无认证**：仅限可信局域网或 VPN 内使用，跨公网务必套 WireGuard/SSH 隧道 |
| 独占性 | 同一设备同一时刻只能 attach 给一个客户端 |
| 防火墙 | 服务端放行 **TCP 3240**（新版本发现机制还需 UDP 3240） |

### 三、与 QEMU usb-host 透传对比

QEMU 直通命令示例：`qemu-system-x86_64 -device qemu-xhci -device usb-host,vendorid=0xcafe,productid=0x4004`。

| 维度 | configfs gadget | usbip | QEMU usb-host |
|---|---|---|---|
| 本质 | 板子硬件真实扮演 USB 设备 | 原始 URB 过网络，客户端类驱动照常工作 | 宿主进程代理真设备给虚拟机控制器 |
| 需要 | 带 UDC 的开发板 | 真实设备 + 两台机器 | 真实设备 + 宿主机 + 虚拟机 |
| 平台 | Linux（板端） | 服务端 Linux 为主，客户端 Linux 稳、Windows 看项目 | Linux 宿主最佳，Windows 宿主受限 |
| 延迟 | 无 | 每 URB 一次网络 RTT | 很小（本机进程间） |
| 加密 | — | 无（自建隧道） | 无（本机） |
| 典型场景 | 固件/协议实验、自制外设 | 远程共享加密狗、WSL2 直通 | 驱动开发在 VM 内复现 |

### 四、常见坑速查

| 坑 | 现象 | 处置 |
|---|---|---|
| UDC 名不对 | `echo xxx > UDC` 报 No such device | `ls /sys/class/udc` 看真实名；无输出说明 UDC 驱动没加载（dwc2/ci_hdrc 等）或无 device 口 |
| UDC 被占用 | 写 UDC 报 Device or resource busy | 已有 g_hid 等旧模块或 g1 已绑定：`rmmod g_*`，或先 `echo "" > UDC` 再改配置 |
| 改描述符不生效 | report_desc/idProduct 写了没变化 | 必须**先解绑 UDC 再改**，改完重写 UDC；HID 报告描述符只允许在绑定前写入 |
| Windows 不认 gadget | 设备管理器感叹号/枚举失败 | Windows 校验苛刻：序列号字符串不能空、复合设备必须 IAD、bmAttributes bit7 必须为 1；先在 Linux 用 `lsusb -v` 比对全量描述符 |
| 主机识别成单接口 | CDC 只出了半个接口 | IAD 缺失或 `idVendor` 用了 Windows 有内嵌驱动的值；换 0x1d6b:0x0104 组合先跑通 |
| usbip attach 失败 | `usbip: error: unable to attach` | 服务端没 bind / usbipd 没跑 / 防火墙拦 3240；`nc -vz <ip> 3240` 先探端口 |
| USB 设备 attach 后 "Device busy" | 客户端内核驱动抢先绑定 | 属正常：设备已被本地类驱动接管；要用户态访问参考 [04-libusb与用户态访问](42-linux-macos-libusb.md) |

## 原文：09-macOS与Linux主机开发

> Source: [60-枝干-主机侧与实现/09-macOS与Linux主机开发.md](https://github.com/tangjianfang/USBTree/blob/main/60-枝干-主机侧与实现/09-macOS与Linux主机开发.md)

macOS 与 Linux 都走"类驱动绑定 + 用户态兜底"的模式，但权限模型截然不同：macOS 用 entitlement/签名体系层层把关，Linux 用 udev 规则+文件权限的开放模型。本文梳理两平台各自的用户态/内核态开发路线与最小骨架。平台 API 随版本演进，**以 Apple 与内核官方文档为准**。

### 一、macOS

#### 1.1 三条路线与权限模型

macOS 的 USB 客户端开发如今只剩两条主干：**App 直连 IOKit（用户态）** 与 **DriverKit（DEXT，用户态驱动）**；内核扩展（kext）路线已被 Apple 淘汰。三者对比：

| 维度 | IOKit 用户态直访 | DriverKit (DEXT) | kext（历史） |
|---|---|---|---|
| 栈/框架 | `IOUSBHostFamily`（IOUSBHostDevice/IOUSBHostInterface），取代旧 IOUSBFamily | `USBDriverKit` 家族（IOUSBHostDevice 的驱动侧镜像） | IOUSBFamily + kext 加载 |
| 运行位置 | 应用进程 | 独立 system extension 进程 | 内核 |
| 准入控制 | 沙盒 App 需 entitlement `com.apple.security.device.usb`；设备被 DEXT 占走后拿不到接口 | **受限 entitlement**：`com.apple.developer.driverkit.family.usb.device`（USB 设备族）+ 匹配用 `com.apple.developer.driverkit.transport.usb`（可限定 VID/PID），需向 Apple 提申请表 | Apple Silicon 上须降低系统安全策略才能加载，量产不可行 |
| 安装门槛 | 无 | 开发者签名 + 公证（notarization），用户在系统设置批准系统扩展 | 降低安全策略 |
| 适用 | 工具/上位机直控自家设备 | 替代 kext 的现代正式路线：专用驱动、需要独占设备 | 仅遗留维护 |

要点：

- **直访的前提是"没人绑走"**：一旦安装了匹配该设备的 DEXT，用户态 App 的 IOKit 通道会被抢占；调试时要先卸载或调整匹配字典。
- DEXT 的 USB 族 entitlement 属于受限资源，申请表按 VID 精确发放（细节以 Apple 文档与申请表为准）；配好 entitlement 后 `Info.plist` 的匹配字典（idVendor/idProduct/bInterfaceClass 等）决定 DEXT 绑定哪些设备。
- App Store 分发：直访 USB 的 App 需声明沙盒 entitlement 并自证用途；DEXT 随 App 上架需 `com.apple.developer.system-extension.install` 等配套 entitlement（名目以官方文档为准）。

#### 1.2 用户态直访骨架（IOKit）

老代码（libusb 旧版、大量开源工具）经 CFPlugIn 插件接口访问 `IOUSBDeviceInterface32x` 系列——**该路径自 macOS 10.11 起随 IOUSBFamily 一并废弃，此处仅作流程示意（伪代码级）**；新栈 `IOUSBHostFamily` 的用户客户端没有公开的 CFPlugIn 封装，实践上要么走 libusb（其后端即 IOUSBHost，见 [04-libusb与用户态访问](42-linux-macos-libusb.md)），要么 `IOServiceOpen` 打开 IOUSBHostDevice/Interface（用户客户端类型常量以官方文档为准）。流程骨架：

```objc
/* mac_usb.m —— IOKit 用户态访问骨架（伪代码级；API 名以官方文档为准） */
#import <IOKit/IOKitLib.h>
#import <IOKit/usb/IOUSBLib.h>        /* 旧栈头文件（已废弃，仅示意） */

static void poke(io_object_t svc)
{
    IOCFPlugInInterface     **plugIn = NULL;
    IOUSBDeviceInterface320 **dev    = NULL;   /* 版本接口随 SDK 演进 */
    SInt32 score = 0;

    /* 1) io_service_t → CFPlugIn 插件接口 */
    if (IOCreatePlugInInterfaceForService(svc, kIOUSBDeviceUserClientTypeID,
                                          kIOCFPlugInInterfaceID, &plugIn, &score) != KERN_SUCCESS)
        return;
    /* 2) QueryInterface 到具体版本设备接口 */
    (*plugIn)->QueryInterface(plugIn, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID320),
                              (LPVOID *)&dev);
    IODestroyPlugInInterface(plugIn);

    /* 3) 打开设备 → 描述符/控制传输 */
    if ((*dev)->USBDeviceOpen(dev) == KERN_SUCCESS) {
        IOUSBConfigurationDescriptorPtr cfg = NULL;
        (*dev)->GetConfigurationDescriptorPtr(dev, 0, &cfg);       /* 读配置描述符 */
        /* 标准/厂商控制请求经 (*dev)->DeviceRequest(dev, &req); 接口级操作
         * 需再对 IOUSBHostInterface/IOUSBInterfaceInterface 同法打开 */
        (*dev)->USBDeviceClose(dev);
    }
    (*dev)->Release(dev);
}

/* 枚举入口： */
CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
io_iterator_t it;
IOServiceGetMatchingServices(kIOMainPortDefault, m, &it);
io_object_t svc;
while ((svc = IOIteratorNext(it))) { poke(svc); IOObjectRelease(svc); }
```

配套工具：`system_profiler SPUSBDataType`、`ioreg -p IOUSB -l`、Xcode 的 IORegistryExplorer——写匹配字典前先看清设备的 IORegistry 结构。热插拔通知用 `IOServiceAddMatchingNotification`。

#### 1.3 DEXT 适用场景与发布约束

- **什么时候写 DEXT**：设备需要专属驱动策略（独占接口、实现私有类语义）、要在 iPadOS（DriverKit 已带去）复用、或 kext 已无处可加载（Apple Silicon 量产机型）。纯上位机通信不必写 DEXT——先试 IOKit 直访或 libusb。
- **签名链**：DEXT 至少需要 Developer Program 团队签名 + 公证；受限 entitlement（USB/HID 族）提交 Apple 申请表批准后绑定到具体 VID。开发期可用 `com.apple.developer.driverkit.developer-mode`-类临时权限在自家机器调试（名目以官方文档为准）。
- **安装体验**：用户首次需在"系统设置 → 隐私与安全性"批准系统扩展；复用一个 App Bundle 携带 DEXT 是标准形态。

### 二、Linux

#### 2.1 四种用户态途径

| 途径 | 位置/依赖 | 能做什么 | 权限来源 | 适用 |
|---|---|---|---|---|
| **libusb 1.0** | 用户态库，后端即 usbfs | 控制传输 + 4 类传输全量、热插拔事件、跨平台 | 打开 `/dev/bus/usb/BB/DD` 的文件权限 | 绝大多数自定义设备首选（见 [04](42-linux-macos-libusb.md)） |
| **hidraw** | 内核 HID 栈暴露的 `/dev/hidraw*` | 原始 report 收发，不必懂 USB | 字符设备权限（udev 分组） | HID 设备"只用 report 不改协议"的最简路径 |
| **usbfs ioctl** | 直接对 `/dev/bus/usb/BB/DD` 发 ioctl（libusb 的底层） | `USBDEVFS_CONTROL`（同步控制传输）、`USBDEVFS_SUBMITURB`/`USBDEVFS_REAPURB`（异步批量/中断）、`USBDEVFS_DISCARDURB`（取消）、`USBDEVFS_RESET`（端口复位）、`USBDEVFS_IOCTL`（配合驱动解绑） | 同上 | 不想引第三方库、要做特殊操作（解绑内核驱动、复位）的工具 |
| **uaccess udev 标签** | systemd-logind 动态授权机制 | 本身不是 API，而是给设备节点打 `TAG+="uaccess"` 后，把权限**动态授予当前坐席登录用户**（现代发行版对 MODE/GROUP 静态授权的替代） | udev 规则 | 桌面产品给"插上就能用的上位机"分发 udev 规则 |

usbfs 直连骨架（不依赖 libusb）：

```c
/* usbfs_demo.c —— 直接用 usbfs 与设备对话（gcc usbfs_demo.c -o demo） */
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/usbdevice_fs.h>     /* 全部 ioctl 与结构体 */
#include <stdio.h>
#include <string.h>

int main(void)
{
    unsigned char buf[64];
    int fd = open("/dev/bus/usb/001/004", O_RDWR);          /* bus/dev 用 lsusb 查 */
    if (fd < 0) { perror("open"); return 1; }

    /* 1) 同步控制传输：GET_DESCRIPTOR(Config), 前 9 字节 */
    struct usbdevfs_ctrltransfer ctrl = {
        .bRequestType = 0x80, .bRequest = 0x06,
        .wValue = 0x0200, .wIndex = 0, .wLength = 9,
        .timeout = 1000, .data = buf };
    if (ioctl(fd, USBDEVFS_CONTROL, &ctrl) < 0) perror("control");

    /* 2) 异步批量读：提交 URB */
    struct usbdevfs_urb urb;
    memset(&urb, 0, sizeof(urb));
    urb.type          = USBDEVFS_URB_TYPE_BULK;
    urb.endpoint      = 0x81;                               /* IN 端点（含方向位） */
    urb.buffer        = buf;
    urb.buffer_length = sizeof(buf);
    if (ioctl(fd, USBDEVFS_SUBMITURB, &urb) < 0) perror("submit");

    /* 3) 收割完成的 URB（阻塞版 REAPURB；轮询/超时用 REAPURBNDELAY） */
    struct usbdevfs_urb *done = NULL;
    if (ioctl(fd, USBDEVFS_REAPURB, &done) == 0)
        printf("recv %d bytes\n", done->actual_length);

    /* 需要中途取消在途 URB 时： ioctl(fd, USBDEVFS_DISCARDURB, &urb); */
    /* 设备卡死急救：       ioctl(fd, USBDEVFS_RESET);              （触发重新枚举） */
    close(fd);
    return 0;
}
```

如果该接口已被内核类驱动绑定，先经 `USBDEVFS_IOCTL` 发 `USBDEVFS_DISCONNECT` 把驱动踢掉（libusb 的 `libusb_kernel_driver_active`/`detach_kernel_driver` 内部即此套路），或用 [02-操作系统USB支持](40-host-controller-os.md) 的 sysfs unbind。

#### 2.2 内核态最小驱动骨架

需要内核级集成（作为标准设备类、深度定制错误恢复、被其它内核子系统消费）时，写 `usb_driver` 客户端驱动。约 50~70 行骨架（**内核版本 API 以[内核文档](https://www.kernel.org/doc/html/latest/driver-api/usb/index.html)为准**）：

```c
/* my_usb.c —— Linux USB 客户端驱动最小骨架 */
#include <linux/module.h>
#include <linux/usb.h>

#define MY_VID 0x1234
#define MY_PID 0x5678
#define BUFLEN 512

struct my_dev {
    struct usb_device *udev;
    struct urb        *urb;
    unsigned char     *buf;
    dma_addr_t         dma;
};

static void bulk_in_complete(struct urb *urb)      /* 完成回调：atomic 上下文 */
{
    struct my_dev *dev = urb->context;

    switch (urb->status) {
    case 0:                     /* 成功：urb->actual_length 字节在 urb->transfer_buffer */
        break;
    case -ECONNRESET: case -ENOENT: case -ESHUTDOWN:
        return;                 /* 被取消或设备已不在：不得重新提交 */
    default:                    /* 其他错误：生产代码应做限速重试/复位恢复 */
        break;
    }
    usb_submit_urb(urb, GFP_ATOMIC);   /* 示例：简单循环收包 */
}

static int my_probe(struct usb_interface *intf, const struct usb_device_id *id)
{
    struct usb_device *udev = interface_to_usbdev(intf);
    struct usb_endpoint_descriptor *ep;
    struct my_dev *dev;
    int ret;

    ret = usb_find_bulk_in_endpoint(intf->cur_altsetting, &ep);  /* 生产代码应逐描述符校验 */
    if (ret)
        return ret;

    dev = kzalloc(sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return -ENOMEM;
    dev->udev = usb_get_dev(udev);
    dev->buf  = usb_alloc_coherent(dev->udev, BUFLEN, GFP_KERNEL, &dev->dma);
    dev->urb  = usb_alloc_urb(0, GFP_KERNEL);
    if (!dev->buf || !dev->urb)
        goto err;

    usb_fill_bulk_urb(dev->urb, dev->udev,
                      usb_rcvbulkpipe(dev->udev, ep->bEndpointAddress),
                      dev->buf, BUFLEN, bulk_in_complete, dev);
    usb_set_intfdata(intf, dev);
    return usb_submit_urb(dev->urb, GFP_KERNEL);     /* 提交后异步收包 */
err:
    usb_free_urb(dev->urb);
    usb_free_coherent(dev->udev, BUFLEN, dev->buf, dev->dma);
    usb_put_dev(dev->udev);
    kfree(dev);
    return -ENOMEM;
}

static void my_disconnect(struct usb_interface *intf)
{
    struct my_dev *dev = usb_get_intfdata(intf);

    usb_kill_urb(dev->urb);                    /* 等待在途 URB 终止后再释放 */
    usb_free_urb(dev->urb);
    usb_free_coherent(dev->udev, BUFLEN, dev->buf, dev->dma);
    usb_put_dev(dev->udev);
    kfree(dev);
}

static const struct usb_device_id my_ids[] = {
    { USB_DEVICE(MY_VID, MY_PID) },
    { }                                        /* 终止项 */
};
MODULE_DEVICE_TABLE(usb, my_ids);              /* 支撑热插拔自动加载 */

static struct usb_driver my_driver = {
    .name       = "my_usb",
    .id_table   = my_ids,
    .probe      = my_probe,
    .disconnect = my_disconnect,
};
module_usb_driver(my_driver);                  /* 注册/注销一步到位 */
MODULE_LICENSE("GPL");
```

配套 Makefile 一行：`obj-m += my_usb.o && make -C /lib/modules/$(uname -r)/build M=$PWD modules`。

**DKMS 打包一句话**：源码放进 `/usr/src/my_usb-1.0/`（含 `Makefile` 与声明 `PACKAGE_NAME/VERSION`、`MAKE/INSTALL` 命令的 `dkms.conf`），执行 `sudo dkms add -m my_usb -v 1.0 && sudo dkms build -m my_usb -v 1.0 && sudo dkms install -m my_usb -v 1.0`，此后每次内核升级 DKMS 自动重编安装——产品分发内核模块的事实标准。

### 三、两平台对比收尾

| 维度 | macOS | Linux |
|---|---|---|
| 免驱用户态首选 | libusb（后端 IOUSBHost）或 IOKit 直访 | libusb（后端 usbfs）/ hidraw |
| 权限模型 | entitlement + 签名 + 公证，受限能力向 Apple 申请 | 文件权限 + udev 规则（MODE/GROUP 或 uaccess），管理员说了算 |
| 正式驱动路线 | DriverKit (DEXT)，kext 已淘汰 | 内核 `usb_driver` 客户端驱动，DKMS 分发 |
| 内核崩溃代价 | DEXT 用户态进程崩溃不影响系统 | oops/panic，注意 URB 与内存生命周期 |
| 热插拔 | IOKit 通知（IOServiceAddMatchingNotification） | udev/netlink（libusb_hotplug 封装） |
| 抓包 | 无原生（见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](50-debug-troubleshooting.md)） | usbmon + Wireshark 原生 |

共同心法：**能用用户态就别进内核**——两平台的正式驱动路线（DEXT/DKMS 模块）都是最后手段，前期用用户态把协议跑通、描述符调稳（见 [06-实战-libusb主机程序](42-linux-macos-libusb.md)、[07-实战-LinuxGadget与usbip](42-linux-macos-libusb.md)），再决定要不要下沉。
