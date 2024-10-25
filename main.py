# Copyright 2021 TerminalWarlord under the terms of the MIT
# License found at https://github.com/TerminalWarlord/TikTok-Downloader-Bot/blob/master/LICENSE
# Encoding = 'utf-8'
# Fork and Deploy, do not modify this repo and claim it as yours
# For collaboration, contact dev.jaybee@gmail.com

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import shutil
import requests
import os
import re
import time
from datetime import timedelta
import ntplib
from progress_bar import progress, TimeFormatter, humanbytes
from dotenv import load_dotenv


def sync_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        print("Time synchronized:", time.ctime(response.tx_time))
    except Exception as e:
        print(f"Failed to synchronize time: {e}")


sync_time()


load_dotenv()
bot_token = os.environ.get('BOT_TOKEN')
workers = int(os.environ.get('WORKERS'))
api = int(os.environ.get('API_KEY'))
hash = os.environ.get('API_HASH')
chnnl = os.environ.get('CHANNEL_URL')
BOT_URL = os.environ.get('BOT_URL')
app = Client("JayBee", bot_token=bot_token, api_id=api, api_hash=hash, workers=workers)


@app.on_message(filters.command('start'))
def start(client, message):
    kb = [[InlineKeyboardButton('Channel 🛡', url=chnnl), InlineKeyboardButton('Repo 🔰', url="https://github.com/TerminalWarlord/TikTok-Downloader-Bot/")]]
    reply_markup = InlineKeyboardMarkup(kb)
    app.send_message(chat_id=message.from_user.id, text=f"Hello there, I am **TikTok Downloader Bot**.\nI can download TikTok videos without Watermark.\n\n"
                          "__**Developer :**__ __@JayBeeDev__\n"
                          "__**Language :**__ __Python__\n"
                          "__**Framework :**__ __🔥 Pyrogram__",
                     reply_markup=reply_markup)


@app.on_message(filters.command('help'))
def help(client, message):
    kb = [[InlineKeyboardButton('Channel 🛡', url=chnnl), InlineKeyboardButton('Repo 🔰', url="https://github.com/TerminalWarlord/TikTok-Downloader-Bot/")]]
    reply_markup = InlineKeyboardMarkup(kb)
    app.send_message(chat_id=message.from_user.id, text="Hello there, I am **TikTok Downloader Bot**.\nI can download any TikTok video from a given link.\n\n"
                                            "__Send me a TikTok video link__",
                     reply_markup=reply_markup)


@app.on_message((filters.regex("http://") | filters.regex("https://")) & (filters.regex('tiktok') | filters.regex('douyin')))
def tiktok_dl(client, message):
    a = app.send_message(chat_id=message.chat.id, text='__Downloading File to the Server__')
    link = re.findall(r'\bhttps?://.*[(tiktok|douyin)]\S+', message.text)[0].split("?")[0]

    params = {
        "link": link
    }
    headers = {
        'x-rapidapi-host': "tiktok-info.p.rapidapi.com",
        'x-rapidapi-key': "16a7a37fbemsha4ba1a2a6863e35p1f39aajsn3f30891d7565"
    }
    api = "https://tiktok-info.p.rapidapi.com/dl/"
    
    try:
        response = requests.get(api, params=params, headers=headers).json()
        print("API response:", response)  # Log API response for debugging

        # Safely access video link
        video_links = response.get('videoLinks', {})
        download_link = video_links.get('download')

        if not download_link:
            raise ValueError("Download link not found in the response. Please check API status.")

        # Proceed with file download
        directory = str(round(time.time()))
        filename = str(int(time.time())) + '.mp4'
        size = int(requests.head(download_link).headers['Content-length'])
        total_size = "{:.2f}".format(int(size) / 1048576)
        
        os.makedirs(directory, exist_ok=True)  # Create directory if not exists
        
        # Download video
        with requests.get(download_link, timeout=(50, 10000), stream=True) as r:
            r.raise_for_status()
            with open(f'./{directory}/{filename}', 'wb') as f:
                chunk_size = 1048576
                dl = 0
                show = 1
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    dl += chunk_size
                    percent = round(dl * 100 / size)
                    percent = min(percent, 100)
                    if show == 1:
                        try:
                            a.edit(
                                f'__**URL :**__ __{message.text}__\n'
                                f'__**Total Size :**__ __{total_size} MB__\n'
                                f'__**Downloaded :**__ __{percent}%__\n',
                                disable_web_preview=False)
                        except:
                            pass
                        if percent == 100:
                            show = 0

            # Notify user of completion
            a.edit(f'__Downloaded to the server!\nUploading to Telegram Now ⏳__')
            start = time.time()
            app.send_document(chat_id=message.chat.id,
                              document=f"./{directory}/{filename}",
                              caption=f"**File :** __{filename}__\n"
                                      f"**Size :** __{total_size} MB__\n\n"
                                      f"__Uploaded by @{BOT_URL}__",
                              file_name=f"{directory}",
                              progress=progress,
                              progress_args=(a, start, filename))
            a.delete()
            shutil.rmtree(directory)  # Clean up

    except requests.RequestException as e:
        a.edit(f"Failed to download video due to a request error: {e}")
    except ValueError as e:
        a.edit(f"Failed to download video: {e}")
    except Exception as e:
        a.edit(f"An unexpected error occurred: {e}")


app.run()
