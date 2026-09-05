---
title: "实战：libusb 跨平台主机程序"
layer: 枝干/主机侧与实现
doc-path: 60-枝干-主机侧与实现/06-实战-libusb主机程序.md
---
# 实战：libusb 跨平台主机程序

> 🌳 知识树位置: 树干 → 枝干[主机侧与实现] → 叶
> ⬆️ 父节点: [04-libusb与用户态访问](04-libusb与用户态访问.md)
> 工具与官方文档缓存索引: [../80-参考资料/README.md](../80-参考资料/README.md)

本文从零写一个能跑的 [libusb](https://libusb.info) 1.0 主机程序：环境准备 → 单文件完整示例（约 120 行，逐段讲解）→ 异步传输 → 热插拔 → Python 对照 → 错误码速查。编程模型总览见 [04-libusb与用户态访问](04-libusb与用户态访问.md)，本文全部是可照抄的实战代码。

- 依赖版本：libusb ≥ 1.0.23（示例只用到 1.0.16 时代稳定 API，最新版以官方 API 文档 [github.com/libusb/libusb](https://github.com/libusb/libusb) 为准）
- 设备端配套：任意提供批量（Bulk）IN/OUT 端点的自定义设备；可直接用 [05-实战-TinyUSB设备固件](05-实战-TinyUSB设备固件.md) 的思路扩展一个 vendor 接口来配对测试

## 一、环境搭建：各平台驱动与权限

libusb 在各平台走不同内核后端，**设备侧的驱动绑定决定了程序能不能打开设备**：

| 平台 | 要求 | 说明 |
|---|---|---|
| Linux | udev 规则放权限 | 不装任何驱动；内核类驱动可用 auto-detach 绕开 |
| Windows | 设备须绑定 WinUSB/libusbK 驱动 | 两条路线：Zadig 手动替换，或设备固件自带 MS OS 描述符免驱 |
| macOS | 无需任何驱动 | 首次访问触发系统授权弹窗，允许即可 |

### Windows：Zadig 替换 vs MS OS 描述符免驱

| 维度 | Zadig 手动替换 | MS OS 描述符（免驱） |
|---|---|---|
| 原理 | 工具把设备的驱动绑定改成 WinUSB/libusbK | 固件在描述符层面声明 `CompatibleID = "WINUSB"`，Windows 自动装 WinUSB |
| 操作 | 插上设备 → 选 VID/PID → 目标驱动选 WinUSB → Install Device | 固件实现 MS OS 1.0 字符串（索引 0xEE）或 MS OS 2.0 描述符（挂在 BOS 上，Win8.1+） |
| 风险 | **全局替换**该设备的驱动：原厂软件可能失效；绝不用于键鼠/存储等系统依赖设备 | 无侵入，随固件走；但需要改固件描述符 |
| 适用 | 调试期临时设备、二手模块 | 量产产品标准做法 |

结论：**自己开发固件，直接做 MS OS 描述符；调试别人的设备，用 Zadig 认准 VID/PID/描述串再点**。

### Linux：udev 规则

非 root 用户访问设备需要 udev（userspace dev）授权。新建 `/etc/udev/rules.d/99-usbtree.rules`：

```
# VID=cafe PID=4004：放开读写权限
SUBSYSTEM=="usb", ATTRS{idVendor}=="cafe", ATTRS{idProduct}=="4004", MODE="0666"
```

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
# 重插设备生效；查询设备节点: udevadm info -n /dev/bus/usb/001/005
```

## 二、完整示例：bulk_demo.c（单文件约 120 行）

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

### 逐段讲解

1. **init（步骤 1）**：`libusb_context` 是会话句柄；多线程程序可共享一个 ctx，或每线程独立 ctx。日志级别建议先 WARNING，排查时临时开 LIBUSB_LOG_LEVEL_DEBUG 看每次 URB（USB Request Block，USB 请求块）的内核调用。
2. **查找（步骤 2）**：`libusb_open_device_with_vid_pid` 是便捷函数；需要按"接口类/序列号/多设备遍历"筛选时，改用 `libusb_get_device_list` + `libusb_get_device_descriptor` 逐个比对后 `libusb_open`（模式见 [04-libusb与用户态访问](04-libusb与用户态访问.md)）。
3. **配置与接口（步骤 3）**：`set_configuration` 必须在 claim 之前；`claim_interface` 是独占声明，被内核类驱动占用时返回 `LIBUSB_ERROR_BUSY`。`set_auto_detach_kernel_driver` 只在 Linux 生效，Windows 上调用返回 0 但不做事。
4. **同步传输（步骤 4）**：`libusb_bulk_transfer` 阻塞直到完成/超时/出错；超时给 2000ms，**不要传 0**（表示无限等待）。`transferred` 指示实际字节数，短包（小于申请长度）不算错误。
5. **控制传输（步骤 5a/5b）**：`libusb_control_transfer` 把 bmRequestType/bRequest/wValue/wIndex/wLength 五元组一次传参，IN 请求返回收到的字节数、OUT 请求返回已发字节数；它不需要先 claim 接口（走端点 0）。
6. **清理（步骤 6）**：漏掉 release/close 在进程退出时通常无害，但常驻进程必须成对释放，否则接口被自己占用。

## 三、异步传输骨架

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

经验值：`QUEUE_DEPTH × BUF_SIZE` 决定吞吐上限；Linux 上单次提交超过 usbfs 限制会报 `LIBUSB_ERROR_NO_MEM`，处置见 [04-libusb与用户态访问](04-libusb与用户态访问.md)。

## 四、热插拔：到达即打开

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

## 五、Python 对照版（pyusb，约 20 行）

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

HID 设备建议直接用 hidapi（`pip install hid`），免分离内核 HID 驱动，选型对照见 [04-libusb与用户态访问](04-libusb与用户态访问.md)。

## 六、错误码速查表

| 错误码 | 值 | 典型原因 | 处置 |
|---|---|---|---|
| `LIBUSB_SUCCESS` | 0 | — | — |
| `LIBUSB_ERROR_IO` | -1 | 线缆差/设备死机/后端底层错误 | 重试；换线换口；抓包定位（见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)） |
| `LIBUSB_ERROR_ACCESS` | -3 | Linux 权限不足；Windows 句柄被占 | 补 udev 规则或 sudo；关闭占用该设备的其他程序 |
| `LIBUSB_ERROR_NO_DEVICE` | -4 | 传输中途设备被拔出 | 释放句柄，回热插拔逻辑重新等设备 |
| `LIBUSB_ERROR_NOT_FOUND` | -5 | 端点/接口不存在，或配置未设置 | 核对端点地址与描述符；先 `set_configuration` |
| `LIBUSB_ERROR_BUSY` | -6 | 接口被内核驱动占用 | auto-detach、卸载驱动模块或换接口号 |
| `LIBUSB_ERROR_TIMEOUT` | -7 | 设备对请求持续 NAK（固件没收/没发） | 查固件端点处理；加大超时；抓包看是否 IN/OUT 停等 |
| `LIBUSB_ERROR_PIPE` | -9 | 端点返回 STALL（halted） | `libusb_clear_halt(h, ep)` 恢复；检查固件为何 stall |
| `LIBUSB_ERROR_OVERFLOW` | -8 | 数据比缓冲大（设备发超） | 加大缓冲或核对端点包大小 |
| `LIBUSB_ERROR_NO_MEM` | -11 | Linux usbfs 内存上限（默认 16MB） | 调大 `usbcore.usbfs_memory_mb`（见 [04-libusb与用户态访问](04-libusb与用户态访问.md)） |
| `LIBUSB_ERROR_NOT_SUPPORTED` | -12 | 平台不支持该调用（如 Windows 调 detach_kernel_driver） | 代码里按平台跳过，不当作致命错误 |

通用打印：`libusb_error_name(rc)` 给出符号名，`libusb_strerror(rc)` 给出人话描述。

## 七、编译与安装命令

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

## 相关节点

- [04-libusb与用户态访问](04-libusb与用户态访问.md)：API 全景与各平台后端差异，本文是其跑通篇
- [02-操作系统USB支持](02-操作系统USB支持.md)：libusb 依赖的 usbfs/WinUSB/IOKit 各自层次
- [05-实战-TinyUSB设备固件.md](05-实战-TinyUSB设备固件.md)：配对的自制设备端
- [../10-树干-USB核心/06-四种传输类型.md](../10-树干-USB核心/06-四种传输类型.md)：bulk/control API 背后的传输语义
- [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)：错误码看不懂时的抓包手段
