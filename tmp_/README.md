<div align="left">

  <img src="https://img.shields.io/badge/Backend-Python-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/AI-LLM-orange?style=flat-square" alt="LLM">
  <img src="https://img.shields.io/badge/AI-RAG-green?style=flat-square" alt="RAG">
  <img src="https://img.shields.io/badge/Database-MySQL-lightblue?style=flat-square&logo=mysql&logoColor=white" alt="MySQL">
</div>

# **🚨[비상사태 매뉴얼 챗봇]**
## 🌟 **프로젝트 소개**
> 이 프로젝트는 비상사태 상황에서 시민들에게 빠르고 정확한 정보를 제공하기 위해 개발되었습니다.
> 💡 **주요 목표**: 비상사태 입력 시 시민들에게 신속하게 정확도가 높은 매뉴얼 소개, 사용자의 위치 정보를 기반으로 가장 가까운 대피소의 위치 안내
궁극적으로 각종 재난에 대한 대처를 용이하게 만들고자 함

<img src="../SourceCode/리드미시연영상1.gif">

## 🎯**프로젝트 핵심 목표**
- **비상사태 대책**
  - 전쟁, 가뭄, 화재, 지진 등 다양한 비상사태에 대한 대처 방안 신속하게 제공.
- **위치 기반 대피소 안내**  
  - 카카오맵 API로 위치 기반 서비스(LBS)를 구현해 사용자 위치를 기반으로 가장 가까운 대피소를 실시간으로 안내.
- **PDF RAG**  
  - LLM, RAG를 이용하여 비상사태 대피 매뉴얼을 학습하는 기능 구현, 자연어 질의에 기반한 정확한 답변 제공.


## 📝 **프로젝트 개요**
**성능 개선**
어느 부분에서 성능개선이 이루어졌는지?
before&after 수치/시각적으로 표현
**트러블슈팅**

---

## 인프라 아키텍쳐 & 적용기술
![](\SourceCode\FigJam_basics.png)
### 적용 기술
<details>
<summary><strong>LLM</strong></summary>
OpenAI의 GTP-4o API를 이용하여 사용자의 자연어 질의에 자동으로 응답을 생성해 출력하는 기능 구현
사용된 시스템 프롬프트: 

> "system", (
            "당신은 비상사태 대처 매뉴얼 전문 챗봇입니다. "
            "재난 상황(지진, 화재, 홍수, 전쟁 등)이 발생했을 때 사용자가 안전하게 대피할 수 있도록 최적의 정보를 제공하는 것이 목표입니다.\n\n"
            "제공된 컨텍스트만 사용해서, 질문에 답변하세요."
            "아래의 지침에 따라 응답하세요:\n"
            "1. 역할 정의: 사용자에게 신뢰할 수 있는 정보를 제공하고, 필요한 경우 함수 호출을 통해 가장 가까운 대피소를 추천하세요.\n"
            "2. 대화 스타일: 간결하고 명확하며 사용자 친화적인 언어를 사용하고, 긴급 상황에 맞는 전문적인 톤을 유지하세요.\n"
            "3. 긴급 연락처: 추가적인 도움이 필요할 경우 즉시 긴급 연락처(예: 119, 112)를 안내하세요.\n"
            "4. 정보의 정확성과 최신성: 최신 데이터를 결합해 응답하세요. 데이터 부족 시 안전한 방향으로 안내하고 추가 도움을 요청하도록 권장하세요.\n"
            "5. 함수 호출 지침: 대피소 검색이나 위치 관련 질문에 적절한 함수를 호출하여 데이터를 검색하세요.\n"
            "6. 다양한 사용자 고려: 복잡한 용어 대신 쉬운 표현을 사용하세요.\n"
            "7. 추가 지침: 필요한 경우 질문을 되묻고, 제공 정보가 명확한지 점검하세요."
        )

</details>

<details>
<summary><strong>RAG</strong></summary>
PDF와 재난안전데이터공유플랫폼에서 가져온 API에서 대응법을 학습해 VectorDB에 임베딩된 데이터를 저장, 사용자의 질문에 관련된 데이터를 검색해 결과 데이터를 LLM에 전달해 정확도 높은 답변 생성

재난 상황에 대한 사용자의 질문을 받아 자연어 질의에 기반한 정확한 답변 제공
제공되는 API의 한계로 인해 등록된 IP 외에는 API의 사용이 불가하여 SourceCode 디렉토리 안에 API로부터 응답받은 json파일이 미리 저장되어 있다. 

사전에 전처리된 데이터가 preprocessed_data_path 변수가 지정하는 디렉토리에 저장되어 있다면 API 호출 비용을 아끼기 위해 저장되어있던 전처리된 데이터를 사용
preprocessed_data_path의 디폴트값은 'SourceCode/preprocessed_docs.pkl'이다. 

필요없는 텍스트를 줄이기 위해 다음의 전처리 과정을 수행: 
- "비상시 국민행동요령 알아야 안전하다"로 시작한다면 제거
- 특정 패턴이 시작 부분에 있으면 제거
- 기타 불필요한 줄바꿈, 공백, 특수문자 정리
각 전처리가 끝난 데이터는 preprocessed_data_path 디렉토리에 저장됨
전처리가 끝난 데이터는 임베딩되어 VectorDB에 저장

FAISS와 Pandas를 이용해 벡터DB 구현 
캐시 지원 임베딩
</details>

<details>
<summary><strong>위치 기반 서비스 (LBS)</strong></summary>
카카오맵 API를 이용하여 검색한 위치의 경도와 위도를 반환함

</details>

## 🔍 **주요 로직**
### 1. **데이터 수집 및 전처리**  
   - 재난안전플랫폼, 카카오맵 등 다양한 플랫폼에서 API를 활용해 실시간 데이터를 수집. 
   - 수집된 데이터를 전처리하여 효과적으로 사용.

### 2. **PDF RAG 활용**  
   - 비상상황 대피 매뉴얼 PDF를 Retrieval-Augmented Generation (RAG) 방식으로 학습하여 답변 제공.

### 3. **위치 기반 서비스 (LBS)**  
   - 사용자 입력 주소를 기준으로, 데이터 내 대피소와의 거리를 계산.  
   - 가장 가까운 대피소를 안내.

### 4. **추가 가능 기능** 
   - 음성 인식 기능, 음성 출력
   - 실시간 재난 알림.  
   - 사용자 맞춤형 경고 메시지.  


## 기술적 고도화

프로젝트 진행하면서 했던 고민 작성


## 👩‍💻 **팀원 소개**
<details>
<summary><strong>팀원 역할 및 담당 파트 보기</strong></summary>

>### 🧑 **박성규(팀장)**
- **담당 파트:** function calling 설계, 프론트엔드 구현(streamlit 기반 챗봇 인터페이스)
- **역할:** SA문서 관리, 발표 🎤  
- [GitHub 링크](https://github.com/PSG4160)

>### 👨‍💻 **김광림**
- **담당 파트:** api 데이터 수집, system_prompt 작성, 음성 입출력 기능 설계, Query_Decomposition 설계, 시연 영상 제작
- **역할:** 시연영상 🎥  
- [GitHub 링크](https://github.com/bgt30)

>### 👨‍🔬 **조현민**
- **담당 파트:** 데이터 수집, 데이터 전처리 
- **역할:** SA 문서관리 📄  
- [GitHub 링크](https://github.com/ddangddang-e)

>### 👨‍💻 **정윤우**
- **담당 파트:** 데이터 수집(PDF매뉴얼, API 데이터), LLM_RAG
- **역할:** README 작성📝  
- [GitHub 링크](https://github.com/mireuk-git)

>### 👨‍💻 **최해찬**
- **담당 파트:** LLM_RAG  
- **역할:** PPT 제작🖼️  
- [GitHub 링크](https://github.com/)

<details>
<summary><strong>999조 그라운드룰 조회하기</strong></summary>

<details>
<summary><strong>Git 관련 작업 시 준수해야 할 규칙입니다.</strong></summary>

### 기본 규칙

1. **작업 시작 전 최신 상태 동기화**  
   항상 작업 전 `git fetch origin`을 통해 원격 저장소의 최신 정보를 동기화합니다.

2. **개인 브랜치에서 작업**  
   각자 자신의 브랜치에서 작업하며, 다른 조원의 브랜치를 수정하지 않도록 유의하세요.

3. **Merge 규칙**  
   main 브랜치로 Merge 시, Pull Request에서 **최소 1명**의 조원 확인(Review Approval)을 받아야 합니다.

4. **충돌 해결**  
   충돌이 발생한 경우, 팀원 간 충분히 공유하여 협업으로 문제를 해결합니다.

5. **위 내용과 더불어 플로우 로직이 이해가 쉽도록 작성 부탁드립니다.**

### 회의 규칙

1. 특별한 일이 없다면, 오전 10시와 오후4시에 회의 진행
2. 특강 등 일정이 있어 앞서 정한 시간에 회의를 진행할 수 없다면, 임의로 회의시간을 정해서 회의 진행

</details>

</details>