import chess
from Board import Board, WHITE, BLACK
from engine.stockfish_engine import StockfishEngine
from renderer import TerminalRenderer
from localization import LocalizationManager
from pieces import queen

class GameVsStockfish:
    """
    Класс, управляющий игровым процессом партии человека против Stockfish.
    """
    def __init__(self, player_color: str, skill_level: int, lang: str = "ru"):
        self.localizer = LocalizationManager(lang=lang)
        
        if player_color not in [WHITE, BLACK]:
            raise ValueError(self.localizer.get("player_color_error"))

        # Теперь все компоненты получают локализатор при создании
        self.board = Board()
        self.engine = StockfishEngine(self.localizer, skill_level=skill_level)
        self.player_color = player_color
        
        self.render_config = {'flip_board': True, 'piece_set': 'unicode'}
        self.renderer = TerminalRenderer(self.render_config, self.localizer)
        self.last_move = None

    def run(self):
        try:
            while self.board.get_game_status() == 'in_progress':
                self.renderer.draw_board(self.board, self.last_move)
                
                if self.board.color_to_move == self.player_color:
                    self._player_turn()
                else:
                    self._ai_turn()
        finally:
            self.renderer.draw_board(self.board)
            print("="*25)
            self.engine.close()
            # Используем локализацию для финального сообщения
            print(self.localizer.get("game_finished_engine_stopped"))

    def _player_turn(self):
        move_made = False
        while not move_made:
            try:
                prompt = self.localizer.get("your_move_prompt")
                user_input = input(prompt)

                if user_input.lower() == self.localizer.get("exit_command"):
                    raise KeyboardInterrupt

                # В _parse_user_input уже используются локализованные ошибки
                move = self._parse_user_input(user_input)

                if move in self.board.get_legal_moves():
                    self.board.make_move(move) # TODO: promotion for player
                    self.last_move = move
                    move_made = True
                else:
                    print(self.localizer.get("illegal_move"))
            except ValueError as e:
                print(self.localizer.get("input_error", error=e))
            except KeyboardInterrupt:
                # Используем локализацию для сообщения о выходе
                print("\n" + self.localizer.get("exit_message"))
                self.board.halfmove_clock = 9999 
                move_made = True

    # Методы _ai_turn, _parse_user_input, _convert_lib_move_to_our остаются без изменений
    def _ai_turn(self):
        print(self.localizer.get("ai_thinking"))
        best_move_lib = self.engine.find_best_move(self.board)
        our_move = self._convert_lib_move_to_our(best_move_lib)
        promo_class = None
        if best_move_lib.promotion:
            if best_move_lib.promotion == chess.QUEEN: promo_class = queen.Queen
        self.board.make_move(our_move, promotion_piece_class=promo_class)
        self.last_move = our_move

    def _parse_user_input(self, uci_move: str) -> tuple:
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
        return self._parse_user_input(lib_move.uci())
