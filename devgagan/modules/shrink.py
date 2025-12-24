# ---------------------------------------------------
# File Name: shrink.py
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
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import string
import aiohttp
from devgagan import app
from devgagan.core.func import *
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB, WEBSITE_URL, AD_API, LOG_GROUP  

# ---------------- DATABASE ---------------- #

tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]

async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)

# ---------------- GLOBAL ---------------- #

Param = {}

# ---------------- FUNCTIONS ---------------- #

async def generate_random_param(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def get_shortened_url(deep_link):
    api_url = f"https://{WEBSITE_URL}/api?api={AD_API}&url={deep_link}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    return None

async def is_user_verified(user_id):
    session = await token.find_one({"user_id": user_id})
    return session is not None

# ---------------- START COMMAND ---------------- #

@app.on_message(filters.command("start"))
async def token_handler(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return

    user_id = message.chat.id

    if len(message.command) <= 1:
        join_button = InlineKeyboardButton(
            "Join Channel",
            url="https://t.me/+5H5tJB8hlJo2MjU1"
        )
        premium_button = InlineKeyboardButton(
            "Get Premium",
            url="https://t.me/Divyanshshukla7"
        )

        keyboard = InlineKeyboardMarkup([
            [join_button],
            [premium_button]
        ])

        await message.reply_photo(
            photo="https://straightforward-pink-s9qrn3ua0z-7cjo3r7zez.edgeone.dev/1766497138025-10b1c2ab-8536-4189-9e4a-8932e9f372c8.png",
            caption=(
                f"Hi 👋 {message.from_user.first_name}\n\n"
                "🔒 Save posts even from channels or groups with forwarding disabled\n\n"
                "📥 Download videos & audio from YouTube, Instagram, and many other platforms effortlessly\n\n"
                "📌 Just send me the post link from any public channel — I'll handle the rest!\n\n"
                "ℹ️ Need help? Type /help to explore all my features\n\n"
                "Developer by - ༺⚡༻ 𝑫𝒊𝒗𝒚𝒂𝒏𝒔𝒉 𝒔𝒉𝒖𝒌𝒍𝒂 ༺⚡༻"
            ),
            reply_markup=keyboard
        )
        return

    param = message.command[1]
    freecheck = await chk_user(message, user_id)

    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return

    if user_id in Param and Param[user_id] == param:
        await token.insert_one({
            "user_id": user_id,
            "param": param,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=3),
        })
        del Param[user_id]
        await message.reply("✅ You have been verified successfully! Enjoy your session for next 3 hours.")
    else:
        await message.reply("❌ Invalid or expired verification link. Please generate a new token.")

# ---------------- TOKEN COMMAND ---------------- #

@app.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id

    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return

    if await is_user_verified(user_id):
        await message.reply("✅ Your free session is already active enjoy!")
        return

    param = await generate_random_param()
    Param[user_id] = param

    deep_link = f"https://t.me/{client.me.username}?start={param}"
    shortened_url = await get_shortened_url(deep_link)

    if not shortened_url:
        await message.reply("❌ Failed to generate the token link. Please try again.")
        return

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Verify the token now...", url=shortened_url)]]
    )

    await message.reply(
        "Click the button below to verify your free access token:\n\n"
        "➤ What will you get?\n"
        "1. Free access for 3 hours\n"
        "2. Batch command limit = FreeLimit + 20\n"
        "3. All functions unlocked",
        reply_markup=button
    )