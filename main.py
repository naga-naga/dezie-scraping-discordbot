import discord
from discord.ext import tasks
from datetime import datetime
import os
import scrape

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

# デヂエのページ
urls = [
    "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=357", # お知らせページ
    "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=391", # 時間割・講義室変更ページ
    "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=361", # 休講通知ページ
    "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=363", # 補講通知ページ
    "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=393", # 学生呼び出しページ
    "https://db.jimu.kyutech.ac.jp/cgi-bin/cbdb/db.cgi?page=DBView&did=364", # 授業調整・期末試験ページ
]

# 各ページのIDの書き出し先
output_ID_path = [
    "data/rid_info.dat",  # お知らせページ
    "data/rid_change.dat",  # 時間割・講義室変更ページ
    "data/rid_cancel.dat",  # 休講通知ページ
    "data/rid_makeup.dat",  # 補講通知ページ
    "data/rid_call.dat",  # 学生呼び出しページ
    "data/rid_exam.dat",  # 授業調整・期末試験ページ
]

# お知らせする時間
info_time_list = [
    "06:00",
    "09:00",
    "12:00",
    "15:00",
    "18:00",
    "21:00",
]

client = discord.Client()

# メッセージを送る
async def send_message(string):
    channel = client.get_channel(CHANNEL_ID)
    await channel.send(string)

# デヂエから情報を拾ってくる
async def get_infomation():
    ret_str = ""
    for url, path in zip(urls, output_ID_path):
        scr = scrape.Scrape(url, path)
        ret_str += scr.get_elems_string()
    return ret_str

# デヂエから拾ってきた情報を送信する
async def send_infomation():
    # デヂエから拾ってきたデータ
    message = await get_infomation()
    if message != "":
        # 新着情報がある場合
        # お知らせを一つずつ分ける
        for text in message.split("\n\n"):
            if text != "":
                # 送信
                await send_message(text)
    else:
        # 新着情報がない場合
        await send_message("新着情報なし！")

# BOTの準備ができた時に呼び出される
@client.event
async def on_ready():
    # loopメソッドを動かす
    loop.start()
    print("ログインしたよ")
    # 再起動時にファイル状態が戻るので，一度読み込む
    await get_infomation()
    await send_message("BOT起動！")

# 60秒ごとに繰り返す
@tasks.loop(seconds=60)
async def loop():
    # 現在時刻を取得
    now = datetime.now().strftime("%H:%M")
    if now in info_time_list:
        await send_infomation()

client.run(TOKEN)
