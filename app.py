import os
import json
import shutil
from flask import Flask, request, jsonify, send_file, send_from_directory
from telegram import Update, Bot, BotCommand
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import config
from telegram_bot import TelegramBot

app = Flask(__name__)
bot = Bot(token=config.API_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

telegram_bot = TelegramBot(dispatcher)


@app.route('/status/<mission>', methods=['GET'])
def get_status(mission):
    status = telegram_bot.current_status.get(mission, 'not started')
    if status == 'completed':
        files = [f for f in os.listdir('downloads') if f.startswith(mission)]
        return jsonify({"status": status, "files": files})
    else:
        return jsonify({"status": status})

@app.route('/delete_all', methods=['DELETE'])
def delete_all():
    for filename in os.listdir('downloads'):
        file_path = os.path.join('downloads', filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    for filename in os.listdir('downloaded_files'):
        file_path = os.path.join('downloaded_files', filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    telegram_bot.set_mission_status()
    return jsonify({"status": "all files deleted"})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('downloads', filename)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

def init_app():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    return app

if __name__ == '__main__':
    app = init_app()
    app.run(host="0.0.0.0", port=6000, debug=True)