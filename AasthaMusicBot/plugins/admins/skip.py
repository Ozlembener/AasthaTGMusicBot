#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
# A Powerful Music Bot Property Of Rocks Indian Largest Chatting Group

# Kanged By © @Dr_Asad_Ali
# Rocks © @Shayri_Music_Lovers
# Owner Asad Ali
# Harshit Sharma
# All rights reserved. Yukki

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from config import BANNED_USERS
from strings import get_command
from AasthaMusicBot import YouTube, app
from AasthaMusicBot.core.call import Alexa
from AasthaMusicBot.misc import db
from AasthaMusicBot.utils.database import get_loop
from AasthaMusicBot.utils.decorators import AdminRightsCheck
from AasthaMusicBot.utils.inline.play import stream_markup, telegram_markup
from AasthaMusicBot.utils.stream.autoclear import auto_clean
from AasthaMusicBot.utils.thumbnails import gen_thumb

# Commands
SKIP_COMMAND = get_command("SKIP_COMMAND")


@app.on_message(filters.command(SKIP_COMMAND) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_12"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check:
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0)
                            except:
                                return await message.reply_text(_["admin_16"])
                            if popped:
                                if config.AUTO_DOWNLOADS_CLEAR == str(True):
                                    await auto_clean(popped)
                            if not check:
                                try:
                                    await message.reply_text(
                                        _["admin_10"].format(
                                            message.from_user.first_name
                                        )
                                    )
                                    await Alexa.stop_stream(chat_id)
                                except:
                                    return
                                break
                    else:
                        return await message.reply_text(_["admin_15"].format(count))
                else:
                    return await message.reply_text(_["admin_14"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_13"])
    else:
        check = db.get(chat_id)
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                if config.AUTO_DOWNLOADS_CLEAR == str(True):
                    await auto_clean(popped)
            if not check:
                await message.reply_text(
                    _["admin_10"].format(message.from_user.first_name)
                )
                try:
                    return await Alexa.stop_stream(chat_id)
                except:
                    return
        except:
            try:
                await message.reply_text(
                    _["admin_10"].format(message.from_user.first_name)
                )
                return await Alexa.stop_stream(chat_id)
            except:
                return
    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return await message.reply_text(_["admin_11"].format(title))
        try:
            await Alexa.skip_stream(chat_id, link, video=status)
        except Exception:
            return await message.reply_text(_["call_9"])
        button = telegram_markup(_)
        img = await gen_thumb(videoid)
        await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                user,
                f"https://t.me/{app.username}?start=info_{videoid}",
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
    elif "vid_" in queued:
        mystic = await message.reply_text(_["call_10"], disable_web_page_preview=True)
        try:
            file_path, direct = await YouTube.download(
                videoid,
                mystic,
                videoid=True,
                video=status,
            )
        except:
            return await mystic.edit_text(_["call_9"])
        try:
            await Alexa.skip_stream(chat_id, file_path, video=status)
        except Exception:
            return await mystic.edit_text(_["call_9"])
        button = stream_markup(_, videoid)
        img = await gen_thumb(videoid)
        await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(
                user,
                f"https://t.me/{app.username}?start=info_{videoid}",
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        await mystic.delete()
    elif "index_" in queued:
        try:
            await Alexa.skip_stream(chat_id, videoid, video=True)
        except Exception:
            return await message.reply_text(_["call_9"])
        button = telegram_markup(_)
        await message.reply_photo(
            photo=config.STREAM_IMG_URL,
            caption=_["stream_2"].format(user),
            reply_markup=InlineKeyboardMarkup(button),
        )
    else:
        try:
            await Alexa.skip_stream(chat_id, queued, video=status)
        except Exception:
            return await message.reply_text(_["call_9"])
        if videoid == "telegram":
            button = telegram_markup(_)
            await message.reply_photo(
                photo=config.TELEGRAM_AUDIO_URL
                if str(streamtype) == "audio"
                else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_3"].format(title, check[0]["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
        elif videoid == "soundcloud":
            button = telegram_markup(_)
            await message.reply_photo(
                photo=config.SOUNCLOUD_IMG_URL
                if str(streamtype) == "audio"
                else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_3"].format(title, check[0]["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            button = stream_markup(_, videoid)
            img = await gen_thumb(videoid)
            await message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    user,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
