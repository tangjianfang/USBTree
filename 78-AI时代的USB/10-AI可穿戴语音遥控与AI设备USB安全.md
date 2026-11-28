---
title: "AI 可穿戴、语音遥控与 AI 设备的 USB 安全"
layer: 枝干/AI时代的USB
doc-path: 78-AI时代的USB/10-AI可穿戴语音遥控与AI设备USB安全.md
---
# AI 可穿戴、语音遥控与 AI 设备的 USB 安全

> 🌿 知识树位置: 树干 → 枝干[AI 时代的 USB] → B 篇 · 叶
> ⬆️ 返回: [00-索引](00-索引.md) · 前置: [HOGP：HID over GATT](../50-枝干-无线关联/BLE-低功耗蓝牙/07-HOGP-HIDoverGATT.md) · [USB 安全与 BadUSB](../70-枝干-调试测试与安全/04-USB安全与BadUSB.md)

AI 戒指、AI 眼镜、AI 胸针、带语音键的遥控器——这些设备平时走 BLE，充电、调试、升级走 USB-C。它们离 USB/HID 老本行很近，也把 USB 的老安全问题带进了新场景。

## 一、AI 可穿戴与语音遥控的协议拼图

**【事实】** HOGP（HID over GATT Profile）让 BLE 设备复用 USB HID 的报告描述符与 Usage 体系，主机侧的 HID 驱动几乎不用区分传输方式（见 [HOGP](../50-枝干-无线关联/BLE-低功耗蓝牙/07-HOGP-HIDoverGATT.md)、[HID 跨传输：I2C 与 BLE](../20-枝干-设备类协议/HID-人机接口设备/10-HID跨传输I2C与BLE.md)）。HUT 的 Consumer 页（0x0C）定义了 Voice Command（0xCF）等用于语音入口的 Usage（见 [HID 规范级附录](../20-枝干-设备类协议/HID-人机接口设备/12-HID规范级附录.md)）。

**【事实】** HOGP 只定义 HID 报告的承载，不定义音频通道。BLE 上的标准化音频是 LE Audio（LC3 编解码，见 [LE Audio 与 LC3](../50-枝干-无线关联/BLE-低功耗蓝牙/09-LEAudio与LC3.md)）；不走 LE Audio 的产品只能用厂商自定义 GATT 服务传语音。

| 功能 | 常见做法 | 标准依据 |
|---|---|---|
| 按键、语音键事件 | HOGP 消费控制报告（如 Voice Command 0xCF） | HOGP + HUT |
| 语音数据上行 | LE Audio，或厂商自定义 GATT 服务 | LE Audio 为 Bluetooth SIG 标准；自定义服务无统一规范 |
| 充电 | USB-C（Type-C 电流广播或 PD） | Type-C / USB PD |
| 调试、日志、产测 | USB-C 上的 CDC-ACM 或厂商接口 | CDC / 厂商自定义 |
| 固件升级 | BLE OTA（厂商方案）或 USB DFU | DFU 1.1（USB 侧） |

**【观点】** 对外设工程师而言，这类产品的难点通常不在协议，而在**功耗与延迟的取舍**：语音键按下到主机开始录音的延迟、连接间隔与电池寿命、何时从 HID 报告切到音频流。你在键鼠上积累的 BLE 连接参数调优经验（连接间隔、从机延迟、监督超时，见 [LLCP 控制过程全表](../50-枝干-无线关联/BLE-低功耗蓝牙/12-LLCP控制过程全表.md)）可以直接迁移。

## 二、BadUSB 在 AI 时代没有过时

**【事实】** 2014 年 Karsten Nohl 与 Jakob Lell 在 Black Hat 公开 BadUSB 研究：通过重编程 U 盘主控固件，让设备枚举成键盘等任意类型，而常规格式化和杀毒无法清除（见 [USB 安全与 BadUSB](../70-枝干-调试测试与安全/04-USB安全与BadUSB.md)）。其根源是主机根据描述符自动绑定驱动，USB 协议本身不验证设备固件。

**【观点】** AI 设备让这个老问题出现了几个新变体：

1. **复合设备更常见**：一个"AI 录音笔/AI 摄像头"同时枚举 UAC + UVC + HID + 网卡（NCM/RNDIS）并不罕见。每多一个接口，主机就多一个自动绑定的驱动和攻击面。
2. **设备字符串进入大模型上下文**：Agent 工具读取的描述符字符串若被当作指令，就是一条从物理设备到 AI 的提示词注入路径（见 [03 篇 4.4 节](03-AI辅助抓包分析与MCP工具.md)）。
3. **"AI 助手"类 HID 设备**：带宏键、可一键调起 AI 的键盘/遥控器本质上是能注入按键的 HID 设备；固件升级通道若未签名，就是一个现成的 BadUSB 载体。

## 三、主机侧的授权机制

**【事实】Linux USB 授权。** 内核支持按总线设置新设备默认不授权，再由用户态逐个放行（[内核文档 · Authorizing USB devices](https://docs.kernel.org/usb/authorization.html)）：

```bash
echo 0 > /sys/bus/usb/devices/usb1/authorized_default            # 总线 1 上新设备默认不授权
echo 1 > /sys/bus/usb/devices/1-2/authorized                      # 放行某个设备
echo 0 > /sys/bus/usb/devices/usb1/interface_authorized_default  # 也可以按接口粒度控制
```

**【事实】USBGuard** 在此基础上提供规则语言，按 VID:PID、序列号、接口类、连接端口等属性允许或拒绝设备（[usbguard.github.io](https://usbguard.github.io/)；规则示例见 [USB 安全与 BadUSB](../70-枝干-调试测试与安全/04-USB安全与BadUSB.md)）。

**【事实】Windows** 可以用组策略限制设备安装，按设备 ID、设置类等允许或阻止（[Manage Device Installation with Group Policy](https://learn.microsoft.com/en-us/windows/client-management/client-tools/manage-device-installation-with-group-policy)）；外接 PCIe/雷电设备的 DMA 由内核 DMA 保护约束（见 [08 篇](08-USB4雷电外接GPU与AI设备供电.md)）。

**【经验】** 对复合型 AI 设备，按**接口**授权比按设备授权更合适：例如只放行它的 UVC 和 UAC 接口，拒绝它的 HID 和网卡接口，除非业务确实需要。

## 四、USB Type-C Authentication

**【事实】** USB Type-C Authentication 规范定义了基于证书的**单向**产品认证：认证发起方（通常是主机或 PD Sink）可以验证响应方（设备、PD 电源、线缆）是否为它声称的厂商与产品。要点（[USB-IF Authentication](https://usb.org/authentication)、[USB-IF 项目发布](https://usb.org/sites/default/files/2019-01/USB-IF_USB%20Type-C%20Authentication%20Program%20Press%20Release_FINAL_20181227.pdf)、IEC 62680-1-4）：

| 项 | 内容 |
|---|---|
| 性质 | 可选规范；规范只提供机制，接受/拒绝的策略由产品或用户决定 |
| 承载 | USB PD 消息，或 USB 数据总线上的控制请求 |
| 密码学 | 证书 X.509v3（DER 编码）、签名 ECDSA NIST P-256、哈希 SHA-256，目标 128 位安全强度 |
| 证书 | USB-IF 证书机构代为签发，申请者需拥有自己的 VID |
| 现行版本 | Rev 1.0（含截至 2019-01-07 的 ECN 与勘误） |

**【观点】** 对 AI 边缘设备与高功率充电场景，它能回答"这个充电器/线缆是不是经过认证的正品"，但它不能回答"这个设备的固件是不是被改过"——那需要设备自己的安全启动与签名升级。两者要一起设计。

## 五、AI 设备 USB 安全清单

- [ ] 设备只暴露业务必需的接口；调试接口（CDC、厂商接口）在量产固件中关闭或需要认证才能打开
- [ ] 固件升级（USB DFU 或 BLE OTA）验证签名，失败可回滚，不接受降级到有漏洞的版本
- [ ] 字符串描述符不含可被误读为指令的内容；主机侧工具把描述符当数据处理并截断
- [ ] 主机侧部署按接口粒度的授权策略（Linux `authorized`/USBGuard，Windows 设备安装限制）
- [ ] 外接 PCIe（雷电/USB4）类 AI 设备确认 IOMMU/内核 DMA 保护开启
- [ ] 高功率供电场景评估 USB Type-C Authentication 的必要性
- [ ] 麦克风/摄像头类设备提供物理静音或指示灯，固件无法绕过（隐私）

## 相关节点

- [AI 辅助驱动/固件开发与模糊测试](04-AI辅助驱动固件开发与模糊测试.md) · [Agent 硬件在环测试与安全护栏](05-Agent硬件在环测试与安全护栏.md)
- [消费控制与多媒体](../20-枝干-设备类协议/HID-人机接口设备/07-消费控制与多媒体.md) · [USB-IF 合规认证](../70-枝干-调试测试与安全/03-USB-IF合规认证.md)
