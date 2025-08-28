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

def select_language():
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
    # Выбор цвета
    while True:
        choice = input(localizer.get("color_choice_prompt")).strip().lower()
        if choice in ['w', 'b', 'б', 'ч']:
            player_color = BLACK if choice in ['b', 'ч'] else WHITE
            break
    
    # Выбор сложности
    while True:
        try:
            skill = int(input(localizer.get("skill_choice_prompt")).strip())
            if 0 <= skill <= 20:
                break
        except ValueError:
            pass # Игнорируем нечисловой ввод, цикл продолжится
    
    return player_color, skill

def start_game(game_class, localizer: LocalizationManager):
    """Запускает выбранный режим игры."""
    player_color, skill_level = get_game_settings(localizer)
    
    game = game_class(
        player_color=player_color,
        skill_level=skill_level,
        lang=localizer.lang
    )
    game.run()
    input(localizer.get("press_enter_to_continue"))

def show_settings(localizer: LocalizationManager):
    """Заглушка для меню настроек."""
    clear_screen()
    print(localizer.get("settings_placeholder"))
    input()


def main_menu(localizer: LocalizationManager):
    """Главный цикл меню."""
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
            start_game(GameVsStockfish, localizer)
        elif choice == '2':
            start_game(GameWithHints, localizer)
        elif choice == '3':
            show_settings(localizer)
        elif choice == '4':
            break
        else:
            print(localizer.get("invalid_menu_choice"))
            input()

if __name__ == "__main__":
    print_welcome()
    lang_code = select_language()
    localizer = LocalizationManager(lang=lang_code)
    main_menu(localizer)
    clear_screen()