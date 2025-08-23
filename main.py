# main.py

import os
import json
import time

from src.board import ChessBoard
from src.game import Game 

# --- КОНФИГУРАЦИЯ ---
LOCALES_DIR = 'locales' # Папка с файлами переводов
settings = { 'lang': 'ru' }

loaded_texts = {}
available_languages = []

def load_locales():
    """Находит все .json файлы в папке locales и загружает их."""
    global available_languages
    available_languages = []

    try:
        if not os.path.isdir(LOCALES_DIR):
            raise FileNotFoundError
            
        for filename in sorted(os.listdir(LOCALES_DIR)): 
            if filename.endswith('.json'):
                lang_code = filename.split('.')[0]
                available_languages.append(lang_code)
                filepath = os.path.join(LOCALES_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    loaded_texts[lang_code] = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Директория '{LOCALES_DIR}' не найдена или пуста.")
        print("Пожалуйста, создайте её и добавьте файлы локализации (например, ru.json, en.json).")
        time.sleep(5)
        exit()
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON файла: {e.doc} в строке {e.lineno}, колонке {e.colno}")
        time.sleep(5)
        exit()


def T(key, **kwargs):
    """
    Главная функция-переводчик. Берет ключ и возвращает текст на текущем языке.
    Поддерживает форматирование строк.
    Пример: T("checkmate", winner="Белые")
    """
    lang = settings.get('lang', 'en') # По умолчанию английский, если настройка слетела
    lang_texts = loaded_texts.get(lang, {})
    text_template = lang_texts.get(key, f"<{key}_NOT_FOUND>")
    
    if kwargs:
        return text_template.format(**kwargs)
    return text_template


def clear_screen():
    """Очищает экран консоли."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_dev_notice():
    """Показывает сообщение о том, что режим в разработке."""
    print(f"\n{T('dev_notice')}")
    time.sleep(2)

def settings_menu():
    """Меню для изменения настроек языка с выводом в столбик."""
    while True:
        clear_screen()
        
        current_lang_name = T("lang_name_flag")
        
        print(T("settings_title"))
        print(T("settings_lang", lang_name=current_lang_name))
        print(T("settings_back"))
        print("===================================")
        
        choice = input(T('choice')).strip()

        if choice == '1':
            # --- НАЧАЛО ИЗМЕНЕНИЙ ---

            clear_screen()
            print(T("lang_choice_prompt")) # 1. Выводим заголовок
            print("-" * 20)
            
            # 2. В цикле выводим каждый язык на новой строке
            for i, lang_code in enumerate(available_languages, 1):
                lang_name_with_flag = loaded_texts.get(lang_code, {}).get("lang_name_flag", lang_code)
                print(f"  {i}. {lang_name_with_flag}")
            
            print("-" * 20)
            
            # 3. Запрашиваем ввод у пользователя
            lang_choice = input(T('input_prompt')).strip()
            
            # Логика обработки выбора остается прежней
            try:
                chosen_index = int(lang_choice) - 1
                if 0 <= chosen_index < len(available_languages):
                    settings['lang'] = available_languages[chosen_index]
            except ValueError:
                pass # Игнорируем нечисловой ввод

        elif choice == '2':
            break

def play_human_vs_human():
    game = Game()
    
    while True:
        clear_screen()
        print(game.board) 
        
        if game.status != "ongoing":
            print(f"\n{T('game_over_title')}")
            if game.status == "checkmate":
                winner_color = "black" if game.board.turn == "white" else "white"
                winner_name_key = 'white_player' if winner_color == 'white' else 'black_player'
                print(T('checkmate', winner=T(winner_name_key)))
            else:
                print(T(game.status, default=f"Ничья ({game.status})"))
            break
        
        player_name = T('white_player') if game.board.turn == 'white' else T('black_player')
        move_str = input(f"\n{T('player_turn', player=player_name)}").strip().lower()

        if move_str in ['exit', 'quit']: break
        
        if not game.make_move(move_str):
            print(f"\n{T('illegal_move')}"); time.sleep(2)
        else:
            print(T(game.status, default=f"Ничья ({game.status})"))



def main_menu():
    """Отображает главное меню и обрабатывает выбор пользователя."""
    clear_screen()
    print(T("welcome_title"))
    print("---------------------------------------")
    print(T("welcome_rules"))
    input(T('press_enter'))
    
    while True:
        clear_screen()
        print(T("menu_title"))
        print(T("menu_play_hvh"))
        print(T("menu_play_ai"))
        print(T("menu_analysis"))
        print(T("menu_settings"))
        print(T("menu_exit"))
        print("======================================")
        
        choice = input(T('choice')).strip()

        if choice == '1':
            play_human_vs_human()
            input(T('back_to_menu'))
        elif choice in ['2', '3']:
            show_dev_notice()
        elif choice == '4':
            settings_menu()
        elif choice == '5':
            print(T("goodbye"))
            break
        else:
            print(f"\n{T('illegal_move')}")
            time.sleep(2)

if __name__ == "__main__":
    load_locales()
    
    if not loaded_texts or not available_languages:
        print("Завершение работы из-за отсутствия файлов локализации.")
    else:
        main_menu()
