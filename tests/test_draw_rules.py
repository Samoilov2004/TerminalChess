import unittest
import sys
import os

# Гарантируем, что src в пути
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from Board import Board, WHITE, BLACK
from pieces import king, knight, bishop, queen, rook

class TestDrawRules(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        # Очищаем доску для тестов
        self.board.board = [[None for _ in range(8)] for _ in range(8)]
        # Сбрасываем историю для каждого теста
        self.board.position_history.clear()
        self.board._update_position_history()


    def test_insufficient_material_king_vs_king(self):
        """Тест: Король против Короля -> Ничья."""
        self.board.set_piece_at((0, 0), king.King(WHITE))
        self.board.set_piece_at((7, 7), king.King(BLACK))
        self.assertEqual(self.board.get_game_status(), 'draw_insufficient_material')

    def test_insufficient_material_king_vs_king_and_knight(self):
        """Тест: Король и Конь против Короля -> Ничья."""
        self.board.set_piece_at((0, 0), king.King(WHITE))
        self.board.set_piece_at((1, 0), knight.Knight(WHITE))
        self.board.set_piece_at((7, 7), king.King(BLACK))
        self.assertEqual(self.board.get_game_status(), 'draw_insufficient_material')
        
    def test_insufficient_material_king_vs_king_and_bishop(self):
        """Тест: Король и Слон против Короля -> Ничья."""
        self.board.set_piece_at((0, 0), king.King(WHITE))
        self.board.set_piece_at((1, 0), bishop.Bishop(WHITE))
        self.board.set_piece_at((7, 7), king.King(BLACK))
        self.assertEqual(self.board.get_game_status(), 'draw_insufficient_material')

    def test_sufficient_material_two_knights(self):
        """Тест: Два коня - материала ДОСТАТОЧНО (формально)."""
        self.board.set_piece_at((0, 0), king.King(WHITE))
        self.board.set_piece_at((1, 0), knight.Knight(WHITE))
        self.board.set_piece_at((2, 0), knight.Knight(WHITE))
        self.board.set_piece_at((7, 7), king.King(BLACK))
        # Формально мат возможен, хоть и не форсированный
        self.assertNotEqual(self.board.get_game_status(), 'draw_insufficient_material')

    def test_sufficient_material_rook(self):
        """Тест: Ладья - материала ДОСТАТОЧНО."""
        self.board.set_piece_at((0, 0), king.King(WHITE))
        self.board.set_piece_at((1, 0), rook.Rook(WHITE))
        self.board.set_piece_at((7, 7), king.King(BLACK))
        self.assertNotEqual(self.board.get_game_status(), 'draw_insufficient_material')

    def test_threefold_repetition(self):
        """Тест: Троекратное повторение позиции -> Ничья."""
        # Ставим позицию "вечного шаха"
        self.board.set_piece_at((0, 4), king.King(BLACK))
        self.board.set_piece_at((2, 4), king.King(WHITE))
        self.board.set_piece_at((2, 6), queen.Queen(WHITE))
        self.board.color_to_move = WHITE
        self.board.position_history.clear()
        self.board._update_position_history() # Позиция 1, счетчик = 1

        # Ход 1 (Белые): Qg4+
        self.board.make_move(((2, 6), (4, 6)))
        # Ход 1 (Черные): Kf8
        self.board.make_move(((0, 4), (1, 4)))
        # Позиция 2, счетчик = 1

        # Ход 2 (Белые): Qe6+
        self.board.make_move(((4, 6), (2, 6)))
        # Позиция 1, счетчик = 2

        # Ход 2 (Черные): Ke8
        self.board.make_move(((1, 4), (0, 4)))
        # Позиция 2, счетчик = 2

        # Ход 3 (Белые): Qg4+
        self.board.make_move(((2, 6), (4, 6)))
         # Ход 3 (Черные): Kf8
        self.board.make_move(((4, 6), (1, 4)))
        # Позиция 1, счетчик = 3. После этого хода должен быть draw

        # Ход 4 (Белые): Qe6+ -> теперь позиция повторяется в 3-й раз, get_game_status должен это увидеть
        self.board.make_move(((4, 6), (2, 6)))
        self.assertEqual(self.board.get_game_status(), 'draw_repetition')
