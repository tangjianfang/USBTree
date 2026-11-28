---
title: "USB4/雷电外接 GPU 与 AI 设备供电"
layer: 枝干/AI时代的USB
doc-path: 78-AI时代的USB/08-USB4雷电外接GPU与AI设备供电.md
---
# USB4/雷电外接 GPU 与 AI 设备供电

> 🌿 知识树位置: 树干 → 枝干[AI 时代的 USB] → B 篇 · 叶
> ⬆️ 返回: [00-索引](00-索引.md) · 前置: [USB4 与雷电整合](../40-枝干-高速演进/02-USB4与雷电整合.md) · [USB PD 协议](../30-枝干-接口与供电/04-USBPD协议.md)

笔记本接一个外置显卡盒跑本地大模型、一根 Type-C 线给边缘 AI 盒子供 100 多瓦——这两件事都建立在 USB4/雷电的 PCIe 隧道和 USB PD 之上。本篇只回答两个可量化的问题：**链路有多宽**、**电够不够**。

## 一、外接 GPU 走的是 PCIe 隧道

**【事实】** USB4 通过隧道（tunneling）在同一条链路上承载 USB3、DisplayPort 与 PCIe（见 [USB4 深入：路由、隧道与配置](../40-枝干-高速演进/05-USB4深入-路由隧道与配置.md)）。外置 GPU 盒（eGPU/eGFX）用的就是 PCIe 隧道。

**【事实】** Intel 雷电官方资料（[Thunderbolt 5 Technology Brief](https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2023-09/thunderbolt-5-technology-brief.pdf)、[雷电概览页](https://www.intel.com/content/www/us/en/architecture-and-technology/thunderbolt/overview.html)）给出的电脑端最低要求：

| 项 | 雷电 5 | 雷电 4 | USB4（Intel 对比表口径） |
|---|---|---|---|
| 链路速率 | 80 Gbps 双向；Bandwidth Boost 发送最高 120 Gbps（接收 40 Gbps） | 40 Gbps | 20 Gbps |
| PCIe 数据 | **64 Gbps** | **32 Gbps** | 未列最低要求 |
| 电脑端口充电 | 至少一个口必须支持 140 W，可选最高 240 W | 必须 100 W，可选最高 140 W | — |
| DMA 保护 | 必须支持基于 Intel VT-d 的 DMA 保护 | 必须 | — |
| 规范 | 必须符合 USB4 规范 | 必须 | — |

**【事实】** Bandwidth Boost 基于 USB4 Version 2.0 规范中的非对称模式（同一技术简报）；USB4 v2.0 规范可在 [USB-IF 文档库](https://www.usb.org/document-library/usb4r-specification-v20) 获取。Intel JHL9580 雷电 5 控制器的 PCIe 配置为 x4 Gen 4（[Intel 产品规格](https://www.intel.com/content/www/us/en/products/sku/225921/intel-jhl9580-thunderbolt-5-controller/specifications.html)）。

**【观点】** "USB4 接口"不等于"能接显卡"：Intel 的对比表里 USB4 一栏没有 PCIe 最低要求，而雷电 4/5 对 PCIe 有硬性要求。买笔记本时要看厂商是否明确标注 PCIe 隧道支持或雷电认证。

## 二、链路宽度 vs 台式机插槽

PCIe 3.0 起使用 128b/130b 编码，每通道有效速率 = 传输速率 × 128/130。

| 链路 | 算式 | 有效带宽（单向） |
|---|---|---|
| PCIe 3.0 ×4（≈ 雷电 4 的 PCIe 32 Gbps） | 8 GT/s × 4 × 128/130 | 31.5 Gbit/s ≈ 3.94 GB/s |
| PCIe 4.0 ×4（≈ 雷电 5 的 PCIe 64 Gbps） | 16 GT/s × 4 × 128/130 | 63.0 Gbit/s ≈ 7.88 GB/s |
| PCIe 4.0 ×16（台式机插槽） | 16 GT/s × 16 × 128/130 | 252 Gbit/s ≈ 31.5 GB/s |
| PCIe 5.0 ×16（台式机插槽） | 32 GT/s × 16 × 128/130 | 504 Gbit/s ≈ 63.0 GB/s |

**【事实】** 以 RTX 5080 为例，NVIDIA 官方规格为 16 GB GDDR7、256 bit 显存位宽、支持 PCI Express Gen 5（[NVIDIA 产品页](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5080/)）。

**【计算】** 把 16 GB 权重从内存装进显存的理论下限：雷电 4（3.94 GB/s）约 4.1 s，雷电 5（7.88 GB/s）约 2.0 s，PCIe 5.0 ×16（63 GB/s）约 0.25 s。实际还有协议开销与存储读取时间，只会更长。

**【观点】** 对本地大模型推理，链路宽度的影响取决于数据是否需要反复过链路：

| 场景 | 每个 token 是否大量过链路 | 雷电/USB4 外接是否明显吃亏 |
|---|---|---|
| 模型完全装进显存，单卡推理 | 否（只有输入 token 和输出 logits 等少量数据） | 主要影响加载时间 |
| 显存不够，框架按层把权重从内存搬到显存 | 是，每次前向都要搬 | 明显，链路带宽直接限制速度 |
| 显存不够，卸载层在 CPU 上计算（如 llama.cpp 部分卸载） | 只有激活值过链路 | 影响较小，瓶颈在 CPU 与内存 |
| 多卡张量并行 | 是，层间频繁同步 | 明显，不建议跨雷电链路做 |
| 训练/微调（大批量数据） | 是 | 明显 |

## 三、USB PD 给 AI 边缘设备供电

**【事实】** USB PD 3.1 引入扩展功率范围（EPR），新增 28/36/48 V 固定电压，最高 48 V × 5 A = 240 W；EPR 需要支持 5 A 的 EPR 线缆（带 E-marker），并通过专门流程进入 EPR 模式（见本库 [USB PD 协议](../30-枝干-接口与供电/04-USBPD协议.md)；规范见 [USB-IF PD 文档库](https://www.usb.org/document-library/usb-power-delivery)）。

| 档位 | 电压 × 电流 | 功率 | 范围 |
|---|---|---|---|
| 默认 Type-C 电流 | 5 V × 1.5 A / 3 A | 7.5 / 15 W | Type-C 电流广播 |
| SPR | 9 V × 3 A | 27 W | SPR |
| SPR | 15 V × 3 A | 45 W | SPR |
| SPR | 20 V × 3 A | 60 W | SPR（3 A 线缆） |
| SPR | 20 V × 5 A | 100 W | SPR（需 5 A 线缆） |
| EPR | 28 V × 5 A | 140 W | EPR |
| EPR | 36 V × 5 A | 180 W | EPR |
| EPR | 48 V × 5 A | 240 W | EPR 上限 |

**【观点】** 给边缘 AI 设备设计供电时的几条原则：

1. **按峰值而不是平均值预算**。NPU/GPU 推理的功耗随负载跳变，PD 协商的是上限，超过合同功率时电源可以保护关断。
2. **留出降级路径**。插到只给 15 W 或 27 W 的充电器上时，设备应该降频继续工作并提示用户，而不是反复重启。PD 的 Source Capabilities 可以让固件在协商阶段就知道能拿到多少功率（消息结构见 [USB PD 消息全表](../30-枝干-接口与供电/08-USBPD消息全表.md)）。
3. **EPR 不是插上就有**：线缆、充电器、设备三方都要支持，任何一环不支持就停在 SPR（最高 100 W）。产品说明里要写清楚。
4. **"边供电边传数据"的设备**（如带 USB4 上行口的 AI 扩展坞）要把端口供电给下游设备的预算（雷电要求每端口最低 15 W 给配件，见上表出处）一并算进去。

## 四、AI PC：Copilot+ PC 的官方要求

**【事实】** Microsoft 公布的 Copilot+ PC 最低硬件要求（[Windows 11 规格页](https://www.microsoft.com/en-us/windows/windows-11-specifications)）：NPU 算力 40+ TOPS（当前包括 AMD Ryzen AI 300/400 系列、Intel Core Ultra 200V/300V 系列、Snapdragon X 系列）、16 GB DDR5/LPDDR5 内存、256 GB SSD/UFS 存储，外加 Windows 11 基本要求。截至本文写作，这份官方要求**没有列出 USB4 或雷电接口要求**。

**【观点】** 所以"AI PC 一定有 USB4/雷电"并不成立。若你的使用场景依赖外接显卡、高速外置存储或 80 Gbps 扩展坞，要单独核对机型的接口规格，不能从"Copilot+ PC"标签推断。

## 五、安全：PCIe 隧道 = DMA 通道

**【事实】** 外接 PCIe 设备可以发起 DMA，雷电 4/5 都要求电脑支持基于 VT-d 的 DMA 保护（见上文 Intel 技术简报）；Windows 的对应机制是"内核 DMA 保护"（[Kernel DMA Protection](https://learn.microsoft.com/en-us/windows/security/hardware-security/kernel-dma-protection-for-thunderbolt)），它阻止不支持 DMA 重映射的外部设备在用户登录前或锁屏时开始 DMA。

**【观点】** 外接 AI 加速盒本质上是一块插在外面的 PCIe 卡，在企业环境里应与外接显卡同等对待：确认 IOMMU/内核 DMA 保护已开启，再允许接入。更多见 [10 篇](10-AI可穿戴语音遥控与AI设备USB安全.md)。

## 相关节点

- [USB4 规范级：配置空间与隧道](../40-枝干-高速演进/07-USB4规范级-配置空间与隧道.md) · [AlternateMode 与 E-marker](../30-枝干-接口与供电/05-AlternateMode与E-marker.md)
- [USB AI 加速器与 AI 外设](06-USB-AI加速器与AI外设.md) · [本地模型 USB 助手工作流](13-本地模型USB助手工作流.md)
