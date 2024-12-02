#API 호출 및 데이터 품질 검사
import re
import os
import requests
import json
import pandas as pd
import pickle
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings
import faiss
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, FunctionMessage
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import Runnable
from math import radians, sin, cos, sqrt, atan2

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 불러오기
api_key = os.getenv("OPENAI_API_KEY")

# 저장할 파일 경로 설정
preprocessed_data_path = 'SourceCode/preprocessed_docs.pkl'

# 저장된 전처리 데이터가 있는지 확인
if os.path.exists(preprocessed_data_path):
    # 전처리된 데이터 로드
    with open(preprocessed_data_path, 'rb') as f:
        all_docs = pickle.load(f)
    print(f"전처리된 데이터 {len(all_docs)}개를 로드했습니다.")
else:
    # PDF 파일들이 저장된 디렉토리
    directory_path = "SourceCode/RAG/"
    
    # PDF 파일 로드
    all_docs = []  # 모든 문서를 저장할 리스트
    
    # 디렉토리에서 모든 파일을 순회
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".pdf"):  # PDF 파일만 처리
            file_path = os.path.join(directory_path, file_name)  # 파일 경로 생성
            loader = PyPDFLoader(file_path=file_path)  # PyPDFLoader 생성
            docs = loader.load()  # 문서 로드
            all_docs.extend(docs)  # 전체 문서 리스트에 추가
    
    # 전처리 함수 정의
    def preprocess_text(text):
        '''전처리 함수'''
        # 처음에 숫자가 나오면 제거
        text = re.sub(r'^\s*\d+\s*', '', text)   
        
        # "비상시 국민행동요령 알아야 안전하다"로 시작하면 제거
        if text.startswith('비상시 국민행동요령 알아야 안전하다'):
            text = text[len('비상시 국민행동요령 알아야 안전하다'):].lstrip()
        
        # 특정 패턴이 시작 부분에 있으면 제거 (패턴 1)
        pattern1 = r'^(\s*만화로 보는 비상시\s*국민행동요령\s*화생방 피해대비\s*행동요령\s*인명시설 피해시\s*행동요령\s*비상대비물자\s*준비 및 사용요령\s*비상사태시\s*행동요령\s*)'
        text = re.sub(pattern1, '', text)
        
        # 특정 패턴이 시작 부분에 있으면 제거 (패턴 2)
        pattern2 = r'^(\s*온 가족이 함께\s*안전하게\s*화생방 피해대비\s*행동요령\s*인명시설 피해시\s*행동요령\s*비상대비물자\s*준비 및 사용요령\s*비상사태시\s*행동요령\s*화생방경보 발령시\s*국민행동요령\s*핵 경보 발령시\s*국민행동요령\s*)'
        text = re.sub(pattern2, '', text)
        
        # 불필요한 줄 바꿈과 공백 정리
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text)
    
        # 한글, ., -, %, /, ()를 제외한 모든 특수문자 제거
        text = re.sub(r'[^a-zA-Z0-9\s%.\-/()\uAC00-\uD7A3]+', '', text)
    
        # 문자열 양쪽 공백 제거
        text = text.strip()
        
        return text
    
    # 각 문서의 page_content 전처리
    for doc in all_docs:
        doc.page_content = preprocess_text(doc.page_content)
    
    # 전처리된 데이터 저장
    with open(preprocessed_data_path, 'wb') as f:
        pickle.dump(all_docs, f)
    print(f"전처리된 데이터 {len(all_docs)}개를 저장했습니다.")

recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

splits = recursive_text_splitter.split_documents(all_docs)

'''
# 청크 확인 디버그 코드
for idx, chunk in enumerate(splits):
    print(f"Chunk {idx + 1}:")
    print("-" * 20)
    print(chunk.page_content)
    print("\n" + "=" * 40 + "\n")
'''

# 1. OpenAI 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. 로컬 파일 저장소 설정 (사용자 환경에 맞는 경로로 설정)
store = LocalFileStore("F:/STUDY/sparta/999/SourceCode/emb")  # 로컬 경로 설정 각자 작성 해야합닏.

# 3. 캐시를 지원하는 임베딩 생성
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings=embeddings,
    document_embedding_cache=store,
    namespace=embeddings.model,  # 모델 이름을 네임스페이스로 설정
)


'''
# 4. 예시 텍스트
example_texts = [
    "OpenAI의 임베딩 모델은 강력한 자연어 처리를 제공합니다.",
    "로컬 캐시는 효율적인 데이터 처리를 가능하게 합니다.",
    "임베딩 모델을 활용하여 고품질의 애플리케이션을 개발할 수 있습니다."
]

# 5. 임베딩 생성 및 저장된 결과 출력
for text in example_texts:
    embedding = cached_embedder.embed_query(text)  # 임베딩 생성
    print(f"텍스트: {text}")
    print(f"임베딩 (첫 10개 값): {embedding[:10]}")  # 임베딩 값의 일부를 출력

print("임베딩 생성 완료 및 로컬 캐시에 저장되었습니다.")
'''

vectorstore = FAISS.from_documents(documents=splits, embedding=cached_embedder)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4}) 

# 테스트 하면서 수정할 예정

# 대피소 정보 불러오기
with open("SourceCode/shelters.json", "r", encoding="utf-8") as f:
    shelters = json.load(f)

# shelters 리스트를 데이터프레임으로 변환
df = pd.DataFrame(shelters)
df = df[df['SHNT_PSBLTY_NOPE'] != '0']  # 대피가능인원수 0인 곳을 제외

print(df.head())

# DMS를 소수점 좌표로 변환하는 함수 (경도 위도 각각 숫자 합치기)
def dms_to_dd(degrees, minutes, seconds):
    return degrees + minutes / 60 + seconds / 3600

# 위도 변환 (LAT_PROVIN, LAT_MIN, LAT_SEC를 사용)
df['위도'] = df.apply(lambda row: dms_to_dd(
    float(row['LAT_PROVIN']), 
    float(row['LAT_MIN']), 
    float(row['LAT_SEC'])
), axis=1)

# 경도 변환 (LOT_PROVIN, LOT_MIN, LOT_SEC를 사용)
df['경도'] = df.apply(lambda row: dms_to_dd(
    float(row['LOT_PROVIN']), 
    float(row['LOT_MIN']), 
    float(row['LOT_SEC'])
), axis=1)

# 주소 컬럼 설정 (도로명 주소 사용)
df['주소'] = df['FCLT_ADDR_RONA']
# 장소 컬럼 설정
df['시설명'] = df['FCLT_NM']

# 필요한 컬럼만 선택 추가가 가능하다. (대피소 정보 불러오고 추가 정보가 필요하다고 판단되면 추가하면 됩니다.) 답변 테스트 할때, 필요하다고 판단되면
df_result = df[['시설명','주소', '위도', '경도']]

print(df_result.head())

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    위도와 경도를 받아 두 지점 사이의 거리를 킬로미터 단위로 계산하는 함수
    """
    # 위도와 경도를 라디안으로 변환
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # 위도와 경도의 차이 계산
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine 공식 적용
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    R = 6371  # 지구 반지름 (킬로미터 단위)
    distance = R * c
    return distance

''' 키워드 검색시 주소를 호출하지 못함 -> 키워드 검색 로직 추가 '''

load_dotenv()
kakaoapikey = os.getenv("REST_API_KEY") # 카카오 API 호출
def get_coordinates(query):
    """
    검색 질의어(query)를 기반으로 주소 검색 API와 장소 검색 API를 순차적으로 호출하여 경도와 위도를 반환.

    Args:
        query (str): 검색할 주소 또는 장소.
        kakaoapikey (str): 카카오맵 REST API 키.

    Returns:
        tuple: (longitude, latitude) - 경도(x), 위도(y)
    """
    # 1. 주소 검색 API 호출
    address_url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {kakaoapikey}"}
    params = {"query": query, "size": 1}

    address_response = requests.get(address_url, headers=headers, params=params)
    if address_response.status_code == 200:
        data = address_response.json()
        documents = data.get("documents", [])
        if documents:
            x = documents[0].get("x")
            y = documents[0].get("y")
            return (x, y)
    
    # 2. 장소 검색 API 호출 (주소 검색 결과가 없을 경우)
    keyword_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    keyword_response = requests.get(keyword_url, headers=headers, params=params)
    if keyword_response.status_code == 200:
        data = keyword_response.json()
        documents = data.get("documents", [])
        if documents:
            x = documents[0].get("x")
            y = documents[0].get("y")
            return (x, y)
    
    # 결과 없음
    print("검색 결과가 없습니다.")
    return None


# # 테스트 실행
# if __name__ == "__main__":
#     query = "동대구역"  # 검색할 장소 또는 주소
#     coordinates = get_coordinates(query)
#     if coordinates:
#         print(f"경도: {coordinates[0]}, 위도: {coordinates[1]}")

def find_nearest_shelters(latitude: float = None, longitude: float = None, address: str = None) -> str:
    """
    주어진 위도와 경도 또는 주소를 기준으로 가장 가까운 대피소를 검색합니다.
    """
    # 주소가 주어진 경우 좌표로 변환
    if address:
        coordinates = get_coordinates(address)
        if coordinates:
            user_lon = float(coordinates[0])
            user_lat = float(coordinates[1])
        else:
            return "주소로부터 좌표를 가져올 수 없습니다."
    elif latitude is not None and longitude is not None:
        user_lat = latitude
        user_lon = longitude
    else:
        return "주소나 위도/경도를 제공해주세요."

    # 거리 계산 함수
    def calculate_distance(row):
        try:
            shelter_lat = float(row['위도'])
            shelter_lon = float(row['경도'])
            return haversine_distance(user_lat, user_lon, shelter_lat, shelter_lon)
        except (ValueError, TypeError):
            return None

    # 데이터프레임에 거리 계산 적용
    df_result['거리'] = df_result.apply(calculate_distance, axis=1)

    # 유효한 거리만 필터링
    df_valid = df_result[df_result['거리'].notnull()]

    # 거리 기준으로 정렬 및 상위 3개 선택
    df_sorted = df_valid.sort_values(by='거리')
    df_top3 = df_sorted.head(3)

    # 결과 문자열 생성
    result = "\n가장 가까운 대피소 정보 (거리순):"
    for idx, row in df_top3.iterrows():
        result += f"\n\n[{idx + 1}]"
        result += f"\n시설명: {row['시설명']}"
        result += f"\n주소: {row['주소']}"
        result += f"\n현재 위치로부터의 거리: {row['거리']:.2f} km"

        # 카카오 지도 링크 추가
        shelter_add = row['주소'].replace(' ', '')
        kakao_map_link = f"https://map.kakao.com/link/search/{shelter_add}"
        result += f"\n지도 링크: {kakao_map_link}\n"

    return result



# 함수 스키마 수정
functions = [
    {
        "name": "find_nearest_shelters",
        "description": "주소나 위도/경도를 기반으로 가장 가까운 대피소 정보를 반환하는 함수.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "사용자의 현재 위도 (옵션)"
                },
                "longitude": {
                    "type": "number",
                    "description": "사용자의 현재 경도 (옵션)"
                },
                "address": {
                    "type": "string",
                    "description": "대피소를 찾고자 하는 주소 또는 장소명 (옵션)"
                }
            },
            "required": []
        }
    }
]

# 대화 기록을 저장할 메모리 초기화
memory = ConversationBufferMemory(return_messages=True)
# 모델 정의
api_key = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.4,
    streaming=True,
    model_kwargs={"functions": functions}
)
# 비상사태 대처 매뉴얼 전문 챗봇 프롬프트 템플릿 정의
chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", (
            "당신은 비상사태 대처 매뉴얼 전문 챗봇입니다. "
            "재난 상황(지진, 화재, 홍수, 전쟁 등)이 발생했을 때 사용자가 안전하게 대피할 수 있도록 최적의 정보를 제공하는 것이 목표입니다.\n\n"
            "제공된 컨텍스트와 일반 상식을 사용해서, 질문에 답변하세요."
            "위도 경도 형태로 사용자 위치가 제공될 수 있습니다"
            "아래의 지침에 따라 응답하세요:\n"
            "1. 역할 정의: 사용자에게 신뢰할 수 있는 정보를 제공하고, 필요한 경우 함수 호출을 통해 가장 가까운 대피소를 추천하세요.\n"
            "2. 대화 스타일: 간결하고 명확하며 사용자 친화적인 언어를 사용하고, 긴급 상황에 맞는 전문적인 톤을 유지하세요.\n"
            "3. 긴급 연락처: 추가적인 도움이 필요할 경우 즉시 긴급 연락처(예: 119, 112)를 안내하세요.\n"
            "4. 정보의 정확성과 최신성: 최신 데이터를 결합해 응답하세요. 데이터 부족 시 안전한 방향으로 안내하고 추가 도움을 요청하도록 권장하세요.\n"
            "5. 함수 호출 지침: 대피소 검색이나 위치 관련 질문에 적절한 함수를 호출하여 데이터를 검색하세요.\n"
            "6. 다양한 사용자 고려: 복잡한 용어 대신 쉬운 표현을 사용하세요.\n"
            "7. 추가 지침: 필요한 경우 질문을 되묻고, 제공 정보가 명확한지 점검하세요."
        )),
        ("human", "안녕하세요!"),
        ("ai", "안녕하세요! 저는 비상사태에서 안전한 대처를 도와드리는 전문 AI 챗봇입니다. 무엇을 도와드릴까요?"),
        ("human", "{user_input}"),
    ]
)

def get_user_input():
    return input("사용자: ")

def handle_function_call(response):
    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        function_name = function_call.get("name")
        function_args = function_call.get("arguments")

        # arguments가 문자열인지 확인하고, 그렇지 않으면 그대로 사용
        if isinstance(function_args, str):
            function_args = json.loads(function_args)

        if function_name == "find_nearest_shelters":
            function_result = find_nearest_shelters(**function_args)
            function_message = FunctionMessage(
                name=function_name,
                content=function_result
            )
            # 대화 기록에 함수 메시지 추가
            memory.save_context({"input": function_message.content}, {"output": function_result})
            # 모델에 함수 결과 전달하여 최종 응답 생성
            final_response = model.invoke(memory.load_memory_variables({})["history"])
            print(f"챗봇: {final_response.content}")
            # 대화 기록에 AI 메시지 추가
            memory.save_context({"input": function_result}, {"output": final_response.content})
        else:
            print(f"알 수 없는 함수 호출: {function_name}")
    else:
        print(f"챗봇: {response.content}")

def process_response(response):
    if response.additional_kwargs.get("function_call"):
        handle_function_call(response)
    else:
        print(f"챗봇: {response.content}")

class ModelInvocation(Runnable):
    def invoke(self, input, config=None):
        # 현재 사용자 입력을 메시지로 변환
        user_message = chat_template.format_messages(user_input=input)
        # 이전 대화 기록과 현재 입력을 결합하여 모델 호출
        messages = memory.load_memory_variables({})["history"] + user_message
        # 모델 응답 생성
        response = model.invoke(messages)
        # 현재 대화를 메모리에 저장
        memory.save_context({"input": input}, {"output": response.content})
        return response

class ResponseProcessor(Runnable):
    def invoke(self, input, config=None):
        process_response(input)
        return input

chat_chain = (
    ModelInvocation()
    | ResponseProcessor()
)

def main():
    # 프로그램 시작 시 초기 AI 메시지를 출력합니다.
    initial_messages = chat_template.format_messages(user_input="")
    response = model.invoke(initial_messages)
    process_response(response)

    while True:
        user_input = get_user_input()
        if user_input.lower() in ["종료", "exit", "quit"]:
            print("대화를 종료합니다.")
            break
        response = chat_chain.invoke(user_input)

'''
if __name__ == "__main__":
    main()
'''


# 함수 추가

# llm.py 수정된 부분

def initialize() -> str:
    """
    챗봇 초기화 및 초기 메시지 생성
    """
    initial_messages = chat_template.format_messages(user_input="")
    response = model.invoke(initial_messages)
    memory.save_context({"input": ""}, {"output": response.content})  # 초기 메시지 메모리에 저장
    return response.content


def get_response(user_input: str, user_location: dict = None):
    """
    사용자 입력을 받아 모델 응답을 처리하고, 함수 호출이 필요한 경우
    적절히 실행하여 최종 응답을 반환합니다.
    """
    # 1. 사용자 입력을 메시지로 변환
    user_message = chat_template.format_messages(user_input=user_input)

    # 2. 위치 정보를 프롬프트에 포함
    if user_location:
        location_message = {
            "role": "system",
            "content": f"현재 사용자의 위도: {user_location['latitude']}, 경도: {user_location['longitude']}입니다."
        }
        user_message.append(location_message)

    # 3. 이전 대화 기록 불러오기
    messages = memory.load_memory_variables({})["history"] + user_message

    # 4. 모델 호출하여 응답 생성
    response = model.invoke(messages)

    # 5. 대화 기록 저장
    memory.save_context({"input": user_input}, {"output": response.content})

    # 6. 함수 호출 처리
    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        function_name = function_call.get("name")
        function_args = function_call.get("arguments")

        # arguments가 문자열인지 확인하고 파싱
        if isinstance(function_args, str):
            function_args = json.loads(function_args)

        # 위치 정보 병합
        if user_location:
            function_args['latitude'] = user_location.get("latitude")
            function_args['longitude'] = user_location.get("longitude")

        if function_name == "find_nearest_shelters":
            # 함수 실행
            function_result = find_nearest_shelters(
                latitude=function_args.get("latitude"),
                longitude=function_args.get("longitude"),
                address=function_args.get("address")
            )

            # 함수 호출 결과를 모델에 전달하여 최종 응답 생성
            function_message = {
                "role": "function",
                "name": function_name,
                "content": function_result
            }
            messages.append(function_message)
            final_response = model.invoke(messages)

            # 대화 기록 저장
            memory.save_context({"input": function_result}, {"output": final_response.content})

            return {
                "function_call": {
                    "name": function_name,
                    "arguments": function_args,
                    "result": function_result
                },
                "response": final_response.content
            }

    # 함수 호출이 없으면 일반 응답 반환
    return {"response": response.content}





'''
def get_response(user_input: str):
    response = chat_chain.invoke(user_input)
    function_call = response.additional_kwargs.get("function_call")
    if function_call:
        function_name = function_call["name"]
        function_args = json.loads(function_call["arguments"])
        function_result = globals()[function_name](**function_args)
        return {
            "function_call": {
                "name": function_name,
                "arguments": function_args,
                "result": function_result
            },
            "response": response.content
        }
    else:
        return {"response": response.content}

'''








