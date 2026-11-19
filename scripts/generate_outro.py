#!/usr/bin/env python3
"""Builds assets/outro.gif from scratch: a navy sign-off card with the headline, a terminal window that
types a little git session, and the mascot. Loops forever.
Needs: pip install pillow fonttools brotli (+ DejaVu Sans Mono, preinstalled on most Linux).
Usage: python scripts/generate_outro.py
"""
import io, math
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

W, H, S = 1200, 440, 2
NAVY, NAVY2, TERM, BAR = (16, 24, 39), (30, 26, 46), (10, 14, 24), (24, 30, 46)
CORAL, SAFFRON, IVORY, MUTED, GREEN = (255, 117, 74), (255, 170, 70), (250, 246, 238), (150, 160, 178), (126, 222, 146)
SOFT = (200, 207, 220)   # terminal output: clearly readable but quieter than commands


def poppins(px, w="bold"):
    f = TTFont(f"assets/fonts/poppins-{w}.woff2"); f.flavor = None; b = io.BytesIO(); f.save(b); b.seek(0)
    return ImageFont.truetype(b, round(px * S))


H1, H2, BADGE, TITLE = poppins(38), poppins(26), poppins(13), poppins(12, "semibold")
MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22 * S)
ease = lambda p: 1 - (1 - max(0.0, min(1.0, p))) ** 3

CMDS = [[("git add .", IVORY)],
        [("git commit -m ", IVORY), ('"chore: improving every day"', SAFFRON)],
        [("git push origin dreams", IVORY)]]
OUT = [("✓ ", GREEN), ("pushed", GREEN), (" · see you in the next commit", SOFT)]
FRAME_MS, CHARS_PER_FRAME, ENTER_FRAMES = 50, 1.2, 6

# ---------- static background ----------
def background():
    bg = Image.new("RGB", (W * S, H * S), NAVY)
    grad = Image.linear_gradient("L").rotate(90).resize((W * S, H * S))      # left->right
    bg = Image.composite(Image.new("RGB", bg.size, NAVY2), bg, grad)
    d = ImageDraw.Draw(bg, "RGBA")
    clip = Image.new("L", bg.size, 0); ImageDraw.Draw(clip).rounded_rectangle((16 * S, 16 * S, (W - 16) * S, (H - 16) * S), 24 * S, fill=255)
    deco = Image.new("RGBA", bg.size, (0, 0, 0, 0)); g = ImageDraw.Draw(deco)
    cx, cy, r = 1150, -30, 120                                               # coral corner, like the hero
    g.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=CORAL + (235,))
    g.ellipse(((cx - r * 1.5) * S, (cy - r * 1.5) * S, (cx + r * 1.5) * S, (cy + r * 1.5) * S), outline=CORAL + (90,), width=2 * S)
    for x in range(40, W - 40, 28):                                          # faint dot grid, bottom-right
        for y in range(250, H - 30, 28):
            if x > 760: g.ellipse(((x - 1) * S, (y - 1) * S, (x + 1) * S, (y + 1) * S), fill=IVORY + (22,))
    deco.putalpha(Image.composite(deco.getchannel("A"), Image.new("L", bg.size, 0), clip))
    bg.paste(deco, (0, 0), deco)
    out = Image.new("RGB", bg.size, (13, 17, 23))                            # outside the card = GitHub dark
    out.paste(bg, (0, 0), clip)
    ImageDraw.Draw(out).rounded_rectangle((16 * S, 16 * S, (W - 16) * S, (H - 16) * S), 24 * S, outline=CORAL + (0,), width=2 * S)
    o = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(o).rounded_rectangle((16 * S, 16 * S, (W - 16) * S, (H - 16) * S), 24 * S, outline=(255, 117, 74, 110), width=2 * S)
    out.paste(o, (0, 0), o)
    return out


BG = background()
mascot = Image.open("assets/vansh-mascot.png").convert("RGBA")
MW = 360 * S; mascot = mascot.resize((MW, round(mascot.height * MW / mascot.width)), Image.LANCZOS)
MX, MY = 812 * S, (H - 22) * S - mascot.height

TX0, TY0, TX1, TY1 = 56, 200, 740, 404                                      # terminal window

# ---------- timeline ----------
INTRO = 14
lens = [sum(len(t) for t, _ in l) for l in CMDS]
type_frames = round(sum(lens) / CHARS_PER_FRAME) + ENTER_FRAMES * len(CMDS)
OUT_AT = INTRO + 6 + type_frames
HOLD = OUT_AT + 6
N = HOLD + 1 + 6                                                             # + fade-out frames


def typed(k):
    """k = frames since typing began -> (line, chars typed on it)."""
    for li, n in enumerate(lens):
        f = math.ceil(n / CHARS_PER_FRAME)
        if k < f: return li, int(k * CHARS_PER_FRAME)
        k -= f
        if k < ENTER_FRAMES: return li, n
        k -= ENTER_FRAMES
    return len(lens), 0


def text(L, xy, s, font, col, a=1.0, anchor="ls"):
    ImageDraw.Draw(L).text((xy[0] * S, xy[1] * S), s, font=font, fill=col + (int(255 * a),), anchor=anchor)


frames, durs = [], []
for f in range(N):
    fade = 1 - ease((f - HOLD - 1) / 6) if f > HOLD else 1.0
    L = Image.new("RGBA", BG.size, (0, 0, 0, 0)); g = ImageDraw.Draw(L)
    # badge
    on = (f // 10) % 2 == 0
    g.ellipse((56 * S, 50 * S, 66 * S, 60 * S), fill=SAFFRON + (int((255 if on else 110) * fade),))
    g.ellipse((53 * S, 47 * S, 69 * S, 63 * S), outline=SAFFRON + (int(80 * fade),), width=S)
    text(L, (80, 60), "OPEN FOR COLLABS  ·  FREELANCE  ·  OPEN SOURCE", BADGE, SAFFRON, fade)
    # headline (slides up)
    p1, p2 = ease(f / 8), ease((f - 4) / 8)
    text(L, (56, 128 + (1 - p1) * 14), "Thanks for visiting!", H1, IVORY, p1 * fade)
    text(L, (56, 172 + (1 - p2) * 14), "Let's connect & build something incredible.", H2, CORAL, p2 * fade)
    # terminal window
    pt = ease((f - 8) / 6)
    if pt > 0:
        a = pt * fade; dy = (1 - pt) * 12
        g.rounded_rectangle((TX0 * S, (TY0 + dy) * S, TX1 * S, (TY1 + dy) * S), 14 * S, fill=TERM + (int(235 * a),),
                            outline=IVORY + (int(30 * a),), width=S)
        g.rounded_rectangle((TX0 * S, (TY0 + dy) * S, TX1 * S, (TY0 + 30 + dy) * S), 14 * S, fill=BAR + (int(255 * a),))
        g.rectangle((TX0 * S, (TY0 + 16 + dy) * S, TX1 * S, (TY0 + 30 + dy) * S), fill=BAR + (int(255 * a),))
        for k, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
            x = TX0 + 20 + k * 18; y = TY0 + 15 + dy
            g.ellipse(((x - 5) * S, (y - 5) * S, (x + 5) * S, (y + 5) * S), fill=c + (int(255 * a),))
        text(L, ((TX0 + TX1) / 2, TY0 + 20 + dy), "vansh@hustler: ~/life", TITLE, MUTED, a, anchor="ms")
        if f >= INTRO + 6:
            cur, n = typed(f - INTRO - 6)
            for li, line in enumerate(CMDS[:min(cur + 1, len(CMDS))]):
                y = TY0 + 66 + li * 34; x = TX0 + 24
                left = lens[li] if li < cur else n
                text(L, (x, y), "$", MONO, CORAL, a); x += MONO.getlength("$ ") / S
                for t, c in line:
                    part = t[:max(0, left)]; left -= len(t)
                    text(L, (x, y), part, MONO, c, a); x += MONO.getlength(part) / S
                if li == cur and (f // 4) % 2 == 0 or (li == cur and n < lens[li]):
                    g.rectangle(((x + 3) * S, (y - 18) * S, (x + 14) * S, (y + 4) * S), fill=SAFFRON + (int(255 * a),))
            if f >= OUT_AT:
                po = ease((f - OUT_AT) / 4); x = TX0 + 24; y = TY0 + 66 + 3 * 34
                for t, c in OUT:
                    text(L, (x, y), t, MONO, c, po * a); x += MONO.getlength(t) / S
    # mascot (rises in)
    pm = ease(f / 10)
    frame = BG.copy().convert("RGBA")
    m = mascot.copy(); m.putalpha(m.getchannel("A").point(lambda v, k=pm * fade: int(v * k)))
    frame.alpha_composite(m, (MX, MY + int((1 - pm) * 24 * S)))
    frame.alpha_composite(L)
    frames.append(frame.convert("RGB").resize((W, H), Image.LANCZOS))
    durs.append(3200 if f == HOLD else (500 if f == N - 1 else FRAME_MS))

# palette from the full final frame plus swatches of the small accent colours (so they survive quantising)
sample = Image.new("RGB", (W, H + 40)); sample.paste(frames[HOLD], (0, 0))
for k, c in enumerate([SOFT, CORAL, SAFFRON, GREEN, (255, 95, 86), (255, 189, 46), (39, 201, 63), MUTED, IVORY]):
    sample.paste(c, (k * 130, H, k * 130 + 130, H + 40))
pal = sample.quantize(255, method=Image.MEDIANCUT)
gif = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
gif[0].save("assets/outro.gif", save_all=True, append_images=gif[1:], duration=durs, loop=0, optimize=False)
print("outro.gif:", N, "frames,", sum(durs) / 1000, "s")
