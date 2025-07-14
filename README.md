# KNOU 공지사항 텔레그램 봇

한국방송통신대학교(KNOU)의 새로운 공지사항을 텔레그램 채널로 보내주는 봇입니다.

## 주요 기능

- 지정된 웹사이트에서 공지사항을 주기적으로 크롤링합니다.
- 이미 보낸 공지사항은 중복해서 보내지 않습니다.
- GitHub Actions를 통해 4시간마다 자동으로 실행됩니다.

## 프로젝트 구조

```
telebot/
├── .github/workflows/crawler.yml  # GitHub Actions 워크플로우
├── teleapi_key/
│   └── .env                       # API 키, 채널 ID 등 환경 변수
├── crawler.py                     # 크롤러 실행 스크립트
├── knou_crawler.py                # 실제 크롤링 로직
├── requirements.txt               # 필요한 파이썬 라이브러리
├── ID.txt                         # 보낸 공지사항 해시 저장 파일
└── README.md                      # 프로젝트 설명 파일
```

## 설정 방법

1.  **저장소 복제:**

    ```bash
    git clone https://github.com/your-username/telebot.git
    cd telebot
    ```

2.  **필요한 라이브러리 설치:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **환경 변수 설정:**

    `teleapi_key` 폴더 안에 `.env` 파일을 생성하고 아래 내용을 채워주세요.

    ```
    tele_api="YOUR_TELEGRAM_BOT_API_KEY"
    TELEGRAM_CHANNEL_ID_CRAWLER="YOUR_TELEGRAM_CHANNEL_ID"
    KNOU_URL="https://www.knou.ac.kr/knou/561/subview.do?epTicket=INV"
    SEEN_NOTICE_FILE="ID.txt"
    ```

## 실행

-   **로컬 테스트:**

    ```bash
    python crawler.py
    ```

-   **자동 실행:**

    이 프로젝트는 GitHub Actions에 의해 4시간마다 자동으로 실행되도록 설정되어 있습니다. (`.github/workflows/crawler.yml`)