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
        page = await browser.new_page()

        # Nitterというサイトを経由してXの投稿を取得（ログイン不要で確実）
        # いくつかあるミラーサイトの一つを使います
        nitter_url = f"https://nitter.net/{TARGET_USER}"
        
        print(f"Connecting to {nitter_url}...")
        try:
            await page.goto(nitter_url, timeout=60000)
            
            # 最新の投稿（ツイート内容）を取得
            # Nitterの画面構成に合わせてテキストを抜き出します
            tweet_element = await page.query_selector('.tweet-content')
            
            if tweet_element:
                tweet_text = await tweet_element.inner_text()
                print(f"Found: {tweet_text[:30]}...")

                # Telegramに送信
                bot = telegram.Bot(token=TOKEN)
                message = f"【{TARGET_USER} の最新投稿】\n\n{tweet_text}"
                await bot.send_message(chat_id=CHAT_ID, text=message)
                print("Success!")
            else:
                print("No tweets found.")
                
        except Exception as e:
            print(f"Error: {e}")
            # エラーが起きたことを自分に知らせる（デバッグ用）
            bot = telegram.Bot(token=TOKEN)
            await bot.send_message(chat_id=CHAT_ID, text=f"取得エラーが発生しました: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
