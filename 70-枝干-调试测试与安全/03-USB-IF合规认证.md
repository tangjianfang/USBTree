---
title: "USB-IF 合规认证"
layer: 枝干/调试测试与安全
doc-path: 70-枝干-调试测试与安全/03-USB-IF合规认证.md
---
# USB-IF 合规认证

> 🌿 知识树位置: 树干 → 枝干[调试测试与安全] → 叶
> ⬆️ 返回: [../10-树干-USB核心/07-描述符详解.md](../10-树干-USB核心/07-描述符详解.md)

合规认证回答两个问题：**你的设备是否真的按规范工作**（互操作性与安全性），以及**你能否合法使用 USB 商标/Logo**。对开发者而言，更重要的是把认证背后的测试项内化为自查手段。

## 一、USB-IF 与合规程序

**USB-IF（USB Implementers Forum）** 是 USB 规范的制定与商标管理机构（由 USB 创始厂商组成的非营利组织）。其**合规程序(Compliance Program)** 覆盖三个独立维度：

| 维度 | 对象 | 典型测试载体 |
|---|---|---|
| 设备/主机认证 | U 盘、手机、主机控制器芯片… | 电气 + 协议 + 互操作三关 |
| 线缆/连接器认证 | C-to-C 线、充电线、eMarker 芯片 | 电气 + 机械 + eMarker 数据（需提交 VIF 获得 TID） |
| 供电认证 | PD 充电器/受电设备 | PD 协议 + 电源质量（见 [../30-枝干-接口与供电/](../30-枝干-接口与供电/)） |

## 二、测试项目全景

### 2.1 电气测试（Electrical Tests）

- **信号完整性眼图(Eye Diagram)**：按速度档在测试模式（test_J/K、test_Packet）下采样眼图，判定抖动、幅度、上升/下降时间是否落在模板内。HS 要求 480Mbps 眼图闭合判定；SS/SSP/USB4 有更严格的信道插损与回损指标。
- **上升/下降时间(Rise/Fall Time)**：驱动器边沿速率超标是互操作杀手（辐射 + 反射）。
- **浪涌电流(Inrush)**：插入瞬间对 100µF 等效负载的充电冲击限值，防止拖垮主机口（对应排障手册症状 D，见 [02-枚举失败排查手册](02-枚举失败排查手册.md)）。
- **VBUS 电压跌落/纹波、Drop/Droop**：满载与突发负载下的电压保持能力。
- Type-C 附加项：**CC 终端(Rp/Rd) 检测**、VBUS 通路电阻、eMarker 通信（SOP' 包）等。

### 2.2 协议测试（Chapter 9 Tests）

以规范第 9 章（设备框架）命名的协议合规测试，官方工具为 **USB Command Verifier (USBCV)**：

- 描述符合法性：各描述符字段取值域、长度自洽性、`bcdUSB` 与实际能力匹配；
- 标准请求响应：11 个标准请求的状态码、STALL 语义、非法请求必须 STALL 而非挂死；
- **挂起电流**：未配置挂起 ≤0.5mA、配置后挂起 ≤2.5mA；
- 恢复/远程唤醒行为、地址生效时机；
- 端点响应时序（NAK 限速、状态阶段时序）。

> USBCV 主要覆盖 2.0 系；3.x/USB4 的协议与链路层测试由授权实验室用专用设备执行。

### 2.3 互操作测试（Interop / PlugFest）

- **PlugFest**：USB-IF 定期举办的厂商互测活动，把自家设备与数十家厂商的主机/集线器交叉插拔；
- 覆盖典型组合矩阵：不同速度、经集线器、挂起唤醒、热插拔疲劳、多设备并发；
- 这是认证中"实验室测不出、用户用得出"问题的过滤器。

### 2.4 3.x / USB4 增项

- **链路训练测试**：LFPS 握手、LTSSM 状态机全路径、均衡(FFE/CTLE)协商；
- **隧道测试(Tunneling)**：USB4 路由器对 PCIe / DisplayPort 隧道的正确封装与带宽仲裁，及 Thunderbolt 3 兼容行为；
- 速率协商矩阵（5/10/20/40/80Gbps 各档回退兼容）。

## 三、Logo 授权体系

### 3.1 速率标识

认证通过 + 签署商标协议后方可使用认证标识。**2019 年起现行命名体系以能力命名，废弃了 3.0/3.1/3.2 消费者传播名**：

| 认证标识 | 对应规范速率 | 旧称（对照） |
|---|---|---|
| USB 5Gbps | 5Gbps | USB 3.0 / 3.1 Gen1 / 3.2 Gen1 (SuperSpeed) |
| USB 10Gbps | 10Gbps | USB 3.1 Gen2 / 3.2 Gen2 (SuperSpeed+) |
| USB 20Gbps | 20Gbps | USB 3.2 Gen2x2 |
| USB 40Gbps | 40Gbps | USB4 Gen 3x2 |
| USB 80Gbps | 80Gbps（非对称） | USB4 v2 |

| 功率标识 | 含义 |
|---|---|
| USB Certified Power 60W | 20V/3A（标准功率档 SPR） |
| USB Certified Power 100W | 20V/5A（SPR 上限） |
| USB Certified Power 240W | 48V/5A（EPR 档） |

线缆标签要求同时标注**带宽 + 功率**（如 "USB 10Gbps · 240W"），5Gbps 及以上线缆强制 eMarker。

Logo 使用基本规则（概述）：

- 未通过认证/未签协议**不得**在产品、包装、宣传上使用 USB 商标与认证标识（可以用规范名描述接口，如 "USB 2.0 接口" 属于技术性描述，具体边界以商标协议为准）；
- 认证按**产品型号**列名，改板/改描述符后需重新评估；
- 线缆与连接器领域的执法最严格（假冒标识高发区）。

### 3.2 参与 USB-IF 的两级方式

| 方式 | 义务 | 能做什么 |
|---|---|---|
| Adopters Agreement（采纳者协议，免费） | 承诺遵守规范、不得以规范主张专利壁垒 | 参加合规测试；通过后在 Integrator's List 列名；Logo 使用需按协议执行 |
| 正式会员（年费） | 缴纳年费、参与工作组 | 参与规范制定、提前获取草案、投票；合规程序全权限 |

小型团队常见路径：先以 Adopters 身份做产品认证，需要影响规范时再升级会员。

## 四、WHQL 与 Windows 硬件兼容

- **WHQL（Windows Hardware Quality Labs）**，现称 **Windows 硬件兼容性计划**：微软的兼容性认证，跑 HLK（Hardware Lab Kit）用例；
- 与 USB-IF 认证**相互独立**：拿 USB-IF 徽标不等于过 WHQL，反之亦然；但 HLK 的 USB 用例与 USB-IF 测试方法高度同源（协议/互操作思想一致），先过 USB-IF 自查会显著降低 HLK 返工；
- 实务关系：需要打"兼容 Windows"徽标 → 走 WHQL；需要打 USB Logo → 走 USB-IF；两者常在同一次送测中规划。

## 五、认证流程与费用概貌

> 以下为量级概貌，具体金额以 USB-IF 官网现行公告为准。

1. **成为成员/采纳者**：USB-IF 年费会员（数千美元/年量级）或签署 Adopters Agreement（免费级别但限制 Logo 使用）；
2. **准备 VIF**：Vendor Information File，设备/线缆的标准化描述文件，认证申请与产品数据库登记的基础（线缆类**必须**提交 VIF 获得 TID）；
3. **送测**：USB-IF 授权实验室（Authorized Independent Test Labs，全球若干家）执行电气+协议+互操作，费用按测试组合计，数千至数万美元量级；
4. **拿报告 → 列名**：测试通过后在 USB-IF Integrator's List 列名，凭此使用 Logo。

## 六、开发者的务实自查（不送认证）

| 工具 | 能测什么 | 平台 |
|---|---|---|
| **USBCV（USB Command Verifier）** | Chapter 9 全套协议测试：描述符合法性、标准请求、挂起电流、枚举状态机 | Windows（需特定环境运行） |
| **USBHSET** | 高速电气测试辅助：令设备进入 test_J/K/test_Packet 等测试模式，配合示波器做眼图 | Windows |
| xHCI/EHCI 内建测试模式 | 主机侧测试模式发生（供线路测量） | 固件/驱动入口 |
| 抓包 + 脚本校验 | 描述符自洽性自动检查（bLength 链、wTotalLength、取值域） | 任意 |

自查优先级：协议（USBCV）→ 挂起电流（实测）→ 互操作（尽可能多的主机/hub 矩阵插拔）→ 电气（有条件再测眼图）。

描述符自洽性可以完全脚本化（USBCV 之外的低成本防线）：

```python
# desc_check.py —— 描述符结构自检骨架（读 /sys 下原始描述符或抓包提取均可）
def check_cfg(buf: bytes):
    total = int.from_bytes(buf[2:4], "little")      # wTotalLength
    assert total == len(buf), f"wTotalLength={total} != 实际 {len(buf)}"
    i, n_if = 9, buf[4]                              # 跳过配置描述符
    seen_if = 0
    while i < len(buf):
        ln, typ = buf[i], buf[i+1]
        assert ln >= 2, f"非法 bLength={ln} @ {i}"   # bLength 必须自洽
        if typ == 0x04:                              # 接口描述符
            n_ep = buf[i + 4]
            seen_if += 1
            eps = 0
            i += ln
            while i < len(buf) and buf[i+1] == 0x05: # 数本接口的端点
                eps += 1; i += buf[i]
            assert eps == n_ep, f"接口{seen_if-1}: bNumEndpoints={n_ep} 实际{eps}"
            continue
        i += ln
    assert seen_if == n_if, f"bNumInterfaces={n_if} 实际 {seen_if}"
    print("描述符结构自检通过")
```

把该检查接入 CI：每次固件构建自动校验描述符二进制，可在"换台电脑就翻车"之前拦截大半低级错误。

## 七、常见不合规点清单（来自实战高频）

| 问题 | 后果 |
|---|---|
| **bMaxPower 忘乘 2**：填 500 想表示 500mA | 实际申请 1000mA 超规格；或反过来填 50 实际只有 100mA 导致外设带不动 |
| **字符串索引悬空**：iProduct=3 但只提供 1 个字符串 | 主机请求失败/显示异常；USBCV 直接判不合规 |
| **挂起电流超标**：挂起后 LED 还亮 | >2.5mA 判 FAIL；节能认证连带不过 |
| **bcdUSB 与能力不符**：设备只能 FS 却写 0x0300 | 主机按 3.x 期望测试 → 行为不一致；另 BOS 缺失被 3.x 主机视为遗留设备 |
| 描述符长度不自洽（bLength/wTotalLength） | 部分主机宽容、部分严格 → "这家电脑能用那家不能" |
| 复合设备无 IAD 且类码不为 0xEF/0x02/0x01 | Windows usbccgp 拆分失败 → 代码 10 |
| 非法请求返回超时而非 STALL | 状态机卡死，互操作测试失败 |
| SET_ADDRESS 前使用地址/时机错误 | 间歇性枚举失败（见 [02-枚举失败排查手册](02-枚举失败排查手册.md)） |

## 相关节点

- [../10-树干-USB核心/07-描述符详解.md](../10-树干-USB核心/07-描述符详解.md)：Chapter 9 测试的对象
- [../10-树干-USB核心/08-枚举流程与标准请求.md](../10-树干-USB核心/08-枚举流程与标准请求.md)：标准请求合规语义
- [02-枚举失败排查手册](02-枚举失败排查手册.md)：合规问题的排障视角
- [../30-枝干-接口与供电/](../30-枝干-接口与供电/)：PD/Type-C 侧认证细则
- [../10-树干-USB核心/01-概述与版本演进.md](../10-树干-USB核心/01-概述与版本演进.md)：新旧命名体系由来
