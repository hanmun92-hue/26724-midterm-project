import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("건의문 자료 검증·시각화 도우미")

# 1단계: 문제 상황 입력
problem = st.text_area("어떤 문제 상황을 건의하고 싶나요?")

# 2단계: 자료 업로드 및 시각화
uploaded = st.file_uploader("관련 데이터(csv) 업로드", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df)
    fig, ax = plt.subplots()
    df.plot(ax=ax)  # 학생 데이터 구조에 맞게 조정
    st.pyplot(fig)

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