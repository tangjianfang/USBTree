# Lessons · 经验库

> 模板：`| id | lesson | how to apply | source | verified |`
> 维护规则：回顾轮逐条复核——被再次印证的 verified+1；失效的改写或删除；≥3 条同主题且合计 ≥5 次 verified 时结晶为机制。

| id | lesson | how to apply | source | verified |
|---|---|---|---|---|
| L1 ✦ | 写规范数值必须从缓存 PDF 提取核对，记忆稿必错：本项目提示稿先后 9 处被纠（Chirp 17~20ms→TUCH 1~7ms、tErrorRecovery 25ms、ECM 包过滤 0x43、UAC1 选择子止于 0x0A、HID GET_IDLE=0x02、CCID 消息码、BT 端点映射、PD 半双工、FS 帧预算 12000 位） | 任何字段/定时器/操作码落表前，先 `pdftotext -layout` 提取缓存规范并 grep 原文 | 六个规范级子任务报告 + evolve #3 | 1 |

> 🧬 **结晶（evolve #22）**：L1/L2/L3/L7 同主题（官方规范提取）合计 5 次验证 → 结晶为 `tools/spec_extract.sh`（解压/提取/检索一步完成）。四条标记 crystallized。
| L2 ✦ | pdftotext 提取的大表格会错位、µ 等字符会变乱码、NUL 字节会让 grep 转入 binary 模式 | 提取后先 `grep -a`；表格错位处写"字段名+位宽+含义"并标"以规范原表为准"，逐位排布不硬抄 | BLE/设备类子任务报告 | 1 |
| L3 ✦ | 官方文档库直链命名随版本漂移（`usb_20_YYYYMMDD.zip`、DocMan doc_id） | 直链 404 时先 WebFetch 官网文档库/落地页拿新直链，再 curl；把"重取直链的方法"写进索引页 | 80-参考资料 建库与两次补缓 | 2 |
| L4 | 后台子任务"报告为空"≠"未执行完成"，报告非空≠"已落盘" | 以 `find` 磁盘清单核对产出，报告行数与实际行数互验；空的子任务直接重做或主会话补写 | 99% 冲刺轮（CDC/MSC/UAC/UVC 子任务 0 产出） | 1 |
| L5 | 库内交叉引用是廉价的错误探测器：速查表与规范提取全表的冲突，直接暴露了树干正文的硬错误 | 新增权威表后，主动 grep 全库同名参数做比对，冲突即缺陷线索 | evolve #3 | 1 |
| L6 | bash 工作目录跨调用残留，相对路径会静默指错位置 | 脚本内一律 `cd "$(dirname "$0")/.."`；交互命令用绝对路径或开头显式 cd | 会话内两次 cd 失败 | 2 |
| L7 ✦ | `files.bluetooth.com` 新式链接会 302 到 HTML 中转页——curl 落盘的是网页不是 PDF；且早前下载的 HID-Service-1.1.pdf 即假 PDF（20K HTML） | 下载后必验 `%PDF` 魔数；中转页里 `?dlm-dp-dl-force=1&dlm-dp-dl-nonce=…` 的完整 href 即直链 | evolve #14 | 1 |
