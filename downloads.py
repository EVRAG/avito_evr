import os
import time
import requests

# URL вашего Flask сервера
base_url = 'http://0.0.0.0:6000'

# Директория для сохранения скачанных файлов
download_directory = 'downloaded_files'
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Список миссий для проверки
missions = ['mission1', 'mission2', 'mission3']
completed_missions = set()

def check_and_download_files(mission):
    # Получение списка файлов для миссии
    status_url = f'{base_url}/status/{mission}'
    response = requests.get(status_url)

    # Проверка ответа
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'completed':
            files = data['files']
            print(f"Файлы для {mission}: {files}")

            # Скачивание каждого файла
            for file in files:
                download_url = f'{base_url}/download/{file}'
                file_response = requests.get(download_url)

                if file_response.status_code == 200:
                    # Сохранение файла локально
                    file_path = os.path.join(download_directory, file)
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                    print(f"Файл {file} успешно скачан")
                else:
                    print(f"Ошибка при скачивании файла {file}: {file_response.status_code}")
            
            # Добавляем миссию в завершенные
            completed_missions.add(mission)
        else:
            print(f"Статус {mission}: {data['status']}")
    else:
        print(f"Ошибка при получении файлов для {mission}: {response.status_code}, {response.text}")

def main():
    while True:
        for mission in missions:
            if mission not in completed_missions:
                check_and_download_files(mission)
        # Ожидание 20 секунд перед следующей проверкой
        time.sleep(5)

if __name__ == '__main__':
    main()