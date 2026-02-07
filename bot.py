import os
import asyncio
from playwright.async_api import async_playwright
import telegram

# 金庫(Secrets)から情報を受け取る
TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# 監視したいXのアカウントID（例：BBCWorld）
# ※ログインしないため、公開設定のアカウントのみ可能です
TARGET_USER = "BBCWorld" 

async def main():
    async with async_playwright() as p:
        # ブラウザを起動
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/5.3.36"
        )
        page = await context.new_page()

        # ターゲットのページへ直接移動（nitterなどのミラーサイトを使うとより安定しますが、まずは本家で）
        print(f"Checking {TARGET_USER}...")
        await page.goto(f"https://x.com/{TARGET_USER}", wait_until="networkidle")
        
        # 読み込み待ち
        await page.wait_for_timeout(5000)

        # 最新ポストのテキストを探す
        # ログインしていない場合、セレクターが異なることがあるため複数の候補を試す
        tweet_element = await page.query_selector('[data-testid="tweetText"]')
        
        if tweet_element:
            tweet_text = await tweet_element.inner_text()
            print(f"Found tweet: {tweet_text[:30]}...")

            # Telegramに送信（今回は翻訳を通さず、まずは届くかテスト！）
            bot = telegram.Bot(token=TOKEN)
            message = f"【{TARGET_USER} の最新投稿】\n\n{tweet_text}"
            await bot.send_message(chat_id=CHAT_ID, text=message)
            print("Message sent!")
        else:
            print("Tweet not found. X might be blocking non-logged in users.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
