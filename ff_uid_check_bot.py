 import aiohttp
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ✅ Token ও Group ID সরাসরি কোডে সেট করা হয়েছে
BOT_TOKEN = "7592894356:AAHMklcnPTSOz6Ay0l7Gps4W-yIfou_EafU"
ALLOWED_GROUP_ID = -1002881479162

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

def unix_to_readable(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%d-%m-%Y %H:%M:%S")
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
        await message.reply("Usage: /check bd 7842525752 #user_id")
        return

    region, uid = args[1], args[2]
    wait_msg = await message.reply("🔍 Fetching player data...")

    url = f"https://freefireinfo.nepcoderapis.workers.dev/?uid={uid}&region={region}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                if res.status != 200:
                    raise Exception(f"HTTP Error: {res.status}")
                data = await res.json()

        acc = data.get("AccountInfo", {})
        guild = data.get("GuildInfo", {})
        pet = data.get("petInfo", {})
        social = data.get("socialinfo", {})

        text = f"""{user_tag}
<b>👤 Player Info</b>
<b>Name:</b> {acc.get("AccountName", "N/A")}
<b>UID:</b> {uid}
<b>Region:</b> {acc.get("AccountRegion", "N/A")}
<b>Level:</b> {acc.get("AccountLevel", "N/A")}
<b>EXP:</b> {acc.get("AccountEXP", 0):,}
<b>Likes:</b> {acc.get("AccountLikes", 0)}
<b>Created At:</b> {unix_to_readable(acc.get("AccountCreateTime", 0))}
<b>Last Login:</b> {unix_to_readable(acc.get("AccountLastLogin", 0))}

<b>🔥 Rank & Stats</b>
<b>BR Rank:</b> {acc.get("BrRankPoint", "N/A")}
<b>CS Rank:</b> {acc.get("CsRankPoint", "N/A")}
<b>Badges:</b> {acc.get("AccountBPBadges", 0)}
<b>Elite Pass:</b> {"Yes" if acc.get("DiamondCost", 0) > 0 else "No"}

<b>🏳️ Guild Info</b>
<b>Name:</b> {guild.get("GuildName", "N/A")}
<b>Owner:</b> {guild.get("GuildOwner", "N/A")}
<b>Members:</b> {guild.get("GuildMember", 0)} / {guild.get("GuildCapacity", 0)}
<b>Level:</b> {guild.get("GuildLevel", "N/A")}

<b>🐾 Pet Info</b>
<b>ID:</b> {pet.get("id", "N/A")}
<b>Level:</b> {pet.get("level", "N/A")}
<b>Skin:</b> {pet.get("skinId", "N/A")}
<b>Skill:</b> {pet.get("selectedSkillId", "N/A")}

<b>🌐 Social</b>
<b>Gender:</b> {social.get("Gender", "N/A").replace("Gender_", "")}
<b>Language:</b> {social.get("AccountLanguage", "N/A").replace("Language_", "")}
<b>Mode:</b> {social.get("ModePreference", "N/A").replace("ModePrefer_", "")}
<b>Signature:</b> {social.get("AccountSignature", "N/A").replace("[B][C]", "").strip()}
"""
        await wait_msg.edit_text(text)

    except Exception as e:
        await wait_msg.edit_text(f"❌ Error fetching info.\n<code>{e}</code>")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
