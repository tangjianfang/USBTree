---
title: "libusb 与用户态访问"
layer: 枝干/主机侧与实现
doc-path: 60-枝干-主机侧与实现/04-libusb与用户态访问.md
---
# libusb 与用户态访问

> 🌿 知识树位置: 树干 → 枝干[主机侧与实现] → 叶
> ⬆️ 返回: [../10-树干-USB核心/06-四种传输类型.md](../10-树干-USB核心/06-四种传输类型.md)

大多数自定义 USB 设备并不需要内核驱动：现代操作系统都提供用户态通道（WinUSB / usbfs / IOKit），而 **libusb 1.0** 把三条路统一成一个 API。本文给出完整的编程模型、生态选型与实战坑位。

## 一、为什么用户态直接访问

| 内核驱动路线 | 用户态路线 |
|---|---|
| 需要签名/安装 INF，跨平台各写一份 | 一个二进制跨三大平台 |
| 崩溃蓝屏/内核 oops | 崩溃只是进程退出 |
| 开发迭代慢 | printf 直接调试 |
| 独占：内核类驱动先绑走，用户拿不到 | 控制绑定关系，接口归属清晰 |

用户态的限制也要清楚：拿不到同步传输的硬件级优先保证之外的特殊调度、无法参与内核即插即用语义（比如伪装成键盘需要 HID 类驱动解析报告的场景除外——libusb 可以裸发报告但系统级"键盘"语义由 HID 栈实现）、高吞吐时受用户态轮询与内存上限约束。

## 二、libusb 1.0 编程模型（C）

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

### 异步传输（高吞吐必须）

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

### 热插拔（hotplug）

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

## 三、各平台内核后端

| 平台 | libusb 后端 | 底层通道 | 备注 |
|---|---|---|---|
| Linux | usbfs 后端 | `/dev/bus/usb/BB/DD` | 受 `usbfs_memory_mb` 限制（默认 16MB，高吞吐需调大：`usbcore.usbfs_memory_mb=1024` 或运行时 echo） |
| Windows | **WinUSB** 后端（默认） | `winusb.sys` | 设备需绑定 WinUSB 驱动（WCID/Zadig）；部分老功能（如同步传输的某些选项）受限 |
| Windows | **libusbK** 后端 | `libusbK.sys`（KMDF） | 功能更全（含同步传输），Zadig 中可手动选择 |
| Windows | usbDk（可选） | 驱动过滤 | 允许**不替换**原驱动并行访问，适合厂商驱动共存场景 |
| macOS | Darwin 后端 | IOKit | 首次访问会触发系统授权弹窗 |

### claim / detach 内核驱动

Linux 上标准类驱动（`usb-storage`、`usbhid` 等）会在设备出现时自动绑定，接口被占用后 `claim_interface` 返回 `LIBUSB_ERROR_BUSY`：

```c
/* 方式一：自动分离（推荐） */
libusb_set_auto_detach_kernel_driver(h, 1);

/* 方式二：显式分离（需权限，Windows/macOS 返回不支持错误） */
if (libusb_kernel_driver_active(h, 0) == 1)
    libusb_detach_kernel_driver(h, 0);
```

取舍：分离 `usb-storage` 后该设备不再有块设备节点，进程退出时应重绑或拔插恢复。

## 四、Python 生态与选型

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

## 五、USB/IP 与设备透传方案

| 方案 | 组成 | 典型场景 |
|---|---|---|
| **usbip** | Linux 内核模块 + `usbip` 工具；Windows 客户端有 usbip-win 项目 | 远程设备透传：实验室加密狗共享给多台机器（同一时刻独占） |
| **usbipd-win** | Windows 服务端 | **WSL2 USB 直通**：Windows 共享 → WSL 内 attach，Linux 工具链直接访问 |
| **usbredir** | spice 协议组件，配合 QEMU `usb-redir` chardev | 虚拟机远程 USB（SPICE 远程桌面内重定向本机设备） |
| QEMU usb-host | `-device usb-host,vendorid=0x1234,productid=0x5678` | 本机设备直通进 VM（Linux 宿主效果最好） |
| 商用方案 | VirtualHere 等 | 网络摄像头/加密狗跨平台共享，免自建 |

排查透传问题时记住：usbip/usbredir 都是把**原始 URB 级流量**搬过网线，主机端类驱动行为不变，抓包在两端语义一致。

## 六、调试组合拳

```bash
lsusb                        # 一行一设备：VID:PID
lsusb -v -d 1234:5678        # 全量描述符树形解析（枚举问题先看这个）
lsusb -t                     # 树形：速度/驱动/带宽
usbhid-dump -a 1:2           # 转储 HID 报告描述符与原始报告(usbutils)
udevadm info -q all -n /dev/bus/usb/001/005   # sysfs 全属性
```

Windows 侧等价物：UsbTreeView（见 [02-操作系统USB支持](02-操作系统USB支持.md)），配合 Wireshark+USBPcap（见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)）。

## 七、常见坑速查

| 坑 | 现象 | 处置 |
|---|---|---|
| 超时设 0 | `*_transfer` 永久阻塞 | 明确给 1000~5000ms；异步用 transfer 自身超时 |
| 接口不可 claim | `LIBUSB_ERROR_BUSY` | 内核驱动占用：auto-detach / `new_id` 换驱动 / 卸载模块 |
| Linux usbfs 内存上限 | 大吞吐提交报 `LIBUSB_ERROR_NO_MEM` | 调大 `usbfs_memory_mb`（sysfs 或内核参数） |
| Windows 驱动不匹配 | `LIBUSB_ERROR_NOT_SUPPORTED` | 用 Zadig 给该 VID/PID 安装 WinUSB/libusbK |
| Zadig 风险 | 原厂驱动被覆盖，官方软件失效 | Zadig 是**全局替换**该设备的驱动绑定：认准 VID/PID/描述串再点；恢复靠卸载设备勾选"删除驱动"后重装原厂包；绝不应用于键鼠/存储等系统依赖设备 |
| 配置未设置 | 传输报 `LIBUSB_ERROR_NOT_FOUND` | 先 `set_configuration(1)` |
| macOS 首次访问无响应 | 数据全 NAK | 系统弹窗未确认；到"系统设置→隐私与安全性"允许 |

## 相关节点

- [../10-树干-USB核心/06-四种传输类型.md](../10-树干-USB核心/06-四种传输类型.md)：transfer API 背后的传输语义
- [../10-树干-USB核心/08-枚举流程与标准请求.md](../10-树干-USB核心/08-枚举流程与标准请求.md)：control_transfer 发的就是这些请求
- [02-操作系统USB支持](02-操作系统USB支持.md)：libusb 在各平台踩到的内核层
- [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)：验证 libusb 行为的抓包手段
- [../70-枝干-调试测试与安全/04-USB安全与BadUSB.md](../70-枝干-调试测试与安全/04-USB安全与BadUSB.md)：用户态访问同样是攻击面，了解管控
