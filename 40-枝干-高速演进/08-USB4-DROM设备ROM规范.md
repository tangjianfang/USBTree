---
title: "USB4 DROM：设备 ROM 规范"
layer: 枝干/高速演进
doc-path: 40-枝干-高速演进/08-USB4-DROM设备ROM规范.md
---
# USB4 DROM：设备 ROM 规范

> 🌳 知识树位置: 树干 → 枝干[高速演进] → 叶
> 上级: [05-USB4深入-路由隧道与配置](05-USB4深入-路由隧道与配置.md) · 规范原文缓存: [../../80-参考资料/usb-core/USB4-Specification-v2-2025-11.zip](../80-参考资料/usb-core/USB4-Specification-v2-2025-11.zip)（内含 `USB4 DROM Specification November 2025.pdf`，Rev 1.2）
> 本叶数值均自该 PDF（pdftotext 提取）。

## 1. DROM 是什么

DROM（Device ROM）是 USB4 产品里的一块**静态只读描述数据**：CM（Connection Manager，通常即主机侧枚举驱动）通过路由器配置空间把它读出来，用于获知设备的厂商信息、适配器偏好与厂商自定义条目。关键性质（§4）：**DROM 是静态的，不反映产品动态状态**——动态能力走 Router/Adapter 配置空间寄存器（见 [05-USB4深入](05-USB4深入-路由隧道与配置.md)）。

## 2. 访问方式（§2）

DROM 以普通 **Read Configuration Request** 读取（就像读 Router 配置空间一样），因此 CM 无需特殊协议。位序约定（§3）：多字节字段**大端**描述、按 32 位 DW 组织——与 USB4 配置空间的其余部分一致。

## 3. 结构（§4）

```
USB4 DROM
├── Header Section（必选, §5）
├── Adapter Entries（§6：DP Adapter 条目等）
└── Generic Entries（§7：厂商/通用条目）
```

- Reserved 字段必须写 0，读到的 Reserved 值一律忽略；
- `bcd` 前缀字段为 BCD 版本编码：0xJJMN = JJ.M.N（如 2.1.3 → 0213H，3.0 → 0300H）。

## 4. Header Section（§5，必选）

头部关键字段（Figure 5-1 / Table 5-1）：

| 偏移 | 内容 | 说明 |
|---|---|---|
| 0~8 | Reserved + 基本标识区 | 保留字段置 0 |
| 9 | CRC32 | 覆盖 DROM 内容的完整性校验 |
| 13 | Version（bcd） | DROM 格式版本 |
| … | Length | DROM 总长（CM 据此界定读取范围） |

（逐字节排布以规范 Figure 5-1/Table 5-1 为准；本叶给出字段语义与偏移锚点。）

## 5. Adapter Entries 与 Generic Entries（§6/§7）

- **Adapter Entries**：按适配器逐个给出覆盖信息——典型如 **DP Adapter 条目**（DP IN/OUT 适配器的厂商特定偏好：DPCD 能力覆盖、引脚赋值偏好等），CM 在建立 DP 隧道前读取；
- **Generic Entries**：键值式通用条目（厂商名、型号字符串、认证信息等），条目类型由规范 §7 的 Type 编码定义；
- 未使用的 Adapter Entry 槽位保留（结构图中的 Unused Adapter Entries）。

## 6. TBT3 兼容（§8）

DROM 需要同时满足雷电 3 互操作场景：TBT3 CM 可能以雷电的方式读取 ROM，因此 DROM 的头部/条目布局保持了与 TBT3 ROM 的兼容映射（§8 详述兼容规则）。

## 7. 工程要点

1. 自研 USB4 扩展坞/卡：DROM 至少要有合法 Header（CRC32 正确），否则 CM 可能拒绝信任其余配置；
2. DP 偏好（如强制 Pin Assignment、禁用某些 DPCD）优先写 DP Adapter Entry，而不是靠 CM 猜；
3. 调试：CM 日志（Windows USB4 CM 日志/Linux thunderbolt-net 邻接工具）会打印 DROM 读取结果。

## 相关节点

- 上一级: [05-USB4深入-路由隧道与配置](05-USB4深入-路由隧道与配置.md) · [07-USB4规范级-配置空间与隧道](07-USB4规范级-配置空间与隧道.md)
- 相邻: [USB4 与雷电整合](02-USB4与雷电整合.md)（TBT3 兼容背景）
- 规范缓存: [80-参考资料](../80-参考资料/README.md)
