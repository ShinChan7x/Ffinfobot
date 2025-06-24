import os
import aiohttp
import logging
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID", "-1000000000000"))

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

def unix_to_readable(timestamp):
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%d-%m-%Y %H:%M:%S")
    except:
        return "N/A"

@dp.message_handler(commands=["check"])
async def check_uid_info(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
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
<b>👤 Player Profile</b>
<b>Name:</b> {b.get("nickname", "N/A")}
<b>UID:</b> {b.get("accountId", "N/A")}
<b>Region:</b> {b.get("region", "N/A")}
<b>Level:</b> {b.get("level", "N/A")}
<b>EXP:</b> {b.get("exp", 0):,}
<b>Likes:</b> {b.get("liked", "N/A")}
<b>Created At:</b> {unix_to_readable(b.get("createAt", 0))}
<b>Last Login:</b> {unix_to_readable(b.get("lastLoginAt", 0))}

<b>🔥 Elite & Stats</b>
<b>Elite Pass:</b> {"Yes" if b.get("hasElitePass") else "No"}
<b>Badges:</b> {b.get("badgeCnt", 0)}

<b>🏳️ Guild Info</b>
<b>Name:</b> {c.get("clanName", "N/A")}
<b>Leader ID:</b> {c.get("captainId", "N/A")}
<b>Members:</b> {c.get("memberNum", 0)} / {c.get("capacity", 0)}
<b>Level:</b> {c.get("clanLevel", "N/A")}

<b>🐾 Pet Info</b>
<b>Name:</b> {p.get("name", "N/A")}
<b>Level:</b> {p.get("level", "N/A")}
<b>Skin ID:</b> {p.get("skinId", "N/A")}
<b>Skill ID:</b> {p.get("selectedSkillId", "N/A")}

<b>🌐 Social Info</b>
<b>Gender:</b> {s.get("gender", "N/A").replace("Gender_", "")}
<b>Language:</b> {s.get("language", "N/A").replace("Language_", "")}
<b>Time Online:</b> {s.get("timeOnline", "N/A").replace("TimeOnline_", "")}
<b>Time Active:</b> {s.get("timeActive", "N/A").replace("TimeActive_", "")}
<b>Signature:</b> {s.get("signature", "N/A").replace("[b][c][i]", "").strip()}
"""

        await wait_msg.edit_text(text)

    except Exception as e:
        await wait_msg.edit_text(f"❌ Error fetching info.\n<code>{e}</code>")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
