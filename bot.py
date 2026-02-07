import os
import asyncio
from playwright.async_api import async_playwright
from googletrans import Translator
import telegram

# 金庫から情報をもらう
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
X_USER = os.environ['X_USER']
X_PASS = os.environ['X_PASS']

# 監視したいアカウント（例：BBCWorld）
TARGET_USER = "BBCWorld" 

async def main():
    async with async_playwright() as p:
        # ブラウザ起動
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Xにログイン
        await page.goto("https://x.com/i/flow/login")
        await page.wait_for_selector('input[autocomplete="username"]')
        await page.fill('input[autocomplete="username"]', X_USER)
        await page.click('text=Next')
        await page.wait_for_selector('input[name="password"]')
        await page.fill('input[name="password"]', X_PASS)
        await page.click('data-testid=LoginForm_Login_Button')
        
        # ログイン後、ターゲットのページへ
        await page.wait_for_url("https://x.com/home", timeout=60000)
        await page.goto(f"https://x.com/{TARGET_USER}")
        await page.wait_for_selector('[data-testid="tweetText"]')

        # 最新ポストを取得して翻訳
        tweet_text = await page.locator('[data-testid="tweetText"]').first.inner_text()
        translator = Translator()
        translated = translator.translate(tweet_text, dest='ja').text

        # Telegramに送信
        bot = telegram.Bot(token=TOKEN)
        message = f"【{TARGET_USER}】\n\n{translated}\n\n---原文---\n{tweet_text}"
        await bot.send_message(chat_id=CHAT_ID, text=message)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
