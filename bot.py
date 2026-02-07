import os
import asyncio
from playwright.async_api import async_playwright
import telegram

# 金庫(Secrets)から情報を受け取る
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# ニュースサイトのURL
URL = "https://www.newsnow.co.uk/h/World+News/Middle+East/Iran/US~Iran?type=ln"

async def main():
    async with async_playwright() as p:
        # ブラウザを起動
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/5.3.36"
        )
        page = await context.new_page()

        print(f"Connecting to {URL}...")
        try:
            # サイトにアクセス
            await page.goto(URL, wait_until="networkidle", timeout=60000)
            
            # 最新のニュース記事のタイトルを取得
            # NewsNowのタイトルは 'hll' というクラス名のリンクに入っていることが多いです
            title_element = await page.query_selector('.hll')
            
            if title_element:
                title_text = await title_element.inner_text()
                print(f"Found News: {title_text}")

                # Telegramに送信
                bot = telegram.Bot(token=TOKEN)
                message = f"【US-Iran News Update】\n\n{title_text}"
                await bot.send_message(chat_id=CHAT_ID, text=message)
                print("Successfully sent to Telegram!")
            else:
                print("Could not find any news titles.")
                
        except Exception as e:
            print(f"Error: {e}")
            bot = telegram.Bot(token=TOKEN)
            await bot.send_message(chat_id=CHAT_ID, text=f"Error occurred: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
