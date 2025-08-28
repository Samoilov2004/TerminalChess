from abc import ABC, abstractmethod
from typing import List, Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    from core.board import Board  # Переписать откуда board брать, он не тут 


WHITE, BLACK = 'w', 'b'

class Piece(ABC):
    """
    An abstract base class for all chess pieces.
    """
    def __init__(self, color: str):
        if color not in (WHITE, BLACK):
            raise ValueError("Недопустимый цвет фигуры")
        self.color = color
        self.symbol = ''  # Будет определен в дочерних классах
        self.has_moved = False # Важно для рокировки и первого хода пешки

    @abstractmethod
    def get_moves(self, board: 'Board', position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Returns a list of all POSSIBLE (pseudo-legal) moves for a piece from a given position.
        Check for check after the move is NOT performed here. This is the Board's task.
        """
        pass

    def __repr__(self) -> str:
        """A representation of an object for debugging, for example: Pawn('w')"""
        return f"{self.__class__.__name__}('{self.color}')"