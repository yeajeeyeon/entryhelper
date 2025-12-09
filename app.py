import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="엔트리 튜터", page_icon="🤖")

st.title("🤖 엔트리 코딩 도우미")
st.caption("정답 대신 힌트로 생각하는 힘을 길러줍니다! (Powered by Gemini)")

# API 키 설정 (Streamlit Secrets에서 가져오기)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # 로컬 테스트용 입력창
    api_key = st.text_input("Google API Key를 입력하세요", type="password")

if not api_key:
    st.info("챗봇을 시작하려면 API 키 설정이 필요합니다.")
    st.stop()

# Gemini 모델 설정
genai.configure(api_key=api_key)

# 챗봇의 페르소나(역할) 설정
system_instruction = """
당신은 초등학생/중학생을 위한 친절한 '엔트리(Entry) 코딩 선생님'입니다.

[행동 지침]
1. 학생이 질문하면 **절대 정답 블록 코드를 바로 보여주지 마세요.**
2. 대신 스스로 생각할 수 있도록 단계적인 **힌트**를 주세요.
3. "만일 ~라면 블록을 써볼까?", "움직임 카테고리에 가보면 좌표를 바꾸는 블록이 있어" 처럼 엔트리 용어를 사용해 가이드하세요.
4. KNN, 인공지능 같은 어려운 개념은 '유유상종', '끼리끼리' 같은 쉬운 비유로 설명하세요.
5. 항상 존댓말을 쓰고, 학생을 격려해주세요.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 화면에 이전 대화 내용 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 사용자 질문 입력 처리
if prompt := st.chat_input("엔트리 코딩하다가 막힌 부분을 물어보세요!"):
    # 사용자 질문 표시
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gemini에게 보낼 대화 내역 구성
    gemini_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # AI 응답 생성 및 표시
    with st.chat_message("assistant"):
        try:
            chat = model.start_chat(history=gemini_history[:-1])
            response = chat.send_message(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")