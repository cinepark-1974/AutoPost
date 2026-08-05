
import os, requests
from pathlib import Path

# 실제 Meta API 연동 자리
# 네가 Meta AI API 키 있으면 여기에 넣으면 됨
# 지금은 테스트용으로 더미 이미지를 생성하거나, 
# meta.ai 의 image generation 엔드포인트를 호출하는 구조

def generate_context_image(context_text: str, style: str, out_path: str):
    """
    context_text: 본문 문단
    style: "data" or "mood"
    out_path: 저장 경로
    """
    # 1. 프롬프트 자동 생성 (Llama로)
    # 실제 연동시:
    # response = requests.post("https://api.meta.com/llama/prompt", ...)
    # prompt = response.json()["prompt"]

    if style=="data":
        auto_prompt = f"Editorial infographic, cinematic data visualization, Korean movie box office, context: {context_text[:100]}, dark background yellow accents, minimal, magazine style, no faces, 16:9"
    else:
        auto_prompt = f"Cinematic mood illustration, movie magazine feature, atmospheric, context: {context_text[:100]}, no text, no real actor faces, artistic, dark tone yellow accent"

    # 2. 이미지 생성 (Meta Emu / Image API)
    # 실제 연동 예시 (키 있으면 주석 해제):
    # headers = {"Authorization": f"Bearer {os.getenv('META_API_KEY')}"}
    # r = requests.post("https://api.llama.meta.com/v1/images/generations", json={"prompt": auto_prompt, "size":"1280x720"}, headers=headers)
    # with open(out_path, "wb") as f: f.write(r.content)
    # return out_path, auto_prompt

    # 테스트용: 플레이스홀더 이미지 생성 (Pillow)
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB",(1280,720),"#101010")
    d = ImageDraw.Draw(img)
    d.text((40,40), f"[Meta API Prompt]\n{auto_prompt[:180]}...", fill="#FFD60A", font=ImageFont.load_default())
    d.text((40,300), f"여기에 Meta API로 생성된 이미지가 들어옵니다\nStyle: {style}\nContext: {context_text[:60]}", fill="white", font=ImageFont.load_default())
    img.save(out_path, quality=95)
    return out_path, auto_prompt
