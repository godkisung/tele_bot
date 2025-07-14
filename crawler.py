# -*- coding: utf-8 -*-

import asyncio
import os
from knou_crawler import fetch_and_send_news

if __name__ == "__main__":
    print("크롤러 실행...")
    
    # YAML 파일에서 설정한 환경 변수를 가져옵니다.
    channel_id = os.environ.get("TELEGRAM_CHANNEL_ID_CRAWLER")
    
    # 크롤러 함수를 실행합니다.
    asyncio.run(fetch_and_send_news(channel_id))
    
    print("실행 완료.")
