# -*- coding: utf-8 -*-

import requests
import bs4
import hashlib
from utils import get_seen_hashes, message_to_hash, summarize_text_with_hf

def get_page_content(url):
    """URL을 입력받아, 웹 페이지의 본문 텍스트만 추출하여 반환하는 함수"""
    print(f"페이지 내용 추출 시도: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        content_area = soup.select_one('.view-content') or soup.select_one('.board_view_content')
        if content_area:
            return content_area.get_text(separator="\n", strip=True)
        print("오류: 본문 영역을 찾을 수 없습니다.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"오류: 페이지 내용을 가져오는 데 실패했습니다 - {e}")
        return None

async def fetch_and_process_news(api_url, seen_file, hf_token):
    """API를 통해 새로운 공지사항을 가져와 처리하고, 보낼 메시지 목록과 새로운 해시를 반환합니다."""
    print("1. 공지사항 API에 접속합니다...")
    try:
        response = requests.post(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"API에 연결할 수 없습니다: {e}")
        return [], []

    print("2. API 응답 HTML을 파싱합니다...")
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    links = soup.select("td.td-subject > a")
    
    print(f"3. 발견된 게시물 링크 수: {len(links)}개")
    if not links:
        print("-> 게시물 링크를 찾지 못했습니다.")
        return [], []

    seen_hashes = get_seen_hashes(seen_file)
    new_hashes = []
    messages_to_send = []

    for link_element in reversed(links):
        title = ' '.join(link_element.text.strip().split())
        link = link_element.get("href")
        
        if not link or not title or "javascript:void(0)" in link:
            continue
        
        try:
            artcl_id = link.split("/")[-2]
            id_hash = message_to_hash(artcl_id)
        except IndexError:
            print(f"경고: 링크 형식 오류로 ID를 추출할 수 없습니다: {link}")
            id_hash = message_to_hash(title)

        if id_hash in seen_hashes:
            continue

        full_link = f"https://www.knou.ac.kr{link}"
        
        print(f"\n4. 처리 중인 게시물: {title}")
        content = get_page_content(full_link)
        summary = summarize_text_with_hf(content, hf_token)
        
        message = (
            f"📌 **{title}**\n\n"
            f"📝 **내용 요약:**\n{summary}\n\n"
            f"🔗 **원문 링크:**\n{full_link}"
        )
        messages_to_send.append(message)
        new_hashes.append(id_hash)

    return messages_to_send, new_hashes
