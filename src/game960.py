import chess
# Наследуемся от игры с подсказками, т.к. там уже есть undo/hint
from game_with_hints import GameWithHints
from Board import Board

class Game960(GameWithHints):
    """
    Класс для игры в Шахматы-960.
    Наследует все возможности игры с подсказками, но использует другую доску.
    """
    def __init__(self, player_color: str, skill_level: int, lang: str = "ru"):
        # Вызываем конструктор родителя, НО не даем ему создать доску
        super().__init__(player_color, skill_level, lang)
        
        # Создаем специальную доску для 960
        self.board = Board(is_chess960=True)
        
        # Выводим полезную информацию для игрока
        print("\n" + "="*40)
        print(self.localizer.get("chess960_cute_name"))
        print(self.localizer.get("chess960_rules_link"))
        print("="*40)
        input(self.localizer.get("press_enter_to_continue"))