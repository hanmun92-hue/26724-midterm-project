import streamlit as st

st.title("건의문 개요 작성")

# 이전 페이지에서 만든 그래프가 있으면 여기에도 보여주기
if "graph_image" in st.session_state:
	st.image(st.session_state["graph_image"], caption=f"확인한 그래프 ({st.session_state.get('chart_type_used', '')})")
	st.info("💡 위 그래프를 다시 확인하면서 아래 '중간' 칸을 작성해보세요!")
else:
	st.warning("아직 그래프를 만들지 않았어요. 먼저 사이드바에서 첫 페이지로 가서 데이터를 올리고 그래프를 확인해보세요.")

st.subheader("건의문 개요 작성")
st.text_input("처음 - 건의 동기와 배경", key="outline_start")
st.text_area(
	"중간 - 문제 상황과 해결 방안",
	placeholder="예) 위 그래프에서 확인한 것처럼 ○○ 항목이 가장 높게(또는 낮게) 나타났습니다. 이는 △△ 때문으로 보이며, 이를 해결하기 위해 □□를 제안합니다.",
	key="outline_middle"
)
st.text_input("끝 - 요약 및 강조", key="outline_end")


st.subheader("내가 쓴 건의문, 이렇게 점검해보세요")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("개요, 이렇게 점검해보세요")
st.checkbox("완결성 — 처음(동기)·중간(문제+해결방안)·끝(요약) 세 칸이 모두 채워졌나요?", key="check_complete")
st.checkbox("근거 연결 — '중간' 칸에서 그래프의 수치를 실제로 언급했나요?", key="check_evidence_linked")
st.checkbox("실현 가능성 — 내가 제안한 해결 방안이 현실적으로 가능한가요?", key="check_feasible")
st.checkbox("논리적 연결 — 문제 상황 → 근거 → 해결 방안이 자연스럽게 이어지나요?", key="check_logic")

st.caption("💡 개요를 완성해 실제 건의문 전체를 쓸 때는 표현이 간결하고 예의 바른지도 함께 점검해보세요.")