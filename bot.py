import os
import asyncio
from playwright.async_api import async_playwright
import telegram

# 金庫(Secrets)から情報を受け取る
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# NewsNowのターゲットURL
URL = "https://www.newsnow.co.uk/h/World+News/Middle+East/Iran/US~Iran?type=ln"

async def main():
    async with async_playwright() as p:
        # ブラウザを起動
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/5.3.36"
        )
        page = await context.new_page()

        print(f"Connecting to NewsNow...")
        try:
            # ページへ移動
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
            # ニュース記事のカードが表示されるまで待つ
            await page.wait_for_selector('.article-card', timeout=15000)

            # 最新のタイトルと時間を取得（調査してくれたセレクターを使用）
            headline_element = await page.query_selector('.article-card__headline')
            time_element = await page.query_selector('.article-card__time')

            if headline_element:
                headline_text = await headline_element.inner_text()
                link_url = await headline_element.get_attribute('href')
                time_text = await time_element.inner_text() if time_element else "Just now"

                print(f"Latest News Found: {headline_text}")

                # Telegramに送信（英語のまま）
                bot = telegram.Bot(token=TOKEN)
                message = f"📰 【US-Iran News Update】\nTime: {time_text}\n\n{headline_text}\n\nLink: {link_url}"
                await bot.send_message(chat_id=CHAT_ID, text=message)
                print("Successfully sent to Telegram!")
            else:
                print("Could not find the headline.")

        except Exception as e:
            print(f"Error occurred: {e}")
            # エラー時も通知を送る
            bot = telegram.Bot(token=TOKEN)
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Script Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
