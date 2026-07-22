import re
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
        except Exception:
            continue  # 실패하면 다음 인코딩으로 시도

    if df is not None:
        st.dataframe(df)

        # 연도형 열(예: '1960','1961',...)을 찾아 시계열로 표시할 수 있으면 국가 선택 UI 제공
        year_cols = [c for c in df.columns if re.match(r"^\d{4}$", str(c))]
        if 'Country Name' in df.columns and year_cols:
            country = st.selectbox("국가 선택", df['Country Name'].dropna().unique())
            if country:
                row = df[df['Country Name'] == country]
                if not row.empty:
                    series = row.iloc[0][year_cols].replace('', pd.NA).apply(pd.to_numeric, errors='coerce')
                    if series.dropna().empty:
                        st.warning("선택한 국가에 시계열로 표시할 수 있는 수치 데이터가 없습니다.")
                    else:
                        fig, ax = plt.subplots()
                        series.plot(ax=ax)
                        ax.set_xlabel('Year')
                        ax.set_ylabel('Value')
                        ax.set_title(f"{country} - 시계열")
                        st.pyplot(fig)
                else:
                    st.warning("선택한 국가의 데이터가 없습니다.")
        else:
            # 숫자형 열만 골라서 선택 목록 만들기
            numeric_columns = df.select_dtypes(include="number").columns.tolist()
            if not numeric_columns:
                # 변환 시도
                coerced = df.apply(lambda col: pd.to_numeric(col, errors='coerce'))
                numeric_columns = coerced.select_dtypes(include='number').columns.tolist()

            if numeric_columns:
                selected_column = st.selectbox(
                    "그래프로 보고 싶은 항목을 선택하세요",
                    numeric_columns
                )
                fig, ax = plt.subplots()
                # 만약 선택된 열이 전체 데이터의 시리즈라면 그대로 플롯
                try:
                    df[selected_column].plot(ax=ax, kind="line")
                except Exception:
                    coerced[selected_column].plot(ax=ax, kind="line")
                ax.set_ylabel(selected_column)
                st.pyplot(fig)
            else:
                st.warning("숫자로 된 데이터가 없어서 그래프를 그릴 수 없어요.")

        # 교과서 타당성·신뢰성 평가 체크리스트
        st.subheader("자료 검증하기 (타당성·신뢰성 평가)")
        st.checkbox("이 자료의 출처가 명확한가요?")
        st.checkbox("이 자료가 문제 상황을 논리적으로 뒷받침하나요?")
        st.checkbox("표현이나 그래프에 과장·왜곡은 없나요?")

# 3단계: 건의문 개요 틀
st.subheader("건의문 개요 작성")
st.text_input("처음 - 건의 동기와 배경")
st.text_area("중간 - 문제 상황과 해결 방안")
st.text_input("끝 - 요약 및 강조")