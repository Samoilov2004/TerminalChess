# src/game_with_hints.py
import chess
from game_vs_stockfish import GameVsStockfish

class GameWithHints(GameVsStockfish):
    """
    Расширенная версия игры, которая позволяет отменять ходы и просить подсказки.
    """
    def __init__(self, player_color: str, skill_level: int, lang: str = "ru"):
        # Вызываем конструктор родительского класса
        super().__init__(player_color, skill_level, lang)
        # Увеличим время на анализ для получения нескольких вариантов
        self.engine.search_time = 0.5 

    def _player_turn(self):
        """
        Переопределяем ход игрока, чтобы добавить команды 'undo' и 'hint'.
        """
        move_made = False
        while not move_made:
            try:
                # Используем новую строку-приглашение из локализации
                prompt = self.localizer.get("your_move_prompt_hints")
                user_input = input(prompt).strip().lower()

                if user_input == self.localizer.get("exit_command"):
                    raise KeyboardInterrupt
                
                elif user_input == self.localizer.get("command_undo"):
                    # Отменяем ход ИИ и ход игрока
                    self.board.undo_move()
                    self.board.undo_move()
                    # После отмены хода нужно перерисовать доску, поэтому выходим из цикла
                    # чтобы главный цикл в run() сделал это за нас
                    self.last_move = None # Сбрасываем подсветку последнего хода
                    return # Выходим из _player_turn

                elif user_input == self.localizer.get("command_hint"):
                    self._show_hints()
                    # После подсказки не выходим, игрок все еще должен сделать ход
                
                else:
                    # Если это не команда, пытаемся обработать как ход
                    move = self._parse_user_input(user_input)
                    if move in self.board.get_legal_moves():
                        self.board.make_move(move)
                        self.last_move = move
                        move_made = True
                    else:
                        print(self.localizer.get("illegal_move"))

            except ValueError as e:
                print(self.localizer.get("input_error", error=e))
            except KeyboardInterrupt:
                print("\n" + self.localizer.get("exit_message"))
                self.board.halfmove_clock = 9999 
                move_made = True

    def _show_hints(self):
        """Запрашивает у движка и выводит 3 лучших хода."""
        print(self.localizer.get("ai_thinking"))
        lib_board = self.engine._convert_to_lib_board(self.board)
        
        print(self.localizer.get("hint_header"))
        try:
            # Используем режим анализа для получения нескольких вариантов
            with self.engine.engine.analysis(lib_board, chess.engine.Limit(time=self.engine.search_time), multipv=3) as analysis:
                for i, info in enumerate(analysis):
                    # `info` содержит много данных, нам нужен первый ход из главной линии
                    move = info.get("pv")[0]
                    score = info.get("score").relative
                    print(f"  {i+1}. Ход: {move.uci()}, Оценка: {score}")

        except Exception as e:
            print(f"Не удалось получить подсказки: {e}")
        print("-" * 35)

