import io
import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("건의문 자료 검증·시각화 도우미")

# 데이터 만드는 방법 안내 (접었다 펼 수 있는 상자)
with st.expander("📋 어떤 데이터를 준비해야 하나요? (누르면 펼쳐져요)"):
    st.markdown("""
    ### 1. 데이터 입력: 붙여넣기 또는 업로드

    스프레드시트에서 복사한 데이터를 붙여넣거나, CSV/Excel 파일을 업로드해서 데이터를 입력할 수 있어요.

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

# 2단계: 자료 입력 및 시각화
tab1, tab2 = st.tabs(["데이터 붙여넣기", "CSV/Excel 업로드"])

with tab1:
    pasted_data = st.text_area(
        "관련 데이터 붙여넣기",
        placeholder="스프레드시트에서 복사한 데이터를 여기에 붙여넣어 주세요. 열 헤더가 포함되어야 합니다."
    )

with tab2:
    uploaded_file = st.file_uploader(
        "CSV 또는 Excel 파일 업로드",
        type=["csv", "xlsx"]
    )


df = None
parse_error = None
if pasted_data:
    try:
        df = pd.read_csv(io.StringIO(pasted_data), sep=None, engine='python')
    except Exception:
        try:
            df = pd.read_csv(io.StringIO(pasted_data))
        except Exception:
            parse_error = "데이터를 읽는 데 실패했습니다. 스프레드시트에서 복사한 내용을 다시 확인해 주세요."
            df = None
elif uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            encodings = ["utf-8", "cp949", "euc-kr"]
            for enc in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    break
                except Exception:
                    continue
            if df is None:
                parse_error = "CSV 파일을 읽는 데 실패했습니다. 다른 인코딩 형식인지 확인해 주세요."
        else:
            df = pd.read_excel(uploaded_file)
    except Exception:
        parse_error = "파일을 읽는 데 실패했습니다. 업로드한 파일을 확인해 주세요."

if df is not None:
    st.dataframe(df)

    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if numeric_columns:
        col1, col2 = st.columns(2)
        with col1:
            selected_columns = st.multiselect(
                "그래프로 보고 싶은 항목을 선택하세요 (여러 개 선택 가능)",
                numeric_columns,
                default=[numeric_columns[0]]
            )
        with col2:
            chart_type = st.selectbox(
                "그래프 종류를 선택하세요",
                ["막대그래프", "선그래프", "꺽은선그래프", "원그래프", "면적그래프", "히스토그램", "박스그래프"]
            )

        if selected_columns:
            fig, ax = plt.subplots()

            if chart_type == "막대그래프":
                df[selected_columns].plot(ax=ax, kind="bar")
            elif chart_type == "선그래프":
                df[selected_columns].plot(ax=ax, kind="line")
            elif chart_type == "꺽은선그래프":
                df[selected_columns].plot(ax=ax, kind="line", marker='o')
            elif chart_type == "면적그래프":
                df[selected_columns].plot(ax=ax, kind="area")
            elif chart_type == "히스토그램":
                df[selected_columns].plot(ax=ax, kind="hist", alpha=0.6, bins=10)
            elif chart_type == "박스그래프":
                df[selected_columns].plot(ax=ax, kind="box")
            elif chart_type == "원그래프":
                if len(selected_columns) == 1:
                    df[selected_columns[0]].value_counts().plot(ax=ax, kind="pie", autopct="%1.1f%%")
                else:
                    df[selected_columns].sum().plot(ax=ax, kind="pie", autopct="%1.1f%%")

            if chart_type not in ["원그래프"]:
                ax.set_ylabel(", ".join(selected_columns))
            st.pyplot(fig)
            st.info("💡 이 그래프는 건의문 개요의 **'중간 - 문제 상황과 해결 방안'** 칸에서 근거 자료로 활용하세요!")
        else:
            st.warning("그래프로 표시할 항목을 하나 이상 선택해 주세요.")
    else:
        st.warning("숫자로 된 데이터가 없어서 그래프를 그릴 수 없어요.")
else:
    if parse_error:
        st.error(parse_error)
    elif pasted_data or uploaded_file is not None:
        st.error("데이터를 확인할 수 없어요. 입력한 내용을 다시 확인해 주세요.")

# 3단계: 건의문 개요 틀
st.subheader("건의문 개요 작성")
st.text_input("처음 - 건의 동기와 배경")
st.text_area(
    "중간 - 문제 상황과 해결 방안",
    placeholder="예) 위 그래프에서 확인한 것처럼 ○○ 항목이 가장 높게(또는 낮게) 나타났습니다. 이는 △△ 때문으로 보이며, 이를 해결하기 위해 □□를 제안합니다."
)
st.text_input("끝 - 요약 및 강조")