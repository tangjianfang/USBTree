---
title: "macOS 与 Linux 主机开发"
layer: 枝干/主机侧与实现
doc-path: 60-枝干-主机侧与实现/09-macOS与Linux主机开发.md
---
# macOS 与 Linux 主机开发

> 🌿 知识树位置: 树干 → 枝干[主机侧与实现] → 叶
> ⬆️ 返回: [../10-树干-USB核心/02-体系架构与分层模型.md](../10-树干-USB核心/02-体系架构与分层模型.md) · 规范缓存索引: [../80-参考资料/README.md](../80-参考资料/README.md)
> 前置: [02-操作系统USB支持](02-操作系统USB支持.md)（三平台全景）· [04-libusb与用户态访问](04-libusb与用户态访问.md)（统一用户态 API）

macOS 与 Linux 都走"类驱动绑定 + 用户态兜底"的模式，但权限模型截然不同：macOS 用 entitlement/签名体系层层把关，Linux 用 udev 规则+文件权限的开放模型。本文梳理两平台各自的用户态/内核态开发路线与最小骨架。平台 API 随版本演进，**以 Apple 与内核官方文档为准**。

## 一、macOS

### 1.1 三条路线与权限模型

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

### 1.2 用户态直访骨架（IOKit）

老代码（libusb 旧版、大量开源工具）经 CFPlugIn 插件接口访问 `IOUSBDeviceInterface32x` 系列——**该路径自 macOS 10.11 起随 IOUSBFamily 一并废弃，此处仅作流程示意（伪代码级）**；新栈 `IOUSBHostFamily` 的用户客户端没有公开的 CFPlugIn 封装，实践上要么走 libusb（其后端即 IOUSBHost，见 [04-libusb与用户态访问](04-libusb与用户态访问.md)），要么 `IOServiceOpen` 打开 IOUSBHostDevice/Interface（用户客户端类型常量以官方文档为准）。流程骨架：

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

### 1.3 DEXT 适用场景与发布约束

- **什么时候写 DEXT**：设备需要专属驱动策略（独占接口、实现私有类语义）、要在 iPadOS（DriverKit 已带去）复用、或 kext 已无处可加载（Apple Silicon 量产机型）。纯上位机通信不必写 DEXT——先试 IOKit 直访或 libusb。
- **签名链**：DEXT 至少需要 Developer Program 团队签名 + 公证；受限 entitlement（USB/HID 族）提交 Apple 申请表批准后绑定到具体 VID。开发期可用 `com.apple.developer.driverkit.developer-mode`-类临时权限在自家机器调试（名目以官方文档为准）。
- **安装体验**：用户首次需在"系统设置 → 隐私与安全性"批准系统扩展；复用一个 App Bundle 携带 DEXT 是标准形态。

## 二、Linux

### 2.1 四种用户态途径

| 途径 | 位置/依赖 | 能做什么 | 权限来源 | 适用 |
|---|---|---|---|---|
| **libusb 1.0** | 用户态库，后端即 usbfs | 控制传输 + 4 类传输全量、热插拔事件、跨平台 | 打开 `/dev/bus/usb/BB/DD` 的文件权限 | 绝大多数自定义设备首选（见 [04](04-libusb与用户态访问.md)） |
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

如果该接口已被内核类驱动绑定，先经 `USBDEVFS_IOCTL` 发 `USBDEVFS_DISCONNECT` 把驱动踢掉（libusb 的 `libusb_kernel_driver_active`/`detach_kernel_driver` 内部即此套路），或用 [02-操作系统USB支持](02-操作系统USB支持.md) 的 sysfs unbind。

### 2.2 内核态最小驱动骨架

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

## 三、两平台对比收尾

| 维度 | macOS | Linux |
|---|---|---|
| 免驱用户态首选 | libusb（后端 IOUSBHost）或 IOKit 直访 | libusb（后端 usbfs）/ hidraw |
| 权限模型 | entitlement + 签名 + 公证，受限能力向 Apple 申请 | 文件权限 + udev 规则（MODE/GROUP 或 uaccess），管理员说了算 |
| 正式驱动路线 | DriverKit (DEXT)，kext 已淘汰 | 内核 `usb_driver` 客户端驱动，DKMS 分发 |
| 内核崩溃代价 | DEXT 用户态进程崩溃不影响系统 | oops/panic，注意 URB 与内存生命周期 |
| 热插拔 | IOKit 通知（IOServiceAddMatchingNotification） | udev/netlink（libusb_hotplug 封装） |
| 抓包 | 无原生（见 [../70-枝干-调试测试与安全/01-协议分析仪与抓包.md](../70-枝干-调试测试与安全/01-协议分析仪与抓包.md)） | usbmon + Wireshark 原生 |

共同心法：**能用用户态就别进内核**——两平台的正式驱动路线（DEXT/DKMS 模块）都是最后手段，前期用用户态把协议跑通、描述符调稳（见 [06-实战-libusb主机程序](06-实战-libusb主机程序.md)、[07-实战-LinuxGadget与usbip](07-实战-LinuxGadget与usbip.md)），再决定要不要下沉。

## 相关节点

- [02-操作系统USB支持](02-操作系统USB支持.md)：三平台组件地图与 udev 规则速查
- [04-libusb与用户态访问](04-libusb与用户态访问.md)：跨平台统一 API，本篇两平台的公共捷径
- [06-实战-libusb主机程序](06-实战-libusb主机程序.md) · [07-实战-LinuxGadget与usbip](07-实战-LinuxGadget与usbip.md)：可直接运行的实战
- [../70-枝干-调试测试与安全/04-USB安全与BadUSB.md](../70-枝干-调试测试与安全/04-USB安全与BadUSB.md)：平台权限模型为什么"紧"
- [../10-树干-USB核心/10-电源管理与挂起唤醒.md](../10-树干-USB核心/10-电源管理与挂起唤醒.md)：挂起唤醒的协议层约束
