from base_test_case import BasePieceTestCase
from pieces import rook
from Board import WHITE, BLACK

class TestRook(BasePieceTestCase):
    def test_rook_empty_board(self):
        r = rook.Rook(WHITE)
        self.board.set_piece_at((3, 3), r) # d5
        expected_moves = [
            # Горизонталь
            (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (3, 7),
            # Вертикаль
            (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3), (7, 3)
        ]
        self.assertMovesUnorderedEqual(expected_moves, r.get_moves(self.board, (3, 3)))

    def test_rook_with_blockers(self):
        r = rook.Rook(WHITE)
        enemy = rook.Rook(BLACK)
        friendly = rook.Rook(WHITE)
        self.board.set_piece_at((3, 3), r)
        self.board.set_piece_at((1, 3), enemy)    # Враг сверху
        self.board.set_piece_at((3, 6), friendly) # Друг справа
        expected_moves = [
            # Вверх до врага, включая взятие
            (2, 3), (1, 3),
            # Вниз
            (4, 3), (5, 3), (6, 3), (7, 3),
            # Влево
            (3, 0), (3, 1), (3, 2),
            # Вправо до друга
            (3, 4), (3, 5)
        ]
        self.assertMovesUnorderedEqual(expected_moves, r.get_moves(self.board, (3, 3)))