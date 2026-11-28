---
title: 框架与 API
description: 从应用代码访问 USB 设备的框架与 API：浏览器 WebUSB / WebHID / Web Serial，Node.js 的 node-usb / node-hid，C 的 libusb / hidapi，Python 的 pyusb，以及 Rust、Go、.NET 生态。本分枝正在编写，先从下面这些站内页面开始。
topic: frameworks
---

:::note[本分枝正在编写]
“框架与 API”会按语言与运行环境梳理主机侧 USB 编程接口：能力边界、权限模型、各平台驱动要求与示例代码。正式内容合入仓库后，本页会自动换成该分枝的目录页。
:::

## 现在就能读的

- [libusb 与用户态访问](page:60-枝干-主机侧与实现/04-libusb与用户态访问.md) 与 [实战：libusb 主机程序](page:60-枝干-主机侧与实现/06-实战-libusb主机程序.md)：C 语言用户态访问的基础。
- [WebUSB 与厂商自定义类](page:20-枝干-设备类协议/其他设备类/06-WebUSB与厂商自定义类.md)：浏览器直连设备需要固件提供什么。
- [macOS 与 Linux 主机开发](page:60-枝干-主机侧与实现/09-macOS与Linux主机开发.md)、[Windows USB 驱动开发](page:60-枝干-主机侧与实现/08-WindowsUSB驱动开发.md)：各平台的驱动与权限前提。
- [usbtest 产测框架](page:labs/usbtest)：hidapi / pyusb / pyserial / bleak 在产线工具里的实际用法。
