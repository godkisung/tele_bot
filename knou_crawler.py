# -*- coding: utf-8 -*-

import os
import telegram
import asyncio
import bs4
import requests
import hashlib
import sys
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
env_path = os.path.join(os.path.dirname(__file__), 'teleapi_key/.env')
load_dotenv(dotenv_path=env_path)

# 텔레그램 봇 토큰
TELEGRAM_API_KEY = os.environ.get("tele_api")
KNOU_URL = os.environ.get("KNOU_URL")
SEEN_NOTICE_FILE = os.environ.get("SEEN_NOTICE_FILE")

def get_seen_hashes():
    """이미 보낸 공지사항의 해시 목록을 파일에서 읽어옵니다."""
    try:
        with open(SEEN_NOTICE_FILE, "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def add_seen_hashes(hashes):
    """새로운 공지사항의 해시를 파일에 추가합니다."""
    with open(SEEN_NOTICE_FILE, "a") as f:
        for h in hashes:
            f.write(h + "\n")

def message_to_hash(message):
    """메시지 내용을 SHA256 해시로 변환합니다."""
    return hashlib.sha256(message.encode()).hexdigest()

import sys

async def fetch_and_send_news(channel_id):
    """웹사이트에서 새로운 공지사항을 가져와 텔레그램으로 전송합니다."""
    sys.stdout.reconfigure(encoding='utf-8')
    bot = telegram.Bot(TELEGRAM_API_KEY)
    response = requests.get(KNOU_URL)

    soup = bs4.BeautifulSoup(response.text, "html.parser")
    links = soup.select("td.td-subject > a")

    seen_hashes = get_seen_hashes()
    new_hashes = []

    for link_element in links:
        parent_tr = link_element.find_parent("tr")
        if "notice" in parent_tr.get("class", []):
            continue

        span_element = link_element.select_one("span")
        if span_element:
            span_element.extract()

        link = link_element.get("href")
        title = link_element.text.strip().replace("\n", "").replace("  ", " ")
        
        if not link:
            continue

        full_link = f"https://www.knou.ac.kr{link}"
        message = f"📌 {title} \n 🔗 링크: {full_link}"
        message_hash = message_to_hash(message)

        if message_hash not in seen_hashes:
            print(f"새 공지: {message}")
            try:
                await bot.send_message(chat_id=channel_id, text=message)
                new_hashes.append(message_hash)
            except telegram.error.TelegramError as e:
                print(f"텔레그램 메시지 전송 실패: {e}")

    if new_hashes:
        add_seen_hashes(new_hashes)
