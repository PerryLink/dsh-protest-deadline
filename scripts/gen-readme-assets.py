#!/usr/bin/env python3
"""README visuals for dsh-protest-deadline, read off the shipped pipeline.

What the plugin really does (src/model.ts -> src/shared/rows.ts -> src/view.ts):
  a project header plus rows[] (JSON or YAML) is parsed once, every column
  alias is canonicalised, and rules/protest-deadline.yaml is applied rule by
  rule. A rule either emits a located Issue (row + field + found + expected +
  fix) or records itself in `skipped` with a reason. The report never decides
  lateness, acceptance or rejection.

Two figures, each anchored to a shipped fixture and to an actual run:

  hero 1440x576 (Pillow, 4 files: zh/en x light/dark)
      One row of tests/fixtures/PD-003/PD-003-unsafe.json:
      raisedAt 2026-03-02, replyDueAt 2026-03-09, replyAt 2026-03-20,
      complaintAt 2026-03-12. The reply lands 11 days past the deadline the
      register itself states, and the complaint sits 8 days before the reply.
      The real run is PD-003 (info) + PD-004 (warn) + PD-005 skipped.
      The drawing never computes a statutory deadline: the dashed line is the
      register's own 答复期限 cell.

  flow 1100x660 (hand-written SVG, 2 files: light/dark)
      tests/fixtures/PD-004/PD-004-unsafe.json: raisedAt 2026-03-02,
      replyDueAt 2026-03-09, replyAt 2026-03-06, complaintAt 2026-03-01.
      The real run is one PD-004 warn (reply later than complaint) and one
      PD-005 skip; PD-001/002/003/006/007 pass. The figure is a timeline:
      three rule brackets over one date axis, a strip for the four
      register-level checks that do not compare dates, and the two report
      channels feeding the reviewer.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + msyh.ttc / msyhbd.ttc / consola.ttf / consolab.ttf.
"""
from __future__ import annotations

import os
from functools import lru_cache
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONTS = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONTS.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing for {_kind}: {_path}")

# Family palette, fixed by the README design spec.
SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a", mark="#b45309",
        mark_bg="#fdf3e9", pill="#ece7f9", band="#f5f2fb",
        grid="#e7e4f0", shadow=(32, 26, 64), glow2="#7a68c9",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950", mark="#d9a441",
        mark_bg="#2a2216", pill="#242d42", band="#202839",
        grid="#262f42", shadow=(0, 0, 0), glow2="#8496f5",
    ),
}

RADIUS = 22
SHADOW = 24


# --------------------------------------------------------------------- helpers
def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


@lru_cache(maxsize=256)
def font(size: int, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[kind], size)


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def text_w(text: str, size: int, kind: str = "cjk") -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def need(text: str, size: int, kind: str, max_w: float, where: str) -> None:
    """Abort instead of shipping a clipped or colliding label."""
    width = text_w(text, size, kind)
    if width > max_w + 0.5:
        raise SystemExit(
            f"FATAL: {where} overflows: {text!r} needs {width:.1f}px > "
            f"{max_w:.1f}px")


def fit_size(text: str, kind: str, max_w: float, high: int, low: int,
             where: str) -> int:
    size = high
    while size > low:
        if text_w(text, size, kind) <= max_w:
            return size
        size -= 1
    if text_w(text, low, kind) > max_w:
        raise SystemExit(f"FATAL: {where} does not fit at {low}px: {text!r}")
    return low


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    image = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(image)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return image


def glow(image: Image.Image, cx: int, cy: int, radius: int,
         color: tuple[int, int, int], alpha: int) -> Image.Image:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for step in range(9, 0, -1):
        r = radius * step / 9
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=color + (int(alpha * (1 - step / 10)),))
    return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")


def card(image: Image.Image, box: tuple[int, int, int, int], s: dict,
         radius: int = RADIUS, shadow: int = SHADOW,
         fill: str | None = None) -> Image.Image:
    """A rounded panel with a soft, low-contrast drop shadow."""
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for offset in range(shadow, 0, -3):
        draw.rounded_rectangle(
            [x0 - offset // 8, y0 + offset // 2,
             x1 + offset // 8, y1 + offset],
            radius=radius + offset // 5,
            fill=s["shadow"] + (int(10 * (1 - offset / shadow)),))
    layer = layer.filter(ImageFilter.GaussianBlur(9))
    base = Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=radius,
                           fill=hx(fill or s["card"]),
                           outline=hx(s["edge"]), width=2)
    return base


def pill(image: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 17) -> tuple[int, int]:
    draw = ImageDraw.Draw(image)
    f = font(size, "cjk_bold")
    x, y = xy
    width = draw.textlength(text, font=f)
    height = size + 20
    draw.rounded_rectangle([x, y, x + width + 30, y + height],
                           radius=height // 2, fill=hx(s["pill"]))
    draw.text((x + 15, y + height / 2), text, font=f,
              fill=hx(s["accent"]), anchor="lm")
    return int(x + width + 30), int(y + height)


def chip(image: Image.Image, x: int, y: int, text: str, fg: str, bg: str,
         size: int = 11, pad: int = 9, height: int = 20,
         kind: str = "cjk_bold") -> int:
    draw = ImageDraw.Draw(image)
    f = font(size, kind)
    width = draw.textlength(text, font=f)
    draw.rounded_rectangle([x, y, x + width + pad * 2, y + height],
                           radius=height // 2, fill=hx(bg))
    draw.text((x + pad, y + height / 2 + 0.5), text, font=f,
              fill=hx(fg), anchor="lm")
    return int(width + pad * 2)


def dash_v(draw: ImageDraw.ImageDraw, x: float, y0: float, y1: float,
           color: str, width: int = 2, dash: int = 6, gap: int = 4) -> None:
    y = y0
    while y < y1:
        draw.line([(x, y), (x, min(y + dash, y1))], fill=hx(color), width=width)
        y += dash + gap


def dash_round_rect(draw: ImageDraw.ImageDraw,
                    box: tuple[int, int, int, int], color: str,
                    width: int = 2, dash: int = 7, gap: int = 4) -> None:
    x0, y0, x1, y1 = box
    for a, b in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)),
                 ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
        length = abs(b[0] - a[0]) + abs(b[1] - a[1])
        steps = max(int(length // (dash + gap)), 1)
        for i in range(steps + 1):
            t0 = i * (dash + gap) / length
            t1 = min((i * (dash + gap) + dash) / length, 1.0)
            if t0 >= 1:
                break
            draw.line(
                [(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                 (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                fill=hx(color), width=width)


def dot(image: Image.Image, x: float, y: float, r: float, color: str,
        halo: str | None = None) -> None:
    draw = ImageDraw.Draw(image)
    if halo:
        draw.ellipse([x - r - 2.5, y - r - 2.5, x + r + 2.5, y + r + 2.5],
                     fill=hx(halo))
    draw.ellipse([x - r, y - r, x + r, y + r], fill=hx(color))


def diamond(image: Image.Image, x: float, y: float, r: float, color: str,
            halo: str | None = None) -> None:
    draw = ImageDraw.Draw(image)
    points = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
    if halo:
        outer = [(x, y - r - 2.5), (x + r + 2.5, y), (x, y + r + 2.5),
                 (x - r - 2.5, y)]
        draw.polygon(outer, fill=hx(halo))
    draw.polygon(points, fill=hx(color))


# ------------------------------------------------------------------------- hero
# Columns: seq / raised / due / reply / complaint / status.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 核查器",
        value=["填漏的、对不上的、超出期限的", "逐条落到行号与栏名"],
        sub=["只核对台账自身能机械核对的部分：",
             "日期填没填、先后是否成立、答复是否落在台账写明的期限内；",
             "不判是否逾期、不认定责任——差异清单交给复核人。"],
        meta="PD-001..PD-007 · 规则包即数据 · 未执行的检查进 skipped[]",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        reg_title="质疑与投诉台账 · rows[]",
        reg_chip="只读原件",
        project="某某设备采购项目 · ZC-2026-018 · 某某采购代理机构",
        note="列名忽略大小写、空格与下划线；原件永不修改",
        headers=["序号", "质疑提出日期", "答复期限", "实际答复日期", "投诉日期", "处理状态"],
        widths=[100, 120, 108, 120, 94, 80],
        cells=["ZY-2026-001", "2026-03-02", "2026-03-09",
               "2026-03-20", "2026-03-12", "已答复"],
        kinds=["mono", "mono", "mono", "mono", "mono", "cjk"],
        timeline_title="日期链 · 第 1 行",
        timeline_hint="只比较先后 · 不换算工作日",
        raised="提出 03-02", due="台账答复期限 03-09", reply="答复 03-20",
        complaint="投诉 03-12 · 早于答复", late="相差 11 天",
        legend="圆点 = 台账里的日期；虚线 = 台账自填的答复期限；橙色 = 跨过该期限的答复",
        findings=[
            ("PD-003", "info", "第 1 行 · 答复 2026-03-20 晚于台账期限 2026-03-09（相差 11 天）"),
            ("PD-004", "warn", "第 1 行 · 答复 2026-03-20 晚于投诉日期 2026-03-12"),
            ("PD-005", "skipped", "处理状态取值清单未配置（values 为空）"),
        ],
        strip=("report · error 0 · warn 1 · info 1 ｜ skipped 1",
               "结论留给复核人"),
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · checker",
        value=["Blank dates, reversed pairs,", "replies past the stated deadline"],
        sub=["It checks only what the register itself can be held to:",
             "are the dates filled, does the order hold, does the reply fall",
             "inside the deadline the register states — no lateness verdict;",
             "the difference list goes to the reviewer."],
        meta="PD-001..PD-007 · rules are data · skipped is always explained",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        reg_title="Query & complaint register · rows[]",
        reg_chip="read-only",
        project="Some equipment procurement · ZC-2026-018 · Some agency",
        note="Column names ignore case, spaces and underscores; the original is never modified",
        headers=["Seq", "Raised on", "Reply due", "Reply sent", "Complaint", "Status"],
        widths=[100, 120, 108, 120, 94, 80],
        cells=["ZY-2026-001", "2026-03-02", "2026-03-09",
               "2026-03-20", "2026-03-12", "Replied"],
        kinds=["mono", "mono", "mono", "mono", "mono", "cjk"],
        timeline_title="Date chain · row 1",
        timeline_hint="order only · no working-day math",
        raised="raised 03-02", due="register due 03-09", reply="reply 03-20",
        complaint="complaint 03-12 · before reply", late="11 days apart",
        legend="dot = a date in the register; dashed = the register's own reply deadline; amber = the reply that crosses it",
        findings=[
            ("PD-003", "info", "row 1 · reply 2026-03-20 is later than the register deadline 2026-03-09 (11 days apart)"),
            ("PD-004", "warn", "row 1 · reply 2026-03-20 is later than the complaint date 2026-03-12"),
            ("PD-005", "skipped", "status vocabulary is unset (values empty) — reported in skipped[]"),
        ],
        strip=("report · error 0 · warn 1 · info 1 ｜ skipped 1",
               "verdict stays with the reviewer"),
    ),
}

HERO_W, HERO_H = 1440, 576
HERO_M = 64
HERO_COL = 596
HERO_RX = 700
HERO_RW = 676


def finding_row(image: Image.Image, x: int, y: int, rule: str, sev: str,
                text: str, s: dict, max_w: float) -> None:
    draw = ImageDraw.Draw(image)
    if sev == "warn":
        rule_fg, chip_fg = s["mark"], s["mark"]
    elif sev == "info":
        rule_fg, chip_fg = s["accent"], s["accent"]
    else:
        rule_fg, chip_fg = s["faint"], s["faint"]
    draw.text((x, y), rule, font=font(11.5, "mono_bold"), fill=hx(rule_fg))
    rule_w = text_w(rule, 11.5, "mono_bold")
    cx = x + rule_w + 8
    chip_w = text_w(sev, 10.5, "cjk_bold") + 16
    draw.rounded_rectangle([cx, y - 2, cx + chip_w, y + 16], radius=9,
                           fill=hx(s["pill"]))
    draw.text((cx + 8, y + 7.5), sev, font=font(10.5, "cjk_bold"),
              fill=hx(chip_fg), anchor="lm")
    tx = cx + chip_w + 8
    need(text, 11.5, "cjk", max_w - (tx - x), f"hero finding {rule}")
    draw.text((tx, y), text, font=font(11.5, "cjk"),
              fill=hx(s["faint"] if sev == "skipped" else s["text"]))


def hero(lang: str, skin: str) -> None:
    H = HERO[lang]
    s = SKIN[skin]
    image = gradient(HERO_W, HERO_H, s["bg_from"], s["bg_to"])
    image = glow(image, 1210, 34, 430, hx(s["accent"]),
                 22 if skin == "light" else 34)
    image = glow(image, 90, 590, 300, hx(s["glow2"]),
                 9 if skin == "light" else 15)
    draw = ImageDraw.Draw(image)

    # ---- left column: kicker / title / value / sub / meta / footer ---------
    pill(image, (HERO_M, 52), H["kicker"], s, 17)
    title = "dsh-protest-deadline"
    title_size = fit_size(title, "mono_bold", HERO_COL, 58, 48, "hero title")
    draw.text((HERO_M - 2, 112), title, font=font(title_size, "mono_bold"),
              fill=hx(s["text"]))

    value_size = 36
    for line in H["value"]:
        need(line, value_size, "cjk_bold", HERO_COL, "hero value")
    for index, line in enumerate(H["value"]):
        draw.text((HERO_M, 198 + index * 48), line,
                  font=font(value_size, "cjk_bold"), fill=hx(s["text"]))

    sub_size = 20 if lang == "zh" else 18
    sub_lead = 32 if lang == "zh" else 27
    for line in H["sub"]:
        need(line, sub_size, "cjk", HERO_COL, "hero sub")
    for index, line in enumerate(H["sub"]):
        draw.text((HERO_M + 1, 300 + index * sub_lead), line,
                  font=font(sub_size, "cjk"), fill=hx(s["sub"]))

    meta_size = 18 if lang == "zh" else 17
    need(H["meta"], meta_size, "cjk", HERO_COL, "hero meta")
    need(H["foot"], 16, "cjk", HERO_COL, "hero footer")
    draw.text((HERO_M + 1, 424), H["meta"], font=font(meta_size, "cjk"),
              fill=hx(s["faint"]))
    draw.line([HERO_M + 1, 456, HERO_M + HERO_COL - 4, 456],
              fill=hx(s["grid"]), width=2)
    draw.text((HERO_M + 1, 470), H["foot"], font=font(16, "cjk"),
              fill=hx(s["faint"]))

    # ---- panel 1: the register row -----------------------------------------
    image = card(image, (HERO_RX, 36, HERO_RX + HERO_RW, 224), s)
    draw = ImageDraw.Draw(image)
    draw.text((HERO_RX + 24, 54), H["reg_title"], font=font(16, "cjk_bold"),
              fill=hx(s["accent"]))
    chip_w = text_w(H["reg_chip"], 11, "cjk_bold") + 18
    chip(image, HERO_RX + HERO_RW - 24 - chip_w, 50, H["reg_chip"],
         s["accent"], s["pill"], size=11, pad=9)
    draw = ImageDraw.Draw(image)
    draw.text((HERO_RX + 24, 82), H["project"], font=font(12, "cjk"),
              fill=hx(s["sub"]))
    need(H["project"], 12, "cjk", 600, "hero project")

    # header band + column grid
    x0 = HERO_RX + 12
    top = 100
    xs: list[int] = []
    acc = HERO_RX + 24
    for width in H["widths"]:
        xs.append(acc)
        acc += width
    x_end = acc
    draw.rounded_rectangle([x0, top, x_end + 8, top + 28], radius=9,
                           fill=hx(s["band"]))
    for index, head in enumerate(H["headers"]):
        inner = H["widths"][index] - 16
        need(head, 11, "cjk_bold", inner, "hero table header")
        draw.text((xs[index] + 10, top + 8), head,
                  font=font(11, "cjk_bold"), fill=hx(s["sub"]))

    row_top, row_h = top + 28, 46
    for index, value in enumerate(H["cells"]):
        cell_x = xs[index] + 2
        cell_w = H["widths"][index] - 4
        if index == 2:  # replyDueAt: the register's own deadline
            draw.rounded_rectangle([cell_x, row_top + 4, cell_x + cell_w,
                                    row_top + row_h - 4], radius=8,
                                   fill=hx(s["band"]))
        if index == 3:  # replyAt: the date past that deadline
            draw.rounded_rectangle([cell_x, row_top + 4, cell_x + cell_w,
                                    row_top + row_h - 4], radius=8,
                                   fill=hx(s["mark_bg"]))
            dash_round_rect(draw, (cell_x + 1, row_top + 5,
                                   cell_x + cell_w - 1, row_top + row_h - 5),
                            s["mark"], width=2, dash=6, gap=4)
        text_size = 11.5 if H["kinds"][index] == "mono" else 13
        kind = H["kinds"][index]
        need(value, text_size, kind, cell_w - 12, "hero table cell")
        fill = s["text"]
        if index == 2:
            fill = s["accent"]
        if index == 3:
            fill = s["mark"]
        draw.text((xs[index] + 10, row_top + 15), value,
                  font=font(text_size, kind), fill=hx(fill))
        if index < len(H["cells"]) - 1:
            draw.line([xs[index + 1] - 4, row_top + 8,
                       xs[index + 1] - 4, row_top + row_h - 8],
                      fill=hx(s["grid"]), width=1)
    draw.text((HERO_RX + 24, 190), H["note"], font=font(11.5, "cjk"),
              fill=hx(s["faint"]))
    need(H["note"], 11.5, "cjk", 620, "hero register note")

    # ---- panel 2: one-row date chain ---------------------------------------
    image = card(image, (HERO_RX, 236, HERO_RX + HERO_RW, 424), s)
    draw = ImageDraw.Draw(image)
    draw.text((HERO_RX + 24, 254), H["timeline_title"],
              font=font(15, "cjk_bold"), fill=hx(s["accent"]))
    draw.text((HERO_RX + HERO_RW - 24, 254), H["timeline_hint"],
              font=font(11, "cjk"), fill=hx(s["faint"]), anchor="ra")
    need(H["timeline_hint"], 11, "cjk", 200, "hero timeline hint")

    axis_y = 340
    ax0, ax1 = HERO_RX + 44, HERO_RX + HERO_RW - 44
    day_span = 21  # 2026-03-01 .. 2026-03-22

    def date_x(day: int) -> float:
        return ax0 + (day - 1) / day_span * (ax1 - ax0)

    # faint day ruler
    for day in range(1, 23):
        x = date_x(day)
        draw.line([x, axis_y - 4, x, axis_y + 4], fill=hx(s["grid"]), width=1)

    due_x, reply_x = date_x(9), date_x(20)
    raised_x, complaint_x = date_x(2), date_x(12)

    # the register's own deadline: dashed, never computed by the plugin
    dash_v(draw, due_x, 304, axis_y + 8, s["accent"], width=2, dash=6, gap=4)

    # the overflow the register itself exposes (03-09 -> 03-20)
    draw.rounded_rectangle([due_x, axis_y - 6, reply_x, axis_y + 6], radius=6,
                           fill=hx(s["mark_bg"]))
    draw.line([ax0, axis_y, due_x, axis_y], fill=hx(s["grid"]), width=2)
    draw.line([due_x, axis_y, reply_x, axis_y], fill=hx(s["mark"]), width=3)
    draw.line([reply_x, axis_y, ax1, axis_y], fill=hx(s["grid"]), width=2)

    dot(image, raised_x, axis_y, 6, s["accent"], halo=s["card"])
    dot(image, complaint_x, axis_y, 6, s["accent"], halo=s["card"])
    dot(image, reply_x, axis_y, 7, s["mark"], halo=s["card"])
    diamond(image, due_x, axis_y, 7, s["accent"], halo=s["card"])

    draw = ImageDraw.Draw(image)
    label_size = 11.5
    labels = [
        (raised_x, 300, H["raised"], s["sub"]),
        (due_x, 290, H["due"], s["accent"]),
        (reply_x, 300, H["reply"], s["mark"]),
        ((due_x + reply_x) / 2, 320, H["late"], s["mark"]),
    ]
    for x, y, text, color in labels:
        need(text, label_size, "cjk", 220, "hero timeline label")
        draw.text((x, y), text, font=font(label_size, "cjk"),
                  fill=hx(color), anchor="mm")
    # complaint label sits below the axis, clear of the dashed deadline line
    need(H["complaint"], label_size, "cjk", 230, "hero complaint label")
    draw.text((complaint_x, 360), H["complaint"],
              font=font(label_size, "cjk"), fill=hx(s["sub"]), anchor="mm")

    need(H["legend"], 11, "cjk", 620, "hero timeline legend")
    draw.text((HERO_RX + 24, 398), H["legend"], font=font(11, "cjk"),
              fill=hx(s["faint"]))

    # ---- panel 3: the two real issues + the skipped rule -------------------
    image = card(image, (HERO_RX, 436, HERO_RX + HERO_RW, 504), s,
                 radius=18, shadow=18)
    for index, (rule, sev, text) in enumerate(H["findings"]):
        finding_row(image, HERO_RX + 24, 446 + index * 19, rule, sev, text,
                    s, HERO_RW - 48)

    # ---- panel 4: the report strip ----------------------------------------
    image = card(image, (HERO_RX, 516, HERO_RX + HERO_RW, 556), s,
                 radius=18, shadow=14)
    draw = ImageDraw.Draw(image)
    left, right = H["strip"]
    need(left, 12.5, "cjk", 470, "hero report strip left")
    need(right, 12.5, "cjk_bold", 360, "hero report strip right")
    draw.text((HERO_RX + 24, 536), left, font=font(12.5, "cjk"),
              fill=hx(s["text"]), anchor="lm")
    draw.text((HERO_RX + HERO_RW - 24, 536), right,
              font=font(12.5, "cjk_bold"), fill=hx(s["accent2"]),
              anchor="rm")

    name = f"dsh-protest-deadline-hero-{lang}-{skin}.webp"
    image.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({HERO_W}×{HERO_H})")


# ------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        panel="#ffffff", edge="#e6e2ef", band="#f5f2fb", text="#141419",
        sub="#4d5261", faint="#8f94a4", accent="#4B67B4",
        accent2="#16a34a", mark="#b45309", mark_bg="#fdf3e9",
        rule="#dcd8ea", bg_from="#f9f6fd", bg_to="#e4eaf8",
        shadow="0.10", shadow_color="#16122c",
    ),
    "dark": dict(
        panel="#1b2231", edge="#2e374b", band="#202839", text="#f0f3f9",
        sub="#a8b1c4", faint="#737b8d", accent="#8496f5",
        accent2="#3fb950", mark="#d9a441", mark_bg="#2a2216",
        rule="#2b3348", bg_from="#131a2a", bg_to="#0c1016",
        shadow="0.45", shadow_color="#000000",
    ),
}

FONT_CSS_CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
                "'Source Han Sans SC',sans-serif")
FONT_CSS_MONO = "'Consolas','SFMono-Regular',Menlo,ui-monospace,monospace"

# PD-004-unsafe.json, the row the flow figure draws.
FLOW_ROW = dict(
    project="某某设备采购项目",
    project_no="ZC-2026-018",
    agency="某某采购代理机构",
    seq="ZY-2026-001",
    raised="2026-03-02",
    due="2026-03-09",
    reply="2026-03-06",
    complaint="2026-03-01",
    status="已答复",
)


class Svg:
    """Small SVG writer that measures every label before emitting it."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.overflow: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", weight: int | None = None,
             mono: bool = False, max_w: float | None = None,
             opacity: float | None = None) -> None:
        if mono:
            kind = "mono_bold" if weight else "mono"
        else:
            kind = "cjk_bold" if weight else "cjk"
        if max_w is not None:
            width = text_w(content, size, kind)
            if width > max_w + 0.5:
                self.overflow.append(
                    f"{content!r} needs {width:.1f}px > {max_w}px")
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{FONT_CSS_MONO if mono else FONT_CSS_CJK}"',
                 f'font-size="{size}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<text {" ".join(attrs)}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, dash: str | None = None) -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"']
        if rx:
            attrs.append(f'rx="{rx}"')
        attrs.append(f'fill="{fill}"')
        if stroke:
            attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def panel(self, x: float, y: float, w: float, h: float, fill: str,
              edge: str, r: float = 18) -> None:
        self.rect(x, y, w, h, fill=fill, rx=r, stroke=edge, sw=1.5,
                  shadow=True)

    def line(self, x1: float, y1: float, x2: float, y2: float, *,
             stroke: str, sw: float = 1.5, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"',
                 'stroke-linecap="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5,
             fill: str = "none", dash: str | None = None) -> None:
        attrs = [f'd="{d}"', f'fill="{fill}"', f'stroke="{stroke}"',
                 f'stroke-width="{sw}"', 'stroke-linecap="round"',
                 'stroke-linejoin="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.add(f'<path {" ".join(attrs)}/>')

    def circle(self, cx: float, cy: float, r: float, fill: str,
               stroke: str | None = None, sw: float = 1.5) -> None:
        attrs = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
        if stroke:
            attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        self.add(f'<circle {" ".join(attrs)}/>')

    def diamond(self, cx: float, cy: float, r: float, fill: str) -> None:
        self.add(f'<path d="M{cx} {cy - r} L{cx + r} {cy} L{cx} {cy + r} '
                 f'L{cx - r} {cy} Z" fill="{fill}"/>')

    def chip(self, x_right: float, y: float, label: str, fg: str, bg: str,
             *, size: float = 11, pad: float = 10, height: float = 24,
             weight: int | None = None, mono: bool = False) -> float:
        kind = ("mono" if mono else "cjk") + ("_bold" if weight else "")
        width = text_w(label, size, kind) + pad * 2
        x = x_right - width
        self.rect(x, y, width, height, fill=bg, rx=height / 2)
        self.text(x + pad, y + height / 2 + size * 0.35, label, size, fg,
                  weight=weight, mono=mono)
        return x

    def bracket(self, x1: float, x2: float, y: float, color: str) -> None:
        self.path(f"M{x1} {y} H{x2}", stroke=color, sw=1.6)
        for x in (x1, x2):
            self.path(f"M{x} {y - 5} V{y + 5}", stroke=color, sw=1.6)

    def svg(self, w: int, h: int, label: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
                f'height="{h}" viewBox="0 0 {w} {h}" role="img" '
                f'aria-label="{escape(label)}">')
        return "\n".join([head, *self.parts, "</svg>"]) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    v = Svg()

    v.add("<defs>")
    v.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">'
          f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
          f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    v.add(f'<filter id="soft" x="-25%" y="-25%" width="150%" height="160%">'
          f'<feDropShadow dx="0" dy="6" stdDeviation="8" '
          f'flood-color="{s["shadow_color"]}" flood-opacity="{s["shadow"]}"/>'
          f'</filter>')
    v.add("</defs>")
    v.add(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # ---- header -------------------------------------------------------------
    v.text(44, 58, "dsh-protest-deadline", 26, s["text"], weight=700,
           mono=True, max_w=660)
    v.text(44, 86,
           "七条规则只读一份质疑与投诉台账：日期先填齐，再把同一行的日期逐对比较；差异落到行号与栏名。",
           13.5, s["sub"], max_w=930)
    v.chip(1056, 38, "规则包 v2026.1 · PD-001..PD-007", s["accent"], s["band"],
           size=11.5, pad=12, height=26)

    # ---- input band: the register row --------------------------------------
    v.panel(44, 104, 1012, 96, s["panel"], s["edge"])
    v.text(62, 124, "输入 · 质疑与投诉台账（JSON / YAML，只读）", 13.5,
           s["accent"], weight=700, max_w=470)
    v.text(1038, 124, "列名已归一 · 原件永不修改", 11, s["faint"],
           anchor="end", max_w=240)
    project = (f"{FLOW_ROW['project']} · {FLOW_ROW['project_no']} · "
               f"{FLOW_ROW['agency']}")
    v.text(62, 145, project, 11.5, s["sub"], max_w=700)

    cols = [62, 212, 386, 536, 710, 860]
    heads = ["序号", "质疑提出日期", "答复期限", "实际答复日期", "投诉日期",
             "处理状态"]
    vals = [FLOW_ROW["seq"], FLOW_ROW["raised"], FLOW_ROW["due"],
            FLOW_ROW["reply"], FLOW_ROW["complaint"], FLOW_ROW["status"]]
    is_mono = [True, True, True, True, True, False]
    v.rect(62, 154, 956, 40, fill=s["band"], rx=10)
    for index, head in enumerate(heads):
        v.text(cols[index] + 10, 168, head, 11, s["sub"], max_w=150)
    for index, value in enumerate(vals):
        if index in (3, 4):  # the pair PD-004 compares
            v.rect(cols[index] + 2, 172, 146, 20, fill=s["mark_bg"], rx=6)
        v.text(cols[index] + 10, 187, value, 11.5,
               s["mark"] if index == 4 else s["text"],
               mono=is_mono[index], max_w=148)

    # ---- timeline panel -----------------------------------------------------
    v.panel(44, 208, 1012, 204, s["panel"], s["edge"])
    v.text(62, 230, "日期链 · 第 1 行（PD-004 样例：投诉早于答复）", 13.5,
           s["accent"], weight=700, max_w=580)
    v.text(1038, 230, "只比较先后 · 不换算工作日", 11, s["faint"],
           anchor="end", max_w=250)

    ax0, ax1, axis_y = 110, 1032, 356
    days = 9  # 2026-03-01 .. 2026-03-10

    def dx(day: int) -> float:
        return ax0 + (day - 1) / days * (ax1 - ax0)

    x_complaint, x_raised = dx(1), dx(2)
    x_reply, x_due = dx(6), dx(9)

    for day in range(1, 11):
        v.line(dx(day), axis_y - 4, dx(day), axis_y + 4, stroke=s["rule"],
               sw=1)
    v.line(ax0, axis_y, ax1, axis_y, stroke=s["rule"], sw=2)

    # three comparisons, one per date rule that does not just count fields
    v.bracket(x_raised, x_reply, 264, s["accent"])
    v.text((x_raised + x_reply) / 2, 256, "PD-002 提出 ≤ 答复 √",
           11.5, s["accent"], anchor="middle", max_w=190)
    v.bracket(x_raised, x_due, 292, s["accent"])
    v.text((x_raised + x_due) / 2, 284, "PD-003 提出 ≤ 答复 ≤ 台账期限 √",
           11.5, s["accent"], anchor="middle", max_w=230)
    v.bracket(x_complaint, x_reply, 320, s["mark"])
    v.text((x_complaint + x_reply) / 2, 312, "PD-004 答复 ≤ 投诉 × 投诉早 5 天",
           11.5, s["mark"], anchor="middle", max_w=240)

    # dates on the axis: three recorded dates plus the register's own limit
    v.circle(x_complaint, axis_y, 6, s["mark"], stroke=s["panel"], sw=2.5)
    v.circle(x_raised, axis_y, 6, s["accent"], stroke=s["panel"], sw=2.5)
    v.circle(x_reply, axis_y, 6, s["accent"], stroke=s["panel"], sw=2.5)
    v.diamond(x_due, axis_y, 7, s["accent"])
    v.text(x_complaint, 376, "投诉 03-01", 11.5, s["mark"], anchor="middle",
           max_w=110)
    v.text(x_raised, 376, "提出 03-02", 11.5, s["text"], anchor="middle",
           max_w=110)
    v.text(x_reply, 376, "答复 03-06", 11.5, s["text"], anchor="middle",
           max_w=110)
    v.text(x_due, 376, "台账期限 03-09", 11.5, s["accent"], anchor="middle",
           max_w=130)

    v.text(62, 400,
           "括号 = 一条规则放在一起比较的日期；√ 成立 · × 不成立；菱形 = 台账自填的期限，插件不代算工作日。",
           11.5, s["faint"], max_w=960)

    # ---- register-level checks strip ---------------------------------------
    v.panel(44, 420, 1012, 44, s["panel"], s["edge"])
    v.text(62, 446, "台账级检查（不比较日期先后）", 13, s["accent"],
           weight=700, max_w=300)
    checks = [
        ("PD-001 至少一项 · 通过", s["accent2"], "通过"),
        ("PD-005 状态取值 · skipped", s["mark"], "skipped"),
        ("PD-006 表头项目 · 通过", s["accent2"], "通过"),
        ("PD-007 编号唯一 · 通过", s["accent2"], "通过"),
    ]
    check_x = [320, 510, 700, 890]
    for x, (label, color, _state) in zip(check_x, checks):
        v.circle(x - 12, 441, 3.5, color)
        v.text(x, 446, label, 11, s["sub"], max_w=190)

    # ---- two output channels ------------------------------------------------
    v.panel(44, 472, 606, 96, s["panel"], s["edge"])
    v.text(62, 496, "issues[] · 1 条", 13.5, s["accent"], weight=700,
           max_w=200, mono=False)
    v.chip(630, 482, "warn 1", s["mark"], s["band"], size=11, pad=10,
           height=22, weight=700)
    v.text(62, 520, "PD-004 · 第 1 行 · replyAt", 11, s["mark"],
           mono=True, max_w=250)
    v.text(62, 542,
           "「replyAt」2026-03-06 晚于「complaintAt」2026-03-01",
           11.5, s["text"], max_w=566)
    v.text(62, 560, "建议核对：两个日期是否填反；本条只比较先后", 11,
           s["faint"], max_w=560)

    v.panel(664, 472, 392, 96, s["panel"], s["edge"])
    v.text(682, 496, "skipped[] · 1 条", 13.5, s["sub"], weight=700, max_w=170)
    v.chip(1036, 482, "PD-005", s["faint"], s["band"], size=11, pad=10,
           height=22, weight=700)
    v.text(682, 520, "PD-005 · values 未配置", 11, s["faint"], mono=True,
           max_w=260)
    v.text(682, 542, "「status」取值口径由本机构规定，不硬编码", 11.5,
           s["text"], max_w=354)
    v.text(682, 560, "空 issues ≠ 没问题：两条通道一起读", 11, s["faint"],
           max_w=354)

    # ---- reviewer -----------------------------------------------------------
    v.panel(44, 576, 1012, 30, s["panel"], s["accent"])
    v.text(62, 596, "复核人 · 结论不在报告里", 13.5, s["text"], weight=700,
           max_w=300)
    v.text(1038, 596, "不判是否逾期 / 是否受理 / 是否驳回", 11.5, s["sub"],
           anchor="end", max_w=300)

    # ---- footer -------------------------------------------------------------
    v.line(44, 616, 1056, 616, stroke=s["rule"], sw=1)
    v.text(44, 636,
           "严重级封顶：direct ≤ error · derived-from-principle ≤ warn · "
           "institutional-configuration ≤ info",
           11, s["sub"], max_w=1012)
    v.text(44, 652,
           "config：rulesFile · disabledRules · onlyRules · skipNotes · "
           "timeoutMs ｜ 只读材料 · 无网络 · 不调用模型",
           11, s["faint"], max_w=1012)

    if v.overflow:
        raise SystemExit("FATAL: SVG label overflow:\n  " +
                         "\n  ".join(v.overflow))
    return v.svg(
        W, H,
        "dsh-protest-deadline 结构图：一份质疑与投诉台账的日期链上，"
        "PD-002、PD-003、PD-004 三条比较以括号标出（PD-004 不成立）；"
        "台账级 PD-001/005/006/007 另列；issues[] 与 skipped[] 汇到复核人，"
        "结论不在报告里")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        name = f"dsh-protest-deadline-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as handle:
            handle.write(flow_svg(skin))
        print(f"wrote {name} (1100×660)")


if __name__ == "__main__":
    main()
