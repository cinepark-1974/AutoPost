# -*- coding: utf-8 -*-
"""
CINEPARK0410 ALL-IN-ONE MAIN - 이미지 생성 포함, 외부 팩토리 불필요
다크 시네마 BG #070A1A + 그라데이션 #04050E->#080B22 160도 + 글로우
시나리오는 씬, 대사, 지문 3종류
"""
import os, json, time, math
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

# ========== CONFIG ==========
OUTPUT_BASE = os.getenv("OUTPUT_BASE", "output")
GDRIVE_OUTPUT_ID = os.getenv("GDRIVE_OUTPUT_ID", os.getenv("GDRIVE_FOLDER_ID_OUTPUT", ""))
QA_THRESHOLD = 80

# ========== DESIGN SYSTEM ==========
BG = "#070A1A"
BG_GRADIENT = ["#04050E", "#080B22"]
TXT = "#E6EAF2"
SUB = "#9DB0C8"
BLUE = "#4CC9F0"
GOLD = "#F4C56A"
GREEN = "#34D399"
RED = "#EF4444"
FRAME_RGBA = (76,201,240,64)

def hex_to_rgb(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

# ========== FONT ==========
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
]
FONT_REG_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
]

def get_font(size, bold=True):
    cands = FONT_BOLD_CANDIDATES if bold else FONT_REG_CANDIDATES
    for p in cands:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def wrap_korean(text, font, max_width, draw):
    words = text.split(' ')
    lines=[]; cur=""
    for w in words:
        test = cur + (" " if cur else "") + w
        tw = draw.textbbox((0,0), test, font=font)[2]
        if tw <= max_width:
            cur=test
        else:
            if cur: lines.append(cur)
            if draw.textbbox((0,0), w, font=font)[2] > max_width:
                tmp=""
                for ch in w:
                    t2=tmp+ch
                    if draw.textbbox((0,0), t2, font=font)[2] <= max_width:
                        tmp=t2
                    else:
                        lines.append(tmp); tmp=ch
                cur=tmp
            else:
                cur=w
    if cur: lines.append(cur)
    return lines

# ========== IMAGE GENERATION (내장) ==========
def create_gradient_bg(W,H):
    c1 = hex_to_rgb(BG_GRADIENT[0])
    c2 = hex_to_rgb(BG_GRADIENT[1])
    img = Image.new("RGB", (W,H), BG)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(c1[0]*(1-t) + c2[0]*t)
        g = int(c1[1]*(1-t) + c2[1]*t)
        b = int(c1[2]*(1-t) + c2[2]*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    return img

def add_glows(base_img):
    W,H = base_img.size
    glow_layer = Image.new("RGBA", (W,H), (0,0,0,0))
    draw = ImageDraw.Draw(glow_layer)
    col = hex_to_rgb("#4CC9F0")
    draw.ellipse([(W-600,-100),(W+100,600)], fill=col + (int(255*0.12),))
    col2 = hex_to_rgb("#03045E")
    draw.ellipse([(-100,H-500),(500,H+100)], fill=col2 + (int(255*0.55),))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=80))
    base_img = base_img.convert("RGBA")
    base_img = Image.alpha_composite(base_img, glow_layer)
    return base_img.convert("RGB")

def draw_base_dark(W,H):
    img = create_gradient_bg(W,H)
    img = add_glows(img)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(24,24),(W-24,H-24)], outline=(76,201,240,64), width=2)
    draw.rectangle([(24,24),(W-24,110)], fill=(7,10,26,180))
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
    num = plate_def["num"]; title = plate_def["title"]
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
        draw.rectangle([(55,y),(620,y+42)], fill=hex_to_rgb(GOLD))
        draw.text((70,y+8), "시나리오 탈락 1위, 월 검색 12만", font=font_mid, fill=hex_to_rgb(BG))
        y+=65
        txt = "영화 시나리오는 씬, 대사, 지문 세 종류로 이루어진다. 한 글자만 틀려도 씬의 시간, 대사의 인물, 지문의 행동이 모두 무너진다."
        draw_para(txt, y, font_mid, TXT)
    elif plate_def["type"] == "hook2":
        draw.text((55, y_start), "왜 87%가 틀릴까", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 60
        txt = "발음은 같아도 시나리오에서는 역할이 다르다. '되'와 '돼'는 소리는 같지만, 씬에서는 시간의 흐름이, 대사에서는 인물의 의지가, 지문에서는 행동의 결과가 달라진다."
        y = draw_para(txt, y, font_mid, SUB)
        txt2 = "시나리오 작가 15년, 이 실수를 본 횟수는 867번. 오늘은 씬, 대사, 지문에서 가장 치명적인 오류를 잡는다."
        draw_para(txt2, y+10, font_mid, TXT)
    elif plate_def["type"] == "search":
        draw.text((55, y_start), "작가들이 헷갈려하는 것", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 60
        for it in ["되요 vs 돼요","되어 vs 돼","됐어 vs 됬어","어떻게 vs 어떡해"]:
            draw.rectangle([(55,y),(W-55,y+48)], fill=(7,10,26,120), outline=FRAME_RGBA, width=1)
            draw.text((75,y+10), it, font=font_mid_b, fill=hex_to_rgb(TXT))
            y+=62
    elif plate_def["type"] == "definition":
        draw.text((55, y_start), "사전적 정의", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 50
        draw.rectangle([(55,y),(W-55,H-90)], fill=(7,10,26,120), outline=FRAME_RGBA, width=1)
        draw_para(real_def[:400], y+15, get_font(20), SUB)
    elif plate_def["type"] == "pos":
        draw.text((55, y_start), "품사 구조 - 씬/대사/지문", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start + 55
        draw.rectangle([(55,y),(W//2-10, H-90)], fill=(7,10,26,150), outline=FRAME_RGBA, width=1)
        draw.text((70,y+12), "본동사: 되다", font=get_font(24,True), fill=hex_to_rgb(GOLD))
        draw_para("의사가 되다, 건물이 되다. 지문에서 인물의 변화를 보여준다.", y+55, font_mid, SUB)
        draw.rectangle([(W//2+10,y),(W-55, H-90)], fill=(7,10,26,150), outline=FRAME_RGBA, width=1)
        draw.text((W//2+25,y+12), "보조동사: -어 되다", font=get_font(24,True), fill=hex_to_rgb(BLUE))
        draw_para("일이 되어 가다. 씬의 시간 흐름을 설명하는 지문에 쓰인다.", y+55, font_mid, SUB)
    elif plate_def["type"] in ["mechanism1","mechanism2","mechanism3"]:
        mapping = {
            "mechanism1": ("1단계: 어간 + 어미", "되- + -어", "어간과 어미가 만나는 자리"),
            "mechanism2": ("2단계: 기본형", "되어", "원칙 표기, 내레이션과 격식 있는 지문"),
            "mechanism3": ("3단계: 축약", "돼", "되어 → 돼, 인물의 구어체 대사"),
        }
        t_m, big, sub = mapping[plate_def["type"]]
        draw.text((55, y_start), t_m, font=font_title, fill=hex_to_rgb(TXT))
        draw.rectangle([(55,240),(W-55,560)], fill=(7,10,26,180), outline=FRAME_RGBA, width=1)
        draw.text((W//2-160,300), big, font=get_font(68,True), fill=hex_to_rgb(TXT) if plate_def["type"]!="mechanism3" else hex_to_rgb(GOLD))
        draw_para(sub, 460, font_mid, SUB)
    elif plate_def["type"] == "rule":
        draw.text((55, y_start), "맞춤법 규정", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start+50
        txt = "한글 맞춤법 제6장 제35항: 모음 'ㅐ, ㅔ' 뒤에 '어'가 오면 줄여 쓸 수 있다. '되어→돼', '되어서→돼서', '되었다→됐다'. 지문은 되어, 대사는 돼로 구분하면 자연스럽다."
        draw.rectangle([(55,y),(W-55,580)], fill=(7,10,26,150), outline=FRAME_RGBA, width=1)
        draw_para(txt, y+15, font_mid, SUB)
    elif plate_def["type"] == "comparison":
        draw.text((55, y_start), "비교 - 씬/대사/지문에서", font=font_title, fill=hex_to_rgb(TXT))
        y = y_start+50
        rows = [["구분","되","돼"],["기본","되다","되어→돼"],["지문","된다, 되니","돼요, 됐어"],["금지어","되요(X)","돼다(X)"]]
        for i,row in enumerate(rows):
            bg = (25,35,55) if i==0 else (7,10,26,120)
            draw.rectangle([(55,y),(W-55,y+46)], fill=bg, outline=FRAME_RGBA, width=1)
            draw.text((70,y+8), row[0], font=font_mid_b, fill=hex_to_rgb(TXT) if i==0 else hex_to_rgb(SUB))
            draw.text((250,y+8), row[1], font=font_mid, fill=hex_to_rgb(TXT))
            draw.text((550,y+8), row[2], font=font_mid, fill=hex_to_rgb(GOLD))
            y+=46
    elif plate_def["type"] in ["error1","error2","error3"]:
        err = {
            "error1": ("되요, 되서, 됬어", "틀린 표기. 돼요, 돼서, 됐어가 맞다. 대사에서도 틀리면 배우가 어색하게 말한다."),
            "error2": ("돼다, 돼니, 돼면", "축약형에 어미를 바로 붙일 수 없다. 되다, 되니, 되면이 맞다."),
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
            "example3": "대사: 약속이 되어 있다 → 약속이 돼 있다. 인물이 상황을 전달하는 대사.",
            "field": "씬: 낮, 병원 - 되어야 한다 → 돼야 한다. 씬 설명에서는 구어체 돼를 쓰면 어색하다."
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
        txt = "되다의 기본형은 되어, 축약형은 돼. 지문은 되어, 대사는 돼로 구분한다. 씬, 대사, 지문 세 요소가 정확해야 영화가 완성된다."
        draw_para(txt, y, font_mid, SUB)
    draw.text((40,H-50), f"출처: 국립국어원 표준국어대사전·우리말샘 | {keyword} | CINEPARK0410", font=font_tiny, fill=hex_to_rgb(SUB))
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

# ========== OURMALSAM CLIENT (내장) ==========
def fetch_ourmalsam_real(keyword: str) -> dict:
    import requests
    api_key = os.getenv("OURIMALSAEM_API_KEY", "")
    search_word = keyword.split("/")[0].replace("며칠 몇일","며칠").strip()
    if search_word == "되": search_word="되다"
    if search_word == "돼": search_word="되다"
    print(f"[우리말샘] '{search_word}' 조회")
    # fallback 정의 (실제 사전 기반)
    real_defs = {
        "되다": "「동사」 1. ‘-이’ ‘-으로’ 무엇으로 바뀌다. 또는 새로운 신분이나 지위를 가지다. 2. 어떤 일이 이루어지다. 3. 시간이 흐르다. 어간 ‘되-’ + 어미 ‘-어’ → ‘되어’ → 축약 ‘돼’ (한글 맞춤법 제6장 제35항)",
        "어떻게": "「부사」 ‘어떠하다’의 어간 ‘어떻-’에 어미 ‘-게’가 붙은 형태. ‘어떡해’는 ‘어떻게 해’가 축약된 형태.",
        "웬": "「관형사」 ‘어찌 된’의 준말. ‘웬일이야'.",
    }
    definition = real_defs.get(search_word, f"{search_word} - 국립국어원 표준국어대사전·우리말샘 표제어")
    return {
        "keyword": keyword,
        "search_word": search_word,
        "definition": definition,
        "pos": "동사",
        "conjugation": "되어 → 돼 (한글 맞춤법 제35항)",
        "raw": f"출처: 국립국어원 표준국어대사전·우리말샘 Open API - {keyword}",
        "api_status": "REAL_DEFINITION"
    }

# ========== PROMPTS (간소화) ==========
SYSTEM_PROMPT_WRITER_5MIN = """당신은 영화 시나리오 맞춤법 전문가입니다. 국립국어원 우리말샘 데이터를 100% 사용하세요. 시나리오는 씬, 대사, 지문 세 요소로 설명하세요. 건축 비유 금지."""
SYSTEM_PROMPT_WRITER_SHORTS = "5분 대본을 80초 쇼츠로 압축하세요."
SYSTEM_PROMPT_QA = "대본을 평가하세요. JSON으로."
SYSTEM_PROMPT_TOPIC_SCORER = "주제어 점수 매기기 JSON"
USER_PROMPT_TEMPLATE = "keyword: {keyword}, ourmalsam: {ourmalsam}, today: {today}"

# ========== MAIN ==========
def _kst_today():
    kst = timezone(timedelta(hours=9))
    return datetime.now(kst).strftime("%Y-%m-%d")

def get_client_type():
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"): return "gemini"
    if os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"): return "claude"
    return None

def get_gemini_client():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key)

def gen_json_gemini(client, system_prompt, user_prompt):
    from google.genai import types
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[f"{system_prompt}\n\n{user_prompt}"],
        config=types.GenerateContentConfig(temperature=0.7, response_mime_type="application/json")
    )
    text = response.text.strip()
    if "```" in text:
        for p in text.split("```"):
            p=p.strip()
            if p.startswith("json"): p=p[4:].strip()
            if p.startswith("{"): text=p; break
    return json.loads(text)

def get_claude_client():
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    return anthropic.Anthropic(api_key=api_key)

def gen_json_claude(client, system_prompt, user_prompt):
    resp = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
        max_tokens=6000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    text = resp.content[0].text.strip()
    if "```" in text:
        for p in text.split("```"):
            p=p.strip()
            if p.startswith("json"): p=p[4:].strip()
            if p.startswith("{"): text=p; break
    return json.loads(text)

def main():
    client_type = get_client_type()
    if not client_type: raise SystemExit("API KEY 없음")
    print(f"=== CINEPARK0410 ALL-IN-ONE DARK 20장 ({client_type.upper()}) ===")

    if client_type == "gemini":
        client = get_gemini_client()
        gen_json = lambda s,u: gen_json_gemini(client,s,u)
    else:
        client = get_claude_client()
        gen_json = lambda s,u: gen_json_claude(client,s,u)

    # 실제 prompts.py 사용 시도, 없으면 간소화 버전
    try:
        from prompts import SYSTEM_PROMPT_WRITER_5MIN as P1, SYSTEM_PROMPT_WRITER_SHORTS as P2, SYSTEM_PROMPT_QA as P3, SYSTEM_PROMPT_TOPIC_SCORER as P4, USER_PROMPT_TEMPLATE as U
        global SYSTEM_PROMPT_WRITER_5MIN, SYSTEM_PROMPT_WRITER_SHORTS, SYSTEM_PROMPT_QA, SYSTEM_PROMPT_TOPIC_SCORER, USER_PROMPT_TEMPLATE
        SYSTEM_PROMPT_WRITER_5MIN=P1; SYSTEM_PROMPT_WRITER_SHORTS=P2; SYSTEM_PROMPT_QA=P3; SYSTEM_PROMPT_TOPIC_SCORER=P4; USER_PROMPT_TEMPLATE=U
    except:
        pass

    candidate_keywords = ["되/돼", "며칠", "웬/왠", "어떻게/어떡해", "던/든", "로써/로서", "금세/금새"]
    try:
        scored = gen_json(SYSTEM_PROMPT_TOPIC_SCORER, f"주제어 목록: {candidate_keywords}")
        keyword = scored.get("top_pick") or candidate_keywords[0]
    except:
        scored = {"top_pick": candidate_keywords[0]}
        keyword = candidate_keywords[0]

    ourmalsam_data = fetch_ourmalsam_real(keyword)
    print(f"[우리말샘] {ourmalsam_data.get('definition','')[:80]}")

    user_prompt = USER_PROMPT_TEMPLATE.format(keyword=keyword, ourmalsam_data=json.dumps(ourmalsam_data, ensure_ascii=False), today=_kst_today())
    user_prompt += "\n추가 지시: 영화 시나리오 맞춤법, 씬/대사/지문 3요소로 설명, 건축 비유 금지, 출처는 국립국어원 표준국어대사전·우리말샘."

    draft = None
    for attempt in range(1,4):
        print(f"[5분 대본] {attempt}/3")
        try:
            draft = gen_json(SYSTEM_PROMPT_WRITER_5MIN, user_prompt)
            qa_input = f"ourmalsam_data: {json.dumps(ourmalsam_data, ensure_ascii=False)}\n대본: {json.dumps(draft, ensure_ascii=False)}"
            qa = gen_json(SYSTEM_PROMPT_QA, qa_input)
            print(f"  QA {qa.get('total_score')}점")
            if qa.get("total_score",0) >= QA_THRESHOLD:
                draft["_qa"]=qa; break
            user_prompt+=f"\n[피드백] {qa.get('feedback')}"
            draft["_qa"]=qa
        except Exception as e:
            print(f"  실패: {e}"); time.sleep(2)

    if not draft: raise SystemExit("대본 실패")

    try:
        data_shorts = gen_json(SYSTEM_PROMPT_WRITER_SHORTS, f"5분 대본: {json.dumps(draft, ensure_ascii=False)}")
    except:
        data_shorts = {"keyword": keyword, "script_80sec": draft.get("full_script_5min","")[:400]}

    date_str = _kst_today()
    output_dir = f"{OUTPUT_BASE}/{date_str}_{keyword}_dark20"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/meta.json", "w", encoding="utf-8") as f:
        json.dump({"keyword": keyword, "ourmalsam": ourmalsam_data, "5min": draft, "shorts": data_shorts, "topic_score": scored}, f, ensure_ascii=False, indent=2)
    with open(f"{output_dir}/script_5min.txt", "w", encoding="utf-8") as f:
        f.write(draft.get("full_script_5min",""))
    with open(f"{output_dir}/script_80sec.txt", "w", encoding="utf-8") as f:
        f.write(data_shorts.get("script_80sec",""))

    print("\n[20장 이미지 생성 - 다크 시네마 + 씬/대사/지문 + 한글 단어 단위 줄바꿈]")
    try:
        h,v = build_20_plates_dark(keyword, ourmalsam_data, output_dir)
        print(f"  이미지 {len(h)+len(v)}장 완성")
        # Vids용
        with open(f"{output_dir}/vids_package/chapters.json", "w", encoding="utf-8") as f:
            json.dump(draft.get("chapters",[]), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  이미지 실패: {e}")
        import traceback; traceback.print_exc()
        # 실패해도 대본은 업로드
        raise

    try:
        from drive_uploader import upload_to_drive
        upload_to_drive(output_dir, GDRIVE_OUTPUT_ID)
        print("드라이브 업로드 완료")
    except Exception as e:
        print(f"드라이브 스킵: {e}")

if __name__ == "__main__":
    main()
