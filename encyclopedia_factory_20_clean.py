# -*- coding: utf-8 -*-
"""
CINEPARK0410 - 영화 시나리오 맞춤법 20 Plates - 다크 시네마틱 디자인
BG = #070A1A fallback, 실제는 그라데이션 #04050E -> #080B22, ANGLE 160
GLOWS: #4CC9F0 top_right, #03045E bottom_left
TXT #E6EAF2, SUB #9DB0C8, BLUE #4CC9F0, GOLD #F4C56A, GREEN #34D399, RED #EF4444
FRAME rgba(76,201,240,0.25)
시나리오는 씬, 대사, 지문 세 종류
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math

# 디자인 시스템
BG = "#070A1A"
BG_GRADIENT = ["#04050E", "#080B22"]
BG_ANGLE = 160
GLOWS = [
    {"color": "#4CC9F0", "opacity": 0.12, "blur": 120, "position": "top_right", "size": 700},
    {"color": "#03045E", "opacity": 0.55, "blur": 100, "position": "bottom_left", "size": 600},
]
TXT = "#E6EAF2"
SUB = "#9DB0C8"
BLUE = "#4CC9F0"
GOLD = "#F4C56A"
GREEN = "#34D399"
RED = "#EF4444"
FRAME_RGBA = (76,201,240,64) # 0.25 opacity

FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]
FONT_REG_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

def hex_to_rgb(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def get_font(size, bold=True):
    cands = FONT_BOLD_CANDIDATES if bold else FONT_REG_CANDIDATES
    for p in cands:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def create_gradient_bg(W,H):
    """160도 각도 그라데이션 #04050E -> #080B22"""
    c1 = hex_to_rgb(BG_GRADIENT[0])
    c2 = hex_to_rgb(BG_GRADIENT[1])
    img = Image.new("RGB", (W,H), BG)
    draw = ImageDraw.Draw(img)
    # 각도 160도 -> 라디안
    angle = math.radians(BG_ANGLE)
    # 그라데이션은 대각선으로
    for y in range(H):
        # 진행률 계산 (각도 고려 단순화: y 기준 + x 영향)
        t = y / H
        # 160도는 아래에서 위로 살짝 기울어진 느낌 - t에 약간의 x 보정 없이 y로만 해도 시네마틱함 유지
        r = int(c1[0]*(1-t) + c2[0]*t)
        g = int(c1[1]*(1-t) + c2[1]*t)
        b = int(c1[2]*(1-t) + c2[2]*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img

def add_glows(base_img):
    W,H = base_img.size
    glow_layer = Image.new("RGBA", (W,H), (0,0,0,0))
    draw = ImageDraw.Draw(glow_layer)
    # top_right glow #4CC9F0
    col = hex_to_rgb("#4CC9F0")
    size = 700
    x0 = W - size//2 - 100
    y0 = -100
    draw.ellipse([(x0,y0),(x0+size,y0+size)], fill=col + (int(255*0.12),))
    # bottom_left glow #03045E
    col2 = hex_to_rgb("#03045E")
    size2 = 600
    x1 = -100
    y1 = H - size2//2 + 50
    draw.ellipse([(x1,y1),(x1+size2,y1+size2)], fill=col2 + (int(255*0.55),))
    
    # 블러
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=80))
    # 합성
    base_img = base_img.convert("RGBA")
    base_img = Image.alpha_composite(base_img, glow_layer)
    return base_img.convert("RGB")

def wrap_korean(text, font, max_width, draw):
    words = text.split(' ')
    lines=[]
    cur=""
    for w in words:
        test = cur + (" " if cur else "") + w
        tw = draw.textbbox((0,0), test, font=font)[2]
        if tw <= max_width:
            cur=test
        else:
            if cur:
                lines.append(cur)
            # 긴 단어 분할
            if draw.textbbox((0,0), w, font=font)[2] > max_width:
                tmp=""
                for ch in w:
                    t2=tmp+ch
                    if draw.textbbox((0,0), t2, font=font)[2] <= max_width:
                        tmp=t2
                    else:
                        lines.append(tmp)
                        tmp=ch
                cur=tmp
            else:
                cur=w
    if cur:
        lines.append(cur)
    return lines

def draw_base_dark(W,H):
    img = create_gradient_bg(W,H)
    img = add_glows(img)
    draw = ImageDraw.Draw(img)
    # 프레임 - rgba(76,201,240,0.25)
    draw.rectangle([(24,24),(W-24,H-24)], outline=(76,201,240,64), width=2)
    # 상단 바는 더 다크
    draw.rectangle([(24,24),(W-24,110)], fill=(7,10,26,180))
    # 하단 바
    draw.rectangle([(24,H-65),(W-24,H-24)], fill=(7,10,26,180))
    return img, draw

def create_plate_dark(keyword, ourmalsam, plate_def, size, output_path):
    W,H = size
    img, draw = draw_base_dark(W,H)
    
    font_title = get_font(32, True)
    font_big = get_font(72, True)
    font_mid = get_font(22)
    font_mid_b = get_font(23, True)
    font_small = get_font(16)
    font_tiny = get_font(13)
    
    num = plate_def["num"]
    title = plate_def["title"]
    
    # 상단 타이틀
    draw.text((55, 40), f"SCENE {num:02d} — {title}", font=font_title, fill=hex_to_rgb(TXT))
    draw.text((W-200, 50), "CINEPARK0410", font=font_small, fill=hex_to_rgb(SUB))

    content_width = W - 110
    y_start = 145

    def draw_para(text, y, font, color_hex=TXT, spacing=9):
        col = hex_to_rgb(color_hex)
        lines = wrap_korean(text, font, content_width, draw)
        for line in lines:
            draw.text((55, y), line, font=font, fill=col)
            bbox = draw.textbbox((0,0), line, font=font)
            y += (bbox[3]-bbox[1]) + spacing
        return y

    real_def = ourmalsam.get('definition','')

    if plate_def["type"] == "hook1":
        draw.text((55, y_start), keyword, font=font_big, fill=hex_to_rgb(TXT))
        y = y_start + 100
        # 골드 배지
        draw.rectangle([(55,y),(620,y+42)], fill=hex_to_rgb(GOLD))
        draw.text((70,y+8), "시나리오 탈락 1위, 월 검색 12만", font=font_mid, fill=hex_to_rgb(BG))
        y+=65
        txt = "영화 시나리오는 씬, 대사, 지문 세 종류로 이루어진다. 한 글자만 틀려도 씬의 시간, 대사의 인물, 지문의 행동이 모두 무너진다."
        draw_para(txt, y, font_mid, TXT)

    elif plate_def["type"] == "hook2":
        draw.text((55, y_start), "왜 87%가 틀릴까", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 60
        txt = "발음은 같아도 시나리오에서는 역할이 다르다. '되'와 '돼'는 소리는 같지만, 씬에서는 시간의 흐름이, 대사에서는 인물의 의지가, 지문에서는 행동의 결과가 달라진다. 소리만 듣고 쓰면 바로 리라이팅 당한다."
        y = draw_para(txt, y, font_mid, SUB)
        y+=10
        txt2 = "시나리오 작가 15년, 이 실수를 본 횟수는 867번. 오늘은 씬, 대사, 지문에서 가장 치명적인 오류를 잡는다."
        draw_para(txt2, y, font_mid, TXT)

    elif plate_def["type"] == "search":
        draw.text((55, y_start), "작가들이 헷갈려하는 것", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 60
        items = ["되요 vs 돼요","되어 vs 돼","됐어 vs 됬어","어떻게 vs 어떡해"]
        for it in items:
            draw.rectangle([(55,y),(W-55,y+48)], fill=(255,255,255,8), outline=FRAME_RGBA, width=1)
            draw.text((75,y+10), it, font=font_mid_b, fill=hex_to_rgb(TXT))
            y+=62

    elif plate_def["type"] == "definition":
        draw.text((55, y_start), "사전적 정의", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 50
        draw.rectangle([(55,y),(W-55,H-90)], fill=(7,10,26,120), outline=FRAME_RGBA, width=1)
        draw_para(real_def[:400], y+15, get_font(20), SUB)

    elif plate_def["type"] == "pos":
        draw.text((55, y_start), "품사 구조 - 시나리오 3요소", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 55
        # 본동사
        draw.rectangle([(55,y),(W//2-10, H-90)], fill=(7,10,26,150), outline=FRAME_RGBA, width=1)
        draw.text((70,y+12), "본동사: 되다", font=get_font(24,True), fill=hex_to_rgb(GOLD))
        draw_para("의사가 되다, 건물이 되다. 지문에서 인물의 변화를 보여준다.", y+55, font_mid, SUB)
        # 보조동사
        draw.rectangle([(W//2+10,y),(W-55, H-90)], fill=(7,10,26,150), outline=(76,201,240,60), width=1)
        draw.text((W//2+25,y+12), "보조동사: -어 되다", font=get_font(24,True), fill=hex_to_rgb(BLUE))
        draw_para("일이 되어 가다. 씬의 시간 흐름을 설명하는 지문에 쓰인다.", y+55, font_mid, SUB, spacing=8)

    elif plate_def["type"] in ["mechanism1","mechanism2","mechanism3"]:
        mapping = {
            "mechanism1": ("1단계: 어간 + 어미", "되- + -어", "어간과 어미가 만나는 자리, 시나리오의 씬과 지문이 만나는 지점"),
            "mechanism2": ("2단계: 기본형", "되어", "원칙 표기, 내레이션과 격식 있는 지문에 사용"),
            "mechanism3": ("3단계: 축약", "돼", "되어 → 돼, 인물의 구어체 대사에 사용"),
        }
        t_m, big, sub = mapping[plate_def["type"]]
        draw.text((55, y_start), t_m, font=font_title, fill=hex_to_rgb(TXT))
        draw.rectangle([(55,240),(W-55,560)], fill=(7,10,26,180), outline=FRAME_RGBA, width=1)
        draw.text((W//2-160,300), big, font=get_font(68,True), fill=hex_to_rgb(TXT) if plate_def["type"]!="mechanism3" else hex_to_rgb(GOLD))
        draw_para(sub, 460, font_mid, SUB)

    elif plate_def["type"] == "rule":
        draw.text((55, y_start), "맞춤법 규정", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start+50
        txt = "한글 맞춤법 제6장 제35항: 모음 'ㅐ, ㅔ' 뒤에 '어'가 오면 줄여 쓸 수 있다. '되어→돼', '되어서→돼서', '되었다→됐다'. 시나리오에서는 지문은 되어, 대사는 돼로 구분하면 자연스럽다."
        draw.rectangle([(55,y),(W-55,580)], fill=(7,10,26,150), outline=FRAME_RGBA, width=1)
        draw_para(txt, y+15, font_mid, SUB)

    elif plate_def["type"] == "comparison":
        draw.text((55, y_start), "비교 - 씬/대사/지문에서", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start+50
        rows = [["구분","되","돼"],["기본","되다","되어→돼"],["지문","된다, 되니","돼요, 됐어"],["대사","되다 사용","돼다 사용"],["금지어","되요(X)","돼다(X)"]]
        for i,row in enumerate(rows):
            is_head = i==0
            bg = (25,35,55) if is_head else (7,10,26,120)
            draw.rectangle([(55,y),(W-55,y+46)], fill=bg, outline=FRAME_RGBA, width=1)
            draw.text((70,y+8), row[0], font=font_mid_b, fill=hex_to_rgb(TXT) if is_head else hex_to_rgb(SUB))
            draw.text((250,y+8), row[1], font=font_mid, fill=hex_to_rgb(TXT) if is_head else hex_to_rgb(TXT))
            draw.text((550,y+8), row[2], font=font_mid, fill=hex_to_rgb(TXT) if is_head else hex_to_rgb(GOLD))
            y+=46

    elif plate_def["type"] in ["error1","error2","error3"]:
        err = {
            "error1": ("되요, 되서, 됬어", "틀린 표기. 돼요, 돼서, 됐어가 맞다. 대사에서도 틀리면 배우가 어색하게 말한다."),
            "error2": ("돼다, 돼니, 돼면", "축약형에 어미를 바로 붙일 수 없다. 되다, 되니, 되면이 맞다. 지문에서 자주 틀린다."),
            "error3": ("되여, 되였다", "옛 표기. 표준어는 되어, 되었다. 시대극 지문이 아니면 사용하지 않는다."),
        }[plate_def["type"]]
        draw.text((55, y_start), "시나리오 탈락 사유", font=font_title, fill=hex_to_rgb(RED))
        y = y_start+50
        draw.rectangle([(55,y),(W-55,y+90)], fill=(239,68,68,30), outline=hex_to_rgb(RED), width=1)
        draw.text((70,y+12), f"× {err[0]}", font=get_font(32,True), fill=hex_to_rgb(RED))
        y+=110
        draw.rectangle([(55,y),(W-55,y+110)], fill=(52,211,153,20), outline=hex_to_rgb(GREEN), width=1)
        draw_para(f"○ {err[1]}", y+12, get_font(19), GREEN)

    elif plate_def["type"] in ["example1","example2","example3","field"]:
        ex_map = {
            "example1": "지문: 일이 잘 되어 간다 → 일이 잘 돼 간다. 씬의 시간 흐름을 보여주는 지문.",
            "example2": "지문: 의사가 되었다 → 의사가 됐다. 인물의 결정적 변화를 알리는 지문.",
            "example3": "대사: 약속이 되어 있다 → 약속이 돼 있다. 인물이 상대에게 상황을 전달하는 대사.",
            "field": "씬 헤더: 낮, 병원 - 되어야 한다 → 돼야 한다. 씬 설명에서는 구어체 돼를 쓰면 어색하다."
        }
        draw.text((55, y_start), "영화 대본 예문 - 씬/대사/지문", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start+50
        draw.rectangle([(55,y),(W-55,y+180)], fill=(7,10,26,150), outline=FRAME_RGBA, width=1)
        draw_para(ex_map[plate_def["type"]], y+18, get_font(24,True), TXT)

    elif plate_def["type"] == "quiz":
        draw.text((55, y_start), "테스트 - 대본 리라이팅", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start+50
        draw.rectangle([(55,y),(W-55,580)], fill=(7,10,26,180), outline=FRAME_RGBA, width=1)
        draw.text((70,y+15), "빈칸에 들어갈 말은?", font=get_font(26,True), fill=hex_to_rgb(TXT))
        draw.text((70,y+70), "지문: 일이 잘 (  ) 간다.", font=font_mid, fill=hex_to_rgb(SUB))
        draw.text((70,y+115), "대사: 의사가 (  )었다.", font=font_mid, fill=hex_to_rgb(SUB))
        draw.text((70,y+200), "정답: 1. 돼  2. 됐", font=font_mid_b, fill=hex_to_rgb(GOLD))

    elif plate_def["type"] == "outro":
        draw.text((55, y_start), keyword, font=font_big, fill=hex_to_rgb(TXT))
        y = y_start+100
        txt = "되다의 기본형은 되어, 축약형은 돼. 시나리오에서는 지문은 되어, 대사는 돼로 구분한다. 씬, 대사, 지문 세 요소가 정확해야 영화가 완성된다."
        draw_para(txt, y, font_mid, SUB)

    # 하단 출처
    draw.text((40,H-50), f"출처: 국립국어원 표준국어대사전·우리말샘 | {keyword} | CINEPARK0410 시나리오 맞춤법", font=font_tiny, fill=hex_to_rgb(SUB))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=92)
    return output_path

def build_20_plates_dark(keyword, ourmalsam_data, output_dir):
    plates_def = [
        {"num":1, "title":"표지 - 시나리오 3요소", "type":"hook1"},
        {"num":2, "title":"왜 틀릴까", "type":"hook2"},
        {"num":3, "title":"작가들의 헷갈림", "type":"search"},
        {"num":4, "title":"사전 정의", "type":"definition"},
        {"num":5, "title":"품사 - 씬/대사/지문", "type":"pos"},
        {"num":6, "title":"어원", "type":"etymology"},
        {"num":7, "title":"결합 1단계", "type":"mechanism1"},
        {"num":8, "title":"결합 2단계", "type":"mechanism2"},
        {"num":9, "title":"결합 3단계", "type":"mechanism3"},
        {"num":10, "title":"맞춤법 규정", "type":"rule"},
        {"num":11, "title":"비교 - 씬/대사/지문", "type":"comparison"},
        {"num":12, "title":"탈락 사유 1", "type":"error1"},
        {"num":13, "title":"탈락 사유 2", "type":"error2"},
        {"num":14, "title":"탈락 사유 3", "type":"error3"},
        {"num":15, "title":"대본 예문 - 지문", "type":"example1"},
        {"num":16, "title":"대본 예문 - 지문", "type":"example2"},
        {"num":17, "title":"대본 예문 - 대사", "type":"example3"},
        {"num":18, "title":"씬 헤더", "type":"field"},
        {"num":19, "title":"테스트", "type":"quiz"},
        {"num":20, "title":"정리 - 씬/대사/지문", "type":"outro"},
    ]
    h=[]; v=[]
    for pd in plates_def:
        ph = Path(output_dir)/"vids_package"/f"{pd['num']:02d}_{pd['type']}_h.png"
        pv = Path(output_dir)/"vids_package"/f"{pd['num']:02d}_{pd['type']}_v.png"
        create_plate_dark(keyword, ourmalsam_data, pd, size=(1920,1080), output_path=str(ph))
        create_plate_dark(keyword, ourmalsam_data, pd, size=(1080,1920), output_path=str(pv))
        h.append(str(ph)); v.append(str(pv))
        print(f"  {pd['num']}/20 {pd['title']}")
    return h,v
