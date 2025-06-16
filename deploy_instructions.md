# MS Azure 배포 방법

## Steps
1. Resource Group 생성
2. ai.azure.com(Azure AI Foundry) 접속 후 Azure AI 파운드리 리소스 생성(Region: Sweden Central)
3. 생성한 AI 파운드리 리소스 내에 AI Agent 생성 및 Instructions 작성
4. 파운드리 리소스의 개요(Overview) 내 Azure AI 파운드리 프로젝트 엔드포인트 값을 AZURE_AI_FOUNDRY_ENDPOINT 환경변수로 등록
5. AI Agent의 agent_id 값을 AGENT_ID 환경변수로 등록
6. Kakao API 사용을 위해 개발자 포털에 프로젝트를 생성하고 api key를 획득하여 KAKAO_API_KEY 환경변수로 등록
7. Azure Web Apps 생성
8. Google Cloud Console에 프로젝트를 생성하고 OAuth 동의 화면과 OAuth 클라이언트를 생성 후, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET을 등록
9. GCP의 Google OAuth 클라이언트 생성 단계에서 웹 애플리케이션 등록 시 redirection uri에 Azure Web Apps 생성 시 발급받은 도메인 주소를 기입 후, GOOGLE_REDIRECT_URI 환경변수 등록
10. Azure Web Apps에 소스코드 배포 수행(VSCode Azure App Service 플러그인 활용)
    - .deployment
    - app.py
    - streamlit.sh
11. Azure Web Apps에서 시작 명령(Startup Command)으로 `bash /home/site/wwwroot/streamlit.sh` 기입하여 streamlit.sh가 구동되도록 지정
12. DefaultAzureCredential을 사용하도록 해 두었기 때문에, `az webapp ssh --name <web-app-name> --resource-group <resource-group>`으로 웹서버 접속하여 az login 수행
    - 보안적으로 적합하지 않으므로 가능하다면 Azure portal의 app restrictions 내에 클라이언트 생성 후, AzureClientCredential로 대체 선호(권한 부족으로 위와 같이 수행)
13. 사이트 진입 후 접속 및 기능 테스트 수행