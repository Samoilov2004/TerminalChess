import copy

# Правило повторения позиции 3 раза не выполнено, ибо история не хранится пока

class ChessBoard:
    def __init__(self):
        """
        Инициализирует доску в начальном состоянии.
        Заглавные буквы - белые фигуры, строчные - черные.
        'p' - pawn (пешка), 'r' - rook (ладья), 'n' - knight (конь),
        'b' - bishop (слон), 'q' - queen (ферзь), 'k' - king (король).
        '.' - пустая клетка.
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
        self.white_to_move = True
        self.castling_rights = [[True, True], [True, True]]
        self.en_passant_target = None  # Coordinates for en passant
        self.halfmove_clock = 0  # Counter of moves without capture and pawn movement (for the 50-move rule)
        self.fullmove_number = 1
        self.move_history = []

    def __str__(self):
        """Визуальное представление доски в консоли."""
        board_str = "   a  b  c  d  e  f  g  h\n"
        board_str += "  -------------------------\n"
        for i, row in enumerate(self.board):
            board_str += f"{8 - i}| {' '.join(row)} |{8 - i}\n"
        board_str += "  -------------------------\n"
        board_str += "   a  b  c  d  e  f  g  h\n"
        return board_str

    def get_color(self, piece):
        """Возвращает цвет фигуры ('white' или 'black') или None."""
        if piece.isupper():
            return 'white'
        if piece.islower():
            return 'black'
        return None

    def _parse_pos(self, pos_str):
        """Преобразует 'e2' в (6, 4)."""
        if not isinstance(pos_str, str) or len(pos_str) != 2:
            return None
        col = ord(pos_str[0]) - ord('a')
        row = 8 - int(pos_str[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return row, col
        return None

    def _to_algebraic(self, pos):
        """Преобразует (6, 4) в 'e2'."""
        row, col = pos
        return chr(ord('a') + col) + str(8 - row)
    
    def get_piece_at(self, pos):
        """Возвращает фигуру по координатам (row, col)."""
        row, col = pos
        return self.board[row][col]

    def is_in_check(self, color):
        """Проверяет, находится ли король указанного цвета под шахом."""
        king_char = 'K' if color == 'white' else 'k'
        king_pos = None
        # Finding the King
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king_char:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos: # In case the king is not on the board (theoretically)
            return False

        # Check if the king is attacked
        return self._is_square_attacked(king_pos, 'white' if color == 'black' else 'black')

    def _is_square_attacked(self, pos, attacker_color):
        """Проверяет, атакована ли клетка `pos` фигурами цвета `attacker_color`."""
        # Checking the pawn attack
        pawn_char = 'p' if attacker_color == 'white' else 'P'
        pawn_dir = 1 if attacker_color == 'white' else -1
        r, c = pos
        if 0 <= r + pawn_dir < 8:
            if 0 <= c - 1 < 8 and self.board[r + pawn_dir][c - 1] == pawn_char: return True
            if 0 <= c + 1 < 8 and self.board[r + pawn_dir][c + 1] == pawn_char: return True

        # Checking the knight's attack
        knight_char = 'n' if attacker_color == 'white' else 'N'
        for dr, dc in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
             nr, nc = r + dr, c + dc
             if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == knight_char:
                 return True

        # Checking on straight lines and diagonals (rooks, bishops, queens, king)
        rook_char = 'r' if attacker_color == 'white' else 'R'
        bishop_char = 'b' if attacker_color == 'white' else 'B'
        queen_char = 'q' if attacker_color == 'white' else 'Q'
        king_char = 'k' if attacker_color == 'white' else 'K'

        # Straight lines (rook, queen)
        for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
            for i in range(1, 8):
                nr, nc = r + i*dr, c + i*dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    piece = self.board[nr][nc]
                    if piece != '.':
                        if piece in (rook_char, queen_char): return True
                        if i == 1 and piece == king_char: return True
                        break # Путь заблокирован
                else:
                    break
        
        # Diagonals (bishop, queen)
        for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            for i in range(1, 8):
                nr, nc = r + i*dr, c + i*dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    piece = self.board[nr][nc]
                    if piece != '.':
                        if piece in (bishop_char, queen_char): return True
                        if i == 1 and piece == king_char: return True
                        break
                else:
                    break
        
        return False

    def get_legal_moves(self):
        """
        Возвращает список всех легальных ходов для текущего игрока.
        Формат хода: ((from_row, from_col), (to_row, to_col))
        """
        legal_moves = []
        current_color = 'white' if self.white_to_move else 'black'
        pseudo_legal_moves = self._generate_pseudo_legal_moves()

        for move in pseudo_legal_moves:
            # We make a move on the temporary board to check if the king is under check
            temp_board = copy.deepcopy(self)
            temp_board._make_move_on_board(move)
            
            if not temp_board.is_in_check(current_color):
                legal_moves.append(move)
        
        return legal_moves
    
    def _generate_pseudo_legal_moves(self):
        """
        Генерирует все возможные ходы, не проверяя, останется ли король под шахом.
        Это "псевдо-легальные" ходы.
        """
        moves = []
        color = 'white' if self.white_to_move else 'black'
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if self.get_color(piece) == color:
                    moves.extend(self._get_moves_for_piece((r, c)))
        return moves

    def _get_moves_for_piece(self, pos):
        """Возвращает псевдо-легальные ходы для одной фигуры."""
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
        color = self.get_color(self.board[r][c])
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        # Move 1 square forward
        if 0 <= r + direction < 8 and self.board[r + direction][c] == '.':
            moves.append(((r, c), (r + direction, c)))
            # Move 2 squares from the starting position
            if r == start_row and self.board[r + 2 * direction][c] == '.':
                moves.append(((r, c), (r + 2 * direction, c)))
        
        # Taking it diagonally
        for dc in [-1, 1]:
            if 0 <= c + dc < 8:
                target_pos = (r + direction, c + dc)
                target_piece = self.get_piece_at(target_pos)
                if target_piece != '.' and self.get_color(target_piece) != color:
                    moves.append(((r, c), target_pos))
                # Взятие на проходе
                if target_pos == self.en_passant_target:
                    moves.append(((r, c), target_pos))
        return moves

    def _get_knight_moves(self, pos):
        moves = []
        r, c = pos
        color = self.get_color(self.board[r][c])
        for dr, dc in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target_piece = self.board[nr][nc]
                if self.get_color(target_piece) != color:
                    moves.append(((r, c), (nr, nc)))
        return moves

    def _get_king_moves(self, pos):
        moves = []
        r, c = pos
        color = self.get_color(self.board[r][c])
        # Usual moves
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if self.get_color(self.board[nr][nc]) != color:
                        moves.append(((r, c), (nr, nc)))
        # Castling
        if color == 'white':
            if self.castling_rights[0][0] and self.board[7][5] == '.' and self.board[7][6] == '.' and \
               not self._is_square_attacked((7, 4), 'black') and \
               not self._is_square_attacked((7, 5), 'black') and \
               not self._is_square_attacked((7, 6), 'black'):
                moves.append(((7, 4), (7, 6)))
            if self.castling_rights[0][1] and self.board[7][1] == '.' and self.board[7][2] == '.' and self.board[7][3] == '.' and \
               not self._is_square_attacked((7, 4), 'black') and \
               not self._is_square_attacked((7, 3), 'black') and \
               not self._is_square_attacked((7, 2), 'black'):
                moves.append(((7, 4), (7, 2)))
        else: # black
            if self.castling_rights[1][0] and self.board[0][5] == '.' and self.board[0][6] == '.' and \
               not self._is_square_attacked((0, 4), 'white') and \
               not self._is_square_attacked((0, 5), 'white') and \
               not self._is_square_attacked((0, 6), 'white'):
                moves.append(((0, 4), (0, 6)))
            if self.castling_rights[1][1] and self.board[0][1] == '.' and self.board[0][2] == '.' and self.board[0][3] == '.' and \
               not self._is_square_attacked((0, 4), 'white') and \
               not self._is_square_attacked((0, 3), 'white') and \
               not self._is_square_attacked((0, 2), 'white'):
                moves.append(((0, 4), (0, 2)))
        return moves

    def _get_sliding_moves(self, pos, directions):
        moves = []
        r, c = pos
        color = self.get_color(self.board[r][c])
        for dr, dc in directions:
            for i in range(1, 8):
                nr, nc = r + i * dr, c + i * dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target_piece = self.board[nr][nc]
                    if target_piece == '.':
                        moves.append(((r, c), (nr, nc)))
                    elif self.get_color(target_piece) != color:
                        moves.append(((r, c), (nr, nc)))
                        break
                    else:
                        break
                else: 
                    break
        return moves

    def make_move(self, move_str):
        """
        Принимает ход в формате 'e2e4', проверяет его легальность и выполняет.
        Возвращает True, если ход выполнен, иначе False.
        """
        if len(move_str) < 4: return False
        
        from_pos_str, to_pos_str = move_str[:2], move_str[2:4]
        promotion_piece = move_str[4] if len(move_str) == 5 else None

        from_pos = self._parse_pos(from_pos_str)
        to_pos = self._parse_pos(to_pos_str)
        
        if from_pos is None or to_pos is None:
            print("Error: Incorrect move format.")
            return False

        move = (from_pos, to_pos)
        legal_moves = self.get_legal_moves()

        if move not in legal_moves:
            print(f"Mistake: Illegal move '{move_str}'.")
            return False

        # If move is legal - come on
        self._make_move_on_board(move, promotion_piece)
        self.move_history.append(move_str)

        return True

    def _make_move_on_board(self, move, promotion_piece=None):
        """Внутренний метод для выполнения хода (без проверок легальности)."""
        from_pos, to_pos = move
        from_r, from_c = from_pos
        to_r, to_c = to_pos
        piece = self.board[from_r][from_c]
        
        # Resetting the 50-move counter if there was a capture or a pawn move
        if self.board[to_r][to_c] != '.' or piece.lower() == 'p':
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        # Updating move number
        if not self.white_to_move:
            self.fullmove_number += 1
            
        # Reset the target to take on the pass
        self.en_passant_target = None
        
        # Handling special moves
        # 1. Double pawn move (creates an opportunity for en passant)
        if piece.lower() == 'p' and abs(from_r - to_r) == 2:
            self.en_passant_target = ( (from_r + to_r) // 2, from_c )
        
        # 2. en passant / взятие на проходе
        if piece.lower() == 'p' and (to_r, to_c) == self.en_passant_target:
            self.board[from_r][to_c] = '.'
            
        # 3. Castling
        if piece.lower() == 'k' and abs(from_c - to_c) == 2:
            if to_c == 6: # Короткая
                self.board[to_r][5] = self.board[to_r][7]
                self.board[to_r][7] = '.'
            else: # Длинная
                self.board[to_r][3] = self.board[to_r][0]
                self.board[to_r][0] = '.'

        # Основное перемещение фигуры
        self.board[to_r][to_c] = piece
        self.board[from_r][from_c] = '.'

        # 4. Pawn transformation
        if piece.lower() == 'p' and (to_r == 0 or to_r == 7):
            promo = promotion_piece if promotion_piece and promotion_piece.lower() in 'qrbn' else 'q'
            self.board[to_r][to_c] = promo.upper() if self.white_to_move else promo.lower()
        
        # Updating catling rights
        if piece == 'K': self.castling_rights[0] = [False, False]
        elif piece == 'k': self.castling_rights[1] = [False, False]
        elif piece == 'R' and from_pos == (7, 7): self.castling_rights[0][0] = False
        elif piece == 'R' and from_pos == (7, 0): self.castling_rights[0][1] = False
        elif piece == 'r' and from_pos == (0, 7): self.castling_rights[1][0] = False
        elif piece == 'r' and from_pos == (0, 0): self.castling_rights[1][1] = False
        
        self.white_to_move = not self.white_to_move

    def is_game_over(self):
        """Проверяет, закончилась ли игра, и возвращает статус."""
        legal_moves = self.get_legal_moves()
        if not legal_moves:
            current_color = 'white' if self.white_to_move else 'black'
            if self.is_in_check(current_color):
                return "checkmate" # Мат
            else:
                return "stalemate" # Пат
        if self.halfmove_clock >= 100: # 50 moves rule
            return "draw_50_moves"
        # Другие правила ничьей (недостаточность материала, троекратное повторение) здесь не реализованы
        return "ongoing"