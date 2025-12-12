import asyncio
from flask import Flask, jsonify, request
from telethon import TelegramClient, events
import re

api_id = 31915120
api_hash = "818357628da747df8f56b255061901aa"
bot_username = "TejaInfo_bot"

app = Flask(__name__)

# --------------------------
# TELETHON HANDLER FUNCTION
# --------------------------
async def fetch_name(uid: str):
    client = TelegramClient("vercel_session", api_id, api_hash)
    await client.start()

    future = asyncio.get_event_loop().create_future()

    @client.on(events.NewMessage(from_users=bot_username))
    async def handler(event):
        text = event.raw_text.replace("\u200b", "")
        if "ғᴇᴛᴄʜɪɴɢ" in text.lower():
            return
        if not future.done():
            future.set_result(text)

    # Send /get command
    await client.send_message(bot_username, f"/get {uid}")

    try:
        text = await asyncio.wait_for(future, timeout=25)
    except asyncio.TimeoutError:
        await client.disconnect()
        return {"error": "Bot did not reply in time"}

    await client.disconnect()

    # Extract name preserving spaces
    match = re.search(r"ɴᴀᴍᴇ[:：]\s*(.+)", text, re.IGNORECASE)
    if match:
        clean_name = re.sub(r'[\u200b\u200c\u200d\u3164]+', ' ', match.group(1))
        return {"name": clean_name.strip()}
    else:
        return {"error": "Name not found"}

# --------------------------
# FLASK ROUTE
# --------------------------
@app.route("/api/fetch_name")
def get_uid():
    uid = request.args.get("uid", "")

    # Validate UID length
    if not uid.isdigit() or not (8 <= len(uid) <= 11):
        return jsonify({"error": "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ! ᴜɪᴅ ᴍᴜsᴛ ʙᴇ 8-11 ᴅɪɢɪᴛs."})

    result = asyncio.run(fetch_name(uid))
    return jsonify(result)
