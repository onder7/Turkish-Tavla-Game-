"""
Tavla oyununun görüntüleme katmanı
"""
import pygame
import math
from typing import List, Tuple, Optional, Dict, TYPE_CHECKING
from dataclasses import dataclass

# Import game logic to access Player enum
from game_logic import Player

# Forward reference to avoid circular imports
if TYPE_CHECKING:
    from game_logic import TavlaGame

from game_logic import TavlaGame, Player, GameState, Move


@dataclass
class Colors:
    """Oyun renkleri"""
    BACKGROUND = (222, 184, 135)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_BROWN = (101, 67, 33)
    LIGHT_BROWN = (160, 82, 45)
    BOARD_BORDER = (139, 69, 19)
    PLAYER1_COLOR = (240, 240, 240)
    PLAYER2_COLOR = (50, 50, 50)
    PUL_BORDER = (100, 100, 100)
    BUTTON_COLOR = (70, 130, 180)
    BUTTON_HOVER = (100, 149, 237)
    BUTTON_TEXT = (255, 255, 255)
    DICE_COLOR = (255, 255, 255)
    DICE_BORDER = (0, 0, 0)
    DICE_DOT = (0, 0, 0)
    SELECTED_COLOR = (255, 215, 0)
    VALID_MOVE_COLOR = (0, 255, 0)
    PANEL_COLOR = (139, 69, 19)
    PANEL_TEXT = (255, 255, 255)
    WIN_COLOR = (255, 0, 0)
    STATS_BG = (50, 50, 50, 180)
    STATS_TEXT = (255, 255, 255)


@dataclass
class Layout:
    """Düzen ayarları"""
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    BOARD_X = 50
    BOARD_Y = 80
    BOARD_WIDTH = 600
    BOARD_HEIGHT = 400
    TRIANGLE_WIDTH = 40
    TRIANGLE_HEIGHT = 150
    BAR_WIDTH = 40
    PUL_RADIUS = 15
    STATS_PANEL_WIDTH = 280
    STATS_PANEL_X = 720
    UI_PANEL_HEIGHT = 60


class BoardRenderer:
    """Tahta çizim sınıfı"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors, layout: Layout):
        self.screen = screen
        self.colors = colors
        self.layout = layout
        
        # Font'ları başlat
        pygame.font.init()
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 42)
        self.title_font = pygame.font.Font(None, 48)
    
    def get_triangle_position(self, point_index: int) -> Tuple[int, int, bool]:
        """Üçgen pozisyonunu hesapla"""
        if point_index <= 11:  # Alt sıra
            point_up = True
            y = self.layout.BOARD_Y + self.layout.BOARD_HEIGHT
            col = 11 - point_index
        else:  # Üst sıra
            point_up = False
            y = self.layout.BOARD_Y
            col = point_index - 12
        
        x = self.layout.BOARD_X + col * self.layout.TRIANGLE_WIDTH
        if col >= 6:
            x += self.layout.BAR_WIDTH
        
        return x, y, point_up
    
    def draw_triangle(self, x: int, y: int, width: int, height: int, 
                     color: Tuple[int, int, int], point_up: bool = True):
        """Üçgen çiz"""
        if point_up:
            points = [(x, y), (x + width, y), (x + width // 2, y - height)]
        else:
            points = [(x, y), (x + width, y), (x + width // 2, y + height)]
        
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, self.colors.BOARD_BORDER, points, 2)
    
    def draw_board_background(self):
        """Tahta arka planını çiz"""
        # Ana çerçeve
        pygame.draw.rect(self.screen, self.colors.BOARD_BORDER,
                        (self.layout.BOARD_X - 5, self.layout.BOARD_Y - 5,
                         self.layout.BOARD_WIDTH + 10, self.layout.BOARD_HEIGHT + 10),
                        0, 10)
        pygame.draw.rect(self.screen, self.colors.BACKGROUND,
                        (self.layout.BOARD_X, self.layout.BOARD_Y,
                         self.layout.BOARD_WIDTH, self.layout.BOARD_HEIGHT))
        
        # Üçgenleri çiz
        for i in range(24):
            color = self.colors.DARK_BROWN if (i // 2) % 2 == 0 else self.colors.LIGHT_BROWN
            x, y, point_up = self.get_triangle_position(i)
            self.draw_triangle(x, y, self.layout.TRIANGLE_WIDTH, 
                             self.layout.TRIANGLE_HEIGHT, color, point_up)
            
            # Hane numaraları
            number_text = self.small_font.render(str(i + 1), True, self.colors.WHITE)
            text_x = x + self.layout.TRIANGLE_WIDTH // 2 - number_text.get_width() // 2
            text_y = y - 20 if point_up else y + self.layout.TRIANGLE_HEIGHT + 5
            self.screen.blit(number_text, (text_x, text_y))
        
        # Bar alanı
        bar_x = self.layout.BOARD_X + 6 * self.layout.TRIANGLE_WIDTH
        pygame.draw.rect(self.screen, self.colors.BOARD_BORDER,
                        (bar_x, self.layout.BOARD_Y, self.layout.BAR_WIDTH, self.layout.BOARD_HEIGHT))
    
    def draw_piece(self, x: int, y: int, player: Player):
        """Pul çiz"""
        color = self.colors.PLAYER1_COLOR if player == Player.WHITE else self.colors.PLAYER2_COLOR
        pygame.draw.circle(self.screen, self.colors.PUL_BORDER, 
                          (int(x), int(y)), self.layout.PUL_RADIUS + 1)
        pygame.draw.circle(self.screen, color, (int(x), int(y)), self.layout.PUL_RADIUS)
    
    def draw_pieces(self, game: 'TavlaGame'):
        """Tüm pulları çiz"""
        # Normal hanelerdeki pullar
        for point_index in range(24):
            point = game.board.points[point_index]
            if point.is_empty():
                continue
            
            piece_count = point.count
            player = point.owner
            x, y, point_up = self.get_triangle_position(point_index)
            center_x = x + self.layout.TRIANGLE_WIDTH // 2
            
            # Maksimum 5 pul çiz
            for i in range(min(piece_count, 5)):
                offset = i * (self.layout.PUL_RADIUS * 1.6)
                piece_y = y - self.layout.PUL_RADIUS - offset if point_up else y + self.layout.PUL_RADIUS + offset
                self.draw_piece(center_x, piece_y, player)
            
            # 5'ten fazla pul varsa sayıyı yaz
            if piece_count > 5:
                text = self.small_font.render(str(piece_count), True, self.colors.WHITE)
                text_x = center_x - text.get_width() // 2
                text_y = y - 70 if point_up else y + self.layout.TRIANGLE_HEIGHT + 30
                self.screen.blit(text, (text_x, text_y))
        
        # Bar'daki pullar
        self.draw_bar_pieces(game)
    
    def draw_bar_pieces(self, game: TavlaGame):
        """Bar'daki pulları çiz"""
        bar_x = self.layout.BOARD_X + 6 * self.layout.TRIANGLE_WIDTH + self.layout.BAR_WIDTH // 2
        
        # Beyaz pullar (alt)
        white_count = game.board.get_bar_count(Player.WHITE)
        if white_count > 0:
            for i in range(min(white_count, 5)):
                piece_y = self.layout.BOARD_Y + self.layout.BOARD_HEIGHT - 30 - (i * self.layout.PUL_RADIUS * 2)
                self.draw_piece(bar_x, piece_y, Player.WHITE)
            if white_count > 5:
                text = self.small_font.render(str(white_count), True, self.colors.WHITE)
                self.screen.blit(text, (bar_x - 10, self.layout.BOARD_Y + self.layout.BOARD_HEIGHT - 120))
        
        # Siyah pullar (üst)
        black_count = game.board.get_bar_count(Player.BLACK)
        if black_count > 0:
            for i in range(min(black_count, 5)):
                piece_y = self.layout.BOARD_Y + 30 + (i * self.layout.PUL_RADIUS * 2)
                self.draw_piece(bar_x, piece_y, Player.BLACK)
            if black_count > 5:
                text = self.small_font.render(str(black_count), True, self.colors.WHITE)
                self.screen.blit(text, (bar_x - 10, self.layout.BOARD_Y + 120))
    
    def draw_bear_off_areas(self, game: TavlaGame):
        """Pul toplama alanlarını çiz"""
        area_rect = pygame.Rect(self.layout.BOARD_X + self.layout.BOARD_WIDTH + 10, 
                               self.layout.BOARD_Y, 60, self.layout.BOARD_HEIGHT)
        pygame.draw.rect(self.screen, self.colors.BOARD_BORDER, area_rect, 2)
        pygame.draw.line(self.screen, self.colors.BOARD_BORDER,
                        (area_rect.left, area_rect.centery), 
                        (area_rect.right, area_rect.centery), 2)
        
        # Siyah toplama (üst)
        black_count = game.board.get_home_count(Player.BLACK)
        if black_count > 0:
            text = self.big_font.render(str(black_count), True, self.colors.PLAYER2_COLOR)
            y_pos = area_rect.y + 50
            self.screen.blit(text, text.get_rect(center=(area_rect.centerx, y_pos)))
        
        # Beyaz toplama (alt)
        white_count = game.board.get_home_count(Player.WHITE)
        if white_count > 0:
            text = self.big_font.render(str(white_count), True, self.colors.PLAYER1_COLOR)
            y_pos = area_rect.y + area_rect.height - 50
            self.screen.blit(text, text.get_rect(center=(area_rect.centerx, y_pos)))
    
    def draw_highlights(self, selected_point: Optional[int], valid_moves: List['Move']):
        """Seçili hane ve geçerli hamleleri vurgula"""
        # Seçili hane
        if selected_point is not None:
            if selected_point == -2:  # Bar
                bar_x = self.layout.BOARD_X + 6 * self.layout.TRIANGLE_WIDTH
                bar_rect = pygame.Rect(bar_x, self.layout.BOARD_Y, 
                                     self.layout.BAR_WIDTH, self.layout.BOARD_HEIGHT)
                pygame.draw.rect(self.screen, self.colors.SELECTED_COLOR, bar_rect, 4)
            elif 0 <= selected_point <= 23:  # Normal hane
                x, y, point_up = self.get_triangle_position(selected_point)
                points = [(x, y), (x + self.layout.TRIANGLE_WIDTH, y),
                         (x + self.layout.TRIANGLE_WIDTH // 2, 
                          y - self.layout.TRIANGLE_HEIGHT if point_up else y + self.layout.TRIANGLE_HEIGHT)]
                pygame.draw.polygon(self.screen, self.colors.SELECTED_COLOR, points, 4)
        
        # Geçerli hamleler
        for move in valid_moves:
            if move.to_point == -1:  # Toplama alanı
                bear_off_rect = pygame.Rect(self.layout.BOARD_X + self.layout.BOARD_WIDTH + 10,
                                          self.layout.BOARD_Y, 60, self.layout.BOARD_HEIGHT)
                pygame.draw.rect(self.screen, self.colors.VALID_MOVE_COLOR, bear_off_rect, 3)
            elif 0 <= move.to_point <= 23:  # Normal hane
                x, y, point_up = self.get_triangle_position(move.to_point)
                points = [(x, y), (x + self.layout.TRIANGLE_WIDTH, y),
                         (x + self.layout.TRIANGLE_WIDTH // 2,
                          y - self.layout.TRIANGLE_HEIGHT if point_up else y + self.layout.TRIANGLE_HEIGHT)]
                pygame.draw.polygon(self.screen, self.colors.VALID_MOVE_COLOR, points, 3)


class DiceRenderer:
    """Zar çizim sınıfı"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors):
        self.screen = screen
        self.colors = colors
    
    def draw_single_die(self, x: int, y: int, value: int, size: int = 40):
        """Tek zar çiz"""
        pygame.draw.rect(self.screen, self.colors.DICE_COLOR, 
                        (x, y, size, size), border_radius=5)
        pygame.draw.rect(self.screen, self.colors.DICE_BORDER, 
                        (x, y, size, size), 2, border_radius=5)
        
        # Zar noktaları
        dots_positions = {
            1: [(0.5, 0.5)],
            2: [(0.25, 0.25), (0.75, 0.75)],
            3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
            4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
            5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
            6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)]
        }
        
        if value in dots_positions:
            for dx, dy in dots_positions[value]:
                pygame.draw.circle(self.screen, self.colors.DICE_DOT,
                                 (int(x + dx * size), int(y + dy * size)), 4)
    
    def draw_dice_area(self, dice_values: Tuple[int, int], dice_rect: pygame.Rect):
        """Zar alanını çiz"""
        if dice_values[0] > 0:
            self.draw_single_die(dice_rect.x, dice_rect.y + 10, dice_values[0])
            self.draw_single_die(dice_rect.x + 50, dice_rect.y + 10, dice_values[1])


class StatsRenderer:
    """İstatistik paneli çizim sınıfı"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors, layout: Layout):
        self.screen = screen
        self.colors = colors
        self.layout = layout
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 28)
    
    def draw_stats_panel(self, game: 'TavlaGame', ai_info: Dict = None):
        """İstatistik panelini çiz"""
        panel_rect = pygame.Rect(self.layout.STATS_PANEL_X, 10, 
                                self.layout.STATS_PANEL_WIDTH, 680)
        
        # Yarı saydam arka plan
        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        s.fill(self.colors.STATS_BG)
        self.screen.blit(s, panel_rect)
        
        # Panel çerçevesi
        pygame.draw.rect(self.screen, self.colors.PANEL_COLOR, panel_rect, 2, 5)
        
        y_offset = 20
        
        # Başlık
        title = self.title_font.render("OYUN BİLGİLERİ", True, self.colors.STATS_TEXT)
        self.screen.blit(title, (panel_rect.x + 10, y_offset))
        y_offset += 40
        
        # Mevcut oyuncu
        current_player = "BEYAZ (SEN)" if game.current_player == Player.WHITE else "SİYAH (AI)"
        player_text = self.font.render(f"Sıra: {current_player}", True, self.colors.STATS_TEXT)
        self.screen.blit(player_text, (panel_rect.x + 10, y_offset))
        y_offset += 30
        
        # Zar bilgileri
        if game.dice_values[0] > 0:
            dice_text = self.font.render(f"Zarlar: {game.dice_values[0]}-{game.dice_values[1]}", 
                                       True, self.colors.STATS_TEXT)
            self.screen.blit(dice_text, (panel_rect.x + 10, y_offset))
            y_offset += 25
            
            if game.moves_left:
                moves_text = self.small_font.render(f"Kalan: {game.moves_left}", 
                                                  True, self.colors.STATS_TEXT)
                self.screen.blit(moves_text, (panel_rect.x + 10, y_offset))
            y_offset += 35
        
        # Oyun durumu
        y_offset = self._draw_game_status(game, panel_rect.x + 10, y_offset)
        
        # Pul sayıları
        y_offset = self._draw_piece_counts(game, panel_rect.x + 10, y_offset)
        
        # AI bilgileri
        if ai_info:
            y_offset = self._draw_ai_info(ai_info, panel_rect.x + 10, y_offset)
        
        # Genel istatistikler
        self._draw_general_stats(game.stats, panel_rect.x + 10, y_offset)
    
    def _draw_game_status(self, game: TavlaGame, x: int, y: int) -> int:
        """Oyun durumu bilgilerini çiz"""
        status_title = self.font.render("DURUM:", True, self.colors.STATS_TEXT)
        self.screen.blit(status_title, (x, y))
        y += 25
        
        if game.game_state == GameState.WAITING_DICE:
            status = "Zar bekleniyor"
        elif game.game_state == GameState.SELECTING_PIECE:
            status = "Pul seçimi"
        elif game.game_state == GameState.SELECTING_TARGET:
            status = "Hedef seçimi"
        elif game.game_state == GameState.GAME_OVER:
            winner = "BEYAZ KAZANDI!" if game.winner == Player.WHITE else "SİYAH KAZANDI!"
            status = winner
        else:
            status = "Bilinmiyor"
        
        status_text = self.small_font.render(status, True, self.colors.STATS_TEXT)
        self.screen.blit(status_text, (x, y))
        return y + 35
    
    def _draw_piece_counts(self, game: TavlaGame, x: int, y: int) -> int:
        """Pul sayılarını çiz"""
        counts_title = self.font.render("PUL SAYILARI:", True, self.colors.STATS_TEXT)
        self.screen.blit(counts_title, (x, y))
        y += 25
        
        # Beyaz pullar
        white_home = game.board.get_home_count(Player.WHITE)
        white_bar = game.board.get_bar_count(Player.WHITE)
        white_board = 15 - white_home - white_bar
        
        white_text = self.small_font.render(f"Beyaz: Tahtada {white_board}, Evde {white_home}, Bar {white_bar}", 
                                          True, self.colors.STATS_TEXT)
        self.screen.blit(white_text, (x, y))
        y += 20
        
        # Siyah pullar
        black_home = game.board.get_home_count(Player.BLACK)
        black_bar = game.board.get_bar_count(Player.BLACK)
        black_board = 15 - black_home - black_bar
        
        black_text = self.small_font.render(f"Siyah: Tahtada {black_board}, Evde {black_home}, Bar {black_bar}", 
                                          True, self.colors.STATS_TEXT)
        self.screen.blit(black_text, (x, y))
        return y + 35
    
    def _draw_ai_info(self, ai_info: Dict, x: int, y: int) -> int:
        """AI bilgilerini çiz"""
        ai_title = self.font.render("AI BİLGİLERİ:", True, self.colors.STATS_TEXT)
        self.screen.blit(ai_title, (x, y))
        y += 25
        
        strategy_text = self.small_font.render(f"Strateji: {ai_info.get('strategy', 'Bilinmiyor')}", 
                                             True, self.colors.STATS_TEXT)
        self.screen.blit(strategy_text, (x, y))
        y += 20
        
        if ai_info.get('games_played', 0) > 0:
            win_rate_text = self.small_font.render(f"Kazanma Oranı: %{ai_info.get('win_rate', 0):.1f}", 
                                                 True, self.colors.STATS_TEXT)
            self.screen.blit(win_rate_text, (x, y))
            y += 20
            
            avg_time_text = self.small_font.render(f"Ort. Düşünme: {ai_info.get('avg_thinking_time', 0):.2f}s", 
                                                 True, self.colors.STATS_TEXT)
            self.screen.blit(avg_time_text, (x, y))
            y += 20
        
        return y + 15
    
    def _draw_general_stats(self, stats, x: int, y: int):
        """Genel istatistikleri çiz"""
        stats_title = self.font.render("GENEL İSTATİSTİKLER:", True, self.colors.STATS_TEXT)
        self.screen.blit(stats_title, (x, y))
        y += 25
        
        games_text = self.small_font.render(f"Toplam Oyun: {stats.games_played}", 
                                          True, self.colors.STATS_TEXT)
        self.screen.blit(games_text, (x, y))
        y += 20
        
        if stats.games_played > 0:
            white_rate_text = self.small_font.render(f"Beyaz Kazanma: %{stats.win_rate_white:.1f}", 
                                                   True, self.colors.STATS_TEXT)
            self.screen.blit(white_rate_text, (x, y))
            y += 20
            
            black_rate_text = self.small_font.render(f"Siyah Kazanma: %{stats.win_rate_black:.1f}", 
                                                   True, self.colors.STATS_TEXT)
            self.screen.blit(black_rate_text, (x, y))
            y += 20
            
            avg_length_text = self.small_font.render(f"Ort. Oyun Uzunluğu: {stats.average_game_length:.1f}", 
                                                   True, self.colors.STATS_TEXT)
            self.screen.blit(avg_length_text, (x, y))


class GameRenderer:
    """Ana oyun görüntüleme sınıfı"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.colors = Colors()
        self.layout = Layout()
        
        self.board_renderer = BoardRenderer(screen, self.colors, self.layout)
        self.dice_renderer = DiceRenderer(screen, self.colors)
        self.stats_renderer = StatsRenderer(screen, self.colors, self.layout)
        
        # Font'lar
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 48)
    
    def render_game(self, game: 'TavlaGame', selected_point: Optional[int] = None, 
                   valid_moves: List['Move'] = None, ai_info: Dict = None):
        """Oyunu çiz"""
        # Arka plan
        self.screen.fill(self.colors.BACKGROUND)
        
        # Tahta
        self.board_renderer.draw_board_background()
        self.board_renderer.draw_pieces(game)
        self.board_renderer.draw_bear_off_areas(game)
        
        # Vurgulamalar
        if valid_moves is None:
            valid_moves = []
        self.board_renderer.draw_highlights(selected_point, valid_moves)
        
        # İstatistik paneli
        self.stats_renderer.draw_stats_panel(game, ai_info)
        
        # Oyun bitti ekranı
        if game.game_state.value == 'game_over':  # Enum value kullan
            self._draw_game_over_overlay(game)
    
    def _draw_game_over_overlay(self, game: 'TavlaGame'):
        """Oyun bitti ekranını çiz"""
        winner_name = "BEYAZ (SEN)" if game.winner == Player.WHITE else "SİYAH (AI)"
        win_text = f"{winner_name} KAZANDI!"
        
        # Yarı saydam arka plan
        s = pygame.Surface((self.layout.WINDOW_WIDTH, self.layout.WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        self.screen.blit(s, (0, 0))
        
        # Kazanma metni
        win_surface = self.big_font.render(win_text, True, self.colors.WIN_COLOR)
        win_rect = win_surface.get_rect(center=(self.layout.WINDOW_WIDTH // 2, 
                                               self.layout.WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(win_surface, win_rect)
        
        # Yeniden başlatma metni
        restart_text = self.font.render("Yeniden başlatmak için 'R' tuşuna basın", 
                                       True, self.colors.WHITE)
        restart_rect = restart_text.get_rect(center=(self.layout.WINDOW_WIDTH // 2,
                                                    self.layout.WINDOW_HEIGHT // 2 + 30))
        self.screen.blit(restart_text, restart_rect)
