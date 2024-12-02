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
if not st.session_state.messages:
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

# 세션 상태 초기화
if "button_clicked" not in st.session_state:
    st.session_state.button_clicked = False 

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

            # 모델에 위치 정보 전달하여 응답 생성
            response = get_response(user_input=user_message, user_location={"latitude": latitude, "longitude": longitude})

            # 챗봇 응답 추가
            st.session_state.messages.append({"role": "ai", "content": response["response"]})

            # # 함수 호출 결과가 있으면 추가
            # if "function_call" in response:
            #     function_result = response["function_call"]["result"]
            #     st.session_state.messages.append({"role": "function", "content": function_result})
        else:
            st.write("위치 정보를 가져오는 데 실패했습니다.")
    else:
        st.write("위치 정보를 가져올 수 없습니다. 브라우저에서 위치 정보 접근을 허용해주세요.")

    # 버튼 클릭 상태 초기화
    st.rerun()  # 즉시 화면 재렌더링
 




# 사용자 입력 처리
if user_input := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = get_response(user_input, user_location=location)

    # 디버깅: 모델 응답 확인
    # st.write(f"[DEBUG] 모델 응답: {response}")

    st.session_state.messages.append({"role": "ai", "content": response["response"]})

    ## 함수 호출 결과가 있으면 추가
    # if "function_call" in response:
    #     function_result = response["function_call"]["result"]
    #     st.session_state.messages.append({"role": "function", "content": function_result})

    st.rerun()