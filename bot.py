import os
import asyncio
from playwright.async_api import async_playwright
import telegram

# 金庫(Secrets)から情報を受け取る
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# 監視したいXのアカウントID（例：BBCWorld）
TARGET_USER = "BBCWorld" 

async def main():
    async with async_playwright() as p:
        # ブラウザを起動
        browser = await p.chromium.launch(headless=True)
        # 人間っぽく見せるための設定
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/5.3.36"
        )
        page = await context.new_page()

        # ログインせずに、直接ユーザーのページを見に行く
        print(f"Checking {TARGET_USER}...")
        # 読み込みを安定させるために、少し特殊なURL（mobile版）を使います
        await page.goto(f"https://mobile.x.com/{TARGET_USER}", wait_until="networkidle")
        
        # 画面が表示されるまで少し待つ
        await page.wait_for_timeout(5000)

        # 最新のポストのテキストを探す
        tweet_element = await page.query_selector('[data-testid="tweetText"]')
        
        if tweet_element:
            tweet_text = await tweet_element.inner_text()
            print(f"Found tweet: {tweet_text[:30]}...")

            # Telegramに送信
            bot = telegram.Bot(token=TOKEN)
            message = f"【{TARGET_USER} の最新投稿】\n\n{tweet_text}"
            await bot.send_message(chat_id=CHAT_ID, text=message)
            print("Message sent to Telegram!")
        else:
            # もし取得できなかった場合のメッセージ
            print("Tweet not found. X is blocking guest access.")
            bot = telegram.Bot(token=TOKEN)
            await bot.send_message(chat_id=CHAT_ID, text="ツイートが見つかりませんでした。Xの制限がかかっている可能性があります。")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
