#!/usr/bin/env python3
"""Builds the animated hero banners (assets/hero.gif, assets/hero-mobile.gif) from the static bases
assets/hero.png / hero-mobile.png + assets/vansh-mascot.png. The tagline arcs over the mascot's head
and types itself in letter by letter; the GIF plays once and rests on the final frame.
Needs: pip install pillow fonttools brotli.   Usage: python scripts/generate_hero.py
"""
import io, math
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

CREAM, CORAL, SAFFRON, INK = (255, 243, 223), (255, 114, 71), (255, 153, 51), (23, 32, 51)
S = 3  # supersampling for smooth glyphs / arcs


def poppins(size):
    f = TTFont("assets/fonts/poppins-bold.woff2"); f.flavor = None; b = io.BytesIO(); f.save(b); b.seek(0)
    return ImageFont.truetype(b, size)


def ease(p): return 1 - (1 - max(0, min(1, p))) ** 3


def arc_text_layout(font, text, track, R):
    """Per-char (char, angle) so the string is centred on the top of a circle of radius R."""
    ws = [font.getlength(c) / S + track for c in text]; total = sum(ws) - track
    a, out = -total / R / 2, []
    for c, w in zip(text, ws):
        out.append((c, a + (w - track) / 2 / R)); a += w / R
    return out, math.degrees(total / R)


def glyph(font, ch, col, alpha, ang):
    n = font.size * 3; g = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(g).text((n // 2, n // 2), ch, font=font, fill=col + (int(255 * alpha),), anchor="ms")
    return g.rotate(-math.degrees(ang), resample=Image.BICUBIC, center=(n // 2, n // 2)), n


def build(base, mascot, cfg, out):
    """cfg["rings"]: [(text, radius, font_px, tracking, colour_fn)] — typed in one after another."""
    W, H = base.size; cx, cy = cfg["cx"], cfg["cy"]
    glyphs, spans = [], []                   # (char, angle, radius, font, colour) in typing order
    for text, R, fpx, track, colour in cfg["rings"]:
        font = poppins(fpx * S); layout, span = arc_text_layout(font, text, track, R)
        assert span < 170, f"{text!r} too long for its arc ({span:.0f}°)"
        glyphs += [(c, a, R, font, colour(i, c)) for i, (c, a) in enumerate(layout)]; spans.append(span)
    half = spans[0] / 2 + 7                  # bands hug the tagline: just a touch wider than the words
    m = mascot.resize((cfg["mw"], round(mascot.height * cfg["mw"] / mascot.width)), Image.LANCZOS)
    BAND, PER = 10, 4                       # frames for the band sweep, frames per glyph fade-in
    n_frames = BAND + len(glyphs) + PER + 1
    frames = []
    for f in range(n_frames):
        L = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
        h = half * ease(f / BAND)            # bands grow outward from the top centre
        for r, col in cfg["bands"]:
            if h < 0.5: continue
            g.arc(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), 270 - h, 270 + h, fill=col, width=5 * S)
            for a in (-h, h):                # round caps
                x, y = cx + r * math.sin(math.radians(a)), cy - r * math.cos(math.radians(a))
                g.ellipse(((x - 2) * S, (y - 2) * S, (x + 2) * S, (y + 2) * S), fill=col)
        if f >= BAND:                        # tiny saffron dots just past the band ends
            for a in (-half - 4.5, half + 4.5):
                r = (cfg["bands"][0][0] + cfg["bands"][1][0]) / 2
                x, y = cx + r * math.sin(math.radians(a)), cy - r * math.cos(math.radians(a))
                g.ellipse(((x - 3) * S, (y - 3) * S, (x + 3) * S, (y + 3) * S), fill=SAFFRON)
        for i, (ch, a, R, font, col) in enumerate(glyphs):
            p = ease((f - BAND - i + 1) / PER)
            if p <= 0 or ch == " ": continue
            gl, n = glyph(font, ch, col, p, a)
            rr = R + (1 - p) * 10            # glyphs drop onto the arc
            x, y = cx + rr * math.sin(a), cy - rr * math.cos(a)
            L.alpha_composite(gl, (int(x * S - n / 2), int(y * S - n / 2)))
        fr = base.copy(); fr.alpha_composite(m, (cx - m.width // 2, cfg["my"]))
        fr.alpha_composite(L.resize((W, H), Image.LANCZOS))
        frames.append(fr)
    # one shared palette (from the final frame) so colours don't shimmer between frames
    pal = frames[-1].convert("RGB").quantize(255, method=Image.MEDIANCUT)
    gifs = []
    for fr in frames:
        q = fr.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE)
        q.paste(255, mask=fr.getchannel("A").point(lambda v: 255 if v < 128 else 0))
        gifs.append(q)
    durs = [40] * (len(gifs) - 1) + [60000]
    gifs[0].save(out, save_all=True, append_images=gifs[1:], duration=durs, transparency=255, disposal=1, optimize=False)
    print(out, len(gifs), "frames")


def wipe(im, box, keep=None, clip=None):
    """Paint `box` cream, optionally keeping an ellipse `keep` and clipping to the rounded card `clip`."""
    mask = Image.new("L", im.size, 0); d = ImageDraw.Draw(mask); d.rectangle(box, fill=255)
    if keep: d.ellipse(keep, fill=0)
    if clip:
        c = Image.new("L", im.size, 0); ImageDraw.Draw(c).rounded_rectangle(clip, radius=22, fill=255)
        mask = Image.composite(mask, Image.new("L", im.size, 0), c)
    im.paste(Image.new("RGBA", im.size, CREAM + (255,)), (0, 0), mask)


mascot = Image.open("assets/vansh-mascot.png").convert("RGBA")
dot = lambda ch: ch in "·/"

# ---------------- desktop ----------------
d = Image.open("assets/hero.png").convert("RGBA"); W, H = d.size
jai = d.crop((40, 22, 320, 62))                       # flag + JAI SHREE RAM
wipe(d, (40, 20, 560, 100))                           # drop the old "THE HUSTLER / BUILD..." line
d.alpha_composite(jai, (40, 44))                      # and let the flag sit a bit lower
wipe(d, (590, 0, W, H), clip=(3, 3, W - 4, H - 4))    # clear the old mascot / circle / ring
c = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))   # supersampled so the edge is smooth
ImageDraw.Draw(c).ellipse(((1150 - 150) * S, (-40 - 150) * S, (1150 + 150) * S, (-40 + 150) * S), fill=(255, 117, 74, 255))
c = c.resize((W, H), Image.LANCZOS)
cm = Image.new("L", d.size, 0); ImageDraw.Draw(cm).rounded_rectangle((3, 3, W - 4, H - 4), radius=22, fill=255)
# the old circle covered part of the top border; patch it back with a clean strip of border
strip = Image.open("assets/hero.png").convert("RGBA").crop((400, 0, 550, 6))
for x in range(840, 1060, 150): d.paste(strip, (x, 0))
d.paste(c, (0, 0), Image.composite(c.getchannel("A"), Image.new("L", d.size, 0), cm))

TAG, NAME = "BUILD · BREAK · SHIP · RESTART", "THE HUSTLER"
tag_col = lambda i, ch: SAFFRON if dot(ch) else CORAL
name_col = lambda i, ch: INK

# tagline rides OUTSIDE the coral band, the name sits INSIDE the saffron band
build(d, mascot, dict(
    cx=870, cy=268, mw=320, my=152,
    bands=[(207, CORAL), (197, SAFFRON)],
    rings=[(TAG, 220, 20, 3.6, tag_col), (NAME, 160, 16, 6.5, name_col)],
), "assets/hero.gif")

# ---------------- mobile ----------------
mb = Image.open("assets/hero-mobile.png").convert("RGBA")
wipe(mb, (105, 30, 665, 505), keep=(660 - 112, 30 - 112, 660 + 112, 30 + 112))
build(mb, mascot, dict(
    cx=378, cy=330, mw=380, my=184,
    bands=[(236, CORAL), (224, SAFFRON)],
    rings=[(TAG, 250, 26, 4.4, tag_col), (NAME, 180, 21, 8, name_col)],
), "assets/hero-mobile.gif")
