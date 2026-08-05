
from PIL import Image, ImageDraw, ImageFont

def create_data_infographic(items=None, out_path="/tmp/data.jpg"):
    # items = [{"title":"명량","value":"17.61M","year":"2014"}]
    if not items:
        items = [
            {"title":"명량","value":"17.61M","year":"2014"},
            {"title":"괴물","value":"13.02M","year":"2006"},
            {"title":"암살","value":"12.70M","year":"2015"},
            {"title":"파묘","value":"11.91M","year":"2024"},
        ]
    W,H = 1280, 720
    img = Image.new("RGB",(W,H),"#0A0E14")
    d = ImageDraw.Draw(img)
    d.rectangle([20,20,W-20,H-20], outline="#FFD60A", width=2)
    d.text((60,30), "한국 3글자 영화 박스오피스 - KOFIC 공식 데이터", fill="#FFD60A", font=ImageFont.load_default())
    y=100
    for it in items:
        d.text((80,y), f"{it['title']} ({it['year']})", fill="white", font=ImageFont.load_default())
        d.text((600,y), f"{it['value']} 관객", fill="#FFD60A", font=ImageFont.load_default())
        # bar
        bar_w = int(float(it['value'].replace('M',''))*30)
        d.rectangle([80,y+30,80+bar_w,y+45], fill="#FFD60A")
        y+=90
    d.text((60,H-40), "출처: KOFIC / Kinolights / Netflix Tudum - 정확한 데이터만", fill="#666", font=ImageFont.load_default())
    img.save(out_path, quality=95)
    return out_path
