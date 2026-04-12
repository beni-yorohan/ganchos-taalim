#!/usr/bin/env python3
"""
Generate a landscape (1920x1080) teleprompter MP4 for the Q4 Newton Centre
real estate reel. The script scrolls upward at a reading pace so the talent
can read straight from the video while recording.

Output: teleprompter-newton-q4.mp4
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# -------- Config --------
WIDTH       = 1920
FRAME_H     = 1080
FPS         = 30
DURATION    = 75            # seconds; target reading duration

FONT_PATH   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE   = 68
LINE_HEIGHT = int(FONT_SIZE * 1.40)   # ~95 px
PARA_GAP    = int(FONT_SIZE * 0.8)    # extra gap between paragraphs

MARGIN_X    = 140
TOP_PAD     = 540   # half a frame of black above the text
BOTTOM_PAD  = 540   # half a frame of black below the text

BG     = (0, 0, 0)
FG     = (245, 245, 245)
ACCENT = (255, 204, 0)   # yellow for key numbers / hook phrases

OUTPUT  = Path("teleprompter-newton-q4.mp4")
PNG_TMP = Path("/tmp/tp_script.png")

# -------- Script, pre-wrapped line-by-line --------
# Each paragraph = list of (text, color). Paragraphs separated by PARA_GAP.
paragraphs = [
    [("\u201cDid you know Newton Centre home prices",  ACCENT),
     ("dropped nearly 17% in Q4 \u2014",               ACCENT),
     ("but the market is already bouncing back?\u201d", ACCENT)],

    [("Hi, this is Batya",                              FG),
     ("with the Batya & Alex Real Estate Team,",        FG),
     ("and here\u2019s your Q4 Newton Centre",          FG),
     ("market update.",                                 FG)],

    [("In Q4 2025, we saw a clear reset.",              FG),
     ("The median sale price came in at $1.79M,",       FG),
     ("down from $2.16M the year before.",              FG)],

    [("Price per square foot",                          FG),
     ("dropped from $626 to $582,",                     FG),
     ("and days to offer increased",                    FG),
     ("from about 8 to 16 days.",                       FG)],

    [("What does that mean?",                           FG),
     ("Buyers became more selective,",                  FG),
     ("more price-sensitive,",                          FG),
     ("and homes needed stronger",                      FG),
     ("pricing and presentation to sell.",              FG)],

    [("But here\u2019s what\u2019s really important \u2014", FG),
     ("that trend didn\u2019t last.",                   ACCENT)],

    [("Since early 2026,",                              FG),
     ("and especially this spring,",                    FG),
     ("the market has picked back up.",                 FG),
     ("Buyer demand has returned,",                     FG),
     ("open houses are busier,",                        FG),
     ("and well-priced homes are once again",           FG),
     ("seeing strong interest \u2014",                  FG),
     ("and even multiple offers.",                      FG)],

    [("So the takeaway is simple:",                     FG),
     ("The market didn\u2019t slow down \u2014",        ACCENT),
     ("it rebalanced,",                                 ACCENT),
     ("and now it\u2019s gaining momentum again.",      ACCENT)],

    [("If you\u2019re thinking about selling,",         FG),
     ("or want to understand your home\u2019s value",   FG),
     ("in today\u2019s market,",                        FG),
     ("we\u2019d love to help.",                        FG)],
]

# -------- Render tall PNG --------
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

# Measure total text block height
text_h = 0
for para in paragraphs:
    text_h += len(para) * LINE_HEIGHT
    text_h += PARA_GAP
text_h -= PARA_GAP  # no trailing gap

img_h = TOP_PAD + text_h + BOTTOM_PAD
print(f"Rendering script image: {WIDTH}x{img_h} (text block {text_h}px)")

img  = Image.new("RGB", (WIDTH, img_h), BG)
draw = ImageDraw.Draw(img)

y = TOP_PAD
for para in paragraphs:
    for (line, color) in para:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += LINE_HEIGHT
    y += PARA_GAP

img.save(PNG_TMP)
print(f"Saved {PNG_TMP}")

# -------- Build MP4 via ffmpeg --------
scroll_dist = img_h - FRAME_H     # total pixels of upward travel
y_expr      = f"-t*{scroll_dist}/{DURATION}"

print(f"Scroll distance: {scroll_dist}px over {DURATION}s "
      f"({scroll_dist/DURATION:.1f} px/s)")

cmd = [
    "ffmpeg", "-y",
    "-f", "lavfi",
    "-i", f"color=c=black:s={WIDTH}x{FRAME_H}:r={FPS}:d={DURATION}",
    "-loop", "1", "-i", str(PNG_TMP),
    "-filter_complex",
    f"[0:v][1:v]overlay=x=0:y='{y_expr}':shortest=1",
    "-t", str(DURATION),
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "22",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    "-r", str(FPS),
    str(OUTPUT),
]
print("Running ffmpeg...")
subprocess.run(cmd, check=True)
print(f"\nDone: {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")
