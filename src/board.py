import copy

# Правило повторения позиции 3 раза не выполнено, ибо история не хранится пока

class ChessBoard:
    """
    Класс представляет шахматную доску и управляет логикой игры.
    Он отслеживает положение фигур, очередность хода, права на рокировку
    и другие состояния игры в соответствии с правилами FIDE.
    """
    def __init__(self):
        """
        Инициализирует доску в стандартном начальном положении.
        """
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        self.turn = 'white'
        self.castling_rights = {
            'white': {'kingside': True, 'queenside': True},
            'black': {'kingside': True, 'queenside': True}
        }
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []

    def __str__(self):
        """
        Простое текстовое представление для отладки.
        Не используется в основном интерфейсе.
        """
        return "\n".join(" ".join(row) for row in self.board)

    def get_piece_color(self, piece):
        """Возвращает цвет фигуры ('white' или 'black') или None."""
        if piece == '.':
            return None
        return 'white' if piece.isupper() else 'black'

    def _parse_pos(self, pos_str):
        if not isinstance(pos_str, str) or len(pos_str) != 2: return None
        col = ord(pos_str[0]) - ord('a')
        row = 8 - int(pos_str[1])
        if 0 <= row < 8 and 0 <= col < 8: return row, col
        return None

    def _to_algebraic(self, pos):
        """Преобразует координаты (row, col) в алгебраическую нотацию 'e2'."""
        if pos is None:
            return None
        row, col = pos
        return chr(ord('a') + col) + str(8 - row)

    def get_piece_at(self, pos):
        row, col = pos
        return self.board[row][col]

    def _is_square_attacked(self, pos, attacker_color):
        """Проверяет, атакована ли клетка `pos` фигурами цвета `attacker_color`."""
        r, c = pos

        pawn_char = 'P' if attacker_color == 'white' else 'p'
        # Направление, ОТКУДА приходит атака пешки
        pawn_dir = 1 if attacker_color == 'white' else -1 
        if 0 <= r + pawn_dir < 8:
            if 0 <= c - 1 < 8 and self.board[r + pawn_dir][c - 1] == pawn_char: return True
            if 0 <= c + 1 < 8 and self.board[r + pawn_dir][c + 1] == pawn_char: return True

        # Проверка атаки конем
        knight_char = 'N' if attacker_color == 'white' else 'n'
        for dr, dc in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
             nr, nc = r + dr, c + dc
             if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == knight_char:
                 return True

        # Проверка по прямым и диагоналям
        rook_char = 'R' if attacker_color == 'white' else 'r'
        bishop_char = 'B' if attacker_color == 'white' else 'b'
        queen_char = 'Q' if attacker_color == 'white' else 'q'
        king_char = 'K' if attacker_color == 'white' else 'k'

        # Прямые линии (ладья, ферзь)
        for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
            for i in range(1, 8):
                nr, nc = r + i*dr, c + i*dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    piece = self.board[nr][nc]
                    if piece != '.':
                        if piece in (rook_char, queen_char): return True
                        if i == 1 and piece == king_char: return True
                        break 
                else: break
        
        # Диагонали (слон, ферзь)
        for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            for i in range(1, 8):
                nr, nc = r + i*dr, c + i*dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    piece = self.board[nr][nc]
                    if piece != '.':
                        if piece in (bishop_char, queen_char): return True
                        if i == 1 and piece == king_char: return True
                        break
                else: break
        return False
    
    def is_in_check(self, color):
        """
        Проверяет, находится ли король указанного цвета под шахом.

        :param color: Цвет короля для проверки ('white' или 'black').
        :type color: str
        :return: True, если король атакован, иначе False.
        :rtype: bool
        """
        king_char = 'K' if color == 'white' else 'k'
        king_pos = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king_char:
                    king_pos = (r, c)
                    break
            if king_pos: break
        
        if not king_pos: return False
        
        opponent_color = 'black' if color == 'white' else 'white'
        return self._is_square_attacked(king_pos, opponent_color)

    def get_legal_moves(self):
        """
        Возвращает список всех легальных ходов для текущего игрока.
        Использует deepcopy для безопасной проверки ходов.
        """
        legal_moves = []
        # Сначала генерируем все ходы, которые фигура может сделать в принципе
        pseudo_legal_moves = self._generate_pseudo_legal_moves()

        for move in pseudo_legal_moves:
            # Создаем ПОЛНУЮ, ГЛУБОКУЮ КОПИЮ доски для симуляции хода
            temp_board = copy.deepcopy(self)
            
            # Делаем ход на временной доске
            temp_board._make_move_on_board(move)
            
            # Проверяем, не оказался ли НАШ король под шахом ПОСЛЕ хода
            # `self.turn`, потому что внутри temp_board ход уже сменился, а нам нужен цвет того, кто ходил
            if not temp_board.is_in_check(self.turn):
                legal_moves.append(move)
        
        return legal_moves
    
    def _generate_pseudo_legal_moves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if self.get_piece_color(piece) == self.turn:
                    moves.extend(self._get_moves_for_piece((r, c)))
        return moves

    def _get_moves_for_piece(self, pos):
        piece = self.get_piece_at(pos)
        piece_type = piece.lower()
        if piece_type == 'p': return self._get_pawn_moves(pos)
        if piece_type == 'n': return self._get_knight_moves(pos)
        if piece_type == 'k': return self._get_king_moves(pos)
        if piece_type == 'r': return self._get_sliding_moves(pos, [(0,1), (0,-1), (1,0), (-1,0)])
        if piece_type == 'b': return self._get_sliding_moves(pos, [(1,1), (1,-1), (-1,1), (-1,-1)])
        if piece_type == 'q': return self._get_sliding_moves(pos, [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)])
        return []

    def _get_pawn_moves(self, pos):
        moves = []
        r, c = pos
        color = self.get_piece_color(self.board[r][c])
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        if 0 <= r + direction < 8 and self.board[r + direction][c] == '.':
            moves.append(((r, c), (r + direction, c)))
            if r == start_row and self.board[r + 2 * direction][c] == '.':
                moves.append(((r, c), (r + 2 * direction, c)))
        
        for dc in [-1, 1]:
            if 0 <= c + dc < 8 and 0 <= r + direction < 8:
                target_pos = (r + direction, c + dc)
                target_piece = self.get_piece_at(target_pos)
                if target_piece != '.' and self.get_piece_color(target_piece) != color:
                    moves.append(((r,c), target_pos))
                if target_pos == self.en_passant_target:
                    moves.append(((r, c), target_pos))
        return moves

    def _get_knight_moves(self, pos):
        moves = []
        r, c = pos
        color = self.get_piece_color(self.board[r][c])
        for dr, dc in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target_piece = self.board[nr][nc]
                if self.get_piece_color(target_piece) != color:
                    moves.append(((r, c), (nr, nc)))
        return moves

    def _get_king_moves(self, pos):
        moves = []
        r, c = pos
        color = self.get_piece_color(self.board[r][c])
        # Usual moves
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if self.get_piece_color(self.board[nr][nc]) != color:
                        moves.append(((r, c), (nr, nc)))
        # Castling
        opponent = 'black' if color == 'white' else 'white'
        if not self.is_in_check(color):
            # Короткая рокировка (kingside)
            if self.castling_rights[color]['kingside']:
                if self.board[r][c+1] == '.' and self.board[r][c+2] == '.' and \
                   not self._is_square_attacked((r, c), opponent) and \
                   not self._is_square_attacked((r, c+1), opponent) and \
                   not self._is_square_attacked((r, c+2), opponent):
                    moves.append(((r, c), (r, c+2)))
            # Длинная рокировка (queenside)
            if self.castling_rights[color]['queenside']:
                if self.board[r][c-1] == '.' and self.board[r][c-2] == '.' and self.board[r][c-3] == '.' and \
                   not self._is_square_attacked((r, c), opponent) and \
                   not self._is_square_attacked((r, c-1), opponent) and \
                   not self._is_square_attacked((r, c-2), opponent):
                    moves.append(((r, c), (r, c-2)))
        return moves

    def _get_sliding_moves(self, pos, directions):
        moves = []
        r, c = pos
        color = self.get_piece_color(self.board[r][c])
        for dr, dc in directions:
            for i in range(1, 8):
                nr, nc = r + i * dr, c + i * dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target_piece = self.board[nr][nc]
                    if target_piece == '.':
                        moves.append(((r, c), (nr, nc)))
                    elif self.get_piece_color(target_piece) != color:
                        moves.append(((r, c), (nr, nc)))
                        break
                    else:
                        break
                else: 
                    break
        return moves

    def make_move(self, move_str):
        """
        Проверяет и выполняет ход, заданный в алгебраической нотации.

        Пример нотации: 'e2e4', 'e7e8q' (превращение пешки в ферзя).
        Если ход легален, состояние доски изменяется и ход передается
        другому игроку. В противном случае, состояние доски не меняется.

        :param move_str: Строка, представляющая ход (например, 'e2e4').
        :type move_str: str
        :return: True, если ход был успешно выполнен, иначе False.
        :rtype: bool
        """
        if len(move_str) < 4: return False
        
        from_pos_str, to_pos_str = move_str[:2], move_str[2:4]
        promotion_piece = move_str[4] if len(move_str) == 5 else None

        from_pos = self._parse_pos(from_pos_str)
        to_pos = self._parse_pos(to_pos_str)
        
        if from_pos is None or to_pos is None:
            # print("Ошибка: Неверный формат хода.") # Убираем print для чистоты тестов
            return False

        piece_to_move = self.get_piece_at(from_pos)
        if self.get_piece_color(piece_to_move) != self.turn:
            return False

        move = (from_pos, to_pos)
        legal_moves = self.get_legal_moves()

        if move not in legal_moves:
            # print(f"Ошибка: Нелегальный ход '{move_str}'.") # Убираем print для чистоты тестов
            return False

        self._make_move_on_board(move, promotion_piece)
        self.move_history.append(move_str)
        return True

    def _make_move_on_board(self, move, promotion_piece=None):
        """
        Внутренний метод для выполнения хода на доске без проверок легальности.
        Обновляет все состояния, связанные с доской.
        """
        from_pos, to_pos = move
        from_r, from_c = from_pos
        to_r, to_c = to_pos
        
        piece_moved = self.board[from_r][from_c]
        piece_captured = self.board[to_r][to_c]
        
        last_state = {
            'move': move,
            'piece_moved': piece_moved,
            'piece_captured': piece_captured,
            'en_passant_target': self.en_passant_target,
            'castling_rights': copy.deepcopy(self.castling_rights),
            'halfmove_clock': self.halfmove_clock,
        }
        self.move_history.append(last_state)

        # Сбрасываем счетчик 50 ходов, если было взятие или ход пешкой
        if piece_captured != '.' or piece_moved.lower() == 'p':
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        if self.turn == 'black':
            self.fullmove_number += 1
            
        current_en_passant_target = self.en_passant_target
        self.en_passant_target = None
        
        # --- 3. Обрабатываем специальные ходы ---
        
        # 3.1 Двойной ход пешки (создает возможность для en passant)
        if piece_moved.lower() == 'p' and abs(from_r - to_r) == 2:
            self.en_passant_target = ((from_r + to_r) // 2, from_c)
        
        # 3.2 Взятие на проходе (En Passant)
        if piece_moved.lower() == 'p' and to_pos == current_en_passant_target and piece_captured == '.':
             captured_pawn_row = from_r
             captured_pawn_col = to_c
             self.board[captured_pawn_row][captured_pawn_col] = '.'
            
        # 3.3 Рокировка (Castling)
        if piece_moved.lower() == 'k' and abs(from_c - to_c) == 2:
            if to_c > from_c:
                self.board[to_r][to_c-1] = self.board[to_r][to_c+1]
                self.board[to_r][to_c+1] = '.'
            else:
                self.board[to_r][to_c+1] = self.board[to_r][to_c-2]
                self.board[to_r][to_c-2] = '.'

        # --- 4. Основное перемещение фигуры ---
        self.board[to_r][to_c] = piece_moved
        self.board[from_r][from_c] = '.'

        if piece_moved.lower() == 'p' and (to_r == 0 or to_r == 7):
            # По умолчанию превращаем в ферзя, если не указано иное
            promo_char = promotion_piece if promotion_piece and promotion_piece.lower() in 'qrbn' else 'q'
            self.board[to_r][to_c] = promo_char.upper() if self.turn == 'white' else promo_char.lower()
        
        # --- 5. Обновляем глобальные состояния ---
        
        color = self.turn
        if piece_moved.lower() == 'k':
            self.castling_rights[color]['kingside'] = False
            self.castling_rights[color]['queenside'] = False
        elif piece_moved.lower() == 'r':
            # Если ладья сдвинулась с начальной позиции
            if from_pos == (7, 0) and color == 'white': self.castling_rights['white']['queenside'] = False
            elif from_pos == (7, 7) and color == 'white': self.castling_rights['white']['kingside'] = False
            elif from_pos == (0, 0) and color == 'black': self.castling_rights['black']['queenside'] = False
            elif from_pos == (0, 7) and color == 'black': self.castling_rights['black']['kingside'] = False

        self.turn = 'black' if self.turn == 'white' else 'white'

    def get_board_string(self, flip=False):
        """
        Возвращает строковое представление доски с правильным выравниванием.
        :param flip: Если True, доска будет перевернута (для игры за черных).
        """
        board_str = ""
        
        # --- 1. Определяем порядок файлов и рядов ---
        if flip:
            # Для черных: файлы h-a, ряды 1-8 (смотрим "снизу вверх" по выводу в консоль)
            files = " h g f e d c b a"
            rank_indices = range(7, -1, -1) # Сначала 8-я, потом 7-я... Вывод начнется с 1-го ряда.
        else:
            # Для белых: файлы a-h, ряды 8-1
            files = " a b c d e f g h"
            rank_indices = range(8) # Сначала 1-я, потом 2-я... Вывод начнется с 8-го ряда.

        # --- 2. Формируем "шапку" доски ---
        header = f'   {files}'
        separator = '  +-----------------+'
        
        board_str += header + "\n" + separator + "\n"

        # --- 3. Рисуем доску, ряд за рядом ---
        for r in rank_indices:
            rank_number = 8 - r if not flip else r + 1
            
            # Собираем содержимое ряда в нужном порядке
            row_list = self.board[r]
            if flip:
                row_list = row_list[::-1] # Переворачиваем ряд h -> a
            
            row_content = " ".join(row_list)
            board_str += f"{rank_number} | {row_content} | {rank_number}\n"
            
        # --- 4. Формируем "подвал" и информацию об игре ---
        board_str += separator + "\n" + header + "\n"
        
        turn_color = "White" if self.turn == 'white' else "Black"
        board_str += f"\nTurn: {self.fullmove_number}. {turn_color} to move.\n"

        if self.is_in_check(self.turn):
            board_str += "CHECK!\n"

        return board_str

    def is_game_over(self):
        """
        Определяет, завершена ли игровая партия, и возвращает ее статус.

        Проверяет на мат, пат и правило 50 ходов.

        :return: Строка со статусом игры:
                 'checkmate' (мат),
                 'stalemate' (пат),
                 'draw_50_moves' (ничья по правилу 50 ходов),
                 'ongoing' (игра продолжается).
        :rtype: str
        """
        if not self.get_legal_moves():
            if self.is_in_check(self.turn):
                return "checkmate"
            else:
                return "stalemate"
        if self.halfmove_clock >= 100:
            return "draw_50_moves"
        return "ongoing"

    def get_position_hash(self):
        """
        Создает уникальную строку (хэш) для текущей позиции.
        Это нужно для отслеживания троекратного повторения.
        Хэш включает в себя положение фигур, право на ход,
        права на рокировку и возможность взятия на проходе.
        """
        # Преобразуем доску в одну строку
        board_str = "".join("".join(row) for row in self.board)
        
        # Собираем права на рокировку в строку
        castling_str = ""
        if self.castling_rights['white']['kingside']: castling_str += 'K'
        if self.castling_rights['white']['queenside']: castling_str += 'Q'
        if self.castling_rights['black']['kingside']: castling_str += 'k'
        if self.castling_rights['black']['queenside']: castling_str += 'q'
        if not castling_str: castling_str = '-'

        en_passant_str = self._to_algebraic(self.en_passant_target) if self.en_passant_target else '-'
        
        # Собираем все в один хэш
        return f"{board_str} {self.turn[0]} {castling_str} {en_passant_str}"

    def has_insufficient_material(self):
        """
        Проверяет, достаточно ли на доске материала для постановки мата.
        Возвращает True, если материала недостаточно (ничья), иначе False.
        """
        # 1. Собираем все фигуры, кроме королей, в один список
        pieces = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != '.' and piece.lower() != 'k':
                    pieces.append(piece)

        # 2. Если остались ферзи, ладьи или пешки, мат возможен.
        for piece in pieces:
            if piece.lower() in 'qrp':
                return False

        # 3. На этом этапе у нас остались только слоны и кони.
        # Если фигур нет (только короли) или осталась только одна легкая фигура.
        if len(pieces) <= 1:
            return True # K vs K, K vs KN, K vs KB - это ничьи.

        # 4. Проверка на двух коней (K+N+N vs K - мат возможен, но крайне редко)
        # В большинстве правил это не считается ничьей.
        if len(pieces) == 2 and pieces[0].lower() == 'n' and pieces[1].lower() == 'n':
            return False # Мат двумя конями возможен.

        # 5. Проверка на слонов одного цвета
        # Если все оставшиеся фигуры - слоны, и они все на полях одного цвета.
        bishops = [p for p in pieces if p.lower() == 'b']
        if len(bishops) == len(pieces): # Убедимся, что кроме слонов ничего нет
            bishop_positions = []
            for r in range(8):
                for c in range(8):
                    if self.board[r][c].lower() == 'b':
                        bishop_positions.append((r, c))
            
            # Определяем цвет поля первого слона
            first_bishop_square_color = (bishop_positions[0][0] + bishop_positions[0][1]) % 2
            # Проверяем, все ли остальные слоны на полях того же цвета
            for i in range(1, len(bishop_positions)):
                bishop_square_color = (bishop_positions[i][0] + bishop_positions[i][1]) % 2
                if bishop_square_color != first_bishop_square_color:
                    return False # Слоны на полях разного цвета, мат возможен
            return True # Все слоны на полях одного цвета, ничья

        # Во всех остальных случаях (например, слон + конь) мат возможен.
        return False

    def undo_move(self):
        """Отменяет последний сделанный ход."""
        if not self.move_history:
            return False

        last_state = self.move_history.pop()

        # Восстанавливаем все ключевые переменные
        self.turn = last_state['turn']
        self.castling_rights = last_state['castling_rights']
        self.en_passant_target = last_state['en_passant_target']
        self.halfmove_clock = last_state['halfmove_clock']
        
        # Если отменяем ход белых, номер полного хода тоже нужно откатить
        if self.turn == 'black':
             self.fullmove_number -=1

        # Возвращаем фигуры на место
        from_pos, to_pos = last_state['move']
        self.board[from_pos[0]][from_pos[1]] = last_state['piece_moved']
        self.board[to_pos[0]][to_pos[1]] = last_state['piece_captured']

        # Особый случай: отмена взятия на проходе
        if last_state['piece_moved'].lower() == 'p' and \
           to_pos == last_state['en_passant_target'] and \
           last_state['piece_captured'] == '.':
            # Возвращаем вражескую пешку на место
            captured_pawn_row = from_pos[0]
            captured_pawn_col = to_pos[1]
            captured_pawn_char = 'p' if self.turn == 'white' else 'P'
            self.board[captured_pawn_row][captured_pawn_col] = captured_pawn_char
        
        # Особый случай: отмена рокировки
        if last_state['piece_moved'].lower() == 'k' and abs(from_pos[1] - to_pos[1]) == 2:
            if to_pos[1] > from_pos[1]: # Короткая
                rook_from, rook_to = (from_pos[0], 5), (from_pos[0], 7)
            else: # Длинная
                rook_from, rook_to = (from_pos[0], 3), (from_pos[0], 0)
            # Возвращаем ладью
            self.board[rook_to[0]][rook_to[1]] = self.board[rook_from[0]][rook_from[1]]
            self.board[rook_from[0]][rook_from[1]] = '.'

        return True

    def to_fen(self):
        """Конвертирует текущее состояние доски в стандартную нотацию FEN."""
        fen_parts = []
        
        # 1. Положение фигур
        for row in self.board:
            empty_count = 0
            row_str = ""
            for piece in row:
                if piece == '.':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece
            if empty_count > 0:
                row_str += str(empty_count)
            fen_parts.append(row_str)
        
        board_fen = "/".join(fen_parts)
        
        # 2. Чей ход
        turn_fen = self.turn[0] # 'w' или 'b'
        
        # 3. Права на рокировку
        castling_fen = ""
        if self.castling_rights.get('white', {}).get('kingside'): castling_fen += 'K'
        if self.castling_rights.get('white', {}).get('queenside'): castling_fen += 'Q'
        if self.castling_rights.get('black', {}).get('kingside'): castling_fen += 'k'
        if self.castling_rights.get('black', {}).get('queenside'): castling_fen += 'q'
        if not castling_fen: castling_fen = '-'
            
        # 4. Возможность взятия на проходе
        en_passant_fen = self._to_algebraic(self.en_passant_target) if self.en_passant_target else '-'
            
        # --- НАЧАЛО ИСПРАВЛЕНИЯ ---
        # 5. Счетчик полуходов и номер хода
        halfmove_fen = str(self.halfmove_clock)
        fullmove_fen = str(self.fullmove_number)
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

        return f"{board_fen} {turn_fen} {castling_fen} {en_passant_fen} {halfmove_fen} {fullmove_fen}"