---
name: build-usb-device
description: 从零创建 USB 设备侧或主机侧工程：TinyUSB 固件（HID/CDC/MSC）、libusb 主机程序、Linux configfs gadget 虚拟设备。当用户要"做一个 USB 设备""写个上位机读 USB 设备""把开发板模拟成键鼠/串口"时使用。按"选形态 → 照模板生成 → 按 checklist 验证"执行。
---

# 构建 USB 设备/主机工程

## 第 0 步：选择形态（按用户目标路由）

| 用户目标 | 形态 | 模板章节 | 前置条件 |
|---|---|---|---|
| 开发板变成键鼠/串口/存储 | TinyUSB 设备固件 | [实战-TinyUSB设备固件](../../60-枝干-主机侧与实现/05-实战-TinyUSB设备固件.md) | MCU 有 USB 外设（RP2040/STM32/ESP32-S3） |
| PC 程序读写已有 USB 设备 | libusb 用户态程序 | [实战-libusb主机程序](../../60-枝干-主机侧与实现/06-实战-libusb主机程序.md) | 设备接口可免驱（HID/CDC/WinUSB）或已装驱动 |
| Linux 机器模拟成 USB 设备 | configfs gadget | [实战-LinuxGadget与usbip](../../60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md) | UDC 硬件或 dummy_hcd；usbip 需 3240 端口 |
| 只改协议行为不改硬件 | 先看 [usbip](../../60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md) 远程共享或 gadget | 同上 | — |

## 第 1 步：固件形态（TinyUSB 路线）

1. 照模板建工程：`tusb_config.h` → `usb_descriptors.c`（设备/配置/字符串描述符回调）→ `main.c`（`tud_task()` 轮询 + 类回调）；
2. 描述符设计遵循树干契约：[描述符详解](../../10-树干-USB核心/07-描述符详解.md)；复合设备（HID+CDC）必须带 IAD，参考 [设备类索引](../../20-枝干-设备类协议/00-设备类索引.md)；
3. HID 报告描述符用官方宏（`TUD_HID_REPORT_DESC_KEYBOARD()`），自定义设备先读 [报告描述符与 Item 编码](../../20-枝干-设备类协议/HID-人机接口设备/02-报告描述符与Item编码.md)。

**验证 checklist**（任一失败回到对应知识树章节）：
- [ ] `lsusb -v` / USBTreeView 能完整解析全部描述符（长度自洽）；
- [ ] 枚举一次成功，无 dmesg 错误（[排查技能](../usb-enum-troubleshoot/SKILL.md)兜底）；
- [ ] 键盘击键 → 主机收到中断 IN 报告；CDC 打开 → DTR 翻转事件到达固件。

## 第 2 步：主机形态（libusb 路线）

1. 免驱前置：HID/CDC 接口天然免驱；厂商类设备需 MS OS 描述符或 Zadig 替换 WinUSB（对比见 [实战-libusb](../../60-枝干-主机侧与实现/06-实战-libusb主机程序.md) 开头表）；
2. Linux 下先写 udev 规则免 sudo；
3. 照模板：init → 按 VID/PID 查找 → claim_interface → 同步传输起步 → 需要吞吐再改异步。

**验证 checklist**：
- [ ] `libusb_get_device_list` 能发现目标设备；
- [ ] `claim_interface` 成功（失败=被内核驱动占用，先 detach 或换接口）；
- [ ] 一次 bulk 回环（配合_LOOPback 固件或 gadget）收发一致。

## 第 3 步：gadget 形态（Linux 模拟设备）

照 [实战-LinuxGadget与usbip](../../60-枝干-主机侧与实现/07-实战-LinuxGadget与usbip.md) 的完整 bash 脚本执行（libcomposite → functions → configs → UDC 绑定）。

**验证 checklist**：
- [ ] 对端主机 `lsusb` 出现自定义 VID/PID；
- [ ] hid gadget 在对端产生输入设备；acm gadget 产生 ttyACM/ttyGS0 互通。

## 通用回退

- 枚举失败 → [usb-enum-troubleshoot](../usb-enum-troubleshoot/SKILL.md)；
- 描述符/请求码疑义 → [usb-spec-lookup](../usb-spec-lookup/SKILL.md) 查缓存规范；
- 需要看主机实际收发 → [usb-capture-analysis](../usb-capture-analysis/SKILL.md)。
