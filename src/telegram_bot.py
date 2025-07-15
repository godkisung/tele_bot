# -*- coding: utf-8 -*-

import telegram
import asyncio
from utils import add_seen_hashes

async def send_telegram_message(api_key, channel_id, messages, new_hashes, seen_file):
    """텔레그램으로 메시지를 전송하고, 성공 시 해시를 파일에 저장합니다."""
    bot = telegram.Bot(api_key)
    
    print("5. 텔레그램 메시지 전송을 시도합니다...")
    sent_hashes = []
    for i, message in enumerate(messages):
        try:
            await bot.send_message(chat_id=channel_id, text=message, parse_mode='Markdown')
            print(f"-> 메시지 전송 성공! ({i+1}/{len(messages)})")
            sent_hashes.append(new_hashes[i])
            await asyncio.sleep(1)  # 텔레그램 API 과부하 방지
        except telegram.error.TelegramError as e:
            print(f"-> 텔레그램 메시지 전송 실패: {e}")

    print("\n6. 게시물 루프 처리가 모두 완료되었습니다.")
    if sent_hashes:
        add_seen_hashes(sent_hashes, seen_file)
        print(f"-> {len(sent_hashes)}개의 새 해시를 '{seen_file}'에 저장했습니다.")
    else:
        print("-> 새로 보낸 메시지가 없어 해시 파일을 업데이트하지 않습니다.")

