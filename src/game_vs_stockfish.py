import chess
from Board import Board, WHITE, BLACK
from engine.stockfish_engine import StockfishEngine
from renderer import TerminalRenderer
from localization import LocalizationManager
from pieces import queen

def board_to_fen(b: Board) -> str:
    """Вспомогательная функция для конвертации нашего Board в FEN."""
    fen_pieces = ""
    for r in range(8):
        empty_count = 0
        for c in range(8):
            piece = b.get_piece_at((r, c))
            if piece:
                if empty_count > 0: fen_pieces += str(empty_count)
                empty_count = 0
                fen_pieces += piece.symbol
            else: empty_count += 1
        if empty_count > 0: fen_pieces += str(empty_count)
        if r < 7: fen_pieces += '/'
    
    active_color = b.color_to_move
    castling_fen = str(b.castling_rights)
    en_passant_fen = "-"
    if b.en_passant_target:
        row, col = b.en_passant_target
        en_passant_fen = f"{'abcdefgh'[col]}{8 - row}"
    
    return f"{fen_pieces} {active_color} {castling_fen} {en_passant_fen} {b.halfmove_clock} {b.fullmove_number}"

class GameVsStockfish:
    def __init__(self, player_color: str, skill_level: int, lang: str = "ru"):
        self.localizer = LocalizationManager(lang=lang)
        
        if player_color not in [WHITE, BLACK]:
            raise ValueError(self.localizer.get("player_color_error"))

        self.board = Board()
        self.player_color = player_color
        
        try:
            self.engine = StockfishEngine(skill_level=skill_level)
        except (FileNotFoundError, RuntimeError) as e:
            if isinstance(e, FileNotFoundError):
                print(self.localizer.get("stockfish_not_found"))
            else:
                print(self.localizer.get("stockfish_exec_error", error=e))
            exit(1)
        
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
            print(self.localizer.get("game_finished_engine_stopped"))

    def _player_turn(self):
        """Обрабатывает ход игрока."""
        move_made = False
        while not move_made:
            try:
                prompt = self.localizer.get("your_move_prompt")
                user_input = input(prompt)

                if user_input.lower() == self.localizer.get("exit_command"):
                    raise KeyboardInterrupt

                move = self._parse_user_input(user_input)

                if move in self.board.get_legal_moves():
                    # TODO: Добавить логику превращения пешки для игрока
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

    def _ai_turn(self):
        """Обрабатывает ход компьютера."""
        print(self.localizer.get("ai_thinking"))
        current_fen = board_to_fen(self.board)
        best_move_lib = self.engine.find_best_move_from_fen(current_fen)
        
        our_move = self._convert_lib_move_to_our(best_move_lib)
        
        promo_class = None
        if best_move_lib.promotion:
            if best_move_lib.promotion == chess.QUEEN: promo_class = queen.Queen
        
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
        """Конвертирует ход из формата python-chess в наш формат."""
        return self._parse_user_input(lib_move.uci())
