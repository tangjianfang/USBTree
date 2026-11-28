---
title: "USB AI 加速器与 AI 外设"
layer: 枝干/AI时代的USB
doc-path: 78-AI时代的USB/06-USB-AI加速器与AI外设.md
---
# USB AI 加速器与 AI 外设

> 🌿 知识树位置: 树干 → 枝干[AI 时代的 USB] → B 篇 · 叶
> ⬆️ 返回: [00-索引](00-索引.md) · 相关: [DFU 固件升级](../20-枝干-设备类协议/其他设备类/01-DFU固件升级.md) · [WebUSB 与厂商自定义类](../20-枝干-设备类协议/其他设备类/06-WebUSB与厂商自定义类.md)

"插一根棒子就能跑 AI"是 USB 推理加速器最大的卖点。本篇用官方资料和开源驱动源码，看清这类设备在 USB 上到底长什么样、该怎么选、有哪些坑。

## 一、Google Coral USB Accelerator

**【事实】** 官方技术参数（[产品页](https://gweb-coral-full.uc.r.appspot.com/products/accelerator/)、[入门文档](https://gweb-coral-full.uc.r.appspot.com/docs/accelerator/get-started/)）：

| 项 | 官方口径 |
|---|---|
| 加速器 | Google Edge TPU 协处理器，4 TOPS（int8），2 TOPS/W（每 TOPS 0.5 W） |
| 接口 | USB 3.0 Type-C（数据与供电）；兼容 USB 2.0，但推理速度更慢 |
| 主机系统 | Debian 系 Linux（含树莓派）、macOS、Windows 10 |
| 模型 | TensorFlow Lite 模型经 Edge TPU Compiler 编译后运行 |
| 运行频率 | 标准运行时 `libedgetpu1-std` 降频运行；`libedgetpu1-max` 全频运行，速度更快但功耗更高，官方警告金属外壳可能烫伤 |

> 注：截至本文写作（2026-11），`coral.ai` 首页已改为介绍新的 Coral 平台（RISC-V NPU 架构），USB Accelerator 的产品页与文档仍可在上面的地址访问。

**【事实】它在 USB 上的真实行为——两次枚举。** 开源运行时 [libedgetpu 的 USB 驱动](https://github.com/google-coral/libedgetpu/blob/master/driver/usb/usb_driver.cc) 定义了两组 ID：DFU 模式 `1A6E:089A`，应用模式 `18D1:9302`。打开设备时，若设备处于 DFU 模式，运行时先用内置或指定的固件镜像做 DFU 下载；若已在应用模式则可发送 DFU Detach。也就是说，**设备上电后先以 DFU 设备出现，由主机端运行时下载固件后再以另一个 VID:PID 重新枚举**。

**【经验】** 由此推出几个实战要点：

- **udev 规则、虚拟机 USB 直通、容器设备映射都要覆盖两组 ID**。只放行 `18D1:9302` 的话，设备永远停在 DFU 模式；只放行 `1A6E:089A` 的话，下载完固件重新枚举后虚拟机就"丢了"设备。
- 在 Wireshark 里看到"设备断开又以新 ID 出现"是正常流程，不是掉线。
- Agent 自动化测试时，把"等待重新枚举"写进流程，超时设长一些（源码里重试间隔为 1 s、复位后最多重试 25 次）。

**【计算】供电预算。** 按厂商口径，4 TOPS × 0.5 W/TOPS = 2 W（这是推理核心按厂商能效比推算的值，不是整机实测）。对照 USB 规范的默认端口供电：USB 2.0 高功率端口 500 mA × 5 V = 2.5 W（USB 2.0 §7.2.1），USB 3.x 900 mA × 5 V = 4.5 W。**【经验】** 在 USB 2.0 口或无源集线器下跑全频运行时，余量很小；树莓派一类主板上同时挂摄像头和加速棒时，优先用有源集线器或 Type-C 供电口。

## 二、Intel Neural Compute Stick 2：已停产

**【事实】** Intel 已停产 NCS2（[停产通知](https://www.intel.com/content/www/us/en/support/articles/000093181/boards-and-kits.html)、[PCN 118636](https://www.intel.com/content/www/us/en/content-details/807455/intel-r-neural-compute-stick-2-pcn-118636-01-product-discontinuance-product-end-of-life-reason-for-revision-updates-on-recommended-replacement-product.html)）：

| 节点 | 日期 |
|---|---|
| 最后订货 | 2022-02-28 |
| 最后发货 | 2022-06-30 |
| 技术支持结束 | 2023-06-30 |
| 保修结束 | 2024-06-30 |
| 软件 | OpenVINO 支持到 2022.3，之后只在 2022.3.x LTS 线上维护 |

**【观点】** 新项目不要再选 NCS2；手上的存量设备若要继续用，固定在 OpenVINO 2022.3.x LTS，不要随主线升级。很多网络教程仍把 NCS2 当作"入门首选"，这是典型的过时信息，也是 AI 助手容易给出的过时建议。

## 三、Hailo：主力形态是 PCIe，不是 USB

**【事实】** Hailo 官方加速器产品页（[AI Accelerators](https://hailo.ai/products/ai-accelerators/)）列出的形态为：Hailo-8 M.2（26 TOPS）、Hailo-8L M.2（13 TOPS）、Hailo-8R mPCIe（13 TOPS）、Hailo-8 Century PCIe 卡（最高 208 TOPS）、Hailo-10H M.2（生成式 AI）。官方页面未列 USB 形态。树莓派官方 AI Kit / AI HAT+ 同样通过 PCIe 连接 Hailo 芯片（[树莓派文档](https://www.raspberrypi.com/documentation/accessories/ai-kit.html)）。

**【观点】** 这反映了一个趋势：算力上到十几、几十 TOPS 后，USB 2.0/3.x 的带宽与延迟、以及端口供电都开始成为瓶颈，厂商倾向于 M.2/PCIe。要在只有 USB 口的主机上用这类模块，就要走 USB4/雷电的 PCIe 隧道（见 [08 篇](08-USB4雷电外接GPU与AI设备供电.md)），而不是找"USB 版"。

## 四、AI 摄像头与其他 AI 外设

**【事实】** UVC 规范提供扩展单元（Extension Unit，XU），允许厂商在标准视频控制接口内定义私有控制（见 [UVC 详解](../20-枝干-设备类协议/Video-UVC/00-UVC详解.md)）；需要更大的数据通道时，复合设备可以另带一个厂商自定义接口（见 [WebUSB 与厂商自定义类](../20-枝干-设备类协议/其他设备类/06-WebUSB与厂商自定义类.md)）。

**【观点】** 带板载 NPU 的智能摄像头，一般有三种把"推理结果"交给主机的方式：

| 方式 | 优点 | 缺点 |
|---|---|---|
| 视频流叠加（结果画在画面上） | 主机零驱动 | 主机拿不到结构化数据 |
| UVC XU 控制 + 标准视频流 | 免驱视频，结构化元数据走控制传输 | 控制传输带宽小、需要轮询 |
| 复合设备：UVC + 厂商批量接口/CDC | 元数据带宽大、可推送 | 主机需要专用软件；Windows 上要配 WinUSB/MS OS 描述符 |

## 五、选型核对表

- [ ] 厂商当前是否仍在供货与维护？最后一次运行时/SDK 发布是什么时候？（NCS2 的教训）
- [ ] 设备是否会多次枚举（DFU → 应用）？直通与权限规则是否覆盖全部 ID？（Coral 的教训）
- [ ] 需要 USB 3.x 才能达到标称性能吗？主机口和线缆是否真的是 USB 3.x？
- [ ] 端口供电是否够用？最坏情况（全频）功耗是多少？是否需要有源集线器？
- [ ] 主机系统与 Python/框架版本是否在官方支持列表内？（Coral 入门文档写明 Python 3.6–3.9）
- [ ] 推理结果如何回传？是否需要专用驱动？

## 相关节点

- [UVC 与 UAC 喂给模型：带宽与延迟计算](07-UVC与UAC喂给模型-带宽与延迟计算.md) · [USB4/雷电外接 GPU 与 AI 设备供电](08-USB4雷电外接GPU与AI设备供电.md)
- [电源管理与挂起唤醒](../10-树干-USB核心/10-电源管理与挂起唤醒.md) · [经验与坑](12-经验与坑.md)
