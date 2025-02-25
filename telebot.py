import os
import telegram
import asyncio
from dotenv import load_dotenv
import bs4
import requests
import time
import schedule 


# bot api 호출
env_path = os.path.join(os.path.dirname(__file__),"teleapi_key/.env")
load_dotenv(env_path)

# 메인 로직
async def main():
    token = os.getenv("tele_api")
    bot = telegram.Bot(token)
    url = "https://www.knou.ac.kr/knou/561/subview.do?epTicket=INV" # 주소 선언
    response = requests.get(url) # 주소 호출
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    links = soup.select("td.td-subject > a ")
  
    
    seen_notice = "ID.txt"
        
    try:
        with open(seen_notice,"r") as f:
            seen_notices = set(f.read().splitlines())
            
    except FileNotFoundError:
        seen_notices = set() # 빈 파일 예외 처리
    
    new_ids = []
        
    
    for link_element in links:
        # tr 탐색
        parent_tr = link_element.find_parent("tr")
        
        # "notice" 제외
        if "notice" in parent_tr.get("class", []):
            continue
        
        span_element = link_element.select_one("span")
        if span_element:
            span_element.extract()

        # 링크와 제목 추출``
        link = link_element["href"] if link_element.has_attr("href") else None
        notice_id = link.split("/")[-2]
        if notice_id in seen_notices:
            continue
        title = link_element.text.strip().replace("\n", "").replace("  ", " ")
    
        # "전공"과 "신설" 붙이기
        combined = f"📌 {title} \n 🔗 링크: https://www.knou.ac.kr{link}"
        print(combined)
        new_ids.append(notice_id)
        
        await bot.send_message(chat_id = "-4595812781", text = combined)
        
    with open(seen_notice,"a") as f:
        for new_id in new_ids:
            f.write(new_id + "\n")

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())