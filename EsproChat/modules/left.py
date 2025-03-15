from EsproChat import EsproChat as app
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from os import environ
from typing import Union, Optional
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------------- #

get_font = lambda font_size, font_path: ImageFont.truetype(font_path, font_size)
resize_text = (
    lambda text_size, text: (text[:text_size] + "...").upper()
    if len(text) > text_size
    else text.upper()
)

# --------------------------------------------------------------------------------- #

async def get_userinfo_img(
    bg_path: str,
    font_path: str,
    user_id: Union[int, str],
    profile_path: Optional[str] = None
):
    bg = Image.open(bg_path)

    if profile_path:
        img = Image.open(profile_path)
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice([(0, 0), img.size], 0, 360, fill=255)

        circular_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        resized = circular_img.resize((400, 400))
        bg.paste(resized, (440, 160), resized)

    img_draw = ImageDraw.Draw(bg)

    img_draw.text(
        (529, 627),
        text=str(user_id).upper(),
        font=get_font(46, font_path),
        fill=(255, 255, 255),
    )

    path = f"./userinfo_img_{user_id}.png"
    bg.save(path)
    return path

# --------------------------------------------------------------------------------- #

bg_path = "EsproChat/assets/userinfo.png"
font_path = "EsproChat/assets/hiroko.ttf"

# --------------------------------------------------------------------------------- #

@app.on_chat_member_updated(filters.group, group=20)
async def member_update_handler(client: app, member: ChatMemberUpdated):
    user = member.new_chat_member.user if member.new_chat_member else member.from_user

    # ------------ New Member Joins (Welcome Message) ------------ #
    if member.new_chat_member and member.new_chat_member.status in {"member"}:
        if user.photo and user.photo.big_file_id:
            try:
                photo = await app.download_media(user.photo.big_file_id)
                welcome_photo = await get_userinfo_img(
                    bg_path=bg_path,
                    font_path=font_path,
                    user_id=user.id,
                    profile_path=photo,
                )
                
                caption = f"**#Welcome**\n\n**๏** {user.mention} **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!** 🎉\n**๏ ʜᴀᴠᴇ ᴀ ɢʀᴇᴀᴛ ᴛɪᴍᴇ!**"
                button_text = "๏ ᴠɪᴇᴡ ᴜsᴇʀ ๏"
                deep_link = f"tg://openmessage?user_id={user.id}"

                await client.send_photo(
                    chat_id=member.chat.id,
                    photo=welcome_photo,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(button_text, url=deep_link)]
                    ])
                )
            except RPCError as e:
                print(e)
        else:
            await client.send_message(
                chat_id=member.chat.id,
                text=f"**#Welcome**\n\n**๏** {user.mention} **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ!** 🎉\n**๏ ʜᴀᴠᴇ ᴀ ɢʀᴇᴀᴛ ᴛɪᴍᴇ!**"
            )

    # ------------ Member Leaves (Goodbye Message) ------------ #
    elif member.old_chat_member and member.old_chat_member.status not in {"banned", "left", "restricted"}:
        if user.photo and user.photo.big_file_id:
            try:
                photo = await app.download_media(user.photo.big_file_id)
                goodbye_photo = await get_userinfo_img(
                    bg_path=bg_path,
                    font_path=font_path,
                    user_id=user.id,
                    profile_path=photo,
                )

                caption = f"**#Goodbye**\n\n**๏** {user.mention} **ʜᴀs ʟᴇғᴛ ᴛʜɪs ɢʀᴏᴜᴘ** 😢\n**๏ sᴇᴇ ʏᴏᴜ ᴀɢᴀɪɴ..!**"
                button_text = "๏ ᴠɪᴇᴡ ᴜsᴇʀ ๏"
                deep_link = f"tg://openmessage?user_id={user.id}"

                await client.send_photo(
                    chat_id=member.chat.id,
                    photo=goodbye_photo,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(button_text, url=deep_link)]
                    ])
                )
            except RPCError as e:
                print(e)
        else:
            await client.send_message(
                chat_id=member.chat.id,
                text=f"**#Goodbye**\n\n**๏** {user.mention} **ʜᴀs ʟᴇғᴛ ᴛʜɪs ɢʀᴏᴜᴘ** 😢\n**๏ sᴇᴇ ʏᴏᴜ ᴀɢᴀɪɴ..!**"
                )
