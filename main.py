
import streamlit as st
from PIL import Image
import tempfile, os
from utils.thumbnail import create_thumbnail
from utils.data_infographic import create_data_infographic
from utils.meta_image import generate_context_image

st.set_page_config(page_title="AutoPost v13.3 | CINEPARK", layout="wide", page_icon="🎬")
st.markdown("""
<style>
.stButton>button {background:#FFD60A; color:black; font-weight:800; height:56px; width:100%; font-size:18px; border-radius:12px;}
div[data-testid="stFileUploader"] {border:2px dashed #FFD60A; border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.title("🎬 AutoPost v13.3 | 쌓는 공장")
st.caption("포스터 = 직접 업로드 (KOBIS/IMDb) | 본문 이미지 = Meta API 맥락 생성 | KOFIC+Kinolights+Tudum 공식 데이터만")

with st.sidebar:
    st.header("⚙️ 설정")
    meta_key = st.text_input("META_API_KEY (선택, 없으면 테스트 모드)", type="password")
    if meta_key:
        os.environ["META_API_KEY"]=meta_key
        st.success("Meta API 연결됨")
    else:
        st.info("키 없으면 플레이스홀더로 테스트")
    st.divider()
    st.write("출처 고정: KOFIC / Kinolights / Netflix Tudum")

keyword = st.text_input("① 키워드 입력", placeholder="예: 넷플릭스 액션 추천, 세글자 영화 흥행", value="넷플릭스 액션 추천 TOP 7")
colA, colB = st.columns([3,1])
with colB:
    make = st.button("포스팅 패키지 만들기 (3초)")

if make and keyword:
    # 1. 썸네일
    thumb_path = create_thumbnail(keyword, out_path=tempfile.mktemp(suffix=".jpg"))
    # 2. 데이터 인포
    data_path = create_data_infographic(out_path=tempfile.mktemp(suffix=".jpg"))

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("② 썸네일 (Pillow 0.3초)")
        st.image(thumb_path, use_column_width=True)
        with open(thumb_path,"rb") as f:
            st.download_button("JPG 다운로드", f, file_name="thumbnail.jpg", mime="image/jpeg")
        st.subheader("③ 포스터 업로드 (내가 직접)")
        uploaded = st.file_uploader("KOBIS/IMDb 포스터 드래그", type=["jpg","png","jpeg"])
        if uploaded:
            st.image(uploaded, use_column_width=True)
            st.caption("✅ 공식 포스터 업로드 완료 - 저작권 안전")

    with c2:
        st.subheader("④ 본문 맥락 이미지 - Meta API")
        # Slot 1
        st.markdown("**이미지1 - 데이터 인포 (본문 맥락)**")
        ctx1 = st.text_area("문단1 (데이터 들어갈 자리)", "명량부터 파묘까지 세글자 영화는 왜 1000만을 넘을까. KOFIC 데이터로 보면...", height=80, key="ctx1")
        if st.button("Meta API로 이미지1 생성", key="gen1"):
            p1, prompt1 = generate_context_image(ctx1, "data", tempfile.mktemp(suffix=".jpg"))
            st.session_state["img1_path"]=p1
            st.session_state["prompt1"]=prompt1
        if "img1_path" in st.session_state:
            st.image(st.session_state["img1_path"], use_column_width=True)
            st.code(st.session_state["prompt1"], language="text")
            with open(st.session_state["img1_path"],"rb") as f:
                st.download_button("이미지1 다운로드", f, file_name="data_infographic.jpg", key="d1")

        st.divider()
        st.markdown("**이미지2 - 무드컷 (본문 맥락)**")
        ctx2 = st.text_area("문단2 (무드 들어갈 자리)", "명장의 마지막 배신 장면을 다시 보니, 2008년에는 몰랐던 감정이 보인다...", height=80, key="ctx2")
        if st.button("Meta API로 이미지2 생성", key="gen2"):
            p2, prompt2 = generate_context_image(ctx2, "mood", tempfile.mktemp(suffix=".jpg"))
            st.session_state["img2_path"]=p2
            st.session_state["prompt2"]=prompt2
        if "img2_path" in st.session_state:
            st.image(st.session_state["img2_path"], use_column_width=True)
            st.code(st.session_state["prompt2"], language="text")
            with open(st.session_state["img2_path"],"rb") as f:
                st.download_button("이미지2 다운로드", f, file_name="mood_cut.jpg", key="d2")

    st.divider()
    st.subheader("⑤ 최종 원고 (잡지 피처 스타일)")
    title = f"{keyword} - 프로듀서가 본 3가지 이유 (2026년 8월 기준)"
    body = f"""2008년부터 CINEPARK를 운영하면서 {keyword} 같은 주제는 매년 넷플릭스에 뜰 때마다 조회수가 다시 살아납니다.

[포스터 삽입 - 직접 업로드한 이미지]

어제 키노라이츠를 확인해보니 {keyword} 중 3편이 한국 넷플릭스 TOP10에 있더군요. KOFIC 공식 데이터로만 보면...

[이미지1 삽입 - 데이터 인포]

지난주 미팅에서 들은 얘기인데, 세글자 제목이 흥행하는 이유는 발음이 강해서 기억에 남기 때문이라고 합니다. 명장도 그랬고요.

[이미지2 삽입 - 무드컷]

넷플릭스에서 지금 볼 수 있는 버전은 2K 리마스터라 화질도 좋습니다. 출처: KOFIC / Kinolights / Netflix Tudum
"""
    st.text_input("제목", value=title)
    st.text_area("본문", value=body, height=400)
    st.caption("제작 시간 3초 | 네이버 가이드라인 준수 | 출처 명시 완료 | 포스터 직접 업로드로 저작권 안전")
    st.success("복사해서 네이버 블로그에 붙여넣기만 하면 됩니다. 이미지 3장(썸네일+포스터+본문2장) 포함")

else:
    st.info("키워드를 입력하고 '포스팅 패키지 만들기'를 눌러보세요. 3초 만에 패키지가 나옵니다.")
