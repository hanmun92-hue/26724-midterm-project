import io
import re
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def set_input_mode_paste():
    st.session_state.data_input_mode = "paste"


def set_input_mode_upload():
    st.session_state.data_input_mode = "upload"


if "data_input_mode" not in st.session_state:
    st.session_state.data_input_mode = "paste"


st.title("건의문 자료 검증·시각화 도우미")

# 데이터 만드는 방법 안내 (접었다 펼 수 있는 상자)
with st.expander("📋 어떤 데이터를 준비해야 하나요? (누르면 펼쳐져요)"):
    st.markdown("""
    ### 1. 데이터 입력 방식

    - `데이터 붙여넣기` 탭에서는 스프레드시트에서 복사한 데이터를 붙여넣을 수 있어요.
    - `CSV/Excel 업로드` 탭에서는 CSV 또는 Excel(.xlsx) 파일을 업로드해서 데이터를 입력할 수 있어요.

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

    **이미 만들어진 큰 데이터(공공데이터 등)를 그대로 올려도 괜찮아요.**
    글자로 된 열(예: 성별, 지역)과 숫자로 된 열(예: 점수, 인구수)이 섞여 있어도,
    아래에서 "무엇을 기준으로 비교할지" 직접 선택할 수 있어요.

    ### 3. 꼭 지켜야 할 것

    - 첫 번째 줄에는 반드시 **열 이름**만 적기 (숫자 X)
    - 숫자 칸에는 순수 숫자만 넣기 (%, 명, kg 같은 글자 넣지 않기)
    - 데이터를 어디서 가져왔는지(출처) 꼭 확인해 두기 — 아래 자료 검증 단계에서 필요해요!
    """)

# 1단계: 문제 상황 입력
st.markdown("**막막하다면 이런 주제는 어떨까요? (버튼을 누르면 아래 칸에 채워져요)**")
example_topics = ["청소년 체육 시설 부족", "층간 소음 문제", "학생 매점의 필요성", "학교 축제 참여율 감소"]
cols = st.columns(len(example_topics))
for col, topic in zip(cols, example_topics):
    with col:
        if st.button(topic):
            st.session_state["problem_example"] = topic

problem = st.text_area(
    "어떤 문제 상황을 건의하고 싶나요?",
    value=st.session_state.get("problem_example", "")
)

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
        key="pasted_data",
        placeholder="스프레드시트에서 복사한 데이터를 여기에 붙여넣어 주세요. 열 헤더가 포함되어야 합니다.",
        on_change=set_input_mode_paste
    )

with tab2:
    uploaded_file = st.file_uploader(
        "CSV 또는 Excel 파일 업로드",
        type=["csv", "xlsx"],
        key="uploaded_file",
        on_change=set_input_mode_upload
    )


df = None
parse_error = None
uploaded_file = st.session_state.get("uploaded_file")
pasted_data = st.session_state.get("pasted_data")
source = None
mode = st.session_state.data_input_mode  # 최근에 사용한 탭 확인

if mode == "upload" and uploaded_file is not None:
    source = "업로드"
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
    except Exception as e:
        parse_error = f"파일을 읽는 데 실패했습니다: {e}"
elif mode == "paste" and pasted_data:
    source = "붙여넣기"
    try:
        df = pd.read_csv(io.StringIO(pasted_data), sep=None, engine='python')
    except Exception:
        try:
            df = pd.read_csv(io.StringIO(pasted_data))
        except Exception as e:
            parse_error = f"데이터를 읽는 데 실패했습니다: {e}"
            df = None

if df is not None:
    st.info(f"현재 데이터 소스: {source}")
    st.dataframe(df)

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    text_columns = df.select_dtypes(exclude="number").columns.tolist()

    if numeric_columns:
        # 가로축(비교 기준)과 세로축(보고 싶은 값)을 나눠서 선택
        col1, col2 = st.columns(2)
        with col1:
            group_column = st.selectbox(
                "무엇을 기준으로 비교하고 싶나요? (가로축)",
                ["전체 데이터 그대로 보기"] + text_columns,
                key="group_column"
            )
        with col2:
            selected_columns = st.multiselect(
                "어떤 값을 보고 싶나요? (세로축, 여러 개 선택 가능)",
                numeric_columns,
                default=[numeric_columns[0]],
                key="selected_columns"
            )

        # 그룹으로 묶을 때는 어떻게 계산할지도 선택
        agg_method = "평균"
        if group_column != "전체 데이터 그대로 보기":
            agg_method = st.radio(
                "어떻게 계산할까요?",
                ["평균", "합계", "개수"],
                horizontal=True,
                key="agg_method"
            )

        chart_type = st.selectbox(
            "그래프 종류를 선택하세요",
            ["막대그래프", "꺾은선그래프", "원그래프", "띠그래프"],
            key="chart_type"
        )

        # 그래프 종류별 설명 (선택하면 바로 아래에 안내가 떠요)
        chart_explanations = {
            "막대그래프": "📊 **막대그래프**: 여러 항목의 크기를 막대 길이로 비교할 때 좋아요. (예: 성별에 따른 평균 점수 비교)",
            "꺾은선그래프": "📈 **꺾은선그래프**: 시간에 따라 값이 어떻게 변하는지 보여줄 때 좋아요. (예: 연도별 인구 변화)",
            "원그래프": "🥧 **원그래프**: 전체에서 각 항목이 차지하는 비율(%)을 한눈에 보여줄 때 좋아요. (예: 우리 반 설문에서 스트레스 원인별 비율)",
            "띠그래프": "▬ **띠그래프**: 전체를 100%로 놓고 각 항목의 비율을 비교할 때 좋아요. 여러 그룹(예: 우리 학교 vs 전국 평균)을 나란히 놓고 비교하기에도 좋아요.",
        }
        st.caption(chart_explanations[chart_type])

        if selected_columns:
            try:
                # 그룹 기준이 있으면 평균/합계/개수로 요약, 없으면 원본 그대로 사용
                if group_column != "전체 데이터 그대로 보기":
                    agg_map = {"평균": "mean", "합계": "sum", "개수": "count"}
                    plot_df = df.groupby(group_column)[selected_columns].agg(agg_map[agg_method])
                else:
                    plot_df = df[selected_columns]

                fig, ax = plt.subplots()

                if chart_type == "막대그래프":
                    plot_df.plot(ax=ax, kind="bar")

                elif chart_type == "꺾은선그래프":
                    plot_df.plot(ax=ax, kind="line", marker='o')

                elif chart_type == "원그래프":
                    if len(selected_columns) == 1:
                        if group_column != "전체 데이터 그대로 보기":
                            plot_df[selected_columns[0]].plot(ax=ax, kind="pie", autopct="%1.1f%%")
                        else:
                            df[selected_columns[0]].value_counts().plot(ax=ax, kind="pie", autopct="%1.1f%%")
                    else:
                        plot_df.sum().plot(ax=ax, kind="pie", autopct="%1.1f%%")

                elif chart_type == "띠그래프":
                    totals = plot_df if group_column != "전체 데이터 그대로 보기" else plot_df.sum().to_frame().T
                    proportions = totals.div(totals.sum(axis=1), axis=0) * 100

                    left = pd.Series(0, index=proportions.index)
                    for col_name in selected_columns:
                        ax.barh(proportions.index.astype(str), proportions[col_name], left=left, label=col_name)
                        left += proportions[col_name]
                    ax.set_xlim(0, 100)
                    ax.set_xlabel("비율 (%)")
                    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)

                if chart_type not in ["원그래프", "띠그래프"]:
                    ax.set_ylabel(", ".join(selected_columns))
                st.pyplot(fig)
                st.info("💡 이 그래프는 건의문 개요의 **'중간 - 문제 상황과 해결 방안'** 칸에서 근거 자료로 활용하세요!")

                st.subheader("자료 검증하기 (타당성·신뢰성 평가)")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**타당성**")
                    st.checkbox("공정성 — 내 생각에 치우치지 않고 근거를 다뤘나요?", key="check_fair")
                    st.checkbox("실현 가능성 — 건의 내용이 현실적으로 가능한가요?", key="check_feasible")
                    st.checkbox("논리적 설득력 — 근거와 주장이 논리적으로 연결되나요?", key="check_logic")
                with col_b:
                    st.markdown("**표현**")
                    st.checkbox("간결성 — 표현이 구체적이고 간결한가요?", key="check_concise")
                    st.checkbox("명료성 — 명확한 표현을 사용했나요?", key="check_clear")
                    st.checkbox("정중성 — 건의 대상에 맞는 예의를 지켰나요?", key="check_polite")
            except Exception as e:
                st.error(f"그래프를 그리는 중 문제가 발생했어요: {e}")
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