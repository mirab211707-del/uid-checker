from flask import Flask, jsonify, request
import asyncio
from telethon import TelegramClient
import re

api_id = 31915120
api_hash = "818357628da747df8f56b255061901aa"
bot_username = "TejaInfo_bot"

app = Flask(__name__)

# Telethon client per request (serverless-friendly)
async def get_telethon_name(uid):
    client = TelegramClient("mysession", api_id, api_hash)
    await client.start()

    response = {"error": "No reply from bot"}

    try:
        # Send command
        await client.send_message(bot_username, f"/get {uid}")

        # Wait for reply
        @client.on(events.NewMessage(from_users=bot_username))
        async def handler(event):
            text = event.raw_text.replace("\u200b", "")
            if "ғᴇᴛᴄʜɪɴɢ" in text.lower():
                return
            match = re.search(r"ɴᴀᴍᴇ[:：]\s*(.+)", text, re.IGNORECASE)
            if match:
                clean_name = re.sub(r'[\u200b\u200c\u200d\u3164]+', ' ', match.group(1))
                response.update({"name": clean_name.strip()})
            else:
                response.update({"error": "Name not found"})
            raise asyncio.CancelledError  # stop waiting

        await asyncio.wait_for(client.run_until_disconnected(), timeout=20)
    except asyncio.TimeoutError:
        response = {"error": "Bot did not reply in time"}
    finally:
        await client.disconnect()

    return response

@app.route("/api/<uid>")
def api_get(uid):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(get_telethon_name(uid))
    return jsonify(data)
