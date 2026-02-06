# devgagan
# Note if you are trying to deploy on vps then directly fill values in ("")

from os import getenv

# VPS --- FILL COOKIES 🍪 in """ ... """ 

INST_COOKIES = """
# wtite up here insta cookies
"""

YTUB_COOKIES = """
# write here yt cookies
"""

API_ID = int(getenv("API_ID", "21834860"))
API_HASH = getenv("API_HASH", "e4acef545ba34ee3fa5c511b38644647")
BOT_TOKEN = getenv("BOT_TOKEN", "8272188727:AAFoKyUKvEK3y8pzIvUPje3fjMdMwQWuXWI")
OWNER_ID = list(map(int, getenv("OWNER_ID", "6334323103").split()))
MONGO_DB = getenv("MONGO_DB", "mongodb+srv://divyanshshukla5375_db_user:1kZ2dsVTktdMljpr@cluster0.lo5qk5v.mongodb.net/?appName=Cluster0")
LOG_GROUP = getenv("LOG_GROUP", "-1003651358527")
CHANNEL_ID = int(getenv("CHANNEL_ID", "-1003651358527"))
FREEMIUM_LIMIT = int(getenv("FREEMIUM_LIMIT", "10"))
PREMIUM_LIMIT = int(getenv("PREMIUM_LIMIT", "500000000"))
WEBSITE_URL = getenv("WEBSITE_URL", "upshrink.com")
AD_API = getenv("AD_API", "52b4a2cf4687d81e7d3f8f2b7bc2943f618e78cb")
STRING = getenv("STRING", None)
YT_COOKIES = getenv("YT_COOKIES", YTUB_COOKIES)
DEFAULT_SESSION = getenv("DEFAUL_SESSION", None)  # added old method of invite link joining
INSTA_COOKIES = getenv("INSTA_COOKIES", INST_COOKIES)
