from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, WHITE, BLACK

if TYPE_CHECKING:
    from ..Board import Board

class Pawn(Piece):
    """
    Реализация пешки.
    Учитывает: движение вперед, двойной ход, взятие по диагонали и взятие на проходе.
    Логика превращения обрабатывается на более высоком уровне (Game/Board).
    """
    def __init__(self, color: str):
        super().__init__(color)
        self.symbol = 'P' if self.color == WHITE else 'p'

    def get_moves(self, board: 'Board', position: Tuple[int, int]) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # Определяем направление движения: -1 для белых (вверх по доске), +1 для черных (вниз)
        direction = -1 if self.color == WHITE else 1
        
        # 1. Одиночный ход вперед
        one_step_fwd = (row + direction, col)
        if board.is_on_board(one_step_fwd) and board.get_piece_at(one_step_fwd) is None:
            moves.append(one_step_fwd)
            
            # 2. Двойной ход вперед (только если одиночный ход возможен и это первый ход пешки)
            if not self.has_moved:
                two_steps_fwd = (row + 2 * direction, col)
                if board.is_on_board(two_steps_fwd) and board.get_piece_at(two_steps_fwd) is None:
                    moves.append(two_steps_fwd)
        
        # 3. Взятия по диагонали
        capture_moves = [
            (row + direction, col - 1),
            (row + direction, col + 1),
        ]
        for move in capture_moves:
            if board.is_on_board(move):
                # 3a. Обычное взятие
                target_piece = board.get_piece_at(move)
                if target_piece and target_piece.color != self.color:
                    moves.append(move)
                
                # 3b. Взятие на проходе (En Passant)
                if move == board.en_passant_target:
                    moves.append(move)
                    
        return moves