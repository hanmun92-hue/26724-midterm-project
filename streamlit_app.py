import io
import re
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = os.path.join(os.path.dirname(__file__), 'font', 'NanumGothic-Regular.ttf')
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.sans-serif'] = ['NanumGothic']
plt.rcParams['axes.unicode_minus'] = False

# 폰트 파일이 존재하면 폰트 매니저에 등록
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    bold_font_path = os.path.join(os.path.dirname(__file__), 'font', 'NanumGothic-Bold.ttf')
    if os.path.exists(bold_font_path):
        fm.fontManager.addfont(bold_font_path)


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
st.session_state["problem_saved"] = problem

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

        # 그룹 순서를 직접 정하는 기능 (그룹 기준을 선택했을 때만 표시)
        custom_order = None
        if group_column != "전체 데이터 그대로 보기":
            unique_values = df[group_column].dropna().unique().tolist()
            with st.expander(f"🔢 '{group_column}'의 순서를 직접 정하고 싶다면 (선택 사항)"):
                st.caption("항목을 순서대로 다시 선택하면 그 순서로 그래프가 그려져요. (예: 학력 낮음 → 높음)")
                custom_order = st.multiselect(
                    "원하는 순서대로 다시 선택하세요",
                    unique_values,
                    default=unique_values,
                    key="custom_order"
                )

        # 그룹으로 묶을 때는 어떻게 계산할지도 선택 (group_column과 같은 레벨)
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

        if chart_type == "꺾은선그래프" and group_column != "전체 데이터 그대로 보기":
            unique_count = df[group_column].nunique()
            if unique_count <= 10:
                st.warning(
                    f"⚠️ '{group_column}'의 순서가 지금은 의미 없이 나열되어 있어요({unique_count}개 항목). "
                    "만약 이 항목에 '학력처럼 자연스러운 순서'가 있다면 위 '순서를 직접 정하고 싶다면' 상자에서 "
                    "순서를 정해주세요. 성별처럼 순서가 없다면 **막대그래프**를 추천해요!"
                )

        if selected_columns:
            try:
                # 그룹 기준이 있으면 평균/합계/개수로 요약, 없으면 원본 그대로 사용
                if group_column != "전체 데이터 그대로 보기":
                    agg_map = {"평균": "mean", "합계": "sum", "개수": "count"}
                    plot_df = df.groupby(group_column)[selected_columns].agg(agg_map[agg_method])
                    # 학생이 지정한 순서가 있으면 그 순서대로 다시 정렬
                    if custom_order and len(custom_order) == len(plot_df):
                        plot_df = plot_df.reindex(custom_order)
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
                    ax.set_xlabel("비율 (%)", fontproperties=font_prop)
                    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)

                if chart_type not in ["원그래프", "띠그래프"]:
                    ax.set_ylabel(", ".join(selected_columns), fontproperties=font_prop)
                
                # 모든 텍스트 요소에 한글 폰트 적용
                ax.set_title(ax.get_title(), fontproperties=font_prop)
                ax.set_xlabel(ax.get_xlabel(), fontproperties=font_prop)
                ax.set_ylabel(ax.get_ylabel(), fontproperties=font_prop)
                
                # legend에 폰트 적용
                if ax.get_legend():
                    for text in ax.get_legend().get_texts():
                        text.set_fontproperties(font_prop)
                
                # tick labels에 폰트 적용
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontproperties(font_prop)
                st.pyplot(fig)

                # 그래프를 이미지 파일로 다운로드할 수 있게 만들기
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format="png", dpi=200, bbox_inches="tight")
                img_buffer.seek(0)
                st.download_button(
                    label="📥 이 그래프를 이미지 파일로 저장하기",
                    data=img_buffer,
                    file_name=f"{chart_type}_그래프.png",
                    mime="image/png"
                )

                # 다음 페이지(건의문 개요 작성)에서도 이 그래프를 볼 수 있도록 저장
                st.session_state["graph_image"] = img_buffer.getvalue()
                st.session_state["chart_type_used"] = chart_type

                st.subheader("자료 검증하기 (이 그래프, 근거로 믿을 만한가요?)")
                st.checkbox("출처 — 이 자료가 어디서 나온 것인지 알고 있나요? (통계청, 학교알리미 등)", key="check_source")
                st.checkbox("사실성 — 이 그래프가 데이터를 있는 그대로 보여주나요? (숫자를 빼거나 왜곡하지 않았나요?)", key="check_accurate")
                st.checkbox("관련성 — 이 그래프가 내가 건의하려는 문제 상황과 직접 관련이 있나요?", key="check_relevant")
                st.checkbox("최신성 — 너무 오래된 자료는 아닌가요?", key="check_recent")
                st.success("✅ 그래프 확인과 자료 검증이 끝났다면, 왼쪽 사이드바에서 **'건의문 개요 작성'** 페이지로 이동해 글을 써 보세요!")

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