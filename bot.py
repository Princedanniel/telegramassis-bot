import logging
import re
from datetime import datetime, timedelta

from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔥 LOGGING (VERY IMPORTANT FOR DEBUGGING)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

import os
TOKEN = os.getenv("BOT_TOKEN")

ALLOWED_LINK = "vestoradigital.com"

BAD_WORDS = [
    "scam", "scamming", "fake", "not real", "crash", "they will crash"
]

user_offenses = {}

# ✅ START COMMAND (WORKS IN PRIVATE + GROUP)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🤖 Bot is active and fully working!")
        logging.info(f"/start triggered by {update.effective_user.id}")
    except Exception as e:
        logging.error(f"Start error: {e}")


# ✅ MODERATION FUNCTION (STRONG VERSION)
async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.text:
        return

    try:
        user = message.from_user
        text = message.text.lower()
        user_id = user.id
        chat_id = message.chat.id

        if user_id not in user_offenses:
            user_offenses[user_id] = 0

        # 🔗 LINK CHECK
        link_pattern = r"(https?://\S+|www\.\S+)"
        found_links = re.findall(link_pattern, text)

        for link in found_links:
            if ALLOWED_LINK not in link:
                await message.delete()
                logging.info(f"Deleted link from {user_id}")
                await punish(user_id, chat_id, context)
                return

        # 🚫 BAD WORD CHECK
        for word in BAD_WORDS:
            if word in text:
                await message.delete()
                logging.info(f"Deleted bad word from {user_id}")
                return

    except Exception as e:
        logging.error(f"Moderation error: {e}")


# ✅ PUNISH SYSTEM (SAFE + LOGGED)
async def punish(user_id, chat_id, context):
    try:
        user_offenses[user_id] += 1
        offense = user_offenses[user_id]

        if offense == 1:
            until = datetime.utcnow() + timedelta(hours=1)
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until
            )
            await context.bot.send_message(chat_id, "⚠️ First warning! Muted for 1 hour.")

        elif offense == 2:
            until = datetime.utcnow() + timedelta(hours=24)
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until
            )
            await context.bot.send_message(chat_id, "⚠️ Final warning! Muted for 24 hours.")

        else:
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.send_message(chat_id, "🚫 User banned.")

        logging.info(f"Punished user {user_id} | offense {offense}")

    except Exception as e:
        logging.error(f"Punish error: {e}")



from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.new_chat_members:
        return

    try:
        for member in message.new_chat_members:
            # 👤 Tag user properly
            if member.username:
                user_tag = f"@{member.username}"
            else:
                user_tag = member.mention_html()

            welcome_text = (
                f"👋 Welcome {user_tag}!\n\n"
                "You're welcome to Vestora Digital 🚀\n"
                "We build, grow and earn together.\n\n"
                "⚠️ Follow group rules and avoid spam.\n"
                "👇 Click below to login to your account"
            )

            # 🔘 Button
            keyboard = [
                [InlineKeyboardButton("🚀 Visit Website", url="https://www.vestoradigital.com/login.php")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            import asyncio

            await message.reply_html(
                welcome_text,
                reply_markup=reply_markup
            )

            # ⏳ Small delay before deleting
            await asyncio.sleep(1)

            await message.delete()

        logging.info("Welcome message with button sent")

    except Exception as e:
        logging.error(f"Welcome error: {e}")



# ✅ ERROR HANDLER (VERY IMPORTANT)
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Exception while handling update:", exc_info=context.error)


    async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id if update.effective_user else "Unknown"

        print(f"CHAT ID: {chat_id}")
        print(f"USER ID: {user_id}")

    except Exception as e:
        logging.error(f"Chat ID error: {e}")


# ✅ MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderate))

    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, get_chat_id))

    # Error handler
    app.add_error_handler(error_handler)

    print("🚀 Bot is running (DEEP MODE)...")

    # 🔥 CRITICAL FIXES INCLUDED
    app.run_polling()
