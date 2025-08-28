import os
import sys

# --- Важная часть: добавляем 'src' в путь, чтобы импорты работали ---
# Это позволяет запускать main.py из корневой папки проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# ---------------------------------------------------------------------

from src.localization import LocalizationManager
from src.game_vs_stockfish import GameVsStockfish, WHITE, BLACK
from src.game_with_hints import GameWithHints

def clear_screen():
    """Очищает экран терминала."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
    """Выводит красивое приветственное сообщение."""
    clear_screen()
    print("*" * 40)
    print("*                                      *")
    print("*         ДОБРО ПОЖАЛОВАТЬ В           *")
    print("*         ТЕРМИНАЛЬНЫЕ ШАХМАТЫ         *")
    print("*                                      *")
    print("*" * 40)
    print("\nWelcome to Terminal Chess!\n")

def select_language(initial_run=True):
    """Запрашивает выбор языка при старте."""
    print("Выберите язык / Select language:")
    print("  1. Русский")
    print("  2. English")
    print("  3. Français")
    print("  4. Español")
    print("  5. 中国语文科")
    while True:
        choice = input(">> ").strip()
        if choice == '1':
            return "ru"
        elif choice == '2':
            return "en"
        elif choice == '3':
            return "fr"
        elif choice == '4':
            return "es"
        elif choice == '5':
            return "zh"

def get_game_settings(localizer: LocalizationManager):
    """Запрашивает у пользователя цвет и сложность."""
    clear_screen()
    while True:
        choice = input(localizer.get("color_choice_prompt")).strip().lower()
        if choice in ['w', 'b', 'б', 'ч']:
            player_color = BLACK if choice in ['b', 'ч'] else WHITE
            break
    
    while True:
        try:
            skill = int(input(localizer.get("skill_choice_prompt")).strip())
            if 0 <= skill <= 20:
                break
        except ValueError:
            pass
    
    return player_color, skill

def start_game(game_class, localizer: LocalizationManager, config: dict):
    """Запускает выбранный режим игры с текущими настройками."""
    player_color, skill_level = get_game_settings(localizer)
    
    # Создаем экземпляр игры...
    game = game_class(
        player_color=player_color,
        skill_level=skill_level,
        lang=localizer.lang
    )
    # ...и применяем к нему текущие настройки!
    game.render_config = config
    
    game.run()
    input(localizer.get("press_enter_to_continue"))

def show_settings(localizer: LocalizationManager, config: dict) -> tuple:
    """Интерактивное меню настроек. Возвращает обновленные (localizer, config)."""
    while True:
        clear_screen()
        print(f"--- {localizer.get('settings_menu_title')} ---")

        # Получаем статусы и стили для отображения в меню
        highlight_status = localizer.get('status_on') if config['highlighting'] else localizer.get('status_off')
        flip_status = localizer.get('status_on') if config['flip_board'] else localizer.get('status_off')
        piece_style_key = 'piece_style_unicode' if config['piece_set'] == 'unicode' else 'piece_style_ascii'
        piece_style = localizer.get(piece_style_key)

        # Выводим опции
        print(localizer.get('settings_option_language'))
        print(localizer.get('settings_option_highlight', status=highlight_status))
        print(localizer.get('settings_option_flip', status=flip_status))
        print(localizer.get('settings_option_pieces', style=piece_style))
        print(localizer.get('settings_option_future1'))
        print(localizer.get('settings_option_future2'))
        print(localizer.get('settings_option_back'))
        
        print("\n" + ("-"*15))
        print(localizer.get("author_credits"))
        print("-" * 15)

        choice = input(">> ").strip()

        if choice == '1':
            lang_code = select_language(initial_run=False)
            localizer = LocalizationManager(lang=lang_code)
            # Цикл продолжится, и меню перерисуется на новом языке
        elif choice == '2':
            config['highlighting'] = not config['highlighting']
        elif choice == '3':
            config['flip_board'] = not config['flip_board']
        elif choice == '4':
            config['piece_set'] = 'ascii' if config['piece_set'] == 'unicode' else 'unicode'
        elif choice == '5' or choice == '6':
            # Заглушки для будущих фич
            input("\nЭта функция находится в разработке. Нажмите Enter для возврата.")
        elif choice == '7':
            break # Выход из меню настроек
        else:
            print(localizer.get("invalid_settings_choice"))
            input()

    return localizer, config


def main_menu(localizer: LocalizationManager, config: dict):
    """Главный цикл меню. Теперь принимает и передает config."""
    while True:
        clear_screen()
        print(f"--- {localizer.get('main_menu_title')} ---")
        print(localizer.get('menu_option_standard'))
        print(localizer.get('menu_option_hints'))
        print(localizer.get('menu_option_settings'))
        print(localizer.get('menu_option_quit'))
        print("-" * (len(localizer.get('main_menu_title')) + 6))
        
        choice = input(">> ").strip()

        if choice == '1':
            start_game(GameVsStockfish, localizer, config)
        elif choice == '2':
            start_game(GameWithHints, localizer, config)
        elif choice == '3':
            # Меню настроек теперь может менять и localizer, и config
            localizer, config = show_settings(localizer, config)
        elif choice == '4':
            break
        else:
            print(localizer.get("invalid_menu_choice"))
            input()

if __name__ == "__main__":
    print_welcome()
    lang_code = select_language()
    
    # Инициализируем локализацию и конфиг здесь, чтобы передавать их по всему приложению
    localizer = LocalizationManager(lang=lang_code)
    config = {
        'highlighting': True,      # Новая настройка для подсветки
        'flip_board': True,
        'piece_set': 'unicode'
    }

    main_menu(localizer, config)
    clear_screen()