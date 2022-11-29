import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext import MessageHandler, filters

from priv_data import bot_token

app_python = "python3"
app_path = os.path.join('..','app','parser.py')
files_dir = os.path.join("..", "data", "incoming")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result_file = await context.bot.get_file(update.message.document)
    orig_file_name = update.message.document.file_name
    file_name, file_extension = os.path.splitext(orig_file_name)
    file_name = update.effective_chat.id
    if file_extension == ".Mission":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Принял файл миссии!")
    elif file_extension == ".json":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Принял файл конфигурации!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Не знаю тип {file_extension}")
        return
    new_file_path = os.path.join(files_dir, f"{file_name}{file_extension}")
    logging.info(f"Saving incoming file to {new_file_path}")
    await result_file.download_to_drive(new_file_path)
    logging.info(f"File {new_file_path} saved")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mission_file_name = os.path.join(files_dir, f"{update.effective_chat.id}.Mission")
    config_file_name = os.path.join(files_dir, f"{update.effective_chat.id}.json")
    if os.path.exists(mission_file_name):
        os.unlink(mission_file_name)
    if os.path.exists(config_file_name):
        os.unlink(config_file_name)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Начнём! Закидывай файлы")

async def process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mission_in_path = os.path.join(files_dir, f"{update.effective_chat.id}.Mission")
    config_in_path = os.path.join(files_dir, f"{update.effective_chat.id}.json")
    mission_out_path = os.path.join(files_dir, f"{update.effective_chat.id}_out.Mission")
    mission_img_path = os.path.join(files_dir, f"{update.effective_chat.id}.png")
    parser_log_path = os.path.join(files_dir, f"{update.effective_chat.id}.log")
    errors = []
    if not os.path.exists(mission_in_path):
        errors.append("-- Не загружен файл миссии")
    if not os.path.exists(config_in_path):
        errors.append("-- Не загружен файл конфигурации")
    if errors:
        errText = '\n'.join(errors)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Не получилось:\n{errText}")
        return
    
    # Start processing
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Начинаем обработку, жди...")
    cmd = f"{app_python} {app_path} -i {mission_in_path} -o {mission_out_path} -v {mission_img_path} -c {config_in_path}"
    logging.info(f"Proc start: {cmd}")
    #res = os.system(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    with open(parser_log_path, 'w') as f:
        f.write(out.decode())
    res = 'OK' if not err else err
    logging.info(f"Proc done: {res}")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Готово! Ответ: {res}")
    if err:
        return
    
    # Send result
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Отправляю файлы...")
    logging.info(f"Begin send files")
    await update.message.reply_document(
        document=mission_out_path,
        caption="Файл линии фронта"
    )
    await update.message.reply_document(
        document=mission_img_path,
        caption="Файл визуализации"
    )
    logging.info(f"Finish send files")


if __name__ == '__main__':
    application = ApplicationBuilder().token(bot_token).build()
    
    start_handler = CommandHandler('start', start)
    process_handler = CommandHandler('process', process)
    file_handler = MessageHandler(filters.Document.ALL, downloader)
    application.add_handler(start_handler)
    application.add_handler(process_handler)
    application.add_handler(file_handler)
    
    application.run_polling()