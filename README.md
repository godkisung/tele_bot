# KNOU 공지사항 텔레그램 봇

이 프로젝트는 한국방송통신대학교(KNOU)의 새로운 공지사항을 주기적으로 확인하여, 지정된 텔레그램 채널로 요약과 함께 알림을 보내는 봇입니다.

## 주요 기능

- **주기적인 공지사항 확인**: GitHub Actions를 통해 4시간마다 자동으로 새로운 공지사항을 확인합니다.
- **AI 기반 내용 요약**: Hugging Face의 요약 모델을 사용하여 공지사항 본문을 자동으로 요약합니다.
- **텔레그램 알림**: 새로운 공지사항이 올라오면, 설정된 텔레그램 채널로 제목, 요약, 원문 링크를 포함한 메시지를 전송합니다.
- **중복 알림 방지**: 이미 보낸 공지사항은 `ID.txt` 파일에 기록하여 중복으로 알림을 보내지 않습니다.

## 프로젝트 구조

```
tele_bot/
├── .github/workflows/         # GitHub Actions 워크플로우
│   └── crawler.yml
├── src/                         # 파이썬 소스 코드
│   ├── __init__.py
│   ├── main.py                # 메인 실행 파일
│   ├── crawler.py             # 웹 크롤링 및 데이터 처리
│   ├── telegram_bot.py        # 텔레그램 메시지 전송
│   └── utils.py               # 보조 함수 (해시, API 요청 등)
├── .gitignore
├── ID.txt                     # 이미 보낸 공지사항 ID 기록
├── requirements.txt           # 파이썬 의존성 패키지
└── README.md                  # 프로젝트 설명 파일
```

## 실행 방법

### 1. 로컬 환경에서 실행

1.  **저장소 복제**:
    ```bash
    git clone https://github.com/your-username/tele_bot.git
    cd tele_bot
    ```

2.  **의존성 패키지 설치**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **환경 변수 설정**:
    `.env` 파일을 생성하고 아래 내용을 채웁니다.
    ```
    TELEGRAM_API_KEY="your_telegram_api_key"
    TELEGRAM_CHANNEL_ID_CRAWLER="@your_telegram_channel_id"
    HF_TOKEN="your_hugging_face_api_token"
    ```

4.  **크롤러 실행**:
    ```bash
    python src/main.py
    ```

### 2. GitHub Actions를 통한 자동 실행

1.  **저장소 Fork 또는 복제**:
    이 저장소를 자신의 GitHub 계정으로 Fork하거나 복제합니다.

2.  **GitHub Secrets 설정**:
    -   `Settings` > `Secrets and variables` > `Actions` 로 이동하여 다음 Secret들을 추가합니다.
        -   `TELEGRAM_API_KEY`: 텔레그램 봇의 API 키
        -   `CHAT_ID`: 알림을 보낼 텔레그램 채널의 ID (예: `@my_channel`)
        -   `HF_TOKEN`: Hugging Face API 토큰

3.  **워크플로우 활성화**:
    -   `.github/workflows/crawler.yml` 파일의 스케줄(`cron`)을 원하는 주기로 설정할 수 있습니다. (기본: 4시간마다)
    -   `main` 브랜치에 코드를 푸시하면 워크플로우가 자동으로 실행됩니다.
    -   GitHub Actions 탭에서 `Run Crawler and Lint` 워크플로우를 수동으로 실행할 수도 있습니다.

## 의존성

-   `beautifulsoup4`: HTML 파싱
-   `python-dotenv`: 환경 변수 관리
-   `python-telegram-bot`: 텔레그램 API 연동
-   `requests`: HTTP 요청
-   `schedule`: 스케줄링 (로컬 실행 시)
-   `ruff`: 코드 린터

자세한 내용은 `requirements.txt` 파일을 참고하세요.
