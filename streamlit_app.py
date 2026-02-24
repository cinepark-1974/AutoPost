import streamlit as st

st.title("✍️ 네이버 블로그 AI 자동화")
st.write("AutoPost v1.0")

# 간단한 테스트 UI
keyword = st.text_input("키워드 입력")
if st.button("시작"):
    st.success(f"'{keyword}' 키워드로 글 생성 준비 완료!")
