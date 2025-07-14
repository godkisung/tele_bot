# -*- coding: utf-8 -*-

import asyncio
import os
# from dotenv import load_dotenv  <- 이 줄 삭제
from knou_crawler import fetch_and_send_news

# .env 파일에서 환경 변수 로드  <- 이 부분 전체 삭제
# env_path = os.path.join(os.path.dirname(__file__), 'teleapi_key/.env')
# load_dotenv(dotenv_path=env_path)

if __name__ == "__main__":
    print("크롤러 실행...")
    # os.environ.get() 만 사용하면 YAML의 env: 와 바로 연결됩니다.
    TELEGRAM_CHANNEL_ID_CRAWLER = os.environ.get("TELEGRAM_CHANNEL_ID_CRAWLER")
    asyncio.run(fetch_and_send_news(TELEGRAM_CHANNEL_ID_CRAWLER))
    print("실행 완료.")