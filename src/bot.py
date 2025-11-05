import os
import logging
from logging.handlers import TimedRotatingFileHandler

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes

import prompts
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
        chat_id = update.effective_chat.id
        input_message = update.effective_message.text
        match input_message.lower().split():
            case [*_, "/clear" | "/clean"]:
                logging.info(f"Cleared memory for chat: {chat_id}")
                agent.clear_memory(chat_id)
                return
            case [*_, "/check"]:
                logger.info(f"Check text form chat: {chat_id}")
                answer = agent.invoke(chat_id, prompts.de_text_check_prompt.format(text=input_message))
                await update.message.reply_text(answer["messages"][-1].content)
                return
            case [*_, "/task"]:
                logging.info(f"Prepare task for chat: {chat_id}")
                answer = agent.invoke(chat_id, prompts.de_task_prompt)
                await update.message.reply_text(answer["messages"][-1].content)
                return
            case [*_, "/uhr"]:
                logging.info(f"Prepare Uhr task for chat: {chat_id}")
                answer = agent.invoke(chat_id, prompts.de_uhr_task_prompt)
                await update.message.reply_text(answer["messages"][-1].content)
                return
            case _:
                logger.info("Pass request to LLM")
                answer = agent.invoke(chat_id, input_message)
                await update.message.reply_text(answer["messages"][-1].content)
                return

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(MessageHandler(None, callback=llm_request))

    app.run_webhook(
        listen='0.0.0.0',
        port=8000,
        webhook_url=f"{os.getenv('OWN_HOST')}{os.getenv('CONTEXT_PATH')}",
        secret_token=os.getenv("TELEGRAM_WEBHOOK_SECRET_TOKEN")
    )
