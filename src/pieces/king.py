from typing import List, Tuple, TYPE_CHECKING
from .piece import Piece, WHITE, BLACK

if TYPE_CHECKING:
    from ..Board import Board

class King(Piece):
    """
    Реализация короля.
    Генерирует только стандартные ходы на 1 клетку.
    Сложная логика рокировки обрабатывается на уровне Board.
    """
    def __init__(self, color: str):
        super().__init__(color)
        self.symbol = 'K' if self.color == WHITE else 'k'

    def get_moves(self, board: 'Board', position: Tuple[int, int]) -> List[Tuple[int, int]]:
        row, col = position
        moves = []
        
        # Все 8 направлений вокруг короля
        potential_moves = [
            (row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
            (row,     col - 1),                 (row,     col + 1),
            (row + 1, col - 1), (row + 1, col), (row + 1, col + 1),
        ]

        for r, c in potential_moves:
            if board.is_on_board((r, c)):
                target_piece = board.get_piece_at((r, c))
                # Если клетка пуста или занята фигурой противника
                if target_piece is None or target_piece.color != self.color:
                    moves.append((r, c))
        
        # ПРИМЕЧАНИЕ: Ходы рокировки здесь не генерируются.
        # Board будет вызывать специальный метод get_castling_moves()
        # и добавлять их к общему списку ходов.
        
        return moves