import os
import telegram
import asyncio
from dotenv import load_dotenv
import bs4
import requests


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
  
    
    for link_element in links:
        # 부모 <tr> 태그 가져오기
        parent_tr = link_element.find_parent("tr")
        
        # "notice" 제외
        if "notice" in parent_tr.get("class", []):
            continue
        
        span_element = link_element.select_one("span")
        if span_element:
            span_element.extract()

        # 링크와 제목 추출
        link = link_element["href"] if link_element.has_attr("href") else None
        title = link_element.text.strip().replace("\n", "").replace("  ", " ")

        # "전공"과 "신설" 붙이기
        combined = f"📌 {title} \n 🔗 링크: https://www.knou.ac.kr{link}"
        print(combined)
        
        await bot.send_message(chat_id = "-4595812781", text = combined)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())