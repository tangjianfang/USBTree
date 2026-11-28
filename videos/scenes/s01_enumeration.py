"""01 · USB 枚举全过程（USB 2.0 §9.1、§7.1.7.3、§7.1.7.5、§9.2.6、§9.4）"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from manim import *  # noqa: F401,F403
from usbstyle import *  # noqa: F401,F403


class Enumeration(USBScene):
    TITLE = "USB 枚举全过程"
    SLUG = "01-enumeration"

    def detail(self, title, lines, color=TEAL, old=None):
        """右侧细节面板：标题 + 若干行（行可以是 (文字, 是否等宽, 颜色)）。"""
        p = panel(5.6, 3.9)
        p.move_to([4.05, -0.45, 0])
        h = T(title, size=24, color=color, weight="BOLD")
        rows = VGroup()
        for ln in lines:
            if isinstance(ln, str):
                ln = (ln, False, FG)
            s, mono, c = ln
            rows.add((M if mono else T)(s, size=20 if mono else 20, color=c))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        g = VGroup(h, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        if g.width > 5.2:
            g.scale_to_fit_width(5.2)
        g.move_to(p).align_to(p, UP).shift(DOWN * 0.3)
        new = VGroup(p, g)
        if old is None:
            self.play(FadeIn(new, shift=LEFT * 0.2), run_time=0.6)
        else:
            self.play(FadeOut(old[1], run_time=0.3))
            self.play(FadeIn(g, shift=UP * 0.15), run_time=0.45)
            new = VGroup(old[0], g)
        return new

    def construct(self):
        self.intro("USB 枚举全过程", "从插入到 SET_CONFIGURATION，主机和设备各做了什么")

        bar = state_bar(["Attached", "Powered", "Default", "Address", "Configured"])
        bar_t = T("设备状态（规范 图 9-1）", size=16, color=MUTED).next_to(bar, DOWN, buff=0.08).align_to(bar, RIGHT)
        self.play(FadeIn(bar), FadeIn(bar_t), run_time=0.8)
        seq = Seq(self, left_x=-5.6, right_x=0.4, step=0.78)
        seq.show()

        # ── 1 插入 ──
        self.chapter("插入与去抖", 1)
        self.play(*lit(bar, 0))
        self.say("设备插入：全速设备把 D+ 上拉，集线器检测到连接")
        seq.marker("D+ 上拉 → 集线器端口状态变化", AMBER)
        self.play(*lit(bar, 1))
        d = self.detail("连接检测", [
            "集线器通过状态变化端点通知主机",
            ("TATTDB：主机去抖 ≥ 100 ms", False, TEAL),
            "保证插头接触与供电稳定后再复位",
            ("§7.1.7.3 图 7-29 · §9.1.2", False, MUTED),
        ])
        self.say("主机至少去抖 100 ms，确认连接稳定、电源就绪")
        seq.marker("去抖 TATTDB ≥ 100 ms", MUTED)
        self.wait(1.2)

        # ── 2 复位 ──
        self.chapter("端口复位", 2)
        self.say("主机让集线器复位端口：总线保持 SE0 至少 10 ms")
        seq.marker("端口复位：SE0 ≥ 10 ms（TDRST）", RED)
        self.play(*lit(bar, 2))
        d = self.detail("复位之后：Default 状态", [
            ("地址 = 0，只响应默认地址", False, FG),
            ("从 VBUS 取电 ≤ 100 mA", False, FG),
            ("复位恢复 TRSTRCY：10 ms", False, TEAL),
            ("高速设备在复位期间完成 Chirp 握手", False, FG),
            ("§7.1.7.5 · §9.1.2 · §9.2.6.2", False, MUTED),
        ], old=d)
        self.say("复位结束后进入 Default 状态，地址为 0；主机再留 10 ms 恢复时间")
        seq.marker("复位恢复 TRSTRCY 10 ms", MUTED)
        self.wait(1.0)

        # ── 3 读设备描述符（地址 0） ──
        self.chapter("读设备描述符", 3)
        self.say("在地址 0 上读设备描述符，目的是拿到端点 0 的最大包长")
        seq.msg("SETUP  GET_DESCRIPTOR(设备)", True, BLUE, note="地址 0 · 端点 0")
        d = self.detail("SETUP 包 8 字节（表 9-2）", [
            ("80 06 00 01 00 00 40 00", True, BLUE),
            "bmRequestType 0x80：设备→主机、标准、设备",
            "bRequest 0x06：GET_DESCRIPTOR",
            "wValue 0x0100：类型 1（设备）索引 0",
            "wLength 0x0040：先要 64 字节",
            ("§9.3 · 表 9-4 · 表 9-5", False, MUTED),
        ], old=d)
        seq.msg("DATA  12 01 00 02 00 00 00 40 …", False, AMBER, mono=False, note="设备描述符共 18 字节")
        d = self.detail("关键字段：bMaxPacketSize0", [
            ("偏移 7 = 0x40 → 端点 0 包长 64", False, AMBER),
            "全速可取 8/16/32/64；高速固定 64；低速 8",
            ("先读 64 字节、随后再复位一次：", False, FG),
            ("是 Windows 等主机的实现习惯，非规范要求", False, MUTED),
            ("§9.6.1 表 9-8 · §5.5.3", False, MUTED),
        ], old=d)
        self.say("关键是偏移 7 的 bMaxPacketSize0；先要 64 字节是主机实现习惯，并非规范要求")
        self.wait(1.4)

        # ── 4 SET_ADDRESS ──
        self.chapter("分配地址", 4)
        self.say("主机发 SET_ADDRESS，给设备一个 1 到 127 的唯一地址")
        seq.msg("SETUP  SET_ADDRESS(5)", True, BLUE, note="仍发往地址 0")
        seq.msg("IN 状态阶段：零长度包 + ACK", False, GREEN)
        d = self.detail("SET_ADDRESS 的两条时限", [
            ("00 05 05 00 00 00 00 00", True, BLUE),
            ("状态阶段须在 50 ms 内完成", False, FG),
            ("之后有 2 ms 恢复期，再改用新地址", False, TEAL),
            "地址在状态阶段完成后才生效",
            ("§9.2.6.3 · §9.4.6", False, MUTED),
        ], old=d)
        self.play(*lit(bar, 3))
        self.say("状态阶段完成后设备才切换地址：50 ms 内完成，再留 2 ms 恢复")
        self.wait(1.4)

        # ── 5 读完整描述符 ──
        self.chapter("读完整描述符", 5)
        self.say("之后所有请求都发往新地址：先读完整的 18 字节设备描述符")
        seq.msg("GET_DESCRIPTOR(设备, 18)", True, BLUE, note="地址 5")
        seq.msg("GET_DESCRIPTOR(配置, 9)", True, BLUE)
        seq.msg("配置描述符头：wTotalLength", False, AMBER)
        seq.msg("GET_DESCRIPTOR(配置, wTotalLength)", True, BLUE)
        seq.msg("配置 + 接口 + 端点 + 类描述符", False, AMBER)
        d = self.detail("两段式读取配置", [
            "第一次只读 9 字节，拿到 wTotalLength",
            "第二次按总长一次读完整棵描述符树",
            "主机据此挑驱动、算带宽、核对供电",
            "常见还会读字符串描述符（厂商/产品名）",
            ("§9.4.3 · §9.6.3", False, MUTED),
        ], old=d)
        self.say("配置描述符分两次读：先读 9 字节拿总长，再一次读完整棵描述符树")
        self.wait(1.4)

        # ── 6 SET_CONFIGURATION ──
        self.chapter("选择配置", 6)
        self.say("最后 SET_CONFIGURATION(1)：端点就绪，设备进入 Configured 状态")
        seq.msg("SETUP  SET_CONFIGURATION(1)", True, BLUE)
        seq.msg("状态阶段 ACK", False, GREEN)
        self.play(*lit(bar, 4, GREEN))
        d = self.detail("Configured：可以干活了", [
            ("00 09 01 00 00 00 00 00", True, BLUE),
            "所选配置的端点全部按描述符生效",
            "可按 bMaxPower 从 VBUS 取电",
            "数据切换位复位为 DATA0",
            ("§9.1.1.5 · §9.4.7", False, MUTED),
        ], old=d)
        self.say("此后设备可按 bMaxPower 取电，类驱动接管各个接口")
        self.wait(1.6)

        # ── 小结 ──
        self.chapter("小结", 7)
        self.clear_stage(bar, bar_t)
        steps = ["去抖 ≥100 ms", "复位 ≥10 ms", "恢复 10 ms", "读设备描述符", "SET_ADDRESS", "恢复 2 ms", "读配置描述符", "SET_CONFIGURATION"]
        cols = [MUTED, RED, MUTED, BLUE, BLUE, MUTED, BLUE, GREEN]
        row = VGroup(*[chip(s, c, size=19) for s, c in zip(steps, cols)]).arrange_in_grid(rows=2, cols=4, buff=(0.45, 0.6)).move_to([0, 0.2, 0])
        arrs = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.06, color=HAIR, stroke_width=2, tip_length=0.12)
                        for i in (0, 1, 2, 4, 5, 6)])
        self.say("一句话记住：去抖、复位、读包长、给地址、读描述符、选配置")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in row], lag_ratio=0.12), FadeIn(arrs), run_time=2.4)
        self.play(*lit(bar, 4, GREEN), run_time=0.3)
        self.wait(2.2)

        self.outro([
            "USB 2.0 规范 §9.1.1 图 9-1（设备状态）、§9.1.2（总线枚举步骤）",
            "USB 2.0 §7.1.7.3 图 7-29（TATTDB 100 ms）、§7.1.7.5（TDRST ≥10 ms、TRSTRCY 10 ms）",
            "USB 2.0 §9.2.6.2–9.2.6.3（复位恢复 10 ms；SET_ADDRESS 50 ms + 2 ms）",
            "USB 2.0 §9.3 表 9-2、§9.4 表 9-4/9-5、§9.6.1 表 9-8",
        ], page="usbtree.gumuhub.com/10-树干-USB核心/08-枚举流程与标准请求/")
