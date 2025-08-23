# main.py

import os
import json
import time
from src.ai_player import AIPlayer

from src.board import ChessBoard
from src.game import Game 

# --- КОНФИГУРАЦИЯ ---
LOCALES_DIR = 'locales'
settings = {
    'lang': 'ru',
    'confirm_move': False,
    'flip_board': False,
    'auto_queen': False,
    'piece_style': 'unicode'
}

PIECE_SETS = {
    'classic': {
        'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K', 'P': 'P',
        'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k', 'p': 'p',
        '.': '.'
    },
    'unicode': {
        'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
        'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
        '.': '·'
    }
}

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

def draw_board(board_obj, flip=False):
    """
    Рисует доску, используя выбранный в настройках стиль фигур.
    Корректно обрабатывает переворот доски.
    """
    # Получаем актуальный набор символов для фигур
    piece_set = PIECE_SETS.get(settings['piece_style'], PIECE_SETS['classic'])
    
    # --- 1. Определяем порядок, в котором мы будем перебирать ИНДЕКСЫ доски ---
    # Индексы в Python-списке всегда идут от 0 до 7 (сверху вниз)
    rank_indices = range(8) if not flip else range(7, -1, -1)
    
    # --- 2. Определяем, как будут выглядеть надписи ---
    files = "a b c d e f g h"
    if flip:
        # Если доска перевернута, буквы тоже должны идти в обратном порядке
        files = "h g f e d c b a"

    # --- 3. Рисуем "шапку" доски ---
    header = f'   {files}'
    separator = '  +-----------------+'
    board_str = header + "\n" + separator + "\n"

    # --- 4. Рисуем саму доску, ряд за рядом ---
    for r_idx in rank_indices:
        # r_idx - это индекс в self.board.board (от 0 до 7)
        # rank_num - это номер, который мы печатаем сбоку (от 1 до 8)
        rank_num = 8 - r_idx

        # Получаем сам ряд данных
        row_list = board_obj.board[r_idx]
        
        # Если доска перевернута, переворачиваем и сам ряд (h-файл становится первым)
        if flip:
            row_list = row_list[::-1]
            
        # Заменяем буквы на символы из выбранного "скина"
        display_row = [piece_set[p] for p in row_list]
        
        # Собираем все в одну строку
        board_str += f"{rank_num} | {' '.join(display_row)} | {rank_num}\n"
    
    # --- 5. Рисуем "подвал" и информацию об игре ---
    board_str += separator + "\n" + header + "\n"
    
    turn_color = "White" if board_obj.turn == 'white' else "Black"
    turn_num = board_obj.fullmove_number
    # Используем ключи локализации
    board_str += f"\n{T('turn_info', turn_num=turn_num, color=T(board_obj.turn + '_player'))}\n"

    if board_obj.is_in_check(board_obj.turn):
        board_str += f"{T('check_status')}\n"

    print(board_str)

def settings_menu():
    """Меню для изменения всех настроек."""
    while True:
        clear_screen()
        
        # Получаем статусы всех настроек для отображения
        lang_name = T("lang_name_flag")
        confirm_status = T("status_on") if settings['confirm_move'] else T("status_off")
        flip_status = T("status_on") if settings['flip_board'] else T("status_off")
        auto_queen_status = T("status_on") if settings['auto_queen'] else T("status_off")
        style_name = T(f"style_{settings['piece_style']}")

        print(T("settings_title"))
        print(T("settings_lang", lang_name=lang_name))
        print(T("settings_confirm_move", status=confirm_status)) # Убедитесь, что этот ключ есть в JSON
        print(T("settings_flip_board", status=flip_status))
        print(T("settings_auto_queen", status=auto_queen_status))
        print(T("settings_piece_style", style=style_name))
        print(T("settings_back")) # Этот ключ должен содержать верный номер
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
        elif choice == '2': # Подтверждение хода
            settings['confirm_move'] = not settings['confirm_move']
        elif choice == '3': # Переворот доски
            settings['flip_board'] = not settings['flip_board']
        elif choice == '4': # Авто-королева
            settings['auto_queen'] = not settings['auto_queen']
        if choice == '5': # Стиль фигур
            if settings['piece_style'] == 'classic':
                settings['piece_style'] = 'unicode'
            else:
                settings['piece_style'] = 'classic'
        elif choice == '6': # Назад
            break

def play_human_vs_human():
    game = Game()
    while True:
        clear_screen()
        should_flip = game.board.turn == 'black' and settings['flip_board']
        draw_board(game.board, flip=(game.board.turn == 'black' and settings['flip_board']))
                
        player_name = T('white_player') if game.board.turn == 'white' else T('black_player')
        move_str = input(f"\n{T('player_turn', player=player_name)}").strip().lower()

        if move_str in ['exit', 'quit']: break

        from_pos_str, to_pos_str = move_str[:2], move_str[2:4]
        from_pos = game.board._parse_pos(from_pos_str)
        if from_pos:
            piece = game.board.get_piece_at(from_pos)
            to_rank = to_pos_str[1]
            if piece.lower() == 'p' and (to_rank == '8' or to_rank == '1') and len(move_str) == 4 and settings['auto_queen']:
                move_str += 'q'
                print(f"Auto-queen: ход изменен на '{move_str}'")
                time.sleep(1)

        if not game.make_move(move_str):
            print(f"\n{T('illegal_move')}"); time.sleep(2)
            continue
            
        if settings['confirm_move']:
            clear_screen()
            print(game.board.get_board_string(flip=should_flip))
            confirmation = input(f"\n{T('confirm_prompt')}").strip().lower()
            if confirmation in ['n', 'no', 'нет', 'т']:
                game.undo_move()
                continue

def play_vs_stockfish():
    """Запускает игру Человек против ИИ."""
    # 1. Выбор сложности ИИ
    skill_level_choice = input(T('choose_skill_level', default="Выберите сложность ИИ (0-20, стандартно 5): ")).strip()
    skill_level = 5 # Значение по умолчанию
    if skill_level_choice.isdigit() and 0 <= int(skill_level_choice) <= 20:
        skill_level = int(skill_level_choice)

    # 2. Инициализация ИИ-игрока
    ai_player = AIPlayer(skill_level=skill_level)
    if not ai_player.engine:
        # Если движок не запустился, сообщение об ошибке уже выведено в AIPlayer
        time.sleep(3)
        return

    # 3. Выбор цвета игроком
    player_color = None
    while player_color not in ['white', 'black']:
        prompt = T('choose_color_prompt', default="За кого вы хотите играть? (б/белые или ч/черные): ")
        choice = input(prompt).strip().lower()
        if choice in ['w', 'white', 'белые', 'б']:
            player_color = 'white'
        elif choice in ['b', 'black', 'черные', 'ч']:
            player_color = 'black'

    # 4. Инициализация игры
    game = Game()
    
    try:
        # 5. Основной игровой цикл
        while game.status == "ongoing":
            clear_screen()
            should_flip = (player_color == 'black' and settings['flip_board'])
            draw_board(game.board, flip=(game.board.turn == 'black' and settings['flip_board']))

            # Определяем, чей сейчас ход
            is_human_turn = (game.board.turn == player_color)

            if is_human_turn:
                # --- Ход Человека ---
                player_name = T(player_color + '_player')
                move_str = input(f"\n{T('player_turn', player=player_name)}").strip().lower()
                
                if move_str in ['exit', 'quit']:
                    print(T('goodbye'))
                    break
                
                if not game.make_move(move_str):
                    print(f"\n{T('illegal_move')}")
                    time.sleep(2)
            else:
                # --- Ход ИИ ---
                print(f"\n{T('ai_thinking', default='ИИ думает...')}")
                
                fen = game.board.to_fen()
                ai_move = ai_player.get_best_move(fen, time_limit=0.5)
                
                if ai_move:
                    print(f"{T('ai_makes_move', default='ИИ делает ход')}: {ai_move}")
                    game.make_move(ai_move)
                    time.sleep(1.5) # Пауза, чтобы игрок успел увидеть ход ИИ
                else:
                    print(f"\n{T('ai_error', default='ИИ не смог сделать ход. Игра прервана.')}")
                    break
        
        # 6. Вывод результата после окончания цикла
        clear_screen()
        final_flip = (player_color == 'black' and settings['flip_board'])
        print(game.board.get_board_string(flip=final_flip))
        print(f"\n{T('game_over_title')}")
        
        if game.status == "checkmate":
            # Если игра закончилась матом, победитель - тот, кто НЕ должен ходить сейчас
            winner_color = "black" if game.board.turn == "white" else "white"
            winner_name_key = winner_color + '_player'
            print(T('checkmate', winner=T(winner_name_key)))
        else:
            # Для всех видов ничьей (stalemate, draw_repetition и т.д.)
            # Мы используем ключ, который хранится в game.status
            print(T(game.status, default=f"Ничья ({game.status})"))

    finally:
        # 7. ОБЯЗАТЕЛЬНО корректно завершаем работу движка
        ai_player.quit()


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
        print(T("menu_play_stockfish"))
        print(T("menu_analysis"))
        print(T("menu_settings"))
        print(T("menu_exit"))
        print("======================================")
        
        choice = input(T('choice')).strip()

        if choice == '1':
            play_human_vs_human()
            input(T('back_to_menu'))
        elif choice == '2':
            play_vs_stockfish()
            input(T('back_to_menu'))
        elif choice == '3':
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
