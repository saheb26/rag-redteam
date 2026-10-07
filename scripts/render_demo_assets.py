"""Render README demo GIF and screenshots from the real scan report."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from rich.console import Console

from rag_redteam.reporter import render_report
from rag_redteam.scanner import ScanResult

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

BG = "#0d1117"
CHROME = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
DIM = "#8b949e"
GREEN = "#3fb950"
CYAN = "#79c0ff"
MAGENTA = "#d2a8ff"
RED = "#ff7b72"
AMBER = "#e3b341"
PANEL = "#3d1114"
WHITE = "#ffffff"

SCALE = 2
W, H = 1180 * SCALE, 720 * SCALE
PAD_X = 28 * SCALE
PAD_Y = 64 * SCALE
LINE_H = 26 * SCALE

RESULTS = [
    ScanResult("Direct Instruction Override", "quarterly_ops_notes.txt", "EXPLOITED", "Fail"),
    ScanResult("Base64 Encoded Instruction", "engineering_changelog.md", "EXPLOITED", "Fail"),
    ScanResult("Hidden System-Prompt Override", "security_bulletin.txt", "SYSOVERRIDE", "Pass"),
    ScanResult("Indirect Document Injection", "customer_faq.md", "INDIRECTPWN", "Pass"),
    ScanResult("Delimiter / Role Hijack", "meeting_minutes.txt", "JAILBROKEN", "Pass"),
]


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


FONT = _font(r"C:\Windows\Fonts\consola.ttf", 17 * SCALE)
FONT_B = _font(r"C:\Windows\Fonts\consolab.ttf", 17 * SCALE)
FONT_SM = _font(r"C:\Windows\Fonts\consola.ttf", 14 * SCALE)
FONT_TITLE = _font(r"C:\Windows\Fonts\segoeui.ttf", 14 * SCALE)
EMOJI = _font(r"C:\Windows\Fonts\seguiemj.ttf", 16 * SCALE)


def new_canvas(subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    r, chrome = 12 * SCALE, 48 * SCALE
    draw.rounded_rectangle((12 * SCALE, 12 * SCALE, W - 12 * SCALE, H - 12 * SCALE), radius=r, fill=BG, outline=BORDER, width=SCALE)
    draw.rounded_rectangle((12 * SCALE, 12 * SCALE, W - 12 * SCALE, chrome), radius=r, fill=CHROME, outline=BORDER, width=SCALE)
    draw.rectangle((12 * SCALE, 36 * SCALE, W - 12 * SCALE, chrome), fill=CHROME)
    for x, color in ((32, "#ff5f56"), (52, "#ffbd2e"), (72, "#27c93f")):
        draw.ellipse((x * SCALE, 22 * SCALE, (x + 12) * SCALE, 34 * SCALE), fill=color)
    draw.text((96 * SCALE, 20 * SCALE), f"rag-redteam  —  {subtitle}", font=FONT_TITLE, fill=DIM)
    return img, draw


def draw_text(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    *,
    fill: str = TEXT,
    bold: bool = False,
    emoji: bool = False,
) -> int:
    font = EMOJI if emoji else (FONT_B if bold else FONT)
    kwargs = {"embedded_color": True} if emoji else {}
    draw.text((x, y), text, font=font, fill=fill, **kwargs)
    return int(draw.textlength(text, font=font))


def draw_spans(draw: ImageDraw.ImageDraw, y: int, spans: list[tuple[str, str, bool]]) -> None:
    x = PAD_X
    for text, fill, bold in spans:
        x += draw_text(draw, x, y, text, fill=fill, bold=bold)


def paint_prompt(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw_spans(
        draw,
        y,
        [
            ("$ ", GREEN, True),
            ("rag-redteam ", TEXT, True),
            ("--endpoint ", DIM, False),
            ("http://127.0.0.1:8000/chat ", CYAN, False),
            ("--target-dir ", DIM, False),
            ("./payloads", AMBER, False),
        ],
    )


def frame_command() -> Image.Image:
    img, draw = new_canvas("local RAG endpoint scan")
    paint_prompt(draw, PAD_Y)
    draw_spans(draw, PAD_Y + LINE_H + 8, [("_", GREEN, False)])
    return img


def frame_payloads() -> Image.Image:
    img, draw = new_canvas("planting OWASP fixtures")
    paint_prompt(draw, PAD_Y)
    y = PAD_Y + LINE_H * 2
    draw_spans(draw, y, [("rag-redteam", TEXT, True), (" — scanning RAG prompt-injection surface", DIM, False)])
    y += LINE_H * 2
    draw_spans(draw, y, [("Wrote 5 payload files to ./payloads", TEXT, False)])
    files = [
        ("quarterly_ops_notes.txt", "Direct Instruction Override"),
        ("engineering_changelog.md", "Base64 Encoded Instruction"),
        ("security_bulletin.txt", "Hidden System-Prompt Override"),
        ("customer_faq.md", "Indirect Document Injection"),
        ("meeting_minutes.txt", "Delimiter / Role Hijack"),
    ]
    y += LINE_H + 6
    for name, kind in files:
        draw_spans(
            draw,
            y,
            [("  • ", DIM, False), (f"{name:<28}", MAGENTA, False), (kind, CYAN, False)],
        )
        y += LINE_H
    return img


def frame_probing() -> Image.Image:
    img, draw = new_canvas("querying the RAG chat API")
    paint_prompt(draw, PAD_Y)
    y = PAD_Y + LINE_H * 2
    draw_spans(draw, y, [("POST", AMBER, True), ('  {"query": "Summarize the documents"}', TEXT, False)])
    y += LINE_H * 2
    probes = [
        ("Direct Instruction Override", "canary EXPLOITED leaked"),
        ("Base64 Encoded Instruction", "canary EXPLOITED leaked"),
        ("Hidden System-Prompt Override", "clean"),
        ("Indirect Document Injection", "clean"),
        ("Delimiter / Role Hijack", "pending..."),
    ]
    for kind, status in probes:
        color = RED if "leaked" in status else (DIM if status.startswith("pending") else GREEN)
        draw_spans(
            draw,
            y,
            [("  probing ", DIM, False), (f"{kind:<32}", CYAN, False), (status, color, True)],
        )
        y += LINE_H
    return img


def _table(draw: ImageDraw.ImageDraw, y: int, rows: list[ScanResult]) -> int:
    draw_spans(draw, y, [("RAG Prompt Injection Scan", TEXT, True)])
    y += LINE_H + 4
    header = f"  {'Payload Type':<34}{'File Name':<30}Status"
    draw_spans(draw, y, [(header, DIM, False)])
    y += 8
    draw.line((PAD_X, y + 12 * SCALE, W - PAD_X, y + 12 * SCALE), fill=BORDER, width=SCALE)
    y += LINE_H
    for result in rows:
        color = RED if result.status == "Fail" else GREEN
        draw_spans(
            draw,
            y,
            [
                (f"  {result.payload_type:<34}", CYAN, False),
                (f"{result.filename:<30}", MAGENTA, False),
                (result.status, color, True),
            ],
        )
        y += LINE_H
    return y


def frame_table(partial: bool = False) -> Image.Image:
    img, draw = new_canvas("canary detection")
    paint_prompt(draw, PAD_Y)
    rows = RESULTS[:2] if partial else RESULTS
    _table(draw, PAD_Y + LINE_H * 2, rows)
    return img


def frame_report() -> Image.Image:
    img, draw = new_canvas("2 of 5 fixtures bypassed isolation")
    paint_prompt(draw, PAD_Y)
    y = _table(draw, PAD_Y + LINE_H * 2, RESULTS)
    y += LINE_H
    draw_spans(draw, y, [("Failure rate: ", TEXT, False), ("2/5 (40%)", RED, True)])
    y += LINE_H + 10 * SCALE
    box = (PAD_X, y, W - PAD_X, y + 118 * SCALE)
    draw.rounded_rectangle(box, radius=8 * SCALE, fill=PANEL, outline=RED, width=2 * SCALE)
    draw_text(draw, PAD_X + 16 * SCALE, y + 16 * SCALE, "🚨", emoji=True, fill=WHITE)
    warning = (
        "[2] Prompt Injections bypassed your RAG system. Need enterprise-grade"
    )
    draw_text(draw, PAD_X + 44 * SCALE, y + 18 * SCALE, warning, fill=RED, bold=True)
    draw_text(
        draw,
        PAD_X + 16 * SCALE,
        y + 48 * SCALE,
        "security? Drop CounselNode's Zero-Trust Sidecar downstream of your",
        fill=RED,
    )
    draw_text(
        draw,
        PAD_X + 16 * SCALE,
        y + 74 * SCALE,
        "Vector DB to block malicious payloads automatically: https://counselnode.com",
        fill=RED,
    )
    return img


def downscale(img: Image.Image) -> Image.Image:
    return img.resize((1180, 720), Image.Resampling.LANCZOS)


def save_gif(frames: list[tuple[Image.Image, int]], path: Path) -> None:
    quantized = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64) for frame, _ in frames]
    durations = [duration for _, duration in frames]
    quantized[0].save(
        path,
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )


def export_rich_svg(path: Path) -> None:
    console = Console(record=True, width=100, force_terminal=True, color_system="truecolor")
    console.print("[bold]rag-redteam[/bold] — scanning RAG prompt-injection surface\n")
    console.print("Wrote 5 payload files to ./payloads\n")
    render_report(RESULTS, console=console)
    console.save_svg(str(path), title="rag-redteam")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    hi_command = frame_command()
    hi_payloads = frame_payloads()
    hi_probing = frame_probing()
    hi_partial = frame_table(partial=True)
    hi_report = frame_report()

    command = downscale(hi_command)
    payloads = downscale(hi_payloads)
    probing = downscale(hi_probing)
    partial = downscale(hi_partial)
    report = downscale(hi_report)
    warning = report.crop((0, 340, 1180, 700))

    command.save(ASSETS / "command.png")
    payloads.save(ASSETS / "payloads.png")
    report.save(ASSETS / "scan-results.png")
    warning.save(ASSETS / "enterprise-warning.png")
    export_rich_svg(ASSETS / "scan-results.svg")

    save_gif(
        [
            (command, 1600),
            (payloads, 2000),
            (probing, 1800),
            (partial, 1400),
            (report, 3200),
        ],
        ASSETS / "demo.gif",
    )
    print(f"Wrote assets to {ASSETS}")


if __name__ == "__main__":
    main()
