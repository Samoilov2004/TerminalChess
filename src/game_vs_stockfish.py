import chess
from Board import Board, WHITE, BLACK
from engine.stockfish_engine import StockfishEngine
from renderer import TerminalRenderer # Assuming renderer.py is on the same level
from localization import LocalizationManager
from pieces import queen # Needed for promotion

class GameVsStockfish:
    """
    Класс, управляющий игровым процессом партии человека против Stockfish.
    """
    def __init__(self, player_color: str, skill_level: int, lang: str = "ru"):
        if player_color not in [WHITE, BLACK]:
            raise ValueError("Player color must be 'w' or 'b'")

        # Инициализация всех компонентов
        self.localizer = LocalizationManager(lang=lang)
        self.board = Board()
        self.engine = StockfishEngine(skill_level=skill_level)
        self.player_color = player_color
        
        # Гибкие настройки для отображения
        self.render_config = {
            'flip_board': True,      # Переворачивать доску за черных?
            'piece_set': 'unicode'   # или 'ascii'
        }
        self.renderer = TerminalRenderer(self.render_config, self.localizer)
        self.last_move = None

    def run(self):
        """Основной игровой цикл."""
        try:
            while self.board.get_game_status() == 'in_progress':
                # 1. Отрисовка текущего состояния
                self.renderer.draw_board(self.board, self.last_move)
                
                # 2. Определяем, чей ход
                if self.board.color_to_move == self.player_color:
                    self._player_turn()
                else:
                    self._ai_turn()
        finally:
            # 3. Конец игры
            self.renderer.draw_board(self.board) # Показать финальную позицию
            print("="*25)
            # Важно! Всегда закрывать движок, чтобы не оставлять висящих процессов
            self.engine.close()
            print("Игра завершена. Движок Stockfish остановлен.")

    def _player_turn(self):
        """Обрабатывает ход игрока."""
        move_made = False
        while not move_made:
            try:
                prompt = self.localizer.get("your_move_prompt")
                user_input = input(prompt)

                if user_input.lower() == self.localizer.get("exit_command"):
                    raise KeyboardInterrupt # Простой способ выйти из цикла

                move = self._parse_user_input(user_input)

                if move in self.board.get_legal_moves():
                    # TODO: Обработка превращения пешки для хода игрока
                    self.board.make_move(move)
                    self.last_move = move
                    move_made = True
                else:
                    print(self.localizer.get("illegal_move"))
            except ValueError as e:
                print(self.localizer.get("input_error", error=e))
            except KeyboardInterrupt:
                print("\nВыход из игры.")
                # Выход из игрового цикла
                self.board.halfmove_clock = 9999 # "Завершаем" игру
                move_made = True

    def _ai_turn(self):
        """Обрабатывает ход компьютера."""
        print(self.localizer.get("ai_thinking"))
        best_move_lib = self.engine.find_best_move(self.board)
        
        our_move = self._convert_lib_move_to_our(best_move_lib)
        
        # Обработка превращения пешки для хода ИИ
        promo_class = None
        if best_move_lib.promotion:
            if best_move_lib.promotion == chess.QUEEN:
                promo_class = queen.Queen
            # ... можно добавить другие фигуры, но Stockfish обычно выбирает ферзя
        
        self.board.make_move(our_move, promotion_piece_class=promo_class)
        self.last_move = our_move

    def _parse_user_input(self, uci_move: str) -> tuple:
        """Конвертирует ход из нотации 'e2e4' в наши координаты ((6,4), (4,4))."""
        uci_move = uci_move.strip().lower()
        if len(uci_move) < 4:
            raise ValueError(self.localizer.get("invalid_move_length"))
        
        start_col = 'abcdefgh'.find(uci_move[0])
        start_row = 8 - int(uci_move[1])
        end_col = 'abcdefgh'.find(uci_move[2])
        end_row = 8 - int(uci_move[3])

        if -1 in [start_col, start_row, end_col, end_row] or not self.board.is_on_board((start_row, start_col)):
            raise ValueError(self.localizer.get("invalid_coordinates"))
        
        return ((start_row, start_col), (end_row, end_col))

    def _convert_lib_move_to_our(self, lib_move: chess.Move) -> tuple:
        """Конвертирует ход из формата python-chess в наш формат, используя UCI-строку."""
        return self._parse_user_input(lib_move.uci())