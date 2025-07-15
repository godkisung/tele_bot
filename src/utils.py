# -*- coding: utf-8 -*-

import hashlib
import requests

def get_seen_hashes(file_path):
    """이미 보낸 공지사항의 해시 목록을 파일에서 읽어옵니다."""
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        print(f"'{file_path}' 파일이 없어 새로 생성합니다.")
        return set()

def add_seen_hashes(hashes, file_path):
    """새로운 공지사항의 해시를 파일에 추가합니다."""
    with open(file_path, "a", encoding='utf-8') as f:
        for h in hashes:
            f.write(h + "\n")

def message_to_hash(message):
    """메시지 내용을 SHA256 해시로 변환합니다."""
    return hashlib.sha256(message.encode('utf-8')).hexdigest()

def summarize_text_with_hf(text_to_summarize, hf_token):
    """Hugging Face API를 이용해 텍스트를 요약하는 함수"""
    import time
    if not hf_token:
        return "(Hugging Face 토큰이 없어 요약을 건너뜁니다.)"
    if not text_to_summarize or len(text_to_summarize.strip()) < 50:
        return "요약할 내용이 충분하지 않습니다."

    print("Hugging Face API로 요약 요청 중...")
    API_URL = "https://api-inference.huggingface.co/models/eenzeenee/t5-base-korean-summarization"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": text_to_summarize, "parameters": {"max_length": 256, "min_length": 30, "early_stopping": True}}
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, headers=headers, json=payload, timeout=300)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Hugging Face API 요청 시간: {duration:.4f}초")

        if response.status_code == 200:
            return response.json()[0]['summary_text']
        else:
            error_message = response.json().get('error', response.text)
            print(f"API 오류: {response.status_code}, {error_message}")
            return f"요약 생성에 실패했습니다 (API 오류: {error_message})"
    except requests.exceptions.RequestException as e:
        print(f"API 요청 실패: {e}")
        return "요약 생성에 실패했습니다 (네트워크 오류)."
