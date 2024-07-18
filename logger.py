import logging

class CustomLogger:
    def __init__(self, level=logging.INFO):
        log_file = 'logfile.log'
        self.logger = logging.getLogger('custom_logger')
        self.logger.setLevel(level)
        self.logger.propagate = False  # Отключение пропагирования

        # Проверка, есть ли уже обработчики у логгера
        if not self.logger.handlers:
            # Создание обработчика для записи логов в файл
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)

            # Создание обработчика для вывода логов в консоль
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Создание форматтера и добавление его к обработчикам
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Добавление обработчиков к логгеру
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_message(self, message, status):
        """
        Запись логов с различными уровнями важности.

        Args:
            message (str): Сообщение для записи.
            status (str): Уровень важности сообщения ('info', 'warning', 'error').
        """
        if status == 'info':
            self.logger.info(message)
        elif status == 'warning':
            self.logger.warning(message)
        elif status == 'error':
            self.logger.error(message)
        else:
            self.logger.debug(message)  # По умолчанию логгировать как debug