import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("건의문 자료 검증·시각화 도우미")

# 1단계: 문제 상황 입력
problem = st.text_area("어떤 문제 상황을 건의하고 싶나요?")

# 2단계: 자료 업로드 및 시각화
uploaded = st.file_uploader("관련 데이터(csv) 업로드", type="csv")
if uploaded:
    # 여러 인코딩 방식을 순서대로 시도
    encodings = ["utf-8", "cp949", "euc-kr"]
    df = None
    for enc in encodings:
        try:
            uploaded.seek(0)  # 파일 읽기 위치를 처음으로 되돌리기
            df = pd.read_csv(uploaded, encoding=enc)
            break  # 성공하면 반복 멈추기
        except UnicodeDecodeError:
            continue  # 실패하면 다음 인코딩으로 시도

    if df is not None:
        st.dataframe(df)
        fig, ax = plt.subplots()
        df.plot(ax=ax)
        st.pyplot(fig)
    else:
        st.error("파일을 읽을 수 없어요. CSV 파일이 손상되지 않았는지 확인해 주세요.")

    # 교과서 타당성·신뢰성 평가 기준을 그대로 체크리스트로
    st.subheader("자료 검증하기 (타당성·신뢰성 평가)")
    st.checkbox("이 자료의 출처가 명확한가요?")
    st.checkbox("이 자료가 문제 상황을 논리적으로 뒷받침하나요?")
    st.checkbox("표현이나 그래프에 과장·왜곡은 없나요?")

# 3단계: 건의문 개요 틀
st.subheader("건의문 개요 작성")
st.text_input("처음 - 건의 동기와 배경")
st.text_area("중간 - 문제 상황과 해결 방안")
st.text_input("끝 - 요약 및 강조")