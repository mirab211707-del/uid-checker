from flask import Flask, request, jsonify
from telethon import TelegramClient
import re
import os

api_id = 31915120
api_hash = "818357628da747df8f56b255061901aa"
bot_username = "TejaInfo_bot"

app = Flask(__name__)

# Load or create Telethon session
client = TelegramClient("mysession", api_id, api_hash)
client.start(bot_token=None)  # Start client (user bot session)

# --------------------------
# UID validation + Name extraction
# --------------------------
@app.route("/<uid>", methods=["GET", "POST"])
def check_uid(uid):
    # Skip favicon
    if uid == "favicon.ico":
        return ""

    # Validate UID: must be 8-11 digits
    if not uid.isdigit() or not (8 <= len(uid) <= 11):
        return jsonify({"error": "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ! ᴜɪᴅ ᴍᴜsᴛ ʙᴇ 8-11 ᴅɪɢɪᴛs."})

    try:
        # Send /get UID command
        message = client.send_message(bot_username, f"/get {uid}")

        # Wait for reply synchronously (up to 20s)
        result = client.get_messages(bot_username, limit=5)
        name = None
        for msg in result:
            text = msg.raw_text.replace("\u200b", "")
            if "ɴᴀᴍᴇ" in text.lower():
                match = re.search(r"ɴᴀᴍᴇ[:：]\s*(.+)", text, re.IGNORECASE)
                if match:
                    clean_name = re.sub(r'[\u200b\u200c\u200d\u3164]+', ' ', match.group(1))
                    name = clean_name.strip()
                    break

        if name:
            return jsonify({"name": name})
        else:
            return jsonify({"error": "Name not found"})

    except Exception as e:
        return jsonify({"error": str(e)})

# --------------------------
if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
