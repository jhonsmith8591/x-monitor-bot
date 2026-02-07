import os
import asyncio
from playwright.async_api import async_playwright
import telegram

# 金庫(Secrets)から情報を受け取る
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# ターゲットURL（NewsNowのUS-Iranニュース）
URL = "https://www.newsnow.co.uk/h/World+News/Middle+East/Iran/US~Iran?type=ln"

async def main():
    async with async_playwright() as p:
        # ブラウザを起動（ログイン不要なのでこれだけでOK）
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"Connecting to NewsNow...")
        try:
            # ページを開く
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
            # ニュースのカードが出るまで待つ
            await page.wait_for_selector('.article-card', timeout=15000)

            # 最新のタイトル（.article-card__headline）を取得
            headline_element = await page.query_selector('.article-card__headline')

            if headline_element:
                headline_text = await headline_element.inner_text()
                # 記事へのリンクもついでに取得
                link_url = await headline_element.get_attribute('href')

                print(f"Found: {headline_text}")

                # Telegramに送信
                bot = telegram.Bot(token=TOKEN)
                message = f"【Latest News】\n\n{headline_text}\n\nLink: {link_url}"
                await bot.send_message(chat_id=CHAT_ID, text=message)
                print("Sent to Telegram!")
            else:
                print("Headline not found.")

        except Exception as e:
            print(f"Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
