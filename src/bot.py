import os
import logging
from logging.handlers import TimedRotatingFileHandler

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from agent import ChatBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        TimedRotatingFileHandler(f"{os.getenv("LOG_DIR", ".")}/bot.log", when='midnight', interval=1, backupCount=14),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

agent = ChatBot()

async def llm_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message and update.effective_message.text:
        logger.info("Pass request to LLM")
        answer = agent.invoke(update.effective_user.id, update.effective_message.text)
        update.message.reply_text(answer["messages"][-1].content)

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("response", llm_request))

    app.run_webhook(
        port=8000,
        webhook_url=f"{os.getenv("OWN_HOST")}{os.getenv("CONTEXT_PATH")}",
        secret_token=os.getenv("TELEGRAM_WEBHOOK_SECRET_TOKEN")
    )
