"""
Tavla AI oyuncu stratejileri
"""
import random
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod

from game_logic import TavlaGame, Move, Player, Board


class AIStrategy(ABC):
    """AI stratejisi için temel sınıf"""
    
    @abstractmethod
    def choose_move(self, game: TavlaGame) -> Optional[Move]:
        """En iyi hamleyi seç"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Strateji adını döndür"""
        pass


class RandomAI(AIStrategy):
    """Rastgele hamle yapan AI"""
    
    def choose_move(self, game: TavlaGame) -> Optional[Move]:
        moves = game.get_valid_moves()
        return random.choice(moves) if moves else None
    
    def get_name(self) -> str:
        return "Random AI"


class GreedyAI(AIStrategy):
    """Açgözlü strateji - kısa vadeli en iyi hamleleri yapar"""
    
    def choose_move(self, game: TavlaGame) -> Optional[Move]:
        moves = game.get_valid_moves()
        if not moves:
            return None
        
        # Hamleleri değerlendir ve en iyisini seç
        best_move = None
        best_score = float('-inf')
        
        for move in moves:
            score = self._evaluate_move(game, move)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _evaluate_move(self, game: TavlaGame, move: Move) -> float:
        """Hamleyi değerlendir"""
        score = 0.0
        
        # Bar'dan çıkma yüksek öncelik
        if move.from_point == -2:
            score += 100
        
        # Pul toplama yüksek öncelik
        if move.to_point == -1:
            score += 80
        
        # Rakip pul vurma
        if move.to_point >= 0 and move.to_point <= 23:
            target_point = game.board.points[move.to_point]
            if (not target_point.is_empty() and 
                target_point.owner != game.current_player and 
                target_point.is_vulnerable()):
                score += 50
        
        # Ev bölgesine götürme
        if game.current_player == Player.WHITE and move.to_point >= 18:
            score += 30
        elif game.current_player == Player.BLACK and move.to_point <= 5:
            score += 30
        
        # İleri gitme
        if game.current_player == Player.WHITE:
            score += move.dice_value * 2
        else:
            score += move.dice_value * 2
        
        # Güvenli haneye gitme (2+ pul olan)
        if move.to_point >= 0 and move.to_point <= 23:
            target_point = game.board.points[move.to_point]
            if (not target_point.is_empty() and 
                target_point.owner == game.current_player and 
                target_point.count >= 1):
                score += 10
        
        return score
    
    def get_name(self) -> str:
        return "Greedy AI"


class AdvancedAI(AIStrategy):
    """Gelişmiş strateji - pozisyon değerlendirmesi ve lookahead"""
    
    def __init__(self, depth: int = 2):
        self.depth = depth
    
    def choose_move(self, game: TavlaGame) -> Optional[Move]:
        moves = game.get_valid_moves()
        if not moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        for move in moves:
            # Hamleyi simüle et
            score = self._minimax(game, move, self.depth, True)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _minimax(self, game: TavlaGame, move: Move, depth: int, maximizing: bool) -> float:
        """Minimax algoritması ile hamle değerlendirmesi"""
        if depth == 0:
            return self._evaluate_position(game)
        
        # Hamleyi simüle et
        original_board = self._copy_board(game.board)
        original_moves = game.moves_left[:]
        
        if not game.make_move(move):
            return float('-inf') if maximizing else float('inf')
        
        if game.winner:
            score = 1000 if game.winner == game.current_player else -1000
        else:
            # Tüm olası zar kombinasyonlarını değerlendir
            score = self._evaluate_dice_outcomes(game, depth - 1, not maximizing)
        
        # Geri al
        game.board = original_board
        game.moves_left = original_moves
        
        return score
    
    def _evaluate_dice_outcomes(self, game: TavlaGame, depth: int, maximizing: bool) -> float:
        """Olası zar sonuçlarını değerlendir"""
        total_score = 0.0
        outcomes = 0
        
        # Tüm zar kombinasyonları (1,1) ile (6,6) arası
        for d1 in range(1, 7):
            for d2 in range(1, 7):
                # Zar sonucunu simüle et
                old_dice = game.dice_values
                old_moves = game.moves_left[:]
                
                game.dice_values = [d1, d2]
                if d1 == d2:
                    game.moves_left = [d1] * 4
                else:
                    game.moves_left = [d1, d2]
                
                # Bu zar sonucu için en iyi hamleyi bul
                possible_moves = game.get_valid_moves()
                if possible_moves:
                    best_move_score = float('-inf') if maximizing else float('inf')
                    for possible_move in possible_moves:
                        score = self._minimax(game, possible_move, depth, maximizing)
                        if maximizing:
                            best_move_score = max(best_move_score, score)
                        else:
                            best_move_score = min(best_move_score, score)
                    total_score += best_move_score
                else:
                    total_score += self._evaluate_position(game)
                
                outcomes += 1
                
                # Geri al
                game.dice_values = old_dice
                game.moves_left = old_moves
        
        return total_score / outcomes if outcomes > 0 else 0.0
    
    def _evaluate_position(self, game: TavlaGame) -> float:
        """Pozisyonu değerlendir"""
        score = 0.0
        player = game.current_player
        opponent = Player.BLACK if player == Player.WHITE else Player.WHITE
        
        # Evdeki pul sayısı
        score += game.board.get_home_count(player) * 10
        score -= game.board.get_home_count(opponent) * 10
        
        # Bar'daki pul sayısı (negatif)
        score -= game.board.get_bar_count(player) * 20
        score += game.board.get_bar_count(opponent) * 20
        
        # Pul dağılımı ve güvenlik
        for point in range(24):
            if game.board.has_pieces_on_point(point, player):
                count = game.board.get_piece_count(point, player)
                # Güvenli haneler (2+ pul)
                if count >= 2:
                    score += 5
                # Tek pul (risk)
                elif count == 1:
                    score -= 2
                
                # İlerleme puanı
                if player == Player.WHITE:
                    score += point * 0.5
                else:
                    score += (23 - point) * 0.5
            
            if game.board.has_pieces_on_point(point, opponent):
                count = game.board.get_piece_count(point, opponent)
                if count == 1:  # Vurulabilir pul
                    score += 3
        
        # Pul toplama yeteneği
        if game.board.can_bear_off(player):
            score += 15
        if game.board.can_bear_off(opponent):
            score -= 15
        
        return score
    
    def _copy_board(self, board: Board) -> Board:
        """Tahtayı kopyala"""
        new_board = Board()
        # Point objelerini kopyala
        for i in range(28):
            new_board.points[i].count = board.points[i].count
            new_board.points[i].owner = board.points[i].owner
        return new_board
    
    def get_name(self) -> str:
        return f"Advanced AI (depth {self.depth})"


class AIPlayer:
    """AI oyuncu sınıfı"""
    
    def __init__(self, strategy: AIStrategy, player_color: Player = Player.BLACK):
        self.strategy = strategy
        self.player_color = player_color
        self.games_won = 0
        self.games_played = 0
        self.total_thinking_time = 0.0
    
    def choose_move(self, game: TavlaGame) -> Optional[Move]:
        """AI'nın hamle seçimi"""
        if game.current_player != self.player_color:
            return None
        
        import time
        start_time = time.time()
        
        move = self.strategy.choose_move(game)
        
        thinking_time = time.time() - start_time
        self.total_thinking_time += thinking_time
        
        return move
    
    def update_stats(self, won: bool):
        """İstatistikleri güncelle"""
        self.games_played += 1
        if won:
            self.games_won += 1
    
    @property
    def win_rate(self) -> float:
        """Kazanma oranı"""
        return (self.games_won / self.games_played * 100) if self.games_played > 0 else 0.0
    
    @property
    def average_thinking_time(self) -> float:
        """Ortalama düşünme süresi"""
        return (self.total_thinking_time / self.games_played) if self.games_played > 0 else 0.0
    
    def get_info(self) -> Dict:
        """AI bilgilerini döndür"""
        return {
            'strategy': self.strategy.get_name(),
            'games_played': self.games_played,
            'games_won': self.games_won,
            'win_rate': self.win_rate,
            'avg_thinking_time': self.average_thinking_time
        }


# Hazır AI stratejileri
def create_easy_ai() -> AIPlayer:
    """Kolay AI - Rastgele ve basit açgözlü karışımı"""
    class EasyAI(AIStrategy):
        def choose_move(self, game: TavlaGame) -> Optional[Move]:
            moves = game.get_valid_moves()
            if not moves:
                return None
            
            # %70 rastgele, %30 açgözlü
            if random.random() < 0.7:
                return random.choice(moves)
            else:
                return GreedyAI().choose_move(game)
        
        def get_name(self) -> str:
            return "Easy AI"
    
    return AIPlayer(EasyAI())


def create_medium_ai() -> AIPlayer:
    """Orta AI - Açgözlü strateji"""
    return AIPlayer(GreedyAI())


def create_hard_ai() -> AIPlayer:
    """Zor AI - Gelişmiş strateji"""
    return AIPlayer(AdvancedAI(depth=2))


def create_expert_ai() -> AIPlayer:
    """Uzman AI - Daha derin analiz"""
    return AIPlayer(AdvancedAI(depth=3))
