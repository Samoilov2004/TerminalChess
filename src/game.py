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
        self._update_history(self.board.get_position_hash())
        self.captured_by_white = []
        self.captured_by_black = []

    def _update_history(self, position_hash):
        """Добавляет хэш позиции в историю."""
        self.position_history[position_hash] += 1

    def make_move(self, move_str):
        """
        Пытается сделать ход. Если успешно, обновляет историю и статус игры.
        Надежная версия с проверкой ввода.
        """
        # --- НАЧАЛО ИСПРАВЛЕНИЙ ---
        if not isinstance(move_str, str) or len(move_str) < 4:
            return False # Сразу отклоняем некорректный ввод

        from_pos = self.board._parse_pos(move_str[:2])
        to_pos = self.board._parse_pos(move_str[2:4])

        # Если парсинг не удался, ход нелегален
        if from_pos is None or to_pos is None:
            return False
        # --- КОНЕЦ ИСПРАВЛЕНИЙ ---

        piece_captured = self.board.get_piece_at(to_pos)
        
        success = self.board.make_move(move_str)
        
        if success:
            if piece_captured != '.':
                if self.board.turn == 'black':
                    self.captured_by_white.append(piece_captured)
                else:
                    self.captured_by_black.append(piece_captured)
            
            new_position_hash = self.board.get_position_hash()
            self._update_history(new_position_hash)
            self._check_game_over()
        
        return success

    def undo_move(self):
        """
        Отменяет последний сделанный ход.
        Этот метод должен быть в классе Game, не в TrainingGame.
        """
        # Проверяем, есть ли что отменять в истории доски
        if not self.board.move_history:
            return False

        # --- ОТКАТ ИСТОРИИ ПОВТОРЕНИЙ ---
        # Сначала уменьшаем счетчик текущей позиции
        current_hash = self.board.get_position_hash()
        if self.position_history.get(current_hash, 0) > 0:
            self.position_history[current_hash] -= 1
        else:
            # Если счетчика нет, это странно, но лучше обработать
            self.position_history.pop(current_hash, None)
        
        # --- ОТКАТ СЪЕДЕННЫХ ФИГУР ---
        last_captured_piece_char = self.board.move_history[-1]['piece_captured']
        if last_captured_piece_char != '.':
            # Определяем, кто сделал отменяемый ход (противоположный текущему self.board.turn)
            moving_player_color = 'black' if self.board.turn == 'white' else 'white'
            if moving_player_color == 'white':
                if self.captured_by_white and self.captured_by_white[-1] == last_captured_piece_char:
                    self.captured_by_white.pop()
            else:
                if self.captured_by_black and self.captured_by_black[-1] == last_captured_piece_char:
                    self.captured_by_black.pop()
        
        # --- ОТКАТ САМОЙ ДОСКИ ---
        # Делегируем это доске, у которой есть вся низкоуровневая информация
        return self.board.undo_move()

    def _check_game_over(self):
        """
        Проверяет все условия окончания игры в правильном порядке и обновляет self.status.
        """
        # ПРИОРИТЕТ 1: НЕДОСТАТОЧНОСТЬ МАТЕРИАЛА
        # Это мгновенное состояние доски, которое не зависит от того, чей ход.
        # Если материала нет, игра - ничья, даже если формально есть мат в 1 ход
        # (такой мат поставить невозможно).
        if self.board.has_insufficient_material():
            self.status = "draw_insufficient_material"
            return
            
        # ПРИОРИТЕТ 2: МАТ И ПАТ
        # Если у текущего игрока нет легальных ходов, игра заканчивается немедленно.
        if not self.board.get_legal_moves():
            if self.board.is_in_check(self.board.turn):
                self.status = "checkmate"
            else:
                self.status = "stalemate"
            return

        # ПРИОРИТЕТ 3: ПРАВИЛО 50 ХОДОВ
        if self.board.halfmove_clock >= 100:
            self.status = "draw_50_moves"
            return
        
        # ПРИОРИТЕТ 4: ТРОЕКРАТНОЕ ПОВТОРЕНИЕ
        current_hash = self.board.get_position_hash()
        if self.position_history[current_hash] >= 3:
            self.status = "draw_repetition"
            return
        
        # Если ничего не сработало, игра продолжается
        self.status = "ongoing"