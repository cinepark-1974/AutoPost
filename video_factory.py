# -*- coding: utf-8 -*-
"""
CINEPARK0410 Video Factory - 5분 가로 + 1분20초 세로 실제 영상 생성
Google TTS + Pillow 건축 도해 + MoviePy 조립
GitHub Actions에서 무료로 실행
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 폰트 로드
def get_font(size, bold=True):
    # GitHub Actions ubuntu에는 나눔 폰트 설치 가능
    candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf" if bold else "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def create_blueprint_image(prompt: str, keyword: str, chapter_title: str, size=(1920,1080), output_path=""):
    """건축 도해 스타일 이미지 생성 - Imagen 없이 Pillow로 신뢰도 확보"""
    W, H = size
    # 배경 - 도면지 색
    img = Image.new("RGB", (W,H), (247, 245, 235))
    draw = ImageDraw.Draw(img)
    
    # 격자 그리기
    grid_color = (200, 210, 225)
    for x in range(0, W, 80):
        draw.line([(x,0),(x,H)], fill=grid_color, width=1)
    for y in range(0, H, 80):
        draw.line([(0,y),(W,y)], fill=grid_color, width=1)
    
    # 테두리
    draw.rectangle([(40,40),(W-40,H-40)], outline=(30,50,90), width=4)
    draw.rectangle([(50,50),(W-50,H-50)], outline=(70,90,130), width=1)
    
    # 타이틀
    font_title = get_font(72 if W>1500 else 56, bold=True)
    font_sub = get_font(36 if W>1500 else 28, bold=False)
    font_keyword = get_font(180 if W>1500 else 120, bold=True)
    
    # 키워드 크게
    draw.text((100, 120), keyword, font=font_keyword, fill=(15,30,70))
    
    # 챕터 제목
    draw.text((100, H-280), chapter_title, font=font_title, fill=(30,50,90))
    
    # 프롬프트 요약
    wrapped = textwrap.fill(prompt[:120], width=40)
    draw.text((100, H-180), wrapped, font=font_sub, fill=(80,90,110))
    
    # 출처 고정 - 신뢰도 하네스
    draw.text((100, H-90), "출처: 국립국어원 우리말샘 Open API / CINEPARK0410", font=font_sub, fill=(100,110,130))
    
    # 도면 심볼
    draw.ellipse([(W-300, 100),(W-100, 300)], outline=(30,50,90), width=3)
    draw.line([(W-300,200),(W-100,200)], fill=(30,50,90), width=2)
    draw.line([(W-200,100),(W-200,300)], fill=(30,50,90), width=2)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path

def create_tts(text: str, output_path: str):
    """TTS - Google Cloud TTS 있으면 사용, 없으면 gTTS"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    text = text[:4000]  # 길이 제한
    
    # 1. Google Cloud TTS 시도 (고품질)
    try:
        from google.cloud import texttospeech
        if os.getenv("GOOGLE_CREDENTIALS_JSON_CONTENT") or Path("./credentials.json").exists():
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name="ko-KR-Chirp3-HD-Achernar",  # 최신 고품질
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            print(f"  TTS (Cloud): {output_path}")
            return output_path
    except Exception as e:
        print(f"  Cloud TTS 실패, gTTS로 대체: {e}")
    
    # 2. gTTS 폴백 (무료)
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='ko')
        tts.save(output_path)
        print(f"  TTS (gTTS): {output_path}")
        return output_path
    except Exception as e:
        print(f"  gTTS 실패: {e}")
        # 빈 mp3 생성 (무음으로 진행)
        with open(output_path, "wb") as f:
            f.write(b"")
        return output_path

def assemble_video(image_paths, audio_paths, output_path, fps=24):
    """이미지 + 오디오 조립 - MoviePy"""
    try:
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
        clips = []
        for img_p, aud_p in zip(image_paths, audio_paths):
            audio = None
            duration = 5
            if Path(aud_p).exists() and Path(aud_p).stat().st_size > 1000:
                try:
                    audio = AudioFileClip(str(aud_p))
                    duration = audio.duration
                except:
                    pass
            img_clip = ImageClip(str(img_p)).set_duration(duration)
            if audio:
                img_clip = img_clip.set_audio(audio)
            clips.append(img_clip)
        
        if not clips:
            print("  클립 없음")
            return None
        
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(str(output_path), fps=fps, codec="libx264", audio_codec="aac", logger=None)
        print(f"  영상 완성: {output_path} ({final.duration:.1f}초)")
        return output_path
    except Exception as e:
        print(f"  MoviePy 조립 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def build_dual_videos(data_5min: dict, data_shorts: dict, output_dir: str):
    """5분 가로 + 1분20초 세로 동시 생성"""
    keyword = data_5min.get("keyword","며칠")
    chapters = data_5min.get("chapters", [])
    if not chapters:
        # 챕터가 없으면 전체 대본으로 1챕터 생성
        chapters = [{"title": "전체", "script": data_5min.get("full_script_5min",""), "visual_prompt": data_5min.get("visual_prompts",["blueprint"])[0]}]
    
    # 폴더
    img_dir_h = Path(output_dir) / "images_h"
    img_dir_v = Path(output_dir) / "images_v"
    audio_dir = Path(output_dir) / "audio"
    img_dir_h.mkdir(parents=True, exist_ok=True)
    img_dir_v.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    image_paths_h = []
    image_paths_v = []
    audio_paths = []
    
    print(f"[영상 제작] {keyword} - 5분 가로용 이미지 생성")
    for i, ch in enumerate(chapters[:5]):
        title = ch.get("title", f"챕터{i+1}")
        script = ch.get("script", "")
        vprompt = ch.get("visual_prompt", f"architectural blueprint of {keyword}")
        
        # 이미지 2종
        img_h = img_dir_h / f"ch{i+1:02d}.png"
        img_v = img_dir_v / f"ch{i+1:02d}.png"
        create_blueprint_image(vprompt, keyword, title, size=(1920,1080), output_path=str(img_h))
        create_blueprint_image(vprompt, keyword, title, size=(1080,1920), output_path=str(img_v))
        image_paths_h.append(img_h)
        image_paths_v.append(img_v)
        
        # 오디오
        aud = audio_dir / f"ch{i+1:02d}.mp3"
        create_tts(script, str(aud))
        audio_paths.append(aud)
    
    # 조립
    print(f"[영상 조립] 가로 1920x1080")
    final_h = Path(output_dir) / "final_horizontal.mp4"
    assemble_video(image_paths_h, audio_paths, final_h)
    
    print(f"[영상 조립] 세로 1080x1920 (쇼츠)")
    # 세로는 쇼츠 대본으로 오디오 재생성
    shorts_script = data_shorts.get("script_80sec", "")
    if shorts_script:
        # 쇼츠용 오디오는 1개로 합침
        short_aud = audio_dir / "shorts.mp3"
        create_tts(shorts_script, str(short_aud))
        # 세로 이미지는 첫 장만 사용하거나 전체 사용
        final_v = Path(output_dir) / "final_vertical.mp4"
        assemble_video(image_paths_v[:3], [short_aud]*len(image_paths_v[:3]), final_v)
    else:
        final_v = Path(output_dir) / "final_vertical.mp4"
        assemble_video(image_paths_v, audio_paths, final_v)
    
    return str(final_h), str(final_v)
