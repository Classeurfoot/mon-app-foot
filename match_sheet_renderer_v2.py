
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
import re
import unicodedata

W, H = 1280, 1220

# ---------- COLORS ----------
BG = (247, 248, 250)
CARD = (252, 252, 252)
TEXT = (16, 28, 45)
MUTED = (78, 92, 112)
BORDER = (199, 211, 224)

PITCH_1 = (166, 213, 105)
PITCH_2 = (155, 205, 95)
PITCH_LINE = (245, 248, 242)

HOME = (224, 18, 30)
AWAY = (37, 37, 37)
WHITE = (255, 255, 255)
YELLOW = (255, 194, 0)
RED = (216, 20, 30)
GREEN = (17, 151, 66)
LIGHT_GREY = (224, 231, 239)


# ---------- FONTS ----------
def _font_candidates(bold=False):
    if bold:
        return [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/Arialbd.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
            "/usr/share/fonts/truetype/arimo/Arimo-Bold.ttf",
        ]
    return [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/usr/share/fonts/truetype/arimo/Arimo-Regular.ttf",
    ]

def font(size, bold=False):
    for p in _font_candidates(bold):
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    # Linux fc-match often maps Arial to Arimo.
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()

F_COMP = font(30, True)
F_SUB = font(25, False)
F_REF = font(24, False)
F_TEAM = font(31, True)
F_COACH = font(24, False)
F_SCORE = font(66, True)
F_GOAL_TOP = font(22, False)
F_PLAYER_NUM = font(19, True)
F_PLAYER_NAME = font(21, True)
F_EVENT = font(18, False)
F_SCORERS = font(24, False)
F_SCORERS_B = font(24, True)
F_LEGEND = font(20, False)
F_LEGEND_B = font(20, True)
F_CAPTAIN = font(14, True)


# ---------- HELPERS ----------
def normalize_name(name):
    if not name:
        return ""
    s = ''.join(
        c for c in unicodedata.normalize("NFD", str(name))
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]", "", s.lower())

def find_logo(team_name, logos_dir="Logos"):
    key = normalize_name(team_name)
    root = Path(logos_dir)
    if not root.exists():
        return None
    for p in root.rglob("*"):
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            if normalize_name(p.stem) == key:
                return str(p)
    return None

def rounded(draw, box, radius=16, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def text_width(draw, text, fnt):
    b = draw.textbbox((0,0), str(text), font=fnt)
    return b[2] - b[0]

def fit_font(draw, text, max_width, preferred=21, minimum=15, bold=True):
    size = preferred
    while size > minimum:
        f = font(size, bold)
        if text_width(draw, text, f) <= max_width:
            return f
        size -= 1
    return font(minimum, bold)

def paste_logo(img, path, center, max_size=(115,115)):
    if not path or not os.path.exists(path):
        return
    try:
        logo = Image.open(path).convert("RGBA")
        logo.thumbnail(max_size, Image.Resampling.LANCZOS)
        x = int(center[0] - logo.width/2)
        y = int(center[1] - logo.height/2)
        img.alpha_composite(logo, (x, y))
    except Exception:
        pass

def draw_ball(draw, x, y, r=12):
    draw.ellipse([x-r, y-r, x+r, y+r], fill=WHITE, outline=TEXT, width=2)
    # stylised central pentagon
    pts = [(x, y-r*0.45), (x+r*0.43,y-r*0.12), (x+r*0.27,y+r*0.4),
           (x-r*0.27,y+r*0.4), (x-r*0.43,y-r*0.12)]
    draw.polygon(pts, fill=TEXT)
    # small spokes
    for dx,dy in [(0,-r),(r*0.9,-r*0.1),(r*0.55,r*0.8),(-r*0.55,r*0.8),(-r*0.9,-r*0.1)]:
        draw.line([(x, y), (x+dx*0.65, y+dy*0.65)], fill=TEXT, width=1)

def draw_card(draw, x, y, color, w=18, h=24):
    rounded(draw, [x, y, x+w, y+h], radius=2, fill=color)

def draw_captain(draw, x, y):
    draw.ellipse([x-11,y-11,x+11,y+11], fill=LIGHT_GREY)
    draw.text((x,y), "C", font=F_CAPTAIN, fill=TEXT, anchor="mm")

def score_text(score):
    s = str(score).replace("–", "-").replace("—","-")
    parts = [p.strip() for p in s.split("-")]
    if len(parts) == 2:
        return f"{parts[0]} - {parts[1]}"
    return s


# ---------- PITCH ----------
def draw_pitch(draw, x1, y1, x2, y2):
    # bands
    bands = 12
    bw = (x2-x1)/bands
    for i in range(bands):
        x = int(x1+i*bw)
        xe = int(x1+(i+1)*bw)
        draw.rectangle([x,y1,xe,y2], fill=PITCH_1 if i%2==0 else PITCH_2)

    rounded(draw, [x1,y1,x2,y2], radius=16, outline=PITCH_LINE, width=3)

    mx = (x1+x2)//2
    my = (y1+y2)//2
    draw.line([(mx,y1),(mx,y2)], fill=PITCH_LINE, width=3)
    draw.ellipse([mx-64,my-64,mx+64,my+64], outline=PITCH_LINE, width=3)
    draw.ellipse([mx-4,my-4,mx+4,my+4], fill=PITCH_LINE)

    # penalty areas
    area_h = 275
    area_w = 125
    six_h = 115
    six_w = 50
    draw.rectangle([x1,my-area_h//2,x1+area_w,my+area_h//2], outline=PITCH_LINE, width=3)
    draw.rectangle([x1,my-six_h//2,x1+six_w,my+six_h//2], outline=PITCH_LINE, width=3)
    draw.ellipse([x1+91-4,my-4,x1+91+4,my+4], fill=PITCH_LINE)

    draw.rectangle([x2-area_w,my-area_h//2,x2,my+area_h//2], outline=PITCH_LINE, width=3)
    draw.rectangle([x2-six_w,my-six_h//2,x2,my+six_h//2], outline=PITCH_LINE, width=3)
    draw.ellipse([x2-91-4,my-4,x2-91+4,my+4], fill=PITCH_LINE)


# ---------- PLAYER ----------
def draw_player(draw, px, py, player, side="home"):
    fill = HOME if side == "home" else AWAY
    outline = WHITE
    num_fill = WHITE

    r = 23
    draw.ellipse([px-r,py-r,px+r,py+r], fill=fill, outline=outline, width=2)
    draw.text((px,py), str(player.get("number","")), font=F_PLAYER_NUM, fill=num_fill, anchor="mm")

    # Event icons to the right of the number circle
    evx = px + 33
    evy = py - 7
    if player.get("goal"):
        draw_ball(draw, evx, evy, r=9)
        if player.get("goal_min"):
            draw.text((evx+15, evy), str(player["goal_min"]), font=F_EVENT, fill=TEXT, anchor="lm")
        evy += 24
    if player.get("yellow"):
        draw_card(draw, evx-7, evy-10, YELLOW, 15, 20)
        if isinstance(player.get("yellow"), str):
            draw.text((evx+15, evy), player["yellow"], font=F_EVENT, fill=TEXT, anchor="lm")
        evy += 23
    if player.get("red"):
        draw_card(draw, evx-7, evy-10, RED, 15, 20)
        if isinstance(player.get("red"), str):
            draw.text((evx+15, evy), player["red"], font=F_EVENT, fill=TEXT, anchor="lm")

    # Name
    name = str(player.get("name",""))
    name_font = fit_font(draw, name, 165, preferred=21, minimum=15, bold=True)
    draw.text((px,py+42), name, font=name_font, fill=TEXT, anchor="mm")

    if player.get("captain"):
        name_w = text_width(draw, name, name_font)
        draw_captain(draw, px + min(name_w/2 + 18, 78), py+42)

    # substitutions below name, small and clean
    y = py + 68
    if player.get("sub_out"):
        draw.text((px, y), f"↓ {player['sub_out']}", font=F_EVENT, fill=RED, anchor="mm")
        y += 23
    if player.get("sub_in"):
        draw.text((px, y), f"↑ {player['sub_in']}", font=F_EVENT, fill=GREEN, anchor="mm")


def render_match_sheet(match, output_path, logos_dir="Logos"):
    img = Image.new("RGBA", (W,H), BG + (255,))
    draw = ImageDraw.Draw(img)

    # Main card
    rounded(draw, [6,6,W-6,H-6], radius=16, fill=CARD, outline=BORDER, width=2)

    # Header
    draw.text((45,27), match["competition_title"], font=F_COMP, fill=TEXT)
    draw.text((45,71), match["subtitle"], font=F_SUB, fill=TEXT)
    draw.text((45,109), f"Arbitre : {match.get('referee','-')}", font=F_REF, fill=TEXT)

    draw.text((W-45,27), match.get("stadium",""), font=F_SUB, fill=TEXT, anchor="ra")
    draw.text((W-45,71), match.get("attendance",""), font=F_SUB, fill=TEXT, anchor="ra")

    # Crest/team/score row
    team_y = 180
    paste_logo(img, find_logo(match["home_team"], logos_dir), (112, 196))
    paste_logo(img, find_logo(match["away_team"], logos_dir), (W-112, 196))

    draw.text((290,team_y), match["home_team"], font=F_TEAM, fill=TEXT, anchor="mm")
    draw.text((W-290,team_y), match["away_team"], font=F_TEAM, fill=TEXT, anchor="mm")

    draw.line([(530,128),(530,228)], fill=BORDER, width=2)
    draw.line([(750,128),(750,228)], fill=BORDER, width=2)
    draw.text((640,178), score_text(match["score"]), font=F_SCORE, fill=TEXT, anchor="mm")

    # Top scorers below score
    goals = match.get("goals_top", [])
    gy = 223
    for g in goals[:3]:
        draw_ball(draw, 565, gy, r=10)
        draw.text((590,gy), g, font=F_GOAL_TOP, fill=TEXT, anchor="lm")
        gy += 35

    # Coaches
    draw.text((75,309), f"Entraîneur : {match.get('home_coach','')}", font=F_COACH, fill=TEXT)
    draw.text((W-75,309), f"Entraîneur : {match.get('away_coach','')}", font=F_COACH, fill=TEXT, anchor="ra")

    # Pitch
    x1, y1, x2, y2 = 24, 340, W-24, 942
    draw_pitch(draw, x1,y1,x2,y2)

    # Players use 0..1 coords over full pitch
    for p in match.get("home_players", []):
        px = int(x1 + p["x"]*(x2-x1))
        py = int(y1 + p["y"]*(y2-y1))
        draw_player(draw, px, py, p, "home")

    for p in match.get("away_players", []):
        px = int(x1 + p["x"]*(x2-x1))
        py = int(y1 + p["y"]*(y2-y1))
        draw_player(draw, px, py, p, "away")

    # Bottom scorers band
    draw.text((50,978), "Buts :", font=F_SCORERS_B, fill=TEXT)
    draw.text((130,978), match.get("home_goals","-"), font=F_SCORERS, fill=TEXT)

    draw.text((W-50,978), f"Buts : {match.get('away_goals','-')}", font=F_SCORERS_B, fill=TEXT, anchor="ra")

    # Legend
    draw.line([(24,1045),(W-24,1045)], fill=BORDER, width=1)
    ly = 1114

    # ball
    draw_ball(draw, 70, ly, r=12)
    draw.text((96,ly), "But", font=F_LEGEND, fill=TEXT, anchor="lm")

    draw_card(draw, 175, ly-12, YELLOW, 20, 24)
    draw.text((210,ly), "Carton jaune", font=F_LEGEND, fill=TEXT, anchor="lm")

    draw_card(draw, 365, ly-12, RED, 20, 24)
    draw.text((400,ly), "Carton rouge", font=F_LEGEND, fill=TEXT, anchor="lm")

    draw.text((598,ly), "↓", font=font(31, True), fill=RED, anchor="mm")
    draw.text((625,ly), "Joueur sortant", font=F_LEGEND, fill=TEXT, anchor="lm")

    draw.text((830,ly), "↑", font=font(31, True), fill=GREEN, anchor="mm")
    draw.text((857,ly), "Joueur entrant", font=F_LEGEND, fill=TEXT, anchor="lm")

    draw_captain(draw, 1075, ly)
    draw.text((1102,ly), "Capitaine", font=F_LEGEND, fill=TEXT, anchor="lm")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, quality=95)
    return output_path
