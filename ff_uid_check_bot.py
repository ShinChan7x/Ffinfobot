
import asyncio
import logging
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode, ChatType
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID", "-1000000000000"))

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def unix_to_readable(timestamp):
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%d-%m-%Y %H:%M:%S")
    except:
        return "N/A"

@dp.message(Command("check"))
async def check_uid_info(message: Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return
    if message.chat.id != ALLOWED_GROUP_ID:
        return

    args = message.text.split()
    user_tag = ""
    for arg in args:
        if arg.startswith("#") and arg[1:].isdigit():
            user_tag = arg
            args.remove(arg)
            break

    if len(args) != 3:
        await message.reply("Usage: /check sg 8431487083 #user_id")
        return

    region, uid = args[1], args[2]
    wait_msg = await message.reply("Fetching player data... Please wait...")

    url = f"https://fred-fire-info-gj.vercel.app/player-info?uid={uid}&region={region}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        b = data.get("basicInfo", {})
        c = data.get("clanBasicInfo", {})
        p = data.get("petInfo", {})
        s = data.get("socialInfo", {})

        text = f"""{user_tag}
Player Profile
Name: {b.get("nickname", "N/A")}
UID: {b.get("accountId", "N/A")}
Region: {b.get("region", "N/A")}
Level: {b.get("level", "N/A")}
EXP: {b.get("exp", 0):,}
Likes: {b.get("liked", "N/A")}
Created At: {unix_to_readable(b.get("createAt", 0))}
Last Login: {unix_to_readable(b.get("lastLoginAt", 0))}

Elite & Stats
Elite Pass: {"Yes" if b.get("hasElitePass") else "No"}
Badges: {b.get("badgeCnt", 0)}

Guild Info
Name: {c.get("clanName", "N/A")}
Leader ID: {c.get("captainId", "N/A")}
Members: {c.get("memberNum", 0)} / {c.get("capacity", 0)}
Level: {c.get("clanLevel", "N/A")}

Pet Info
Name: {p.get("name", "N/A")}
Level: {p.get("level", "N/A")}
Skin ID: {p.get("skinId", "N/A")}
Skill ID: {p.get("selectedSkillId", "N/A")}

Social Info
Gender: {s.get("gender", "N/A").replace("Gender_", "")}
Language: {s.get("language", "N/A").replace("Language_", "")}
Time Online: {s.get("timeOnline", "N/A").replace("TimeOnline_", "")}
Time Active: {s.get("timeActive", "N/A").replace("TimeActive_", "")}
Signature: {s.get("signature", "N/A").replace("[b][c][i]", "").strip()}
"""
        await wait_msg.edit_text(text)

    except Exception as e:
        await wait_msg.edit_text(f"Error fetching info.\n{e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
