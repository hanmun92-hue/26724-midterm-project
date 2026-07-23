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

