# knou_crawler.py 파일

import asyncio
import telegram
import os  # 'os' 모듈 import 추가

# GitHub Actions가 설정해준 환경 변수를 읽어서 변수에 할당합니다.
# 👇 이 코드를 파일 상단(함수 정의 전)에 추가하세요.
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")


# 기존 함수 코드는 그대로 둡니다.
async def fetch_and_send_news(channel_id):
    # 이제 이 라인에서 TELEGRAM_API_KEY 변수는 정상적인 값을 가집니다.
    bot = telegram.Bot(TELEGRAM_API_KEY)
    
    # ... (이하 생략) ...