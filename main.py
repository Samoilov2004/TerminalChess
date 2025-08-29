import os
import sys
import json

# Добавляем 'src' в путь
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from localization import LocalizationManager
from game_vs_stockfish import GameVsStockfish, WHITE, BLACK, board_to_fen
from game_with_hints import GameWithHints
from Board import Board

# Константы для путей
USER_DATA_DIR = "user_data"
SETTINGS_FILE = os.path.join(USER_DATA_DIR, "settings.json")
SAVED_GAME_FILE = os.path.join(USER_DATA_DIR, "saved_game.json")

def ensure_user_data_dir():
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

def save_config(config: dict, lang: str):
    ensure_user_data_dir()
    data = {"language": lang, "config": config}
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_config() -> tuple:
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        default_config, _ = get_default_config()
        loaded_config = data.get("config", {})
        default_config.update(loaded_config)
        return default_config, data.get("language")
    except (FileNotFoundError, json.JSONDecodeError):
        default_config, _ = get_default_config()
        return default_config, None

def get_default_config() -> tuple:
    config = {
        'highlighting': True, 'flip_board': True,
        'piece_set': 'unicode', 'board_style': 'classic'
    }
    lang = "ru"
    return config, lang

def save_game_state(game):
    """Сохраняет состояние текущей игры в JSON файл."""
    ensure_user_data_dir()
    # Собираем все необходимые данные для воссоздания игры
    state = {
        "game_type": game.__class__.__name__,
        "player_color": game.player_color,
        "skill_level": game.engine.skill_level if hasattr(game.engine, 'skill_level') else 5,
        "lang": game.localizer.lang,
        "fen": board_to_fen(game.board) # Самое важное - состояние доски
    }
    with open(SAVED_GAME_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)
    print(game.localizer.get("game_saved_message"))

def continue_game(config: dict, localizer: LocalizationManager):
    """Загружает сохраненную игру и передает управление в start_game_instance."""
    if not os.path.exists(SAVED_GAME_FILE):
        print(localizer.get("no_saved_game"))
        input(localizer.get("press_enter_to_continue"))
        return

    try:
        with open(SAVED_GAME_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        if os.path.exists(SAVED_GAME_FILE):
            os.remove(SAVED_GAME_FILE) # Удаляем битый файл
        return

    # Определяем, какой класс игры нужно создать (обычный или с подсказками)
    game_class = GameVsStockfish if state.get('game_type') == 'GameVsStockfish' else GameWithHints
    
    # Создаем экземпляр игры с сохраненными параметрами
    game = game_class(
        player_color=state['player_color'],
        skill_level=state['skill_level'],
        lang=state['lang']
    )
    # Применяем текущие настройки отображения из главного меню
    game.render_config = config
    # Восстанавливаем позицию на доске из FEN-строки
    game.board.load_from_fen(state['fen'])
    
    # Запускаем игровой цикл для этого экземпляра
    start_game_instance(game, localizer)

def start_game_instance(game_instance, localizer: LocalizationManager):
    game_active = True
    try:
        while game_instance.board.get_game_status() == 'in_progress' and game_active:
            game_instance.renderer.draw_board(game_instance.board, game_instance.last_move)
            if game_instance.board.color_to_move == game_instance.player_color:
                game_active = game_instance._player_turn() # Correctly calls the overridden method.
            else:
                game_instance._ai_turn()
        
        # Если вышли из цикла по причине конца игры (мат, пат, ничья), удаляем сохранение
        if game_active and os.path.exists(SAVED_GAME_FILE):
            os.remove(SAVED_GAME_FILE)

    except Exception:
        # В случае любой ошибки, корректно закрываем движок
        game_instance.engine.close()
        raise # и снова выбрасываем ошибку, чтобы увидеть ее в консоли

    finally:
        # Этот блок выполнится всегда
        if not game_active: # Если игрок решил выйти (game_active стало False)
            save_game_state(game_instance)
        
        # Закрываем движок в любом случае
        game_instance.engine.close()
        # Показываем финальную доску
        game_instance.renderer.draw_board(game_instance.board)
        input(localizer.get("press_enter_to_continue"))

def start_new_game(game_class, localizer: LocalizationManager, config: dict):
    """
    Запрашивает настройки для новой игры, создает экземпляр и запускает его.
    """
    player_color, skill_level = get_game_settings(localizer)
    game = game_class(
        player_color=player_color,
        skill_level=skill_level,
        lang=localizer.lang
    )
    # Применяем текущие настройки отображения из главного меню
    game.render_config = config
    
    # Запускаем игровой цикл для нового экземпляра
    start_game_instance(game, localizer)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
    clear_screen()
    print("*" * 40 + "\n*                                      *\n*         ДОБРО ПОЖАЛОВАТЬ В           *\n*         ТЕРМИНАЛЬНЫЕ ШАХМАТЫ         *\n*                                      *\n" + "*" * 40 + "\n\nWelcome to Terminal Chess!\n")

def select_language(initial_run=True):
    if not initial_run:
        print("\n" + ("-" * 20))
        print("Смена языка / Change language:")
    print("  1. Русский 🇷🇺\n  2. English 🇬🇧/🇺🇸\n  3. Español 🇪🇸\n  4. Français 🇫🇷\n  5. 中文 🇨🇳")
    while True:
        choice = input(">> ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return {'1': 'ru', '2': 'en', '3': 'es', '4': 'fr', '5': 'zh'}[choice]

def get_game_settings(localizer: LocalizationManager):
    """Запрашивает у игрока цвет и сложность ИИ."""
    clear_screen()
    # Выбор цвета
    while True:
        prompt = localizer.get("choose_color_prompt")
        choice = input(prompt).strip().lower()
        # Добавим больше вариантов для разных языков (w/b, б/ч, n/b и т.д.)
        if choice in ['w', 'b', 'б', 'ч', 'w', 'n', 'b', 'n', '白', '黑']:
            player_color = BLACK if choice in ['b', 'ч', 'n', '黑'] else WHITE
            break
        else:
            print(localizer.get("invalid_menu_choice"))

    # Выбор сложности
    while True:
        try:
            prompt = localizer.get("choose_skill_level")
            skill = int(input(prompt).strip())
            if 0 <= skill <= 20: 
                break
            else:
                print(localizer.get("invalid_menu_choice"))
        except ValueError:
            print(localizer.get("invalid_menu_choice"))
            
    return player_color, skill


# --- ВОССТАНОВЛЕННАЯ ФУНКЦИЯ НАСТРОЕК ---
def show_settings(localizer: LocalizationManager, config: dict) -> tuple:
    """Интерактивное меню настроек. Возвращает обновленные (localizer, config)."""
    while True:
        clear_screen()
        print(f"--- {localizer.get('settings_menu_title')} ---")

        highlight_status = localizer.get('status_on') if config.get('highlighting', True) else localizer.get('status_off')
        flip_status = localizer.get('status_on') if config.get('flip_board', True) else localizer.get('status_off')
        
        piece_style_key = 'piece_style_unicode' if config.get('piece_set') == 'unicode' else 'piece_style_ascii'
        piece_style = localizer.get(piece_style_key)

        board_style_key = 'board_style_pretty' if config.get('board_style') == 'pretty' else 'board_style_classic'
        board_style = localizer.get(board_style_key)

        # Выводим опции с правильной нумерацией
        print(f"1. {localizer.get('settings_option_language')}")
        print(f"2. {localizer.get('settings_option_highlight', status=highlight_status)}")
        print(f"3. {localizer.get('settings_option_flip', status=flip_status)}")
        print(f"4. {localizer.get('settings_option_pieces', style=piece_style)}")
        print(f"5. {localizer.get('settings_option_board_style', style=board_style)}")
        print(f"6. {localizer.get('settings_option_future1')}")
        print(f"7. {localizer.get('settings_option_future2')}")
        print(f"8. {localizer.get('settings_option_back')}")
        
        print("\n" + ("-"*25))
        print(localizer.get("author_credits"))
        print("-" * 25)

        choice = input(">> ").strip()

        if choice == '1':
            lang_code = select_language(initial_run=False)
            localizer = LocalizationManager(lang=lang_code)
        elif choice == '2':
            config['highlighting'] = not config.get('highlighting', True)
        elif choice == '3':
            config['flip_board'] = not config.get('flip_board', True)
        elif choice == '4':
            config['piece_set'] = 'ascii' if config.get('piece_set') == 'unicode' else 'unicode'
        elif choice == '5':
             config['board_style'] = 'pretty' if config.get('board_style') == 'classic' else 'classic'
        elif choice == '6' or choice == '7':
            input(f"\n{localizer.get('dev_notice')}")
        elif choice == '8':
            break # Выход из меню настроек
        else:
            print(localizer.get("invalid_settings_choice"))
            input()

    return localizer, config
# --- КОНЕЦ ВОССТАНОВЛЕННОЙ ФУНКЦИИ ---


def main_menu(localizer: LocalizationManager, config: dict):
    """Главный цикл меню."""
    while True:
        clear_screen()
        print(f"--- {localizer.get('main_menu_title')} ---")
        if os.path.exists(SAVED_GAME_FILE):
             print(localizer.get('menu_option_continue'))
        print(localizer.get('menu_option_standard'))
        print(localizer.get('menu_option_hints'))
        print(localizer.get('menu_option_settings'))
        print(localizer.get('menu_option_quit'))
        print("-" * (len(localizer.get('main_menu_title')) + 6))
        
        choice = input(">> ").strip()
        if choice == '0' and os.path.exists(SAVED_GAME_FILE):
            continue_game(config, localizer)
        elif choice == '1':
            start_new_game(GameVsStockfish, localizer, config)
        elif choice == '2':
            start_new_game(GameWithHints, localizer, config)
        elif choice == '3':
            localizer, config = show_settings(localizer, config)
            save_config(config, localizer.lang)
        elif choice == '4':
            break
        else:
            print(localizer.get("invalid_menu_choice"))
            input()

if __name__ == "__main__":
    ensure_user_data_dir()
    config, lang_code = load_config()

    if lang_code is None:
        print_welcome()
        lang_code = select_language()
        save_config(config, lang_code)

    localizer = LocalizationManager(lang=lang_code)
    
    main_menu(localizer, config)
    clear_screen()