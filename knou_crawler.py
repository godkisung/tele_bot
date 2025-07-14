# -*- coding: utf-8 -*-

import os
import telegram
import asyncio
import bs4
import requests
import hashlib
import sys

# --- 환경 변수 읽기 ---
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
# 중요: GitHub Actions의 yml 파일에서 KNOU_URL 값을 새 주소로 변경해야 합니다.
# https://www.knou.ac.kr/knou/561/subview.do
KNOU_URL = os.environ.get("KNOU_URL")
SEEN_NOTICE_FILE = os.environ.get("SEEN_NOTICE_FILE")
HF_TOKEN = os.environ.get("HF_TOKEN")
# --- 환경 변수 읽기 끝 ---

def get_page_content(url):
    """URL을 입력받아, 웹 페이지의 본문 텍스트만 추출하여 반환하는 함수"""
    print(f"페이지 내용 추출 시도: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        
        # 변경된 사이트 구조에 맞춰 본문 선택자를 수정합니다.
        content_area = soup.select_one('.board_view_content')

        if content_area:
            return content_area.get_text(separator="\n", strip=True)
        else:
            print("오류: 본문 영역('.board_view_content')을 찾을 수 없습니다.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지 내용을 가져오는 데 실패했습니다 - {e}")
        return None

def summarize_text_with_hf(text_to_summarize):
    """Hugging Face API를 이용해 텍스트를 요약하는 함수"""
    if not text_to_summarize or len(text_to_summarize.strip()) < 50:
        return "요약할 내용이 충분하지 않습니다."

    print("Hugging Face API로 요약 요청 중...")
    API_URL = "https://api-inference.huggingface.co/models/eenzeenee/t5-base-korean-summarization"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    payload = {
        "inputs": text_to_summarize,
        "parameters": {"max_length": 256, "min_length": 50}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            return response.json()[0]['summary_text']
        else:
            print(f"API 오류: {response.status_code}, {response.text}")
            return "요약 생성에 실패했습니다 (API 오류)."
    except requests.exceptions.RequestException as e:
        print(f"API 요청 실패: {e}")
        return "요약 생성에 실패했습니다 (네트워크 오류)."

def get_seen_hashes():
    """이미 보낸 공지사항의 해시 목록을 파일에서 읽어옵니다."""
    if not SEEN_NOTICE_FILE: return set()
    try:
        with open(SEEN_NOTICE_FILE, "r", encoding='utf-8') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def add_seen_hashes(hashes):
    """새로운 공지사항의 해시를 파일에 추가합니다."""
    if not SEEN_NOTICE_FILE: return
    with open(SEEN_NOTICE_FILE, "a", encoding='utf-8') as f:
        for h in hashes:
            f.write(h + "\n")

def message_to_hash(message):
    """메시지 내용을 SHA256 해시로 변환합니다."""
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

async def fetch_and_send_news(channel_id):
    """웹사이트에서 새로운 공지사항을 가져와 요약 후 텔레그램으로 전송합니다."""
    if not all([TELEGRAM_API_KEY, KNOU_URL, channel_id, HF_TOKEN]):
        print("오류: 필수 환경 변수가 설정되지 않았습니다.")
        return

    bot = telegram.Bot(TELEGRAM_API_KEY)
    
    print("1. 공지사항 목록 페이지에 접속합니다...")
    try:
        response = requests.get(KNOU_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"웹사이트에 연결할 수 없습니다: {e}")
        return

    print("2. 목록 페이지 HTML을 파싱합니다...")
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    
    # 변경된 사이트 구조에 맞춰 게시물 링크 선택자를 수정합니다.
    links = soup.select("td.subject > a")
    
    print(f"3. 발견된 게시물 링크 수: {len(links)}개")
    if not links:
        print("-> 게시물 링크를 찾지 못했습니다. CSS 선택자('td.subject > a')를 확인하세요.")

    seen_hashes = get_seen_hashes()
    new_hashes = []

    for link_element in reversed(links): 
        parent_tr = link_element.find_parent("tr")
        if "notice" in parent_tr.get("class", []):
            continue

        # strong 태그 등 다른 태그가 있을 수 있으므로 text 속성으로 직접 가져옵니다.
        title = link_element.text.strip()
        link = link_element.get("href")
        
        if not link or not title:
            continue
        
        print(f"\n4. 처리 중인 게시물: {title}")

        title_hash = message_to_hash(title)
        if title_hash in seen_hashes:
            print("-> 이미 보낸 게시물입니다. 건너뜁니다.")
            continue

        print("-> 새로운 게시물입니다. 요약을 시작합니다.")
        # 링크가 전체 주소가 아닐 수 있으므로, 도메인을 붙여줍니다.
        full_link = f"https://www.knou.ac.kr{link}"
        
        content = get_page_content(full_link)
        
        if content:
            summary = summarize_text_with_hf(content)
        else:
            summary = "본문 내용을 가져올 수 없어 요약에 실패했습니다."
        
        message = (
            f"📌 **{title}**\n\n"
            f"📝 **내용 요약:**\n{summary}\n\n"
            f"🔗 **원문 링크:**\n{full_link}"
        )
        
        print("5. 텔레그램 메시지 전송을 시도합니다...")
        try:
            await bot.send_message(chat_id=channel_id, text=message, parse_mode='Markdown')
            print("-> 메시지 전송 성공!")
            new_hashes.append(title_hash)
        except telegram.error.TelegramError as e:
            print(f"-> 텔레그램 메시지 전송 실패: {e}")

    print("\n6. 게시물 루프 처리가 모두 완료되었습니다.")
    if new_hashes:
        add_seen_hashes(new_hashes)
        print(f"-> {len(new_hashes)}개의 새 해시를 ID.txt에 저장했습니다.")
    else:
        print("-> 새로 보낸 메시지가 없어 ID.txt를 업데이트하지 않습니다.")
