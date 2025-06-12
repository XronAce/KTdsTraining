# KTdsTraining

## MVP Project 목표
모닝 브리핑을 그 날의 일정과 날씨 정보를 곁들어 해주는 AI Agent 개발
### 구현 Step
1. 인프라 준비
   - 리소스 그룹 생성
   - Azure OpenAI 생성
   - Azure Logic Apps 생성(MSN 날씨 Tool 생성 목적)
   - gpt-4o-mini 모델 배포(in Azure OpenAI)
2. 각종 키를 .env 환경변수 등록
3. Streamlit app 개발 착수
   - 채팅 인터페이스
   - 구글 로그인 연동 -> 구글 캘린더 정보 연동 -> 사용자로부터 현재 위치 입력(자동 or 수동) -> AI Agent에게 모닝 브리핑 요청

## MVP Project 평가 주요 요건
### 핵심 기능
#### AI 에이전트 또는 RAG 파이프라인
[사용 기술 스택]
- Azure AI Foundry 기반 AI Agent + Azure Logic Apps 기반 Tool 연동
- Azure OpenAI w/ gpt-4o-mini
#### 사용자 인터페이스
[사용 기술 스택]
- Streamlit
- Google OAuth Login
#### 데이터 소스/지식베이스 (RAG 사용 시) - 미사용

### 기술 스택
- Azure OpenAI Service(gpt-40-mini)
- Azure Logic Apps
- Azure Web App
- Streamlit
- Python

### 배포 대상
- Azure Web App에 Streamlit 기반 앱 배포

### 코드 저장소 및 협업 도구
- GitHub repo로 Git을 활용하여 제출
- README.md에 주제, 설치 방법, 실행 가이드 등 deep step 기재

### 발표 자료
1. 슬라이드 1: 프로젝트 개요
2. 슬라이드 2: 아키텍처 다이어그램
3. 슬라이드 3: 핵심 기술 포인트
4. 슬라이드 4: 라이브 데모 화면 전환
5. 슬라이드 5: 향후 개선 및 확장 계획

### 완성 후 제출
youngwook@outlook.com