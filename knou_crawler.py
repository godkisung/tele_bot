# -*- coding: utf-8 -*-

import os
import telegram
import asyncio
import bs4
import requests
import hashlib
import sys

# --- 환경 변수 읽기 ---
# GitHub Actions의 env: 블록에서 설정한 변수들을 직접 읽어옵니다.
# dotenv 라이브러리는 더 이상 필요하지 않습니다.
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
KNOU_URL = os.environ.get("KNOU_URL")
SEEN_NOTICE_FILE = os.environ.get("SEEN_NOTICE_FILE")
# --- 환경 변수 읽기 끝 ---

def get_seen_hashes():
    """이미 보낸 공지사항의 해시 목록을 파일에서 읽어옵니다."""
    # SEEN_NOTICE_FILE 변수가 None이면 오류가 발생하므로 확인합니다.
    if not SEEN_NOTICE_FILE:
        print("오류: SEEN_NOTICE_FILE 환경 변수가 설정되지 않았습니다.")
        return set()
    try:
        with open(SEEN_NOTICE_FILE, "r", encoding='utf-8') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def add_seen_hashes(hashes):
    """새로운 공지사항의 해시를 파일에 추가합니다."""
    if not SEEN_NOTICE_FILE:
        print("오류: SEEN_NOTICE_FILE 환경 변수가 설정되지 않았습니다.")
        return
    with open(SEEN_NOTICE_FILE, "a", encoding='utf-8') as f:
        for h in hashes:
            f.write(h + "\n")

def message_to_hash(message):
    """메시지 내용을 SHA256 해시로 변환합니다."""
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

async def fetch_and_send_news(channel_id):
    """웹사이트에서 새로운 공지사항을 가져와 텔레그램으로 전송합니다."""
    # API 키나 URL이 없는 경우 함수를 중단합니다.
    if not TELEGRAM_API_KEY:
        print("오류: TELEGRAM_API_KEY 환경 변수가 설정되지 않았습니다. GitHub Secrets를 확인하세요.")
        return
    if not KNOU_URL:
        print("오류: KNOU_URL 환경 변수가 설정되지 않았습니다.")
        return
    if not channel_id:
        print("오류: TELEGRAM_CHANNEL_ID_CRAWLER 환경 변수가 설정되지 않았습니다. GitHub Secrets를 확인하세요.")
        return

    sys.stdout.reconfigure(encoding='utf-8')
    bot = telegram.Bot(TELEGRAM_API_KEY)
    
    try:
        response = requests.get(KNOU_URL)
        response.raise_for_status() # HTTP 오류 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        print(f"웹사이트에 연결할 수 없습니다: {e}")
        return

    soup = bs4.BeautifulSoup(response.text, "html.parser")
    links = soup.select("td.td-subject > a")

    seen_hashes = get_seen_hashes()
    new_hashes = []

    # 오래된 공지부터 순서대로 보내기 위해 reversed() 사용
    for link_element in reversed(links): 
        parent_tr = link_element.find_parent("tr")
        # 'notice' 클래스가 있는 tr은 고정 공지이므로 건너뜁니다.
        if "notice" in parent_tr.get("class", []):
            continue

        # 제목 안의 불필요한 span 태그(예: '새글') 제거
        span_element = link_element.select_one("span")
        if span_element:
            span_element.extract()

        link = link_element.get("href")
        title = link_element.text.strip().replace("\n", "").replace("  ", " ")
        
        if not link or not title:
            continue

        full_link = f"https://www.knou.ac.kr{link}"
        message = f"📌 {title}\n🔗 링크: {full_link}"
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
        print(f"{len(new_hashes)}개의 새 공지를 전송했습니다.")
    else:
        print("새로운 공지가 없습니다.")
