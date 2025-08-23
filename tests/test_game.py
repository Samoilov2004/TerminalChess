# tests/test_game.py

import unittest
from src.game import Game

class TestGameRules(unittest.TestCase):

    def setUp(self):
        """Создает новую игру перед каждым тестом."""
        self.game = Game()

    def test_initial_game_status(self):
        """Проверяет, что игра начинается в статусе 'ongoing'."""
        self.assertEqual(self.game.status, "ongoing")

    def test_threefold_repetition_draw(self):
        """Проверяет ничью из-за троекратного повторения позиции."""
        # Последовательность ходов, приводящая к повторению
        # Кони ходят туда-сюда
        moves = ["g1f3", "g8f6", "f3g1", "f6g8"]
        
        # Повторяем последовательность 2 раза
        self.game.make_move(moves[0])
        self.game.make_move(moves[1])
        self.game.make_move(moves[2])
        self.game.make_move(moves[3]) # Позиция 1 (повтор #1)

        self.assertEqual(self.game.status, "ongoing", "Игра все еще должна продолжаться")

        self.game.make_move(moves[0])
        self.game.make_move(moves[1])
        self.game.make_move(moves[2])
        self.game.make_move(moves[3]) # Позиция 1 (повтор #2)
        
        self.assertEqual(self.game.status, "ongoing", "Игра все еще должна продолжаться")
        
        # Третье повторение позиции
        self.game.make_move(moves[0])
        self.game.make_move(moves[1])

        # После этого хода игра должна закончиться ничьей
        self.assertEqual(self.game.status, "draw_repetition", "Должна быть ничья по троекратному повторению")

    def test_50_move_rule_draw(self):
        """Проверяет ничью по правилу 50 ходов."""
        # Нам нужно сделать 50 полных ходов (100 полуходов) без взятий и ходов пешками.
        # Используем простую последовательность ходов конями.
        moves = ["b1c3", "b8c6", "c3b1", "c6b8"] # 4 полухода
        
        # Повторяем 24 раза (24 * 4 = 96 полуходов)
        for _ in range(24):
            for move in moves:
                self.game.make_move(move)

        self.assertEqual(self.game.board.halfmove_clock, 96)
        self.assertEqual(self.game.status, "ongoing", "Игра не должна закончиться до 100-го полухода")

        # Делаем еще 3 хода, чтобы добраться до 99
        self.game.make_move("b1c3")
        self.game.make_move("b8c6")
        self.game.make_move("c3b1")
        self.assertEqual(self.game.board.halfmove_clock, 99)
        self.assertEqual(self.game.status, "ongoing")

        # 100-й полуход!
        self.game.make_move("c6b8")
        self.assertEqual(self.game.board.halfmove_clock, 100)
        
        # Проверяем статус игры
        self.assertEqual(self.game.status, "draw_50_moves", "Должна быть ничья по правилу 50 ходов")


if __name__ == '__main__':
    unittest.main()
