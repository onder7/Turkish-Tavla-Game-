"""
Tavla oyununun temel mantık sınıfları ve kuralları - DÜZELTİLMİŞ
"""
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict


class Player(Enum):
    WHITE = "beyaz"
    BLACK = "siyah"


class GameState(Enum):
    WAITING_DICE = "waiting_dice"
    SELECTING_PIECE = "selecting_piece"
    SELECTING_TARGET = "selecting_target"
    GAME_OVER = "game_over"


@dataclass
class Point:
    """Tavla tahtasındaki bir haneyi temsil eder"""
    count: int = 0
    owner: Optional[Player] = None
    
    def is_empty(self) -> bool:
        return self.count == 0
    
    def is_safe(self) -> bool:
        """Güvenli mi (2+ pul var mı)?"""
        return self.count >= 2
    
    def is_vulnerable(self) -> bool:
        """Vurulabilir mi (1 pul var mı)?"""
        return self.count == 1
    
    def can_land(self, player: Player) -> bool:
        """Bu oyuncu bu haneye inebilir mi?"""
        if self.is_empty():
            return True
        if self.owner == player:
            return True
        return self.is_vulnerable()  # Rakip tek pul varsa vurabilir
    
    def add_piece(self, player: Player) -> bool:
        """Pul ekle"""
        if self.is_empty():
            self.count = 1
            self.owner = player
            return True
        elif self.owner == player:
            self.count += 1
            return True
        return False
    
    def remove_piece(self) -> bool:
        """Pul çıkar"""
        if self.is_empty():
            return False
        self.count -= 1
        if self.count == 0:
            self.owner = None
        return True
    
    def hit_piece(self) -> bool:
        """Rakip pulu vur (tek pul varsa)"""
        if self.is_vulnerable():
            self.count = 0
            self.owner = None
            return True
        return False


@dataclass
class Move:
    """Bir hamleyi temsil eden sınıf"""
    from_point: int  # -2: bar, -1: bear_off, 0-23: normal haneler
    to_point: int    # -2: bar, -1: bear_off, 0-23: normal haneler
    dice_value: int
    
    def __str__(self):
        from_str = "Bar" if self.from_point == -2 else f"P{self.from_point + 1}"
        to_str = "Home" if self.to_point == -1 else f"P{self.to_point + 1}"
        return f"{from_str} -> {to_str} ({self.dice_value})"
    
    def __eq__(self, other):
        """Hamleleri karşılaştır"""
        if not isinstance(other, Move):
            return False
        return (self.from_point == other.from_point and 
                self.to_point == other.to_point and 
                self.dice_value == other.dice_value)


@dataclass
class GameStats:
    """Oyun istatistikleri"""
    games_played: int = 0
    white_wins: int = 0
    black_wins: int = 0
    total_moves: int = 0
    average_game_length: float = 0.0
    hit_pieces: int = 0
    
    @property
    def win_rate_white(self) -> float:
        return (self.white_wins / self.games_played * 100) if self.games_played > 0 else 0.0
    
    @property
    def win_rate_black(self) -> float:
        return (self.black_wins / self.games_played * 100) if self.games_played > 0 else 0.0


class Board:
    """Tavla tahtası ve pul pozisyonları"""
    
    def __init__(self):
        # 24 normal hane + 2 bar + 2 home
        self.points = [Point() for _ in range(28)]
        self.initialize_starting_position()
    
    def initialize_starting_position(self):
        """Standart tavla başlangıç pozisyonu"""
        # Tüm haneleri sıfırla
        for point in self.points:
            point.count = 0
            point.owner = None
        
        # Beyaz pullar (0->23 yönünde hareket, hane 24'ten 1'e)
        self.points[0].count = 2
        self.points[0].owner = Player.WHITE    # Hane 24: 2 beyaz pul
        
        self.points[11].count = 5
        self.points[11].owner = Player.WHITE   # Hane 13: 5 beyaz pul
        
        self.points[16].count = 3
        self.points[16].owner = Player.WHITE   # Hane 8: 3 beyaz pul
        
        self.points[18].count = 5
        self.points[18].owner = Player.WHITE   # Hane 6: 5 beyaz pul
        
        # Siyah pullar (23->0 yönünde hareket, hane 1'den 24'e)
        self.points[23].count = 2
        self.points[23].owner = Player.BLACK   # Hane 1: 2 siyah pul
        
        self.points[12].count = 5
        self.points[12].owner = Player.BLACK   # Hane 12: 5 siyah pul
        
        self.points[7].count = 3
        self.points[7].owner = Player.BLACK    # Hane 17: 3 siyah pul
        
        self.points[5].count = 5
        self.points[5].owner = Player.BLACK    # Hane 19: 5 siyah pul
    
    def get_piece_count(self, point_index: int, player: Player) -> int:
        """Belirtilen hanedeki oyuncu pullarının sayısını döndürür"""
        point = self.points[point_index]
        if point.owner == player:
            return point.count
        return 0
    
    def has_pieces_on_point(self, point_index: int, player: Player) -> bool:
        """Belirtilen hanede oyuncunun pulu var mı?"""
        return self.get_piece_count(point_index, player) > 0
    
    def get_bar_count(self, player: Player) -> int:
        """Bar'daki pul sayısını döndürür"""
        bar_index = 24 if player == Player.WHITE else 25
        return self.get_piece_count(bar_index, player)
    
    def get_home_count(self, player: Player) -> int:
        """Evdeki (toplanan) pul sayısını döndürür"""
        home_index = 26 if player == Player.WHITE else 27
        return self.get_piece_count(home_index, player)
    
    def has_pieces_in_bar(self, player: Player) -> bool:
        """Bar'da pul var mı?"""
        return self.get_bar_count(player) > 0
    
    def can_bear_off(self, player: Player) -> bool:
        """Pul toplayabilir mi?"""
        if self.has_pieces_in_bar(player):
            return False
        
        # Ev bölgesindeki haneleri kontrol et
        home_range = range(18, 24) if player == Player.WHITE else range(0, 6)
        total_pieces = 0
        
        for i in range(24):
            if self.has_pieces_on_point(i, player):
                if i not in home_range:
                    return False
                total_pieces += self.get_piece_count(i, player)
        
        # Evde toplanan pulları da say
        total_pieces += self.get_home_count(player)
        return total_pieces == 15
    
    def get_highest_piece_in_home(self, player: Player) -> int:
        """Ev bölgesindeki en yüksek pulu döndürür"""
        if player == Player.WHITE:
            for i in range(23, 17, -1):  # 23'ten 18'e
                if self.has_pieces_on_point(i, player):
                    return i
        else:
            for i in range(0, 6):  # 0'dan 5'e
                if self.has_pieces_on_point(i, player):
                    return i
        return -1
    
    def is_point_available(self, point_index: int, player: Player) -> bool:
        """Hane oyuncu için uygun mu?"""
        if point_index < 0 or point_index > 23:
            return False
        
        point = self.points[point_index]
        return point.can_land(player)
    
    def move_piece(self, from_point: int, to_point: int, player: Player) -> bool:
        """Pul hamlesini gerçekleştir"""
        # From point'ten pul al
        if from_point == -2:  # Bar'dan
            bar_index = 24 if player == Player.WHITE else 25
            if not self.has_pieces_in_bar(player):
                return False
            if not self.points[bar_index].remove_piece():
                return False
        else:  # Normal haneden
            if not self.has_pieces_on_point(from_point, player):
                return False
            if not self.points[from_point].remove_piece():
                return False
        
        # To point'e pul koy
        if to_point == -1:  # Toplama
            home_index = 26 if player == Player.WHITE else 27
            self.points[home_index].add_piece(player)
        else:  # Normal hane
            target_point = self.points[to_point]
            
            # Rakip pul varsa vur
            if target_point.owner and target_point.owner != player and target_point.is_vulnerable():
                opponent = target_point.owner
                opponent_bar = 24 if opponent == Player.WHITE else 25
                target_point.hit_piece()
                self.points[opponent_bar].add_piece(opponent)
            
            # Kendi pulunu koy
            target_point.add_piece(player)
        
        return True


class TavlaGame:
    """Ana oyun mantığı sınıfı"""
    
    def __init__(self):
        self.board = Board()
        self.current_player = Player.WHITE
        self.game_state = GameState.WAITING_DICE
        self.dice_values = [0, 0]
        self.moves_left = []
        self.winner = None
        self.move_count = 0
        self.stats = GameStats()
    
    def roll_dice(self) -> Tuple[int, int]:
        """Zar at"""
        if self.game_state != GameState.WAITING_DICE:
            return self.dice_values
        
        self.dice_values = [random.randint(1, 6), random.randint(1, 6)]
        
        # Çift gelirse 4 hamle
        if self.dice_values[0] == self.dice_values[1]:
            self.moves_left = [self.dice_values[0]] * 4
        else:
            self.moves_left = self.dice_values[:]
        
        self.game_state = GameState.SELECTING_PIECE
        return tuple(self.dice_values)
    
    def get_valid_moves(self, from_point: int = None) -> List[Move]:
        """Geçerli hamleleri döndürür"""
        moves = []
        
        # Eğer bar'da pul varsa sadece giriş hamleleri
        if self.board.has_pieces_in_bar(self.current_player):
            return self._get_bar_entry_moves()
        
        # Belirli bir haneden hamleler
        if from_point is not None:
            return self._get_moves_from_point(from_point)
        
        # Tüm geçerli hamleler
        for point in range(24):
            if self.board.has_pieces_on_point(point, self.current_player):
                moves.extend(self._get_moves_from_point(point))
        
        return moves
    
    def _get_bar_entry_moves(self) -> List[Move]:
        """Bar'dan giriş hamleleri"""
        moves = []
        unique_dice = sorted(list(set(self.moves_left)), reverse=True)
        
        for dice_val in unique_dice:
            if self.current_player == Player.WHITE:
                entry_point = dice_val - 1
            else:
                entry_point = 24 - dice_val
            
            if self.board.is_point_available(entry_point, self.current_player):
                moves.append(Move(-2, entry_point, dice_val))
        
        return moves
    
    def _get_moves_from_point(self, from_point: int) -> List[Move]:
        """Belirli bir haneden geçerli hamleler"""
        moves = []
        
        if not self.board.has_pieces_on_point(from_point, self.current_player):
            return moves
        
        unique_dice = sorted(list(set(self.moves_left)), reverse=True)
        
        for dice_val in unique_dice:
            # Normal hamle
            if self.current_player == Player.WHITE:
                to_point = from_point + dice_val
            else:
                to_point = from_point - dice_val
            
            # Tahtada kalır mı?
            if 0 <= to_point <= 23:
                if self.board.is_point_available(to_point, self.current_player):
                    moves.append(Move(from_point, to_point, dice_val))
            
            # Pul toplama kontrolü
            elif self.board.can_bear_off(self.current_player):
                # Tam çıkış
                if ((self.current_player == Player.WHITE and to_point == 24) or
                    (self.current_player == Player.BLACK and to_point == -1)):
                    moves.append(Move(from_point, -1, dice_val))
                # Aşırı çıkış (en yüksek puldan)
                elif from_point == self.board.get_highest_piece_in_home(self.current_player):
                    moves.append(Move(from_point, -1, dice_val))
        
        return moves
    
    def make_move(self, move: Move) -> bool:
        """Hamleyi gerçekleştir - ARTIK OTOMATİK END_TURN YOK"""
        if move.dice_value not in self.moves_left:
            return False
        
        # Hamleyi kontrol et
        valid_moves = self.get_valid_moves(move.from_point if move.from_point >= 0 else None)
        if move not in valid_moves:
            return False
        
        # Hamleyi yap
        if self.board.move_piece(move.from_point, move.to_point, self.current_player):
            self.moves_left.remove(move.dice_value)
            self.move_count += 1
            self._check_winner()
            
            # Otomatik tur sonu kontrolü KALDIRILDI
            # Artık sadece hamleyi yapar, tur yönetimi main.py'da
            
            return True
        
        return False
    
    def should_end_turn(self) -> bool:
        """Tur bitirmeli mi?"""
        return not self.moves_left or not self.can_move()
    
    def _check_winner(self):
        """Kazananı kontrol et"""
        if self.board.get_home_count(Player.WHITE) >= 15:
            self.winner = Player.WHITE
            self.game_state = GameState.GAME_OVER
            self._update_stats()
        elif self.board.get_home_count(Player.BLACK) >= 15:
            self.winner = Player.BLACK
            self.game_state = GameState.GAME_OVER
            self._update_stats()
    
    def _update_stats(self):
        """İstatistikleri güncelle"""
        self.stats.games_played += 1
        self.stats.total_moves += self.move_count
        
        if self.winner == Player.WHITE:
            self.stats.white_wins += 1
        elif self.winner == Player.BLACK:
            self.stats.black_wins += 1
        
        self.stats.average_game_length = self.stats.total_moves / self.stats.games_played
    
    def end_turn(self):
        """Turu bitir"""
        if self.game_state == GameState.GAME_OVER:
            return
        
        self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE
        self.game_state = GameState.WAITING_DICE
        self.dice_values = [0, 0]
        self.moves_left = []
    
    def can_move(self) -> bool:
        """Oyuncu hamle yapabilir mi?"""
        return len(self.get_valid_moves()) > 0
    
    def validate_board_state(self) -> bool:
        """Tahta durumunu doğrula (debug için)"""
        white_count = 0
        black_count = 0
        
        # Normal hanelerdeki pulları say
        for i in range(24):
            point = self.board.points[i]
            if not point.is_empty():
                if point.owner == Player.WHITE:
                    white_count += point.count
                elif point.owner == Player.BLACK:
                    black_count += point.count
        
        # Bar'daki pulları say
        white_count += self.board.get_bar_count(Player.WHITE)
        black_count += self.board.get_bar_count(Player.BLACK)
        
        # Evdeki pulları say
        white_count += self.board.get_home_count(Player.WHITE)
        black_count += self.board.get_home_count(Player.BLACK)
        
        valid = white_count == 15 and black_count == 15
        if not valid:
            print(f"HATA: Pul sayıları yanlış! Beyaz: {white_count}, Siyah: {black_count}")
        
        return valid
    
    def print_board_state(self):
        """Tahta durumunu konsola yazdır (debug için)"""
        print("\n=== TAHTA DURUMU ===")
        
        # Üst sıra (13-24)
        print("Üst:  ", end="")
        for i in range(12, 24):
            point = self.board.points[i]
            if point.is_empty():
                print("  .  ", end="")
            else:
                symbol = "W" if point.owner == Player.WHITE else "B"
                print(f"{symbol:>2}{point.count:<2}", end=" ")
        print()
        
        # Hane numaraları
        print("Hane: ", end="")
        for i in range(13, 25):
            print(f"{i:>4}", end=" ")
        print()
        
        print("      " + "="*60)
        
        # Hane numaraları
        print("Hane: ", end="")
        for i in range(12, 0, -1):
            print(f"{i:>4}", end=" ")
        print()
        
        # Alt sıra (12-1)
        print("Alt:  ", end="")
        for i in range(11, -1, -1):
            point = self.board.points[i]
            if point.is_empty():
                print("  .  ", end="")
            else:
                symbol = "W" if point.owner == Player.WHITE else "B"
                print(f"{symbol:>2}{point.count:<2}", end=" ")
        print()
        
        # Bar ve home bilgileri
        white_bar = self.board.get_bar_count(Player.WHITE)
        black_bar = self.board.get_bar_count(Player.BLACK)
        white_home = self.board.get_home_count(Player.WHITE)
        black_home = self.board.get_home_count(Player.BLACK)
        
        print(f"\nBar: Beyaz {white_bar}, Siyah {black_bar}")
        print(f"Ev:  Beyaz {white_home}, Siyah {black_home}")
        print(f"Sıra: {self.current_player.value}")
        if self.moves_left:
            print(f"Kalan hamleler: {self.moves_left}")
        print("="*60)
    
    def reset_game(self):
        """Oyunu sıfırla"""
        self.board = Board()
        self.current_player = Player.WHITE
        self.game_state = GameState.WAITING_DICE
        self.dice_values = [0, 0]
        self.moves_left = []
        self.winner = None
        self.move_count = 0
        
        # Başlangıç durumunu doğrula
        if not self.validate_board_state():
            print("UYARI: Başlangıç tahta durumu geçersiz!")
        else:
            print("Oyun başarıyla sıfırlandı - tahta durumu geçerli")
    
    def get_game_statistics(self) -> Dict:
        """Oyun istatistiklerini döndür"""
        white_on_board = 0
        black_on_board = 0
        
        for i in range(24):
            point = self.board.points[i]
            if not point.is_empty():
                if point.owner == Player.WHITE:
                    white_on_board += point.count
                elif point.owner == Player.BLACK:
                    black_on_board += point.count
        
        return {
            'move_count': self.move_count,
            'current_player': self.current_player.value,
            'game_state': self.game_state.value,
            'white_pieces': {
                'board': white_on_board,
                'bar': self.board.get_bar_count(Player.WHITE),
                'home': self.board.get_home_count(Player.WHITE),
                'total': white_on_board + self.board.get_bar_count(Player.WHITE) + self.board.get_home_count(Player.WHITE)
            },
            'black_pieces': {
                'board': black_on_board,
                'bar': self.board.get_bar_count(Player.BLACK),
                'home': self.board.get_home_count(Player.BLACK),
                'total': black_on_board + self.board.get_bar_count(Player.BLACK) + self.board.get_home_count(Player.BLACK)
            },
            'can_bear_off': {
                'white': self.board.can_bear_off(Player.WHITE),
                'black': self.board.can_bear_off(Player.BLACK)
            }
        }
