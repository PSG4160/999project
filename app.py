import streamlit as st
from llm import initialize, get_response
from streamlit_geolocation import streamlit_geolocation

st.title("비상사태 대처 매뉴얼 챗봇")
st.write("안녕하세요! \n\n 비상사태에서 안전한 대처를 도와드리는 챗봇입니다. 질문이 있다면 자유롭게 입력하세요.")

# 사용자 위치 정보 가져오기
location = streamlit_geolocation()
# st.write(location)  # 디버깅용 위치 정보 확인

if location.get("latitude") is not None and location.get("longitude") is not None:
    st.write("현재 위치를 확인했습니다.")
else:
    st.write("위치 정보를 가져올 수 없습니다. 브라우저에서 위치 정보 접근을 허용하고 위 버튼을 눌러주세요.")
    latitude, longitude = None, None

# 메시지 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 초기 메시지 설정
    initial_message = initialize()
    st.session_state.messages.append({"role": "ai", "content": initial_message})

# 이전 메시지 출력
for message in st.session_state.messages:
    if message["role"] == "ai":
        st.chat_message("assistant").write(message["content"])
    elif message["role"] == "function":
        st.chat_message("function").write(message["content"])
    else:
        st.chat_message("user").write(message["content"])

# 위치 기반 대피소 검색 버튼
if st.button("가까운 대피소 검색"):
    # 위치 정보 확인
    if location:
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        # latitude와 longitude 값이 존재하는지 확인
        if latitude and longitude:
            # 명시적인 요청 메시지 추가
            user_message = "현재 위치에서 가까운 대피소 정보를 알려줘."
            st.session_state.messages.append({"role": "user", "content": user_message})

            # 사용자 메시지 즉시 표시
            st.chat_message("user").write(user_message)

            # 응답 자리 확보 및 로딩 메시지 표시
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.write("답변을 생성 중입니다...")

                # 모델에 위치 정보 전달하여 응답 생성
                response = get_response(user_input=user_message, user_location={"latitude": latitude, "longitude": longitude})

                # 챗봇 응답 업데이트
                message_placeholder.markdown(response["response"])
                st.session_state.messages.append({"role": "ai", "content": response["response"]})
        else:
            st.write("위치 정보를 가져오는 데 실패했습니다.")
    else:
        st.write("위치 정보를 가져올 수 없습니다. 브라우저에서 위치 정보 접근을 허용해주세요.")

# 사용자 입력 처리
if user_input := st.chat_input("질문을 입력하세요"):
    # 사용자 메시지 추가 및 즉시 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # 응답 자리 확보 및 로딩 메시지 표시
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.write("답변을 생성 중입니다...")

        # 응답 생성
        response = get_response(user_input, user_location=location)

        # 챗봇 응답 업데이트
        message_placeholder.markdown(response["response"])
        st.session_state.messages.append({"role": "ai", "content": response["response"]})
