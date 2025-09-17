import os
import asyncio
from PIL import ImageDraw, Image, ImageFont, ImageChops
from pyrogram import *
from pyrogram.types import *
from logging import getLogger
from EsproChat import EsproChat as EsproChat

LOGGER = getLogger(__name__)
lock = asyncio.Lock()

class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None

def circle(pfp, size=(500, 500)):
    pfp = pfp.resize(size, Image.LANCZOS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

def welcomepic(pic, user, chatname, id, uname):
    os.makedirs("downloads", exist_ok=True)  # ✅ Ensure folder exists
    background = Image.open("EsproChat/assets/wel2.png")
    pfp = Image.open(pic).convert("RGBA")
    pfp = circle(pfp)
    pfp = pfp.resize((825, 824))
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype('EsproChat/assets/font.ttf', size=110)
    draw.text((2100, 1420), f'ID: {id}', fill=(255, 255, 255), font=font)
    pfp_position = (1990, 435)
    background.paste(pfp, pfp_position, pfp)
    output_path = f"/tmp/welcome#{id}.png"  # ✅ Using /tmp instead of downloads
    background.save(output_path)
    return output_path

@EsproChat.on_chat_member_updated(filters.group, group=-3)
async def greet_group(_, member: ChatMemberUpdated):
    if (
        not member.new_chat_member
        or member.new_chat_member.status in {"banned", "left", "restricted"}
        or member.old_chat_member
    ):
        return

    user = member.new_chat_member.user if member.new_chat_member else member.from_user
    try:
        pic = await EsproChat.download_media(
            user.photo.big_file_id, file_name=f"/tmp/pp{user.id}.png"
        )
    except AttributeError:
        pic = "EsproChat/assets/upic.png"

    async with lock:
        if temp.MELCOW.get(f"welcome-{member.chat.id}") is not None:
            try:
                await temp.MELCOW[f"welcome-{member.chat.id}"].delete()
            except Exception as e:
                LOGGER.error(e)

        try:
            bot_info = await EsproChat.get_me()
            bot_username = bot_info.username
            url = f"https://t.me/ShiriMusicbot?startgroup=true"

            welcomeimg = welcomepic(
                pic, user.first_name, member.chat.title, user.id, user.username
            )
            temp.MELCOW[f"welcome-{member.chat.id}"] = await EsproChat.send_photo(
                member.chat.id,
                photo=welcomeimg,
                caption=f"""
**Wᴇʟᴄᴏᴍᴇ Tᴏ {member.chat.title}
➖➖➖➖➖➖➖➖➖➖➖➖
Nᴀᴍᴇ ✧ {user.mention}
Iᴅ ✧ {user.id}
Usᴇʀɴᴀᴍᴇ ✧ @{user.username}
➖➖➖➖➖➖➖➖➖➖➖➖**
""",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"⦿ ᴀᴅᴅ ᴍᴇ ⦿", url=url)]])
            )
        except Exception as e:
            LOGGER.error(e)

        try:
            os.remove(f"/tmp/welcome#{user.id}.png")  # ✅ Deleting from temp
            os.remove(f"/tmp/pp{user.id}.png")  # ✅ Deleting profile pic
        except Exception:
            pass
