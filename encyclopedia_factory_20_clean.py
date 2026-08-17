# -*- coding: utf-8 -*-
"""
CINEPARK0410 Encyclopedia 20 Plates - KOREAN FONT FIX
Ubuntu fonts-nanum 경로 강제 지정
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap, os

# 한글 폰트 경로 (apt-get fonts-nanum 설치 후 경로)
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
    "/usr/share/fonts/truetype/nanum/NanumSquareB.ttf",
]
FONT_PATHS_REGULAR = [
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumSquareR.ttf",
]

def get_font(size, bold=True):
    paths = FONT_PATHS_BOLD if bold else FONT_PATHS_REGULAR
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception as e:
                print(f"폰트 로드 실패 {p}: {e}")
                continue
    # 최후 폴백 - 나눔이 없으면 DejaVu + 한글 미지원 경고
    print(f"WARNING: 한글 폰트 없음, 기본 폰트 사용 - 한글이 □로 깨질 수 있음. size={size}")
    return ImageFont.load_default()

def draw_base(W,H):
    img = Image.new("RGB", (W,H), (242,235,220))
    draw = ImageDraw.Draw(img)
    for x in range(0,W,80):
        draw.line([(x,0),(x,H)], fill=(210,200,180), width=1)
    for y in range(0,H,80):
        draw.line([(0,y),(W,y)], fill=(210,200,180), width=1)
    draw.rectangle([(30,30),(W-30,H-30)], outline=(45,35,25), width=3)
    draw.rectangle([(45,45),(W-45,H-45)], outline=(90,70,50), width=1)
    draw.rectangle([(50,50),(W-50,145)], fill=(45,35,25))
    return img, draw

def create_plate(keyword, ourmalsam, plate_def, size, output_path):
    W,H = size
    img, draw = draw_base(W,H)
    
    font_title = get_font(34, True)
    font_big = get_font(80, True)
    font_mid = get_font(24)
    font_mid_b = get_font(26, True)
    font_small = get_font(18)
    font_tiny = get_font(15)
    
    num = plate_def["num"]
    title = plate_def["title"]
    ptype = plate_def["type"]
    
    draw.text((80, 60), f"PLATE {num:02d} {title}", font=font_title, fill=(242,235,220))
    draw.text((W-280, 70), "CINEPARK0410", font=font_small, fill=(200,190,170))

    real_def = ourmalsam.get('definition','') or "어떻게: 어떠하다의 어간 어떻-에 -게가 붙은 부사. 어떡해: 어떻게 해가 축약된 형태."

    if ptype == "hook1":
        draw.text((80,185), keyword, font=font_big, fill=(25,20,15))
        draw.rectangle([(80,300),(720,350)], fill=(180,40,40))
        draw.text((90,308), "월 검색 12만, 국립국어원 상담 1위", font=font_mid, fill=(255,255,255))
        draw.text((80,380), textwrap.fill("왜 건축 보고서에서도 가장 많이 틀릴까? 도면으로 완전 분해한다.", width=38), font=get_font(22), fill=(60,50,40))

    elif ptype == "hook2":
        draw.text((80,185), "87%가 틀리는 이유", font=font_title, fill=(45,35,25))
        draw.text((80,260), textwrap.fill("발음은 같아도 표기는 다르다. '되'와 '돼'는 소리는 같지만 구조가 다르다. 소리만 듣고 쓰면 틀린다.", width=48), font=font_mid, fill=(60,50,40))
        draw.text((80,360), textwrap.fill("같은 콘크리트라도 기초와 마감은 구분해야 하는 것과 같다.", width=48), font=font_mid, fill=(60,50,40))

    elif ptype == "search":
        draw.text((80,185), "무엇을 헷갈려 하는가", font=font_title, fill=(45,35,25))
        y=260
        for s in ["되요 vs 돼요","되어 vs 돼","됐어 vs 됬어","어떻게 vs 어떡해"]:
            draw.rectangle([(80,y),(W-80,y+55)], fill=(255,253,245), outline=(90,70,50), width=1)
            draw.text((100,y+12), s, font=font_mid_b, fill=(30,25,20))
            y+=70

    elif ptype == "definition":
        draw.text((80,185), "사전적 정의", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,250),(W-80,620)], fill=(255,253,245), outline=(90,70,50), width=1)
        draw.text((100,270), textwrap.fill(real_def, width=58), font=get_font(21), fill=(30,25,20))

    elif ptype == "pos":
        draw.text((80,185), "품사 구조", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,250),(W//2-10, H-110)], fill=(255,253,245), outline=(90,70,50), width=2)
        draw.text((100,270), "본동사: 되다", font=get_font(28,True), fill=(25,20,15))
        draw.text((100,320), textwrap.fill("의사가 되다, 건물이 되다. 스스로 변화한다.", width=26), font=font_mid, fill=(60,50,40))
        draw.rectangle([(W//2+10,250),(W-80, H-110)], fill=(45,35,25))
        draw.text((W//2+30,270), "보조동사: -어 되다", font=get_font(28,True), fill=(242,235,220))
        draw.text((W//2+30,320), textwrap.fill("일이 되어 가다, 약속이 되어 있다. 다른 동사를 돕는다.", width=26), font=font_mid, fill=(200,190,170))

    elif ptype == "etymology":
        draw.text((80,185), "어원", font=font_title, fill=(45,35,25))
        draw.text((80,260), textwrap.fill("어간 '되-'는 중세 한국어부터 사용된 고유어. '이루어지다, 성취되다' 의미를 600년 이상 유지한다.", width=50), font=font_mid, fill=(60,50,40))

    elif ptype == "mechanism1":
        draw.text((80,185), "결합 1단계", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,270),(W-80,610)], fill=(45,35,25))
        draw.text((W//2-200,350), "되- + -어", font=get_font(65,True), fill=(242,235,220))
        draw.text((W//2-180,480), "어간 + 어미 결합", font=font_mid, fill=(200,190,170))

    elif ptype == "mechanism2":
        draw.text((80,185), "결합 2단계", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,270),(W-80,610)], fill=(255,253,245), outline=(90,70,50), width=2)
        draw.text((W//2-180,350), "되어", font=get_font(75,True), fill=(25,20,15))
        draw.text((W//2-180,480), "기본형. 원칙적인 표기", font=font_mid, fill=(60,50,40))

    elif ptype == "mechanism3":
        draw.text((80,185), "결합 3단계", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,270),(W-80,610)], fill=(180,40,40))
        draw.text((W//2-120,350), "돼", font=get_font(75,True), fill=(255,255,255))
        draw.text((W//2-200,480), "되어 → 돼. 모음 축약", font=font_mid, fill=(255,220,220))

    elif ptype == "rule":
        draw.text((80,185), "맞춤법 규정", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,250),(W-80,610)], fill=(255,253,245), outline=(90,70,50), width=2)
        draw.text((100,270), textwrap.fill("한글 맞춤법 제6장 제35항: 모음 'ㅐ, ㅔ' 뒤에 '어'가 오면 'ㅐ, ㅔ'로 줄여 쓸 수 있다. '되어→돼', '되어서→돼서', '되었다→됐다'.", width=52), font=font_mid, fill=(30,25,20))

    elif ptype == "comparison":
        draw.text((80,185), "비교", font=font_title, fill=(45,35,25))
        rows = [["구분","되","돼"],["기본","되다","되어→돼"],["쓰임","된다, 되니","돼요, 됐어"],["주의","되요(X)","돼다(X)"]]
        y=250
        for i,row in enumerate(rows):
            bg = (45,35,25) if i==0 else (255,253,245) if i%2==0 else (242,235,220)
            fg = (242,235,220) if i==0 else (30,25,20)
            draw.rectangle([(80,y),(W-80,y+52)], fill=bg, outline=(90,70,50), width=1)
            draw.text((110,y+10), row[0], font=font_mid_b, fill=fg)
            draw.text((380,y+10), row[1], font=font_mid, fill=fg)
            draw.text((850,y+10), row[2], font=font_mid, fill=fg)
            y+=52

    elif ptype in ["error1","error2","error3"]:
        err = {
            "error1": ("되요, 되서, 됬어", "틀린 표기. 돼요, 돼서, 됐어가 맞다."),
            "error2": ("돼다, 돼니, 돼면", "축약형에 어미를 바로 붙일 수 없다. 되다, 되니, 되면이 맞다."),
            "error3": ("되여, 되였다", "옛 표기. 표준어는 되어, 되었다.")
        }[ptype]
        draw.text((80,185), "틀리기 쉬운 표기", font=font_title, fill=(180,40,40))
        draw.rectangle([(80,260),(W-80,410)], fill=(255,230,230), outline=(180,40,40), width=2)
        draw.text((100,290), f"× {err[0]}", font=get_font(38,True), fill=(180,40,40))
        draw.rectangle([(80,440),(W-80,590)], fill=(230,255,230), outline=(40,120,40), width=2)
        draw.text((100,470), f"○ {err[1]}", font=get_font(22), fill=(30,80,30))

    elif ptype in ["example1","example2","example3","field"]:
        ex_map = {
            "example1": "일이 잘 되어 간다 → 일이 잘 돼 간다",
            "example2": "의사가 되었다 → 의사가 됐다",
            "example3": "약속이 되어 있다 → 약속이 돼 있다",
            "field": "공사 진행이 되어야 합니다 → 공사 진행이 돼야 합니다"
        }
        draw.text((80,185), "예문", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,260),(W-80,540)], fill=(255,253,245), outline=(90,70,50), width=2)
        draw.text((100,320), ex_map[ptype], font=get_font(34,True), fill=(30,25,20))
        draw.text((100,430), "격식체에서는 되어, 구어체에서는 돼를 쓴다.", font=font_small, fill=(90,70,50))

    elif ptype == "quiz":
        draw.text((80,185), "확인", font=font_title, fill=(45,35,25))
        draw.rectangle([(80,260),(W-80,610)], fill=(45,35,25))
        draw.text((100,290), "빈칸에 들어갈 말은?", font=get_font(30,True), fill=(242,235,220))
        draw.text((100,360), "1. 일이 잘 (  ) 간다.", font=font_mid, fill=(200,190,170))
        draw.text((100,410), "2. 의사가 (  )었다.", font=font_mid, fill=(200,190,170))
        draw.text((100,510), "정답: 1. 돼  2. 됐", font=font_mid, fill=(242,235,220))

    elif ptype == "outro":
        draw.text((80,185), keyword, font=font_big, fill=(25,20,15))
        draw.text((80,310), "정리", font=get_font(30,True), fill=(45,35,25))
        draw.text((80,370), textwrap.fill("되다의 기본형은 되어, 축약형은 돼. 격식체에는 되어, 일상에서는 돼를 사용한다.", width=42), font=font_mid, fill=(60,50,40))
        draw.rectangle([(80,510),(W-80,610)], fill=(45,35,25))
        draw.text((100,535), "다음: 어떻게/어떡해", font=get_font(24,True), fill=(242,235,220))

    draw.rectangle([(30,H-70),(W-30,H-30)], fill=(45,35,25))
    draw.text((50,H-55), f"출처: 국립국어원 표준국어대사전·우리말샘 | {keyword}", font=font_tiny, fill=(200,190,170))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=92)
    return output_path

def build_20_plates(keyword, ourmalsam_data, output_dir):
    plates_def = [
        {"num":1, "title":"표지", "type":"hook1"},
        {"num":2, "title":"혼동 원인", "type":"hook2"},
        {"num":3, "title":"검색어 분석", "type":"search"},
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
        {"num":15, "title":"예문 1", "type":"example1"},
        {"num":16, "title":"예문 2", "type":"example2"},
        {"num":17, "title":"예문 3", "type":"example3"},
        {"num":18, "title":"현장 예문", "type":"field"},
        {"num":19, "title":"확인 문제", "type":"quiz"},
        {"num":20, "title":"정리", "type":"outro"},
    ]
    h=[]; v=[]
    for pd in plates_def:
        ph = Path(output_dir)/"vids_package"/f"{pd['num']:02d}_{pd['type']}_h.png"
        pv = Path(output_dir)/"vids_package"/f"{pd['num']:02d}_{pd['type']}_v.png"
        create_plate(keyword, ourmalsam_data, pd, size=(1920,1080), output_path=str(ph))
        create_plate(keyword, ourmalsam_data, pd, size=(1080,1920), output_path=str(pv))
        h.append(str(ph)); v.append(str(pv))
        print(f"  {pd['num']}/20 {pd['title']}")
    return h,v
