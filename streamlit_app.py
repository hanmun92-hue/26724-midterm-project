import io
import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("건의문 자료 검증·시각화 도우미")

# 데이터 만드는 방법 안내 (접었다 펼 수 있는 상자)
with st.expander("📋 어떤 데이터를 준비해야 하나요? (누르면 펼쳐져요)"):
    st.markdown("""
    ### 1. 파일 형식: CSV 파일만 올릴 수 있어요

    엑셀에서 작업했다면 **"다른 이름으로 저장" → "CSV UTF-8(쉼표로 분리)"** 를 선택해 저장해 주세요.

    ### 2. 데이터 종류에 따라 양식이 달라요

    **여러 항목을 비교하고 싶을 때** (예: 스트레스 원인별 비율)

    | 항목 | 수치 |
    |---|---|
    | 장애인 관련 편의 시설 부족 | 52.3 |
    | 외출 시 동반자가 없어서 | 22.1 |

    **시간에 따른 변화를 보여주고 싶을 때** (예: 연도별 인구 추이)

    | 연도 | 수치 |
    |---|---|
    | 2022 | 216.6 |
    | 2023 | 214.2 |

    ### 3. 꼭 지켜야 할 것

    - 첫 번째 줄에는 반드시 **열 이름**만 적기 (숫자 X)
    - 숫자 칸에는 순수 숫자만 넣기 (%, 명, kg 같은 글자 넣지 않기)
    - 데이터를 어디서 가져왔는지(출처) 꼭 확인해 두기 — 아래 자료 검증 단계에서 필요해요!

    
    """)

# 1단계: 문제 상황 입력
problem = st.text_area("어떤 문제 상황을 건의하고 싶나요?")

# 참고할 수 있는 공식 데이터 출처 안내
st.subheader("🔗 이런 곳에서 자료를 찾아볼 수 있어요")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("[통계청 국가통계포털(KOSIS)](https://kosis.kr)")
with col2:
    st.markdown("[공공데이터포털](https://www.data.go.kr)")
with col3:
    st.markdown("[학교알리미](https://www.schoolinfo.go.kr)")

# 2단계: 자료 붙여넣기 및 시각화
pasted_data = st.text_area(
    "관련 데이터 붙여넣기",
    placeholder="스프레드시트에서 복사한 데이터를 여기에 붙여넣어 주세요. 열 헤더가 포함되어야 합니다."
)
if pasted_data:
    try:
        df = pd.read_csv(io.StringIO(pasted_data), sep=None, engine='python')
    except Exception:
        try:
            df = pd.read_csv(io.StringIO(pasted_data))
        except Exception:
            st.error("데이터를 읽는 데 실패했습니다. 스프레드시트에서 복사한 내용을 다시 확인해 주세요.")
            df = None

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
                        st.info("💡 이 그래프는 건의문 개요의 **'중간 - 문제 상황과 해결 방안'** 칸에서 근거 자료로 활용하세요!")
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
st.text_area(
    "중간 - 문제 상황과 해결 방안",
    placeholder="예) 위 그래프에서 확인한 것처럼 ○○ 항목이 가장 높게(또는 낮게) 나타났습니다. 이는 △△ 때문으로 보이며, 이를 해결하기 위해 □□를 제안합니다."
)
st.text_input("끝 - 요약 및 강조")