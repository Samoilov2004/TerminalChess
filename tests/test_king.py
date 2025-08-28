from base_test_case import BasePieceTestCase
from pieces import king, rook
from Board import WHITE, BLACK

class TestKing(BasePieceTestCase):
    def test_king_from_center(self):
        k = king.King(WHITE)
        self.board.set_piece_at((3, 3), k)
        expected_moves = [
            (2, 2), (2, 3), (2, 4),
            (3, 2),         (3, 4),
            (4, 2), (4, 3), (4, 4)
        ]
        self.assertMovesUnorderedEqual(expected_moves, k.get_moves(self.board, (3, 3)))

    def test_king_does_not_generate_castling(self):
        # Этот тест проверяет, что фигура короля сама по себе НЕ генерирует рокировку
        # Это ответственность класса Board
        k = king.King(WHITE)
        self.board.set_piece_at((7, 4), k)
        expected_moves = [(6, 3), (6, 4), (6, 5), (7, 3), (7, 5)]
        self.assertMovesUnorderedEqual(expected_moves, k.get_moves(self.board, (7, 4)))