import collections
from src.board import ChessBoard

class Game:
    """
    Управляет течением шахматной партии.
    Хранит историю позиций и определяет результат игры.
    """
    def __init__(self):
        self.board = ChessBoard()
        self.position_history = collections.Counter()
        self.status = "ongoing"
        # Сразу записываем начальную позицию в историю
        self._update_history(self.board.get_position_hash())

    def _update_history(self, position_hash):
        """Добавляет хэш позиции в историю."""
        self.position_history[position_hash] += 1

    def make_move(self, move_str):
        """
        Пытается сделать ход. Если успешно, обновляет историю и статус игры.
        """
        # --- НАЧАЛО ИЗМЕНЕНИЙ ---
        
        # 1. Делаем ход на доске. Если он нелегален, сразу выходим.
        success = self.board.make_move(move_str)
        if not success:
            return False

        # 2. Если ход успешен, получаем хэш НОВОЙ позиции
        new_position_hash = self.board.get_position_hash()
        
        # 3. Добавляем новую позицию в историю
        self._update_history(new_position_hash)
        
        # 4. Теперь, когда вся информация актуальна, проверяем конец игры
        self._check_game_over()
        
        return True
        # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    def undo_move(self):
        """
        Отменяет последний ход, откатывая и доску, и историю позиций.
        """
        # Сначала уменьшаем счетчик текущей (новой) позиции
        current_hash = self.board.get_position_hash()
        if self.position_history[current_hash] > 0:
            self.position_history[current_hash] -= 1
        
        # Затем откатываем саму доску
        return self.board.undo_move()

    def _check_game_over(self):
        """
        Проверяет все условия окончания игры в правильном порядке и обновляет self.status.
        """
        # ПРИОРИТЕТ 1: МАТ И ПАТ
        if not self.board.get_legal_moves():
            if self.board.is_in_check(self.board.turn):
                self.status = "checkmate"
            else:
                self.status = "stalemate"
            return

        # --- НАЧАЛО ИЗМЕНЕНИЯ ---
        # ПРИОРИТЕТ 2: НЕДОСТАТОЧНОСТЬ МАТЕРИАЛА
        # Это мгновенное состояние доски, которое важнее счетчиков.
        if self.board.has_insufficient_material():
            self.status = "draw_insufficient_material"
            return
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---

        # ПРИОРИТЕТ 3: ПРАВИЛО 50 ХОДОВ
        if self.board.halfmove_clock >= 100:
            self.status = "draw_50_moves"
            return
        
        # ПРИОРИТЕТ 4: ТРОЕКРАТНОЕ ПОВТОРЕНИЕ
        current_hash = self.board.get_position_hash()
        if self.position_history[current_hash] >= 3:
            self.status = "draw_repetition"
            return
        
        self.status = "ongoing"