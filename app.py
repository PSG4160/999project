import streamlit as st
from llm import initialize, get_response

st.title("비상사태 대처 매뉴얼 챗봇")
st.write("안녕하세요! 비상사태에서 안전한 대처를 도와드리는 챗봇입니다. 질문이 있다면 자유롭게 입력하세요.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    initial_message = initialize()
    st.session_state.messages.append({"role": "ai", "content": initial_message})

for message in st.session_state.messages:
    if message["role"] == "ai":
        st.chat_message("assistant").write(message["content"])
    elif message["role"] == "function":
        st.chat_message("function").write(message["content"])
    else:
        st.chat_message("user").write(message["content"])

if user_input := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = get_response(user_input)
    st.session_state.messages.append({"role": "ai", "content": response["response"]})
    if "function_call" in response:
        function_result = response["function_call"]["result"]
        st.session_state.messages.append({"role": "function", "content": function_result})
    st.rerun()
