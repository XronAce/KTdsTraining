# 일정 자동 분석 및 날씨 데이터 기반 모닝 브리핑 AI Agent

## 애플리케이션 준비 및 배포 환경 구축 순서
1. [Azure Portal](https://portal.azure.com)에 접속합니다.
2. 리소스 그룹을 생성합니다. (예: donggi-RG)
3. [Azure AI Foundry](https://ai.azure.com)에서 Azure AI 파운드리 리소스를 생성합니다.
4. 생성한 Azure AI 파운드리 리소스에서 '에이전트'를 클릭하고, gpt-4o-mini를 배포합니다.
5. 생성된 에이전트의 설정에서 '지침'에 [system_prompt_for_ai_agent.txt](./MorningBriefingApp/system_prompt_for_ai_agent.txt) 내에 기술되어 잇는 지침을 복사하여 입력합니다.
6. 리소스 그룹으로 돌아가서, Azure Web App을 생성합니다.
7. 생성된 web app 리소스로 이동하여, 좌측의 설정 > Identity > System assigned 탭에서 status를 on으로 바꾸고 저장합니다. 이는 web app이 ManagedIdentityCredential을 통해 Azure AI Foundry 리소스를 접근할 수 있도록 하기 위함입니다.
8. web app의 설정 > 구성(Configuration)에 진입하여 시작 명령에 `bash /home/site/wwwroot/streamlit.sh`를 기입합니다.
9. Azure Portal에서 리소스 그룹에 생성된 Azure AI 파운드리 리소스로 진입하여 좌측의 Access control(IAM) 메뉴에 진입합니다.
10. '+ Add' 버튼을 통해 role을 다음과 같이 추가합니다: Job function roles: Azure AI User, Members에는 생성한 Azure Web App을 선택하여 IAM 역할을 부여합니다. 이렇게 하여 web app이 ManagedIdentityCredential을 통해 AI 에이전트를 호출할 수 있는 권한을 최종적으로 얻게 됩니다.
11. 리소스 그룹으로 돌아가서, Azure Database for PostgreSQL flexible server를 생성합니다. 프로덕션이 아닌 개발로 선택하고, 외부에서 postgresql 계정만으로 접근이 가능하도록 옵션을 선택합니다. (추후 보안을 위해 프로덕션 레벨에서는 네트워크 통제 및 액세스 제어를 엄격하게 하는 것이 좋습니다.)
12. Google OAuth 로그인 구축을 위해, [Google Cloud Console](https://console.cloud.google.com)에서 프로젝트를 생성하고 OAuth 동의 화면 및 OAuth 클라이언트를 생성합니다. 이때 redirection uri의 경우 web app public 주소를 기입합니다.
13. GPS 미사용 시 사용자가 입력한 주소 기반으로 좌표를 추출할 수 있도록, [Kakao Developers](https://developers.kakao.com/)에서 애플리케이션을 생성하고 REST API 키를 취득합니다.
14. [Fernet Keygen](https://fernetkeygen.com/)에서 사용자 정보 암호화에 사용할 키를 생성합니다.
15. 모든 리소스가 준비되면, MorningBriefingApp 폴더 하위에 `.env` 파일을 다음과 같이 생성합니다:
    ```sh
    AZURE_AI_FOUNDRY_ENDPOINT="<Azure_AI_Foundry_리소스_내에서_Azure_AI_파운드리_엔드포인트>"
    AGENT_ID="<Azure_AI_Foundry_리소스_내에서_만들어둔_에이전트의_agent_id>"
    KAKAO_API_KEY="<Kakao_developers에서_취득한_REST_API_키>"
    GOOGLE_CLIENT_ID="<Google_Cloud_Console에서_생성한_OAuth_클라이언트_ID>"
    GOOGLE_CLIENT_SECRET="<Google_Cloud_Console에서_생성한_OAuth_클라이언트_secret키>"
    GOOGLE_REDIRECT_URI="<Google_Cloud_Console에서_기입한_redirection_uri>"
    DATABASE_URL="postgresql+psycopg2://<DB_계정_ID>:<DB_비밀번호>@<Azure_Postgresql_host주소>:<포트번호>/<DB_데이터베이스_이름>"
    ENCRYPTION_KEY="<Fernet_Keygen에서_생성한_암호키>"
    ```
16. [MorningBriefingApp](./MorningBriefingApp) 폴더 전체를 생성해둔 web app에 배포합니다.

## 프로젝트에 사용된 외부 API 목록
| API 이름                                                                                            | 목적                            |
|---------------------------------------------------------------------------------------------------|-------------------------------|
| [Kakao Developer](https://developers.kakao.com) REST API                                          | 카카오맵 주소 및 위치 정보(위도, 경도 추출목적)  |
| [Google Calendar API](https://developers.google.com/workspace/calendar/api/guides/overview?hl=ko) | Google 캘린더 이벤트 데이터 조회         |
| [Open Meteo](https://open-meteo.com)                                                              | 위도, 경도 기반 날씨 데이터 조회           |
| [KT Groupmail CalDAV 연동 API](https://groupmail.kt.co.kr:1985/dav/<username>/calendar/)            | 사내 캘린더 이벤트 데이터 조회             |

## .env 샘플 예시
```sh 
AZURE_AI_FOUNDRY_ENDPOINT="https://my-azure-ai-foundry-resource.services.ai.azure.com/api/projects/my-project"
AGENT_ID="asst_abcdefghijklmnopqrstuvwxyz"
KAKAO_API_KEY="abcdefghijklmnopqrstuvwxyz1234567890"
GOOGLE_CLIENT_ID="1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-abcdefghijklmnopqrstuvwxyz1234567890"
GOOGLE_REDIRECT_URI="https://morning-briefing.azurewebsites.net"
DATABASE_URL="postgresql+psycopg2://my-account-name:my-account-password@my-azure-db.postgres.database.azure.com:5432/postgres"
ENCRYPTION_KEY="abcdefghijklmnopqrstuvwxyz1234567890"
```