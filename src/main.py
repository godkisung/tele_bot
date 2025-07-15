# -*- coding: utf-8 -*-

import os
import asyncio
import sys
from crawler import fetch_and_process_news
from telegram_bot import send_telegram_message

# --- 환경 변수 ---
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID_CRAWLER")
SEEN_NOTICE_FILE = os.environ.get("SEEN_NOTICE_FILE", "ID.txt")
HF_TOKEN = os.environ.get("HF_TOKEN")
KNOU_API_URL = "https://www.knou.ac.kr/bbs/knou/51/artclList.do"

async def main():
    """
    메인 실행 함수
    1. 새로운 공지사항을 가져와 처리합니다.
    2. 처리된 메시지를 텔레그램으로 전송합니다.
    """
    if not all([TELEGRAM_API_KEY, TELEGRAM_CHANNEL_ID]):
        print("오류: 필수 환경 변수(TELEGRAM_API_KEY, TELEGRAM_CHANNEL_ID_CRAWLER)가 설정되지 않았습니다.")
        sys.exit(1)

    print("새로운 공지사항 확인을 시작합니다...")
    
    # 뉴스를 가져오고 처리하는 부분
    messages_to_send, new_hashes = await fetch_and_process_news(KNOU_API_URL, SEEN_NOTICE_FILE, HF_TOKEN)

    if not messages_to_send:
        print("새로운 공지사항이 없습니다.")
        return

    print(f"총 {len(messages_to_send)}개의 새로운 공지사항을 텔레그램으로 전송합니다.")

    # 텔레그램 메시지 전송
    await send_telegram_message(
        TELEGRAM_API_KEY,
        TELEGRAM_CHANNEL_ID,
        messages_to_send,
        new_hashes,
        SEEN_NOTICE_FILE
    )

    print("모든 작업이 완료되었습니다.")

if __name__ == '__main__':
    # 윈도우 환경에서 cp949 인코딩 오류 방지
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        
    asyncio.run(main())
