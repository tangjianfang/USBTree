"""USBTree 代码视频的共享样式与工具（Manim Community Edition ≥ 0.18）。

约定
- 画面 16:9，深色底 + teal 主色，与站点 https://usbtree.gumuhub.com 的深色主题一致。
- 只用 Text / MarkupText（Pango 渲染），不依赖 LaTeX；中文字体 Noto Sans CJK SC，等宽 JetBrains Mono（缺失时 Pango 自动回退）。
- 每个场景继承 USBScene：
    intro(标题, 副标题)  片头
    chapter(文字)        左上角章节标签
    say(字幕)            底部字幕条，同时记录时间轴 → videos/out/<Scene>.cues.json（render.sh 转成 WebVTT）
    outro(出处列表)      片尾：规范出处卡
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from manim import (
    DOWN, LEFT, RIGHT, UP, ORIGIN, UL, UR, DL, DR,
    AnimationGroup, Create, FadeIn, FadeOut, LaggedStart, Line, RoundedRectangle,
    Rectangle, Scene, Text, VGroup, Write, config, Arrow, DashedLine, Dot,
)

# ── 颜色（取自 site/src/styles/custom.css 深色主题） ──
BG = "#0e1116"
PANEL = "#131820"
HAIR = "#262e3a"
FG = "#e6edf3"
MUTED = "#8b949e"
TEAL = "#2dd4bf"       # 主色
TEAL_DK = "#0f766e"
BLUE = "#60a5fa"       # 主机 / Host
AMBER = "#fbbf24"      # 设备 / Device
GREEN = "#4ade80"      # ACK / 成功
RED = "#f87171"        # NAK / STALL / 错误
PURPLE = "#c084fc"

CJK = "Noto Sans CJK SC"
MONO = "JetBrains Mono"

config.background_color = BG

# 画面安全区（单位：Manim 坐标，画面宽 14.22、高 8）
TOP_Y = 3.45
CAPTION_Y = -3.42
CONTENT_TOP = 2.9
CONTENT_BOTTOM = -2.75


def T(s: str, size: float = 28, color: str = FG, weight: str = "NORMAL", **kw) -> Text:
    """中文文本（Pango）。size 是 Manim font_size。"""
    return Text(s, font=CJK, font_size=size, color=color, weight=weight, **kw)


def M(s: str, size: float = 26, color: str = FG, **kw) -> Text:
    """等宽文本：十六进制字节、位串、寄存器名。"""
    return Text(s, font=MONO, font_size=size, color=color, **kw)


def chip(label: str, color: str = TEAL, size: float = 22, mono: bool = False, pad: float = 0.16,
         fill_opacity: float = 0.16, text_color: str | None = None) -> VGroup:
    """圆角色块 + 文字（用作包、字段、状态标签）。"""
    t = (M if mono else T)(label, size=size, color=text_color or color)
    box = RoundedRectangle(corner_radius=0.1, width=t.width + 2 * pad, height=t.height + 1.5 * pad,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)


def panel(w: float, h: float, color: str = HAIR, fill: str = PANEL) -> RoundedRectangle:
    return RoundedRectangle(corner_radius=0.16, width=w, height=h, stroke_color=color, stroke_width=1.6,
                            fill_color=fill, fill_opacity=1)


def field_row(fields, height: float = 0.62, unit: float = 0.11, size: float = 20, colors=None) -> VGroup:
    """包格式条：fields = [(名称, 位数), ...]，宽度按位数缩放（unit = 每位宽度，有最小宽度）。"""
    colors = colors or [TEAL, BLUE, AMBER, PURPLE, GREEN, RED]
    cells = VGroup()
    for i, (name, bits) in enumerate(fields):
        c = colors[i % len(colors)]
        w = max(1.05, bits * unit) if isinstance(bits, int) else 1.05
        r = Rectangle(width=w, height=height, stroke_color=c, stroke_width=2, fill_color=c, fill_opacity=0.14)
        lab = T(name, size=size, color=FG)
        if lab.width > w - 0.12:
            lab.scale_to_fit_width(w - 0.12)
        lab.move_to(r)
        bl = M(f"{bits} bit" if isinstance(bits, int) else str(bits), size=15, color=MUTED).next_to(r, DOWN, buff=0.08)
        cells.add(VGroup(r, lab, bl))
    cells.arrange(RIGHT, buff=0)
    return cells


class USBScene(Scene):
    """所有讲解视频的基类：统一片头、章节标签、字幕时间轴与片尾。"""

    TITLE = "USBTree"
    SLUG = "video"

    def setup(self):
        self._cues: list[dict] = []
        self._caption = None
        self._chapter = None
        self.wm = T("USBTree · usbtree.gumuhub.com", size=16, color=MUTED).to_corner(UR, buff=0.22)
        self.wm.set_opacity(0.55)
        self.add(self.wm)

    # ── 时间轴 ──
    @property
    def now(self) -> float:
        return float(self.renderer.time)

    def _close_cue(self):
        if self._cues and self._cues[-1]["end"] is None:
            self._cues[-1]["end"] = round(self.now, 2)

    READ_CPS = 7.0       # 中文阅读速度（字/秒），字幕至少停留 1.2 s + 字数 / READ_CPS

    def hold(self):
        """保证当前字幕停留够长、能读完。"""
        if self._cues and self._cues[-1]["end"] is None:
            need = 1.0 + len(self._cues[-1]["text"]) / self.READ_CPS
            left = need - (self.now - self._cues[-1]["start"])
            if left > 0.05:
                self.wait(left)

    def say(self, text: str, run_time: float = 0.35):
        """切换底部字幕（同时写入字幕时间轴）。text 为空时只清除。切换前自动 hold()。"""
        anims = []
        self.hold()
        self._close_cue()
        if self._caption is not None:
            anims.append(FadeOut(self._caption, run_time=run_time))
        new = None
        if text:
            t = T(text, size=27, color=FG)
            if t.width > 12.6:
                t.scale_to_fit_width(12.6)
            bar = RoundedRectangle(corner_radius=0.12, width=max(t.width + 0.6, 4), height=t.height + 0.32,
                                   stroke_width=0, fill_color="#000000", fill_opacity=0.55)
            new = VGroup(bar, t).move_to([0, CAPTION_Y, 0])
            t.move_to(bar)
            anims.append(FadeIn(new, run_time=run_time))
            self._cues.append({"start": round(self.now, 2), "end": None, "text": text})
        if anims:
            self.play(*anims)
        self._caption = new

    def chapter(self, text: str, n: int | None = None):
        self.hold()
        label = T((f"{n:02d}  " if n is not None else "") + text, size=24, color=TEAL, weight="BOLD")
        label.to_corner(UL, buff=0.35)
        line = Line(label.get_corner(DL) + DOWN * 0.08, label.get_corner(DR) + DOWN * 0.08, color=TEAL, stroke_width=2)
        g = VGroup(label, line)
        if self._chapter is not None:
            self.play(FadeOut(self._chapter, shift=UP * 0.2), FadeIn(g, shift=UP * 0.2), run_time=0.5)
        else:
            self.play(FadeIn(g, shift=RIGHT * 0.2), run_time=0.5)
        self._chapter = g

    def intro(self, title: str, subtitle: str, tag: str = "USBTree 代码视频"):
        t1 = T(tag, size=24, color=TEAL)
        t2 = T(title, size=60, color=FG, weight="BOLD")
        t3 = T(subtitle, size=28, color=MUTED)
        g = VGroup(t1, t2, t3).arrange(DOWN, buff=0.35)
        bar = Line(LEFT * 2.2, RIGHT * 2.2, color=TEAL, stroke_width=4).next_to(t2, DOWN, buff=0.18)
        t3.next_to(bar, DOWN, buff=0.3)
        self.play(FadeIn(t1, shift=DOWN * 0.2), Write(t2), run_time=1.2)
        self.play(Create(bar), FadeIn(t3, shift=UP * 0.2), run_time=0.8)
        self._cues.append({"start": 0.0, "end": round(self.now + 1.2, 2), "text": f"{title}：{subtitle}"})
        self.wait(1.2)
        self.play(FadeOut(VGroup(t1, t2, t3, bar)), run_time=0.6)

    def clear_stage(self, *keep, run_time: float = 0.6):
        """淡出舞台上除水印 / 字幕 / 章节标签 / keep 外的全部对象（先让当前字幕读完）。"""
        self.hold()
        keepset = {self.wm, self._caption, self._chapter, *keep}
        objs = [m for m in self.mobjects if m not in keepset]
        if objs:
            self.play(*[FadeOut(m) for m in objs], run_time=run_time)

    def outro(self, sources: list[str], page: str = ""):
        self.say("")
        if self._chapter is not None:
            self.play(FadeOut(self._chapter), run_time=0.3)
            self._chapter = None
        self.clear_stage()
        head = T("规范出处", size=34, color=TEAL, weight="BOLD")
        rows = VGroup(*[T("· " + s, size=22, color=FG) for s in sources]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        if rows.width > 12.4:
            rows.scale_to_fit_width(12.4)
        foot = T("数值均按官方规范原文核对；主机实现差异会在字幕中注明。", size=20, color=MUTED)
        link = T(page or "usbtree.gumuhub.com", size=22, color=BLUE)
        g = VGroup(head, rows, foot, link).arrange(DOWN, buff=0.4)
        rows.align_to(head, LEFT) if False else None
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.15), run_time=1.6)
        self.play(FadeIn(foot), FadeIn(link), run_time=0.6)
        self._cues.append({"start": round(self.now - 2.2, 2), "end": None, "text": "规范出处：" + "；".join(sources)})
        self.wait(3.2)
        self._close_cue()
        self._write_cues()

    def _write_cues(self):
        out = Path(os.environ.get("USBTREE_VIDEO_OUT", Path(__file__).resolve().parent / "out"))
        out.mkdir(parents=True, exist_ok=True)
        self._close_cue()
        (out / f"{self.SLUG}.cues.json").write_text(
            json.dumps({"slug": self.SLUG, "title": self.TITLE, "duration": round(self.now, 2), "cues": self._cues},
                       ensure_ascii=False, indent=1), encoding="utf-8")


class Seq:
    """简易时序图：左右两条生命线，消息箭头逐条向下排，超出底部时整体上移。"""

    def __init__(self, scene: USBScene, left_x: float = -5.2, right_x: float = 0.6, head_y: float = 2.05,
                 first_y: float = 1.35, bottom: float = -2.55, step: float = 0.66,
                 left_label: str = "主机 Host", right_label: str = "设备 Device",
                 left_color: str = BLUE, right_color: str = AMBER):
        self.s, self.lx, self.rx, self.step, self.bottom = scene, left_x, right_x, step, bottom
        self.first_y = first_y
        self.y = first_y
        self.hl = chip(left_label, left_color, size=22).move_to([left_x, head_y, 0])
        self.hr = chip(right_label, right_color, size=22).move_to([right_x, head_y, 0])
        self.ll = DashedLine([left_x, head_y - 0.3, 0], [left_x, bottom - 0.15, 0], color=HAIR, stroke_width=2)
        self.rl = DashedLine([right_x, head_y - 0.3, 0], [right_x, bottom - 0.15, 0], color=HAIR, stroke_width=2)
        self.msgs = VGroup()

    def show(self):
        self.s.play(FadeIn(self.hl, shift=DOWN * 0.2), FadeIn(self.hr, shift=DOWN * 0.2), Create(self.ll), Create(self.rl), run_time=0.8)

    def _make_room(self):
        if self.y < self.bottom:
            top = [m for m in self.msgs if m.get_center()[1] + self.step > self.first_y + 0.1]
            if top:
                self.s.play(*[FadeOut(m) for m in top], run_time=0.25)
                for m in top:
                    self.msgs.remove(m)
            self.s.play(self.msgs.animate.shift(UP * self.step), run_time=0.35)
            self.y += self.step

    def msg(self, label: str, to_device: bool = True, color: str = TEAL, note: str | None = None,
            run_time: float = 0.7, mono: bool = False):
        from manim import GrowArrow
        self._make_room()
        a, b = (self.lx, self.rx) if to_device else (self.rx, self.lx)
        arr = Arrow([a, self.y, 0], [b, self.y, 0], buff=0.08, color=color, stroke_width=3.5,
                    max_tip_length_to_length_ratio=0.04, tip_length=0.18)
        lab = (M if mono else T)(label, size=19 if mono else 20, color=color)
        if lab.width > abs(b - a) - 0.3:
            lab.scale_to_fit_width(abs(b - a) - 0.3)
        lab.next_to(arr, UP, buff=0.04)
        g = VGroup(arr, lab)
        if note:
            n = T(note, size=16, color=MUTED).next_to(arr, DOWN, buff=0.03)
            g.add(n)
        self.msgs.add(g)
        self.s.play(GrowArrow(arr), FadeIn(lab, shift=RIGHT * 0.15 if to_device else LEFT * 0.15), *( [FadeIn(g[2])] if note else []), run_time=run_time)
        self.y -= self.step
        return g

    def marker(self, label: str, color: str = MUTED, run_time: float = 0.5):
        """横跨两条生命线的事件条（如“端口复位 SE0 ≥10 ms”）。"""
        self._make_room()
        w = abs(self.rx - self.lx) + 0.6
        box = RoundedRectangle(corner_radius=0.08, width=w, height=0.42, stroke_color=color, stroke_width=1.5,
                               fill_color=color, fill_opacity=0.12).move_to([(self.lx + self.rx) / 2, self.y, 0])
        t = T(label, size=19, color=color).move_to(box)
        if t.width > w - 0.2:
            t.scale_to_fit_width(w - 0.2)
        g = VGroup(box, t)
        self.msgs.add(g)
        self.s.play(FadeIn(g, scale=0.95), run_time=run_time)
        self.y -= self.step
        return g

    def all(self) -> VGroup:
        return VGroup(self.hl, self.hr, self.ll, self.rl, self.msgs)


def state_bar(states, y: float = 2.85, color: str = TEAL) -> VGroup:
    chips = VGroup(*[chip(s, MUTED, size=20, fill_opacity=0.05) for s in states]).arrange(RIGHT, buff=0.42).move_to([0, y, 0])
    arrows = VGroup(*[Arrow(chips[i].get_right(), chips[i + 1].get_left(), buff=0.05, color=HAIR, stroke_width=2,
                            tip_length=0.12) for i in range(len(states) - 1)])
    return VGroup(chips, arrows)


def lit(bar: VGroup, i: int, color: str = TEAL):
    """返回把状态条第 i 格点亮（其余变暗）的动画列表。"""
    anims = []
    for j, c in enumerate(bar[0]):
        on = j == i
        anims.append(c[0].animate.set_stroke(color if on else MUTED).set_fill(color if on else MUTED, opacity=0.25 if on else 0.05))
        anims.append(c[1].animate.set_color(color if on else MUTED))
    return anims
