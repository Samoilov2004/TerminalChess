# src/game_with_hints.py
import chess
from game_vs_stockfish import GameVsStockfish  # Наследуемся от базовой игры

class GameWithHints(GameVsStockfish):
    """Расширенная версия игры с командами 'undo' и 'hint'."""
    def __init__(self, player_color: str, skill_level: int, lang: str = "ru"):
        super().__init__(player_color, skill_level, lang)
        self.engine.search_time = 0.5 

    def _player_turn(self) -> bool:
        """Переопределенный метод для обработки undo/hint и выхода."""
        while True:
            try:
                prompt = self.localizer.get("your_move_prompt_hints")
                user_input = input(prompt).strip().lower()

                # Команда выхода
                if user_input == self.localizer.get("exit_command"):
                    save_prompt = self.localizer.get("save_and_quit_prompt")
                    choice = input(save_prompt).lower().strip()
                    return False if choice == self.localizer.get("confirm_yes") else True
                
                # Команда отмены хода
                elif user_input == self.localizer.get("command_undo"):
                    if len(self.board.history) >= 2:
                        self.board.undo_move() # Отменяем ход ИИ
                        self.board.undo_move() # Отменяем свой ход
                        self.last_move = None
                    else:
                        print(f"\n{self.localizer.get('illegal_move')}") # Можно использовать эту же ошибку
                    return True # Возвращаемся в игровой цикл для перерисовки
                
                # Команда подсказки
                elif user_input == self.localizer.get("command_hint"):
                    self._show_hints()
                    continue # Снова ждем ввода от игрока
                
                # Обычный ход
                else:
                    move = self._parse_user_input(user_input)
                    if move in self.board.get_legal_moves():
                        self.board.make_move(move)
                        self.last_move = move
                        return True
                    else:
                        print(self.localizer.get("illegal_move"))
            except ValueError as e:
                print(self.localizer.get("input_error", error=e))

    def _show_hints(self):
        """Запрашивает у движка и выводит 3 лучших хода."""
        print(self.localizer.get("ai_thinking"))
        from game_vs_stockfish import board_to_fen
        current_fen = board_to_fen(self.board)
        lib_board = chess.Board(current_fen)
        print("\n" + self.localizer.get("hint_header"))
        try:
            info = self.engine.engine.analyse(
                lib_board, 
                chess.engine.Limit(time=self.engine.search_time), 
                multipv=3
            )
            if not info:
                print("  " + self.localizer.get("illegal_move")) # Используем общую ошибку
            for i, move_info in enumerate(info):
                if move_info.get("pv"):
                    move = move_info["pv"][0]
                    score = move_info["score"].relative
                    score_points = score.score() / 100.0 if score.score() is not None else "Мат"
                    print(f"  {i+1}. Ход: {move.uci()}, Оценка: {score_points:+.2f}")
                else: break
        except Exception as e:
            print(f"Не удалось получить подсказки: {e}")
        print("-" * 40)
        input(self.localizer.get("press_enter_to_continue"))

