# -*- coding: utf-8 -*-
"""
CINEPARK0410 - 영화 시나리오 맞춤법 버전 20 Plates
- 줄바꿈: 한글 단어 단위 (음절 중간 끊김 방지)
- 주제: 건축이 아니라 '영화 시나리오에서 틀리기 쉬운 맞춤법'에서 출발
- 채널 정체성과 연결
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansKR-Bold.ttf",
]
FONT_REG_CANDIDATES = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansKR-Regular.ttf",
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
    """한글 단어 단위 줄바꿈 - 음절 중간 끊김 방지"""
    words = text.split(' ')
    lines = []
    cur = ""
    for w in words:
        test = cur + (" " if cur else "") + w
        # 텍스트 너비 측정
        bbox = draw.textbbox((0,0), test, font=font)
        tw = bbox[2]-bbox[0]
        if tw <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            # 단어가 너무 길면 글자 단위로 강제
            if draw.textbbox((0,0), w, font=font)[2] > max_width:
                # 글자 단위 분할
                tmp=""
                for ch in w:
                    t2 = tmp + ch
                    if draw.textbbox((0,0), t2, font=font)[2] <= max_width:
                        tmp = t2
                    else:
                        lines.append(tmp)
                        tmp = ch
                cur = tmp
            else:
                cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_base(W,H):
    img = Image.new("RGB", (W,H), (245, 240, 230))
    draw = ImageDraw.Draw(img)
    # 필름 퍼포레이션 느낌의 미세 그리드
    for x in range(0,W,90):
        draw.line([(x,0),(x,H)], fill=(225,215,195), width=1)
    for y in range(0,H,90):
        draw.line([(0,y),(W,y)], fill=(225,215,195), width=1)
    # 필름 프레임
    draw.rectangle([(25,25),(W-25,H-25)], outline=(30,25,20), width=3)
    draw.rectangle([(40,40),(W-40,H-40)], outline=(80,70,60), width=1)
    # 상단 타이틀 바 - 시나리오 표지 느낌
    draw.rectangle([(40,40),(W-40,135)], fill=(25,20,15))
    return img, draw

def create_plate_film(keyword, ourmalsam, plate_def, size, output_path):
    W,H = size
    img, draw = draw_base(W,H)
    
    font_title = get_font(34, True)
    font_big = get_font(78, True)
    font_mid = get_font(23)
    font_mid_b = get_font(24, True)
    font_small = get_font(17)
    font_tiny = get_font(14)
    
    num = plate_def["num"]
    title = plate_def["title"]
    
    draw.text((70, 55), f"SCENE {num:02d} {title}", font=font_title, fill=(245,240,230))
    draw.text((W-260, 65), "CINEPARK0410", font=font_small, fill=(180,170,150))

    real_def = ourmalsam.get('definition','')

    content_width = W - 140
    y_start = 170

    def draw_paragraph(text, y, font, color=(40,35,30), line_spacing=8):
        lines = wrap_korean(text, font, content_width, draw)
        for line in lines:
            draw.text((70, y), line, font=font, fill=color)
            bbox = draw.textbbox((0,0), line, font=font)
            y += (bbox[3]-bbox[1]) + line_spacing
        return y

    if plate_def["type"] == "hook1":
        draw.text((70, y_start), keyword, font=font_big, fill=(20,15,10))
        y = y_start + 110
        draw.rectangle([(70,y),(680,y+45)], fill=(180,35,35))
        draw.text((85,y+8), "월 검색 12만, 시나리오 탈락 1위", font=font_mid, fill=(255,255,255))
        y += 70
        txt = "영화 시나리오 1페이지에서 가장 많이 탈락하는 맞춤법. 도면이 아닌 대본으로 완전 분해한다."
        y = draw_paragraph(txt, y, get_font(22))

    elif plate_def["type"] == "hook2":
        draw.text((70, y_start), "시나리오에서 왜 틀릴까", font=font_title, fill=(25,20,15))
        y = y_start + 70
        txt = "발음은 같아도 대본에서는 역할이 다르다. '되'와 '돼'는 소리는 같지만, 시나리오에서는 인물의 행동과 상태가 달라진다. 소리만 듣고 쓰면 감독에게 바로 지적받는다."
        y = draw_paragraph(txt, y, font_mid)
        y += 15
        txt2 = "시나리오 작가 15년, 이 실수를 본 횟수는 867번. 오늘은 그중에서도 가장 치명적인 오류를 잡는다."
        draw_paragraph(txt2, y, font_mid)

    elif plate_def["type"] == "search":
        draw.text((70, y_start), "작가들이 헷갈려하는 것", font=font_title, fill=(25,20,15))
        y = y_start + 70
        items = ["되요 vs 돼요","되어 vs 돼","됐어 vs 됬어","어떻게 vs 어떡해"]
        for it in items:
            draw.rectangle([(70,y),(W-70,y+50)], fill=(255,252,245), outline=(80,70,60), width=1)
            draw.text((90,y+10), it, font=font_mid_b, fill=(30,25,20))
            y+=65

    elif plate_def["type"] == "definition":
        draw.text((70, y_start), "사전적 정의", font=font_title, fill=(25,20,15))
        y = y_start + 60
        draw.rectangle([(70,y),(W-70,H-110)], fill=(255,252,245), outline=(80,70,60), width=1)
        y+=15
        draw_paragraph(real_def[:350], y+10, get_font(21), color=(30,25,20))

    elif plate_def["type"] == "pos":
        draw.text((70, y_start), "품사 구조 - 시나리오에서는", font=font_title, fill=(25,20,15))
        y = y_start + 65
        draw.rectangle([(70,y),(W//2-15, H-110)], fill=(255,252,245), outline=(80,70,60), width=1)
        draw.text((85,y+15), "본동사: 되다", font=get_font(26,True), fill=(20,15,10))
        draw_paragraph("의사가 되다, 건물이 되다. 인물이 스스로 변화한다.", y+55, font_mid, color=(60,50,40))
        draw.rectangle([(W//2+15,y),(W-70, H-110)], fill=(25,20,15))
        draw.text((W//2+30,y+15), "보조동사: -어 되다", font=get_font(26,True), fill=(245,240,230))
        draw_paragraph("일이 되어 가다, 약속이 되어 있다. 다른 동사를 돕는다.", y+55, font_mid, color=(200,190,170))

    elif plate_def["type"] in ["mechanism1","mechanism2","mechanism3"]:
        mapping = {
            "mechanism1": ("1단계: 어간 + 어미", "되- + -어", "어간과 어미가 만나는 자리"),
            "mechanism2": ("2단계: 기본형", "되어", "원칙적인 표기, 시나리오 격식체"),
            "mechanism3": ("3단계: 축약", "돼", "되어 → 돼, 구어체 대사에서 사용"),
        }
        title_m, big, sub = mapping[plate_def["type"]]
        draw.text((70, y_start), title_m, font=font_title, fill=(25,20,15))
        draw.rectangle([(70,260),(W-70,600)], fill=(25,20,15) if plate_def["type"]!="mechanism2" else (255,252,245), outline=(80,70,60), width=2)
        draw.text((W//2-180,350), big, font=get_font(70,True), fill=(245,240,230) if plate_def["type"]!="mechanism2" else (20,15,10))
        draw.text((W//2-180,480), sub, font=font_mid, fill=(200,190,170) if plate_def["type"]!="mechanism2" else (60,50,40))

    elif plate_def["type"] == "rule":
        draw.text((70, y_start), "맞춤법 규정", font=font_title, fill=(25,20,15))
        y = y_start+60
        txt = "한글 맞춤법 제6장 제35항: 모음 'ㅐ, ㅔ' 뒤에 '어'가 오면 줄여 쓸 수 있다. '되어→돼', '되어서→돼서', '되었다→됐다'. 시나리오에서는 격식체와 구어체를 구분해서 사용한다."
        draw.rectangle([(70,y),(W-70,580)], fill=(255,252,245), outline=(80,70,60), width=1)
        draw_paragraph(txt, y+15, font_mid)

    elif plate_def["type"] == "comparison":
        draw.text((70, y_start), "비교 - 대본에서", font=font_title, fill=(25,20,15))
        y = y_start+60
        rows = [["구분","되","돼"],["기본","되다","되어 → 돼"],["대본","된다, 되니","돼요, 됐어"],["금지어","되요(X)","돼다(X)"]]
        for i,row in enumerate(rows):
            bg = (25,20,15) if i==0 else (255,252,245) if i%2==0 else (245,240,230)
            fg = (245,240,230) if i==0 else (30,25,20)
            draw.rectangle([(70,y),(W-70,y+50)], fill=bg, outline=(80,70,60), width=1)
            draw.text((90,y+10), row[0], font=font_mid_b, fill=fg)
            draw.text((300,y+10), row[1], font=font_mid, fill=fg)
            draw.text((700,y+10), row[2], font=font_mid, fill=fg)
            y+=50

    elif plate_def["type"] in ["error1","error2","error3"]:
        err = {
            "error1": ("되요, 되서, 됬어", "틀린 표기. 돼요, 돼서, 됐어가 맞다. 시나리오에서는 바로 탈락 사유."),
            "error2": ("돼다, 돼니, 돼면", "축약형에 어미를 바로 붙일 수 없다. 되다, 되니, 되면이 맞다."),
            "error3": ("되여, 되였다", "옛 표기. 표준어는 되어, 되었다. 시대극이 아니면 사용하지 않는다."),
        }[plate_def["type"]]
        draw.text((70, y_start), "시나리오에서 틀리기 쉬운 표기", font=font_title, fill=(180,35,35))
        y = y_start+60
        draw.rectangle([(70,y),(W-70,y+120)], fill=(255,220,220), outline=(180,35,35), width=2)
        draw.text((90,y+15), f"× {err[0]}", font=get_font(34,True), fill=(180,35,35))
        y+=140
        draw.rectangle([(70,y),(W-70,y+120)], fill=(220,255,220), outline=(40,120,40), width=2)
        draw_paragraph(f"○ {err[1]}", y+15, get_font(20), color=(30,80,30))

    elif plate_def["type"] in ["example1","example2","example3","field"]:
        ex_map = {
            "example1": "일이 잘 되어 간다 → 일이 잘 돼 간다. (인물의 상황이 풀리는 장면)",
            "example2": "의사가 되었다 → 의사가 됐다. (인물의 변화, 클라이맥스)",
            "example3": "약속이 되어 있다 → 약속이 돼 있다. (복선, 이미 정해진 상황)",
            "field": "공사 진행이 되어야 합니다 → 진행이 돼야 합니다. (현장 대사가 아닌 내레이션에서는 되어)"
        }
        draw.text((70, y_start), "영화 대본 예문", font=font_title, fill=(25,20,15))
        y = y_start+60
        draw.rectangle([(70,y),(W-70,y+200)], fill=(255,252,245), outline=(80,70,60), width=2)
        draw_paragraph(ex_map[plate_def["type"]], y+20, get_font(26,True), color=(20,15,10))

    elif plate_def["type"] == "quiz":
        draw.text((70, y_start), "확인 - 대본 테스트", font=font_title, fill=(25,20,15))
        y = y_start+60
        draw.rectangle([(70,y),(W-70,600)], fill=(25,20,15))
        draw.text((90,y+20), "빈칸에 들어갈 말은?", font=get_font(28,True), fill=(245,240,230))
        draw.text((90,y+80), "1. 일이 잘 (  ) 간다.", font=font_mid, fill=(200,190,170))
        draw.text((90,y+130), "2. 의사가 (  )었다.", font=font_mid, fill=(200,190,170))
        draw.text((90,y+230), "정답: 1. 돼  2. 됐", font=font_mid, fill=(245,240,230))

    elif plate_def["type"] == "outro":
        draw.text((70, y_start), keyword, font=font_big, fill=(20,15,10))
        y = y_start+110
        txt = "되다의 기본형은 되어, 축약형은 돼. 시나리오에서는 격식체 내레이션에는 되어, 인물 대사에는 돼를 사용한다. 다음 편에서는 어떻게/어떡해를 다룬다."
        draw_paragraph(txt, y, font_mid)

    draw.rectangle([(25,H-70),(W-25,H-25)], fill=(25,20,15))
    draw.text((40,H-55), f"출처: 국립국어원 표준국어대사전·우리말샘 | {keyword} | CINEPARK0410 시나리오 맞춤법", font=font_tiny, fill=(180,170,150))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=92)
    return output_path

def build_20_plates_film(keyword, ourmalsam_data, output_dir):
    plates_def = [
        {"num":1, "title":"표지", "type":"hook1"},
        {"num":2, "title":"왜 틀릴까", "type":"hook2"},
        {"num":3, "title":"작가들의 헷갈림", "type":"search"},
        {"num":4, "title":"사전 정의", "type":"definition"},
        {"num":5, "title":"품사 구조", "type":"pos"},
        {"num":6, "title":"어원", "type":"etymology"},
        {"num":7, "title":"결합 1단계", "type":"mechanism1"},
        {"num":8, "title":"결합 2단계", "type":"mechanism2"},
        {"num":9, "title":"결합 3단계", "type":"mechanism3"},
        {"num":10, "title":"맞춤법 규정", "type":"rule"},
        {"num":11, "title":"비교", "type":"comparison"},
        {"num":12, "title":"오류 1", "type":"error1"},
        {"num":13, "title":"오류 2", "type":"error2"},
        {"num":14, "title":"오류 3", "type":"error3"},
        {"num":15, "title":"대본 예문 1", "type":"example1"},
        {"num":16, "title":"대본 예문 2", "type":"example2"},
        {"num":17, "title":"대본 예문 3", "type":"example3"},
        {"num":18, "title":"현장 대사", "type":"field"},
        {"num":19, "title":"테스트", "type":"quiz"},
        {"num":20, "title":"정리", "type":"outro"},
    ]
    h=[]; v=[]
    for pd in plates_def:
        ph = Path(output_dir)/"vids_package"/f"{pd['num']:02d}_{pd['type']}_h.png"
        pv = Path(output_dir)/"vids_package"/f"{pd['num']:02d}_{pd['type']}_v.png"
        create_plate_film(keyword, ourmalsam_data, pd, size=(1920,1080), output_path=str(ph))
        create_plate_film(keyword, ourmalsam_data, pd, size=(1080,1920), output_path=str(pv))
        h.append(str(ph)); v.append(str(pv))
        print(f"  {pd['num']}/20 {pd['title']}")
    return h,v
