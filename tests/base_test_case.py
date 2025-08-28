import unittest
import sys
import os

# Гарантируем, что src в пути
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from Board import Board

class BasePieceTestCase(unittest.TestCase):
    def setUp(self):
        """Создает пустую доску перед каждым тестом."""
        self.board = Board()
        # Очищаем доску, чтобы расставлять фигуры вручную
        self.board.board = [[None for _ in range(8)] for _ in range(8)]

    def assertMovesUnorderedEqual(self, expected_moves, actual_moves):
        """Сравнивает два списка ходов без учета порядка."""
        self.assertCountEqual(expected_moves, actual_moves, 
                              f"Moves are not equal.\nExpected: {sorted(expected_moves)}\nGot:      {sorted(actual_moves)}")