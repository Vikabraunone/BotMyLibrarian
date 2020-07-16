import requests
import mytoken
import os
from time import sleep

token = mytoken.token

URL = 'https://api.telegram.org/bot{}/'.format(token)

global last_update_id
last_update_id = 0

global last_comand
last_comand = ''

global str_format
str_format = '№{}. {}\n'

def get_updates():
    url = URL + "getupdates"
    r = requests.get(url)
    return r.json()

def get_message():
    data = get_updates()
    last_object = data['result'][-1]
    current_update_id = last_object['update_id']
    global last_update_id
    if last_update_id != current_update_id:
        last_update_id = current_update_id
        chat_id = last_object['message']['chat']['id']
        message_text = last_object['message']['text']
        message = {'chat_id': chat_id,
                   'text': message_text}
        return message
    return None

def send_message(chat_id, text='Напиши /help'):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    requests.get(url)

def read_file(filename):
    try:
        f = open(filename)
        result = f.read()
        f.close()
        return result
    except FileNotFoundError:
        print('Файл не найден: read_file')
        return None
    except Exception:
        print('Ошибка: read_file')
        return None

def read_lines_file(filename):
    try:
        f = open(filename, 'r')
        result = f.readlines()
        f.close()
        return result
    except FileNotFoundError:
        print('Файл не найден: read_lines_file')
        return None
    except Exception:
        print('Ошибка: read_lines_file')
        return None

def append_file(filename, text):
    try:
        lines = read_lines_file(filename)
        if lines is not None:
            global str_format
            f = open(filename, 'a')
            f.write(str_format.format(len(lines) + 1, text))
            f.close()
    except FileNotFoundError:
        print('Файл не найден: append_file')
        return None
    except Exception:
        print('Ошибка: append_file')
        return None

def write_file(filename, text):
    try:
        last_file_lines = read_lines_file(filename)
        global str_format
        if last_file_lines is None: #если старый список пуст
            f = open(filename, 'w')
            f.write(str_format.format(1, text))
            f.close()
        else:
            i = 1
            outfile = 'outfile.txt'
            f = open(outfile, 'w')
            for line in last_file_lines:
                if line[1] != text:
                    f.write(str_format.format(i, line[4:-1]))
                    i+=1
            f.close()
            os.remove(filename)
            os.rename(outfile, filename)
    except FileExistsError:
        print("Такой файл существует: write_file")
        return None
    except Exception:
        print("Ошибка: write_file")
        return None

def delete_books():
    try:
        filename = 'bot.txt'
        os.remove(filename)
    except Exception:
        print("Ошибка: delete_books")

def modify_books(text):
     global last_comand
     if last_comand == 'добавить':
         if os.path.exists('bot.txt'):
             append_file('bot.txt', text)
         else:
             write_file('bot.txt', text)
     elif last_comand == 'удалить':
         if text.isdigit():
             write_file('bot.txt', text)
         else:
             return False
     return True
            

def get_books():
    result = read_file('bot.txt')
    if result is None:
        return "Твой список книг пуст!"
    else:
        return "Твой список состоит из таких книг:\n{}".format(result)
     
def main():
    while True:
        answer = get_message()
        if answer is not None:
            chat_id = answer['chat_id']
            text = answer['text']
            global last_comand
            if '/help' in text:
                send_message(chat_id, """Привет, я твой личный библиотекарь! Напиши ДОБАВИТЬ, УДАЛИТЬ, чтобы редактировать список твоих книг.
Чтобы просмотреть весь список, напиши СПИСОК.
Чтобы очистить список, напиши УДАЛИТЬ СПИСОК.""")
                last_comand = ''
            elif last_comand:
                if (modify_books(text)):
                    last_comand = ''
                    send_message(chat_id, "Изменение списка прошло успешно.")
                    send_message(chat_id, get_books())
                else:
                    send_message(chat_id, "Это не число!")
            elif 'удалить список' in text.lower():
                delete_books()
                send_message(chat_id, get_books())
            elif 'добавить' in text.lower():
                last_comand = 'добавить'
                send_message(chat_id, 'Напиши название и автора. Например: "Война и мир" Толстой')
            elif 'удалить' in text.lower():
                last_comand = 'удалить'
                send_message(chat_id, get_books())
                send_message(chat_id, 'Напиши номер книги. Если ты хочешь удалить первую книгу в списке, напиши 1')
            elif 'список' in text.lower():
                send_message(chat_id, get_books())
            else:
                send_message(chat_id)
        sleep(2)

if __name__ == '__main__':
   main() 
