# ---------------------------------------------------
# File Name: main.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# More readable 
# --------------------------------------------
import time
import random
import string
import asyncio
from datetime import datetime, timedelta

from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from devgagan import app, userrbot
from devgagan.core.get_func import get_msg
from devgagan.core.func import *
from devgagan.core.mongo import db
from devgagan.modules.shrink import is_user_verified

from config import (
    API_ID,
    API_HASH,
    FREEMIUM_LIMIT,
    PREMIUM_LIMIT,
    OWNER_ID,
    DEFAULT_SESSION
)

# ---------------- BASIC UTILS ---------------- #

async def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

users_loop = {}
interval_set = {}
batch_mode = {}

# ---------------- CORE PROCESS ---------------- #

async def process_and_upload_link(userbot, user_id, msg_id, link, retry_count, message):
    await get_msg(userbot, user_id, msg_id, link, retry_count, message)
    await asyncio.sleep(10)

# ---------------- INTERVAL SYSTEM ---------------- #

async def check_interval(user_id, freecheck):
    if freecheck != 1 or await is_user_verified(user_id):
        return True, None

    now = datetime.now()
    if user_id in interval_set:
        cooldown_end = interval_set[user_id]
        if now < cooldown_end:
            remaining = (cooldown_end - now).seconds
            return False, f"Please wait {remaining} seconds before sending another link."
        else:
            del interval_set[user_id]

    return True, None

async def set_interval(user_id, interval_minutes=45):
    interval_set[user_id] = datetime.now() + timedelta(seconds=interval_minutes)

# ---------------- LINK CHECK (FIXED) ---------------- #

def is_normal_tg_link(link: str) -> bool:
    if not link.startswith("https://t.me/"):
        return False
    blocked = ["/c/", "/b/", "tg://", "t.me/+"]
    return not any(x in link for x in blocked)

# ---------------- SINGLE LINK HANDLER ---------------- #

@app.on_message(filters.regex(r'https?://t\.me/') & filters.private)
async def single_link(_, message):
    user_id = message.chat.id

    if await subscribe(_, message) == 1:
        return

    if users_loop.get(user_id):
        await message.reply("You already have a running process. Use /cancel.")
        return

    freecheck = await chk_user(message, user_id)
    can_proceed, response = await check_interval(user_id, freecheck)
    if not can_proceed:
        await message.reply(response)
        return

    users_loop[user_id] = True
    msg = await message.reply("Processing...")

    try:
        link = get_link(message.text)

        # ✅ PUBLIC LINK (NO USERBOT)
        if is_normal_tg_link(link):
            await get_msg(None, user_id, msg.id, link, 0, message)
            await set_interval(user_id, 45)

        # 🔒 PRIVATE LINK (USERBOT)
        else:
            userbot = await initialize_userbot(user_id)
            if not userbot:
                await msg.edit_text("Login required for private links.")
                return

            await process_and_upload_link(userbot, user_id, msg.id, link, 0, message)
            await set_interval(user_id, 45)

    except FloodWait as fw:
        await msg.edit_text(f"FloodWait: Try again after {fw.x} seconds.")
    except Exception as e:
        await msg.edit_text(f"Error:\n<code>{e}</code>")
    finally:
        users_loop[user_id] = False
        try:
            await msg.delete()
        except:
            pass

# ---------------- USERBOT INIT ---------------- #

async def initialize_userbot(user_id):
    data = await db.get_data(user_id)
    if data and data.get("session"):
        try:
            userbot = Client(
                "userbot",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=data.get("session")
            )
            await userbot.start()
            return userbot
        except:
            await app.send_message(user_id, "Login expired. Login again.")
            return None
    else:
        return userrbot if DEFAULT_SESSION else None

# ---------------- BATCH MODE ---------------- #

@app.on_message(filters.command("batch") & filters.private)
async def batch_link(_, message):
    if await subscribe(_, message) == 1:
        return

    user_id = message.chat.id
    if users_loop.get(user_id):
        await message.reply("Batch already running.")
        return

    freecheck = await chk_user(message, user_id)
    max_batch = FREEMIUM_LIMIT if freecheck == 1 else PREMIUM_LIMIT

    start = await app.ask(user_id, "Send start link")
    start_link = start.text.strip()
    start_id = int(start_link.split("/")[-1])

    count = await app.ask(user_id, f"How many messages? (Max {max_batch})")
    total = int(count.text.strip())

    can_proceed, response = await check_interval(user_id, freecheck)
    if not can_proceed:
        await message.reply(response)
        return

    users_loop[user_id] = True
    pin = await app.send_message(
        user_id,
        f"Batch started\nProcessing: 0/{total}"
    )
    await pin.pin()

    try:
        userbot = await initialize_userbot(user_id)
        for i in range(start_id, start_id + total):
            if not users_loop.get(user_id):
                break

            url = f"{'/'.join(start_link.split('/')[:-1])}/{i}"
            link = get_link(url)

            msg = await app.send_message(user_id, "Processing...")
            if is_normal_tg_link(link):
                await get_msg(None, user_id, msg.id, link, 0, message)
            else:
                await process_and_upload_link(userbot, user_id, msg.id, link, 0, message)

            await pin.edit_text(f"Batch started\nProcessing: {i-start_id+1}/{total}")

        await set_interval(user_id, 300)
        await pin.edit_text("Batch completed 🎉")

    except Exception as e:
        await app.send_message(user_id, f"Error: {e}")
    finally:
        users_loop[user_id] = False

# ---------------- CANCEL ---------------- #

@app.on_message(filters.command("cancel"))
async def cancel(_, message):
    user_id = message.chat.id
    if users_loop.get(user_id):
        users_loop[user_id] = False
        await message.reply("Process cancelled.")
    else:
        await message.reply("No active process.")
