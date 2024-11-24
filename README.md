<div align="left">

  <img src="https://img.shields.io/badge/Backend-Python-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/AI-LLM-orange?style=flat-square" alt="LLM">
  <img src="https://img.shields.io/badge/AI-RAG-green?style=flat-square" alt="RAG">
  <img src="https://img.shields.io/badge/Database-MySQL-lightblue?style=flat-square&logo=mysql&logoColor=white" alt="MySQL">
</div>

## 🔍 GitHub Flow

<details>
<summary><strong>Git 관련 작업 시 준수해야 할 규칙입니다.</strong></summary>

### 기본 규칙

1. **작업 시작 전 최신 상태 동기화**  
   항상 작업 전 `git fetch origin`을 통해 원격 저장소의 최신 정보를 동기화합니다.

2. **개인 브랜치에서 작업**  
   각자 자신의 브랜치에서 작업하며, 다른 조원의 브랜치를 수정하지 않도록 유의하세요.

3. **Merge 규칙**  
   main 브랜치로 Merge 시, Pull Request에서 **최소 2명**의 조원 확인(Review Approval)을 받아야 합니다.

4. **충돌 해결**  
   충돌이 발생한 경우, 팀원 간 충분히 공유하여 협업으로 문제를 해결합니다.

5. **위 내용과 더불어 플로우 로직이 이해가 쉽도록 작성 부탁드립니다.**

---

</details>

---

## 🌟 **프로젝트 주제**

<details>
<summary><strong>비상사태 대책 챗봇 프로젝트 보기</strong></summary>

### **🚨[비상사태 챗봇]**  
> 이 프로젝트는 비상사태 상황에서 시민들에게 빠르고 정확한 정보를 제공하기 위해 개발되었습니다.  
> 💡 **주요 목표**: 비상사태 입력 시 정확도가 높은 매뉴얼 소개, 추가 기능 구현  

---

### 🎯 **프로젝트 주요 키워드**
- **비상사태 대책**  
  - 전쟁, 가뭄, 화재, 지진 등 다양한 비상사태에 대한 대처 방안 제공.
- **위치 기반 대피소 안내**  
  - 사용자 위치를 기반으로 가장 가까운 대피소를 실시간으로 안내.
- **PDF RAG**  
  - 비상사태 대피 매뉴얼을 학습하여 자연어 질의에 기반한 정확한 답변 제공.

---

### 📝 **프로젝트 개요**
**주제**: 비상사태 매뉴얼 챗봇  
**이유**:  
- 전쟁, 가뭄, 화재, 지진 등 다양한 비상사태 발생 시 시민들이 빠르고 정확한 정보를 얻어야 합니다.  
- 대피장소 및 상황별 매뉴얼 정보를 제공하는 챗봇으로 재난 대처를 용이하게 하고자 합니다.

---

### 🔍 **주요 예상 로직**
1. **데이터 수집 및 전처리**  
   - 재난안전플랫폼, 카카오맵 등 다양한 플랫폼에서 API를 활용해 실시간 데이터를 수집.  
   - 수집된 데이터를 전처리하여 효과적으로 사용.

2. **PDF RAG 활용**  
   - 비상상황 대피 매뉴얼 PDF를 Retrieval-Augmented Generation (RAG) 방식으로 학습하여 답변 제공.

3. **위치 기반 서비스 (LBS)**  
   - 사용자 입력 주소를 기준으로, 데이터 내 대피소와의 거리를 계산.  
   - 가장 가까운 대피소를 안내.

4. **추가 가능 기능**  
   - 실시간 재난 알림.  
   - 사용자 맞춤형 경고 메시지.  

---

</details>




---

## 👩‍💻 **팀원 소개**

<details>
<summary><strong>팀원 역할 및 담당 파트 보기</strong></summary>

### 🧑 **박성규(팀장)**
- **담당 파트:** streamlit  
- **역할:** 발표 🎤  
- [GitHub 링크](https://github.com/PSG4160)

### 👨‍💻 **김광림**
- **담당 파트:** LLM_RAG  
- **역할:** 시연영상 🎥  
- [GitHub 링크](https://github.com/bgt30)

### 👨‍🔬 **조현민**
- **담당 파트:** 데이터 수집, 전처리  
- **역할:** SA 문서관리 📄  
- [GitHub 링크](https://github.com/ddangddang-e)

### 👨‍💻 **정윤우**
- **담당 파트:** LLM_RAG  
- **역할:** README 📝  
- [GitHub 링크](https://github.com/mireuk-git)

### 👨‍💻 **최해찬**
- **담당 파트:** LLM_RAG  
- **역할:** PPT 🖼️  
- [GitHub 링크](https://github.com/)

</details>

<details>
<summary><strong>개발 기간 및 개발 환경</strong></summary>
개발 기간: 2024.11.21 ~ 2024.12.04
개발 환경: 프로젝트동안 사용한 개발환경 기술

---

## 🛠️ **로직**

<details>
<summary><strong>로직 상세 보기</strong></summary>



###  🧭 코드 흐름도

1. 사용자가 입력 (프론트엔드)
   ↓
2. 데이터가 서버로 전달 (API)
   ↓
3. LLM 및 RAG를 활용한 데이터 처리 및 분석 (백엔드)
   ↓
4. 결과를 사용자가 확인 (UI 출력)


### 🔍 상세 로직

1. **데이터 수집:** 사용자의 입력을 받음.
```python
# 사용자가 입력한 데이터 예시
user_input = "현재 위치에서 가장 가까운 대피소를 알려주세요"

# 수집 코드 작성해야 해요
~~~~~~

```

2. **데이터 처리:** 백엔드에서 데이터 전처리 및 분석 수행.
```python
# 아직 예시코드입니다. 수정 후 이 부분을 지워주세요
# 데이터 전처리 및 PDF에서 관련 정보 검색
def process_input(query):
    preprocessed_query = preprocess(query)  # 입력 데이터 전처리
    results = search_pdf_manual(preprocessed_query)  # RAG를 활용한 검색
    return results
```

3. **AI 예측:** 학습된 모델을 활용해 결과를 예측.
```python
# LLM을 활용한 사용자 질문 처리
from langchain
# 파이프라인 코드 예시로 들어주면 될 것 같음
```

4. **결과 출력:** 사용자에게 시각적으로 결과 제공.
```python
# UI에 출력할 결과 데이터 (예시입니다 수정 후 이 부분을 지워주세요.)
output = {
    "shelter": "OOO 대피소",
    "distance": "1.2km",
    "additional_info": "대피소는 24시간 개방 중입니다."
}

print("대피소 정보:", output)
```
</details>

---

## 🧩 **기능 구현**

<details>
<summary><strong>기능 목록 상세 보기</strong></summary>

| 기능               | 설명                                         |
|--------------------|---------------------------------------------|
| 📊 **데이터 시각화**  | 결과 데이터를 그래프로 출력합니다.             |
| 🤖 **AI 분석**       | 사용자 요청을 분석하여 예측 결과를 제공합니다.  |
| 🔍 **검색 기능**      | 특정 키워드를 검색하여 관련 데이터를 제공합니다. |
| ⚙️ **커스터마이징**  | 사용자 환경에 맞게 UI를 조정할 수 있습니다.     |

</details>

---

## 저작권 및 사용권 정보

---

## 🌍 **배포 링크**

[🔗 프로젝트 바로가기](https://project-link.com)

프로젝트에 가상환경 yml 포함하기
설치방법 기술, 기타 요구사항 기술
---

## 참고 자료
<details>
<summary><strong>참고 자료</strong></summary>
[참고 자료 제목](자료 링크)

</details>

## 업데이트
<details>
<summary><strong></strong></summary>
</details>