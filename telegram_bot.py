import os
import base64
import json
import requests
import threading
from telegram import Update, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import fitz  # PyMuPDF
import config
from logger import CustomLogger

class TelegramBot:
    def __init__(self, dispatcher):
        self.current_command = None
        self.current_status = {}
        self.missionlist = ['mission1', 'mission2','mission3','mission4','mission5','mission6','mission7','mission8','mission9','mission10']

        self.logger = CustomLogger()
        self.dispatcher = dispatcher

        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("mission1", self.set_mission1))
        self.dispatcher.add_handler(CommandHandler("mission2", self.set_mission2))
        self.dispatcher.add_handler(CommandHandler("mission3", self.set_mission3))

        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.log_all_messages))
        self.dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), self.handle_pdf))

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Привет! Я ваш бот.')

    def set_mission1(self, update: Update, context: CallbackContext) -> None:
        self.current_command = 'mission1'
        update.message.reply_text('Миссия 1 выбрана. Пожалуйста, отправьте PDF файл.')

    def set_mission2(self, update: Update, context: CallbackContext) -> None:
        self.current_command = 'mission2'
        update.message.reply_text('Миссия 2 выбрана. Пожалуйста, отправьте PDF файл.')

    def set_mission3(self, update: Update, context: CallbackContext) -> None:
        self.current_command = 'mission3'
        update.message.reply_text('Миссия 3 выбрана. Пожалуйста, отправьте PDF файл.')

    def handle_pdf(self, update: Update, context: CallbackContext) -> None:
        if not self.current_command:
            update.message.reply_text('Пожалуйста, выберите миссию перед отправкой PDF файла.')
            return
        
        self.logger.log_message('Скачивание PDF файла на сервер', 'info')
        update.message.reply_text('Скачивание PDF файла на сервер')
        document_file = update.message.document.get_file()
        pdf_path = os.path.join('downloads', f'{document_file.file_id}.pdf')
        document_file.download(pdf_path)
        update.message.reply_text('PDF файл скачан')
        self.logger.log_message('PDF файл скачан', 'info')

        self.current_status[self.current_command] = 'pending'
        self.clean_up_previous_files(self.current_command)

        update.message.reply_text('Запущен парсинг страниц')
        self.logger.log_message('Запущен парсинг страниц', 'info')
        threading.Thread(target=self.process_pdf, args=(pdf_path, document_file.file_id)).start()
        update.message.reply_text('Парсинг закончен')

    def process_pdf(self, pdf_path, file_id):
        results = {}
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                image_name = f'{self.current_command}_{page_num + 1}.jpg'
                image_path = os.path.join('downloads', image_name)
                pix.save(image_path)
                # update.message.reply_text(f'Сохранена страница {page_num + 1} из {len(doc)}')
                self.logger.log_message(f'Сохранена страница {page_num + 1} из {len(doc)}', 'info')

                
                response_text = self.send_image_to_openai(image_path)
                self.logger.log_message(f'Пришел ответ OpenAI', 'info')
                results[image_name] = response_text
                self.logger.log_message(f'OpenAI вернул ответ {response_text}', 'info')
                # update.message.reply_text(f'OpenAI вернул ответ')
            
            results_path = os.path.join('downloads', f'{self.current_command}_results.json')
            with open(results_path, 'w') as json_file:
                json.dump(results, json_file, ensure_ascii=False, indent=4)
            
            self.current_status[self.current_command] = 'completed'
        except Exception as e:
            self.current_status[self.current_command] = f'error: {e}'
            self.logger.log_message(f'Ошибка при обработке PDF файла: {e}', 'info')
            # update.message.reply_text(f'Ошибка при обработке PDF файла: {e}')

    def clean_up_previous_files(self, command):
        for filename in os.listdir('downloads'):
            if filename.startswith(command):
                file_path = os.path.join('downloads', filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def send_image_to_openai(self, image_path):
        base64_image = self.encode_image(image_path)
        self.logger.log_message('Ушел запрос на OpenAI', 'info')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('OPENAI_KEY')}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": config.PROMPT
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_json = response.json()

        if 'choices' not in response_json:
            self.logger.log_message(f'Ошибка при обработке PDF файла: {response_json}', 'error')

        return response_json['choices'][0]['message']['content'] if 'choices' in response_json else 'Ошибка получения ответа от API'

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def set_mission_status(self):
        for item in self.missionlist:
            self.current_status[item] = 'not started'

    def log_all_messages(self, update: Update, context: CallbackContext) -> None:
        self.logger.log(update.message.text)