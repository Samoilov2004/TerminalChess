import copy
from dataclasses import dataclass
from typing import List, Tuple, Optional
import random

from pieces import piece, pawn, knight, bishop, rook, queen, king

# Удобные константы
WHITE, BLACK = 'w', 'b'


@dataclass
class MoveRecord:
    """Хранит всю информацию, необходимую для отмены хода."""
    move: Tuple[Tuple[int, int], Tuple[int, int]]
    captured_piece: Optional[piece.Piece]
    castling_rights: 'CastlingRights'
    en_passant_target: Optional[Tuple[int, int]]
    halfmove_clock: int
    piece_had_moved: bool
    is_promotion: bool = False
    is_en_passant_capture: bool = False


class CastlingRights:
    """Простой класс для хранения прав на рокировку."""
    def __init__(self, w_king: bool, w_queen: bool, b_king: bool, b_queen: bool):
        self.wk = w_king
        self.wq = w_queen
        self.bk = b_king
        self.bq = b_queen

    def __repr__(self) -> str:
        s = ""
        if self.wk: s += "K"
        if self.wq: s += "Q"
        if self.bk: s += "k"
        if self.bq: s += "q"
        return s or "-"


class Board:
    """
    Класс, представляющий шахматную доску.
    Отвечает за состояние доски, генерацию ходов и их выполнение.
    Координаты: (ряд, колонка), где (0, 0) - это a8, (7, 7) - это h1.
    """
    def __init__(self, is_chess960: bool = False):
        self.board: List[List[Optional[piece.Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.color_to_move: str = WHITE
        self.castling_rights: CastlingRights = CastlingRights(True, True, True, True)
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1
        self.history: List[MoveRecord] = []
        self.is_chess960 = is_chess960
        # В 960 сохраняем начальные позиции ладей
        self.initial_rook_files: dict = {'w': [], 'b': []}
        
        if is_chess960:
            self._setup_board_960()
        else:
            self._setup_board()
    
    def _setup_board(self):
        pieces_map = {0: rook.Rook, 1: knight.Knight, 2: bishop.Bishop, 3: queen.Queen, 4: king.King, 5: bishop.Bishop, 6: knight.Knight, 7: rook.Rook}
        for i in range(8):
            self.board[0][i] = pieces_map[i](BLACK); self.board[1][i] = pawn.Pawn(BLACK)
            self.board[6][i] = pawn.Pawn(WHITE); self.board[7][i] = pieces_map[i](WHITE)

    def _setup_board_960(self):
        """Расставляет фигуры для Шахмат-960 с исправленной логикой."""
        for i in range(8):
            self.board[1][i] = pawn.Pawn(BLACK)
            self.board[6][i] = pawn.Pawn(WHITE)

        dark_squares = [0, 2, 4, 6]
        light_squares = [1, 3, 5, 7]
        random.shuffle(dark_squares)
        random.shuffle(light_squares)
        
        b1_pos, b2_pos = dark_squares.pop(), light_squares.pop()
        
        remaining_squares = dark_squares + light_squares
        random.shuffle(remaining_squares)
        n1_pos, n2_pos = remaining_squares.pop(), remaining_squares.pop()
        
        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        # Строка `remaining_squares.append(n2_pos)` была удалена.
        # Теперь в `remaining_squares` 4 элемента.
        
        random.shuffle(remaining_squares)
        q_pos = remaining_squares.pop()
        
        # Теперь в `remaining_squares` 3 элемента, как и должно быть.
        r1_pos, k_pos, r2_pos = sorted(remaining_squares)

        placement = {
            b1_pos: bishop.Bishop, b2_pos: bishop.Bishop,
            n1_pos: knight.Knight, n2_pos: knight.Knight,
            q_pos: queen.Queen,
            r1_pos: rook.Rook, k_pos: king.King, r2_pos: rook.Rook
        }
        
        self.initial_rook_files['w'] = [r1_pos, r2_pos]
        self.initial_rook_files['b'] = [r1_pos, r2_pos]

        for col, piece_class in placement.items():
            self.board[7][col] = piece_class(WHITE)
            self.board[0][col] = piece_class(BLACK)

    def get_piece_at(self, pos: Tuple[int, int]) -> Optional[piece.Piece]:
        row, col = pos
        return self.board[row][col]

    def set_piece_at(self, pos: Tuple[int, int], p: Optional[piece.Piece]):
        row, col = pos
        self.board[row][col] = p

    @staticmethod
    def is_on_board(pos: Tuple[int, int]) -> bool:
        """Проверяет, находятся ли координаты в пределах доски."""
        row, col = pos
        return 0 <= row < 8 and 0 <= col < 8

    def is_attacked_by(self, pos: Tuple[int, int], attacking_color: str) -> bool:
        """Проверяет, атакована ли клетка `pos` фигурами цвета `attacking_color`."""
        # Атака пешкой
        pawn_dir = 1 if attacking_color == WHITE else -1
        for col_offset in [-1, 1]:
            p_pos = (pos[0] + pawn_dir, pos[1] + col_offset)
            if self.is_on_board(p_pos):
                p = self.get_piece_at(p_pos)
                if isinstance(p, pawn.Pawn) and p.color == attacking_color:
                    return True

        # Атака конем
        knight_moves = [(-2, 1),(-2,-1),(-1, 2),(-1,-2),(1, 2),(1,-2),(2, 1),(2,-1)]
        for dr, dc in knight_moves:
            k_pos = (pos[0] + dr, pos[1] + dc)
            if self.is_on_board(k_pos):
                p = self.get_piece_at(k_pos)
                if isinstance(p, knight.Knight) and p.color == attacking_color:
                    return True

        # Атака скользящими фигурами (ладья, слон, ферзь) и королем
        directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        for dr, dc in directions:
            for i in range(1, 8):
                check_pos = (pos[0] + i * dr, pos[1] + i * dc)
                if not self.is_on_board(check_pos): break
                p = self.get_piece_at(check_pos)
                if p:
                    if p.color == attacking_color:
                        is_rook_dir = (dr == 0 or dc == 0)
                        is_bishop_dir = (dr != 0 and dc != 0)
                        if (isinstance(p, king.King) and i==1) or \
                           (isinstance(p, rook.Rook) and is_rook_dir) or \
                           (isinstance(p, bishop.Bishop) and is_bishop_dir) or \
                           isinstance(p, queen.Queen):
                            return True
                    break # Фигура блокирует дальнейшую атаку в этом направлении
        return False

    def find_king(self, color: str) -> Optional[Tuple[int, int]]:
        """Находит позицию короля заданного цвета."""
        for r in range(8):
            for c in range(8):
                p = self.get_piece_at((r, c))
                if isinstance(p, king.King) and p.color == color:
                    return (r, c)
        return None

    def is_in_check(self, color: str) -> bool:
        """Проверяет, находится ли король цвета `color` под шахом."""
        king_pos = self.find_king(color)
        if king_pos is None: return False
        return self.is_attacked_by(king_pos, BLACK if color == WHITE else WHITE)

    def get_legal_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Генерирует все легальные ходы для текущего игрока."""
        legal_moves = []
        for move in self._generate_pseudo_legal_moves():
            start_pos, end_pos = move
            # Симулируем ход, чтобы проверить, не окажется ли король под шахом
            piece_at_start = self.get_piece_at(start_pos)
            self.set_piece_at(start_pos, None)
            piece_at_end = self.get_piece_at(end_pos)
            self.set_piece_at(end_pos, piece_at_start)

            if not self.is_in_check(self.color_to_move):
                legal_moves.append(move)
            
            # Отменяем симуляцию
            self.set_piece_at(start_pos, piece_at_start)
            self.set_piece_at(end_pos, piece_at_end)
        return legal_moves

    def _generate_pseudo_legal_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Генерирует все ходы, не проверяя на шах королю."""
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.get_piece_at((r, c))
                if p and p.color == self.color_to_move:
                    for move_end in p.get_moves(self, (r, c)):
                        moves.append(((r, c), move_end))
        moves.extend(self._generate_castling_moves())
        return moves

    def _generate_castling_moves(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Генерирует ходы рокировки. Теперь поддерживает классику и 960."""
        moves = []
        if self.is_in_check(self.color_to_move): return []

        king_pos = self.find_king(self.color_to_move)
        if not king_pos: return []
        
        king_row, king_col = king_pos
        opponent_color = BLACK if self.color_to_move == WHITE else WHITE

        # --- Целевые поля для короля и ладьи ПОСЛЕ рокировки (всегда одни и те же) ---
        q_side_king_dest_col, q_side_rook_dest_col = 2, 3  # c-file, d-file
        k_side_king_dest_col, k_side_rook_dest_col = 6, 5  # g-file, f-file

        # --- Начальные поля ладей ---
        # В 960 они случайные, в классике - фиксированные
        if self.is_chess960:
            rook_files = self.initial_rook_files[self.color_to_move]
            q_side_rook_col = min(rook_files) if rook_files else -1
            k_side_rook_col = max(rook_files) if rook_files else -1
        else:
            q_side_rook_col, k_side_rook_col = 0, 7
        
        opponent_color = BLACK if self.color_to_move == WHITE else WHITE
        if self.color_to_move == WHITE:
            row = 7
            if self.castling_rights.wk and \
               self.get_piece_at((row, 5)) is None and self.get_piece_at((row, 6)) is None and \
               not self.is_attacked_by((row, 4), opponent_color) and \
               not self.is_attacked_by((row, 5), opponent_color) and \
               not self.is_attacked_by((row, 6), opponent_color):
                moves.append(((row, 4), (row, 6)))
            if self.castling_rights.wq and \
               self.get_piece_at((row, 1)) is None and self.get_piece_at((row, 2)) is None and self.get_piece_at((row, 3)) is None and \
               not self.is_attacked_by((row, 4), opponent_color) and \
               not self.is_attacked_by((row, 3), opponent_color) and \
               not self.is_attacked_by((row, 2), opponent_color):
                moves.append(((row, 4), (row, 2)))
        else: # Черные
            row = 0
            if self.castling_rights.bk and \
               self.get_piece_at((row, 5)) is None and self.get_piece_at((row, 6)) is None and \
               not self.is_attacked_by((row, 4), opponent_color) and \
               not self.is_attacked_by((row, 5), opponent_color) and \
               not self.is_attacked_by((row, 6), opponent_color):
                moves.append(((row, 4), (row, 6)))
            if self.castling_rights.bq and \
               self.get_piece_at((row, 1)) is None and self.get_piece_at((row, 2)) is None and self.get_piece_at((row, 3)) is None and \
               not self.is_attacked_by((row, 4), opponent_color) and \
               not self.is_attacked_by((row, 3), opponent_color) and \
               not self.is_attacked_by((row, 2), opponent_color):
                moves.append(((row, 4), (row, 2)))

        return moves


    def make_move(self, move: Tuple[Tuple[int, int], Tuple[int, int]], promotion_piece_class=None):
        """Выполняет ход, обновляет все состояния и сохраняет историю."""
        start_pos, end_pos = move
        piece_to_move = self.get_piece_at(start_pos)
        if piece_to_move is None:
            raise ValueError("No piece at start position to move.")

        # --- СОХРАНЕНИЕ СОСТОЯНИЯ ДЛЯ ОТМЕНЫ ХОДА ---
        captured_piece = self.get_piece_at(end_pos)
        is_en_passant_capture = isinstance(piece_to_move, pawn.Pawn) and end_pos == self.en_passant_target
        if is_en_passant_capture:
            pawn_dir = -1 if piece_to_move.color == WHITE else 1
            captured_piece_pos = (end_pos[0] - pawn_dir, end_pos[1])
            captured_piece = self.get_piece_at(captured_piece_pos)

        record = MoveRecord(
            move=move, captured_piece=captured_piece, 
            castling_rights=copy.deepcopy(self.castling_rights),
            en_passant_target=self.en_passant_target, 
            halfmove_clock=self.halfmove_clock,
            piece_had_moved=piece_to_move.has_moved,
            is_promotion=(isinstance(piece_to_move, pawn.Pawn) and (end_pos[0] in [0, 7])),
            is_en_passant_capture=is_en_passant_capture
        )
        self.history.append(record)
        
        # --- ИСПОЛНЕНИЕ ХОДА ---
        self.en_passant_target = None # Сброс флага в начале хода

        # 1. Двойной ход пешки (создает возможность для en passant)
        if isinstance(piece_to_move, pawn.Pawn) and abs(start_pos[0] - end_pos[0]) == 2:
            self.en_passant_target = ((start_pos[0] + end_pos[0]) // 2, start_pos[1])
        # 2. Взятие на проходе - удаляем съеденную пешку
        if is_en_passant_capture:
            self.set_piece_at(record.captured_piece.get_position_from_board(self.board), None) # Усложнено, найдем позицию по ссылке
        # 3. Рокировка - перемещаем ладью
        if isinstance(piece_to_move, king.King) and abs(start_pos[1] - end_pos[1]) == 2:
            rook_start = (start_pos[0], 7 if end_pos[1] > start_pos[1] else 0)
            rook_end = (start_pos[0], 5 if end_pos[1] > start_pos[1] else 3)
            rook_piece = self.get_piece_at(rook_start)
            self.set_piece_at(rook_end, rook_piece)
            self.set_piece_at(rook_start, None)
            if rook_piece: rook_piece.has_moved = True

        # Основное движение фигуры
        self.set_piece_at(end_pos, piece_to_move)
        self.set_piece_at(start_pos, None)
        piece_to_move.has_moved = True

        # 4. Превращение пешки
        if record.is_promotion:
            self.set_piece_at(end_pos, (promotion_piece_class or queen.Queen)(self.color_to_move))

        # --- ОБНОВЛЕНИЕ СОСТОЯНИЙ ПОСЛЕ ХОДА ---
        # Обновление прав на рокировку (если двинулся король/ладья или съедена ладья)
        self._update_castling_rights(start_pos, end_pos)
        
        # Обновление счетчиков
        if isinstance(piece_to_move, pawn.Pawn) or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        if self.color_to_move == BLACK:
            self.fullmove_number += 1
            
        self.color_to_move = BLACK if self.color_to_move == WHITE else WHITE

    def undo_move(self):
        """Отменяет последний сделанный ход."""
        if not self.history: return
        last_record = self.history.pop()
        start_pos, end_pos = last_record.move
        
        # Восстановление состояния доски
        self.castling_rights = last_record.castling_rights
        self.en_passant_target = last_record.en_passant_target
        self.halfmove_clock = last_record.halfmove_clock
        
        self.color_to_move = BLACK if self.color_to_move == WHITE else WHITE
        if self.color_to_move == BLACK: self.fullmove_number -= 1

        # Перемещение фигур обратно
        moved_piece = self.get_piece_at(end_pos)
        if last_record.is_promotion:
            moved_piece = pawn.Pawn(self.color_to_move)

        self.set_piece_at(start_pos, moved_piece)
        if moved_piece: moved_piece.has_moved = last_record.piece_had_moved
        
        # Возврат съеденной фигуры
        if last_record.is_en_passant_capture:
            self.set_piece_at(end_pos, None)
            pawn_dir = -1 if self.color_to_move == WHITE else 1
            captured_pos = (end_pos[0] - pawn_dir, end_pos[1])
            self.set_piece_at(captured_pos, last_record.captured_piece)
        else:
            self.set_piece_at(end_pos, last_record.captured_piece)
            
        # Отмена рокировки
        if isinstance(moved_piece, king.King) and abs(start_pos[1] - end_pos[1]) == 2:
            rook_start = (start_pos[0], 7 if end_pos[1] > start_pos[1] else 0)
            rook_end = (start_pos[0], 5 if end_pos[1] > start_pos[1] else 3)
            rook_piece = self.get_piece_at(rook_end)
            self.set_piece_at(rook_start, rook_piece)
            self.set_piece_at(rook_end, None)
            if rook_piece: rook_piece.has_moved = False

    def _update_castling_rights(self, start_pos: tuple, end_pos: tuple):
        """Обновляет права на рокировку после хода."""
        piece = self.get_piece_at(end_pos) # Уже перемещенная
        # Движение короля
        if isinstance(piece, king.King):
            if piece.color == WHITE: self.castling_rights.wk = self.castling_rights.wq = False
            else: self.castling_rights.bk = self.castling_rights.bq = False
        # Движение ладьи
        if isinstance(piece, rook.Rook):
            if start_pos == (7, 0): self.castling_rights.wq = False
            elif start_pos == (7, 7): self.castling_rights.wk = False
            elif start_pos == (0, 0): self.castling_rights.bq = False
            elif start_pos == (0, 7): self.castling_rights.bk = False

    def get_game_status(self) -> str:
        """Определяет текущий статус игры."""
        if not self.get_legal_moves():
            return 'checkmate' if self.is_in_check(self.color_to_move) else 'stalemate'
        if self.halfmove_clock >= 100: return 'draw'
        # TODO: Добавить проверку на троекратное повторение и недостаток материала
        return 'in_progress'

    def load_from_fen(self, fen: str):
        """Загружает позицию и состояние игры из FEN-строки."""
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.history = []
        
        parts = fen.split(' ')
        piece_placement, active_color, castling, en_passant, halfmove, fullmove = parts[:6]

        # 1. Расстановка фигур
        piece_map = {'p':pawn.Pawn,'r':rook.Rook,'n':knight.Knight,'b':bishop.Bishop,'q':queen.Queen,'k':king.King}
        rows = piece_placement.split('/')
        for r, row_str in enumerate(rows):
            c = 0
            for char in row_str:
                if char.isdigit():
                    c += int(char)
                else:
                    color = WHITE if char.isupper() else BLACK
                    piece_class = piece_map[char.lower()]
                    self.set_piece_at((r, c), piece_class(color))
                    c += 1
        
        # 2. Чей ход
        self.color_to_move = active_color
        
        # 3. Права на рокировку
        self.castling_rights = CastlingRights(
            'K' in castling, 'Q' in castling,
            'k' in castling, 'q' in castling
        )
        
        # 4. Взятие на проходе
        if en_passant != '-':
            col = 'abcdefgh'.find(en_passant[0])
            row = 8 - int(en_passant[1])
            self.en_passant_target = (row, col)
        else:
            self.en_passant_target = None
            
        # 5-6. Счетчики
        self.halfmove_clock = int(halfmove)
        self.fullmove_number = int(fullmove)

    def __str__(self) -> str:
        """Строковое представление доски для отладки."""
        s = "  a b c d e f g h\n"
        for r in range(8):
            s += f"{8 - r} "
            for c in range(8):
                p = self.board[r][c]
                s += (p.symbol if p else '.') + ' '
            s += f" {8 - r}\n"
        s += "  a b c d e f g h\n"
        return s

