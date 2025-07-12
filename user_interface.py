"""
Tavla oyununun kullanıcı arayüzü ve input yönetimi
"""
import pygame
from typing import Optional, Tuple, List, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

from game_logic import TavlaGame, Player, GameState, Move
from renderer import Layout, Colors


class ButtonState(Enum):
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"


@dataclass
class Button:
    """Buton sınıfı"""
    rect: pygame.Rect
    text: str
    callback: Callable
    enabled: bool = True
    state: ButtonState = ButtonState.NORMAL
    
    def is_clicked(self, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> bool:
        """Butona tıklandı mı?"""
        if not self.enabled:
            return False
        
        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed:
                self.state = ButtonState.PRESSED
                return True
            else:
                self.state = ButtonState.HOVER
        else:
            self.state = ButtonState.NORMAL
        
        return False


class UIManager:
    """Kullanıcı arayüzü yöneticisi"""
    
    def __init__(self, screen: pygame.Surface, layout: Layout, colors: Colors):
        self.screen = screen
        self.layout = layout
        self.colors = colors
        
        # Font'lar
        self.font = pygame.font.Font(None, 24)
        self.button_font = pygame.font.Font(None, 20)
        
        # UI elementleri
        self.buttons: Dict[str, Button] = {}
        self.mouse_pos = (0, 0)
        self.mouse_pressed = False
        
        # Butonları oluştur
        self._create_buttons()
    
    def _create_buttons(self):
        """UI butonlarını oluştur"""
        button_y = self.layout.WINDOW_HEIGHT - 50
        
        # Zar at butonu
        dice_rect = pygame.Rect(50, button_y, 100, 35)
        self.buttons['roll_dice'] = Button(dice_rect, "Zar At", None)
        
        # Yeni oyun butonu
        new_game_rect = pygame.Rect(160, button_y, 100, 35)
        self.buttons['new_game'] = Button(new_game_rect, "Yeni Oyun", None)
        
        # AI zorluk butonları
        ai_x = 270
        for i, difficulty in enumerate(['Kolay', 'Orta', 'Zor', 'Uzman']):
            ai_rect = pygame.Rect(ai_x + i * 80, button_y, 75, 35)
            self.buttons[f'ai_{difficulty.lower()}'] = Button(ai_rect, difficulty, None)
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool):
        """UI durumunu güncelle"""
        self.mouse_pos = mouse_pos
        self.mouse_pressed = mouse_pressed
    
    def handle_button_click(self, button_name: str) -> bool:
        """Buton tıklamasını işle"""
        if button_name in self.buttons:
            button = self.buttons[button_name]
            return button.is_clicked(self.mouse_pos, self.mouse_pressed)
        return False
    
    def set_button_enabled(self, button_name: str, enabled: bool):
        """Buton durumunu ayarla"""
        if button_name in self.buttons:
            self.buttons[button_name].enabled = enabled
    
    def draw_button(self, button: Button):
        """Buton çiz"""
        # Buton rengi
        if not button.enabled:
            color = (100, 100, 100)
            text_color = (150, 150, 150)
        elif button.state == ButtonState.PRESSED:
            color = (50, 100, 150)
            text_color = self.colors.BUTTON_TEXT
        elif button.state == ButtonState.HOVER:
            color = self.colors.BUTTON_HOVER
            text_color = self.colors.BUTTON_TEXT
        else:
            color = self.colors.BUTTON_COLOR
            text_color = self.colors.BUTTON_TEXT
        
        # Buton çiz
        pygame.draw.rect(self.screen, color, button.rect, border_radius=5)
        pygame.draw.rect(self.screen, self.colors.BLACK, button.rect, 2, border_radius=5)
        
        # Metin çiz
        text_surface = self.button_font.render(button.text, True, text_color)
        text_rect = text_surface.get_rect(center=button.rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_ui_panel(self, game: TavlaGame, current_ai_difficulty: str = "Orta"):
        """UI panelini çiz"""
        # Panel arka planı
        panel_rect = pygame.Rect(0, self.layout.WINDOW_HEIGHT - 60, 
                                self.layout.WINDOW_WIDTH, 60)
        pygame.draw.rect(self.screen, self.colors.PANEL_COLOR, panel_rect)
        pygame.draw.line(self.screen, self.colors.BLACK, 
                        (0, self.layout.WINDOW_HEIGHT - 60), 
                        (self.layout.WINDOW_WIDTH, self.layout.WINDOW_HEIGHT - 60), 2)
        
        # Zar at butonunu güncelle
        can_roll = (game.game_state == GameState.WAITING_DICE and 
                   game.current_player == Player.WHITE)
        self.set_button_enabled('roll_dice', can_roll)
        
        # AI zorluk butonlarını güncelle
        for difficulty in ['kolay', 'orta', 'zor', 'uzman']:
            button = self.buttons[f'ai_{difficulty}']
            if difficulty == current_ai_difficulty.lower():
                button.state = ButtonState.PRESSED
            else:
                button.state = ButtonState.NORMAL
        
        # Butonları çiz
        for button in self.buttons.values():
            self.draw_button(button)
        
        # Zar alanı
        if game.dice_values[0] > 0:
            dice_area = pygame.Rect(self.layout.WINDOW_WIDTH - 150, 
                                   self.layout.WINDOW_HEIGHT - 55, 120, 50)
            from renderer import DiceRenderer
            dice_renderer = DiceRenderer(self.screen, self.colors)
            dice_renderer.draw_dice_area(game.dice_values, dice_area)


class InputHandler:
    """Input işleme sınıfı"""
    
    def __init__(self, layout: Layout):
        self.layout = layout
        self.selected_point = None
        self.valid_moves = []
    
    def get_clicked_point(self, mouse_pos: Tuple[int, int]) -> Optional[int]:
        """Tıklanan haneyi bul"""
        mx, my = mouse_pos
        
        # Toplama alanı kontrolü
        bear_off_rect = pygame.Rect(self.layout.BOARD_X + self.layout.BOARD_WIDTH + 10,
                                   self.layout.BOARD_Y, 60, self.layout.BOARD_HEIGHT)
        if bear_off_rect.collidepoint(mouse_pos):
            return -1  # Toplama alanı
        
        # Bar alanı kontrolü
        bar_rect = pygame.Rect(self.layout.BOARD_X + 6 * self.layout.TRIANGLE_WIDTH,
                              self.layout.BOARD_Y, self.layout.BAR_WIDTH, 
                              self.layout.BOARD_HEIGHT)
        if bar_rect.collidepoint(mouse_pos):
            return -2  # Bar alanı
        
        # Normal haneler
        for point in range(24):
            tri_x, tri_y, point_up = self._get_triangle_position(point)
            triangle_rect = pygame.Rect(tri_x, 
                                       tri_y - self.layout.TRIANGLE_HEIGHT if point_up else tri_y,
                                       self.layout.TRIANGLE_WIDTH, self.layout.TRIANGLE_HEIGHT)
            if triangle_rect.collidepoint(mouse_pos):
                return point
        
        return None
    
    def _get_triangle_position(self, point_index: int) -> Tuple[int, int, bool]:
        """Üçgen pozisyonunu hesapla (BoardRenderer'dan kopyalandı)"""
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
    
    def handle_board_click(self, game: TavlaGame, mouse_pos: Tuple[int, int]) -> Optional[Move]:
        """Tahta tıklamasını işle - GAME STATE DEĞİŞTİRMEZ"""
        print(f"Tahta tıklaması: {mouse_pos}")
        print(f"Oyun durumu: {game.game_state}")
        print(f"Sıra: {game.current_player}")
        
        if game.current_player != Player.WHITE or game.game_state == GameState.WAITING_DICE:
            print("Oyuncu sırası değil veya zar bekleniyor")
            return None
        
        clicked_point = self.get_clicked_point(mouse_pos)
        print(f"Tıklanan nokta: {clicked_point}")
        
        if clicked_point is None:
            # Tahta dışına tıklandı, seçimi sıfırla
            print("Tahta dışına tıklandı, seçim sıfırlanıyor")
            self.selected_point = None
            self.valid_moves = []
            # GAME STATE DEĞİŞTİRİLMEDİ - main.py'da yapılacak
            return None
        
        if game.game_state == GameState.SELECTING_PIECE:
            print("Pul seçim modunda")
            return self._handle_piece_selection(game, clicked_point)
        elif game.game_state == GameState.SELECTING_TARGET:
            print("Hedef seçim modunda")
            return self._handle_target_selection(game, clicked_point)
        
        return None
    
    def _handle_piece_selection(self, game: TavlaGame, clicked_point: int) -> Optional[Move]:
        """Pul seçimi işlemi - GAME STATE DEĞİŞTİRMEZ"""
        print(f"Pul seçimi: Tıklanan nokta {clicked_point}")
        
        # Bar'da pul varsa sadece bar seçilebilir
        if game.board.has_pieces_in_bar(Player.WHITE):
            if clicked_point == -2:  # Bar seçildi
                print("Bar seçildi")
                self.selected_point = -2
                self.valid_moves = game.get_valid_moves()
                # GAME STATE DEĞİŞTİRİLMEDİ - main.py'da yapılacak
                print(f"Geçerli hamleler: {[str(m) for m in self.valid_moves]}")
                return None
            else:
                # Bar'da pul varken başka yer seçilemez
                print("Bar'da pul var, önce bar'dan çıkmalısınız!")
                return None
        
        # Normal hane seçimi
        if clicked_point >= 0 and clicked_point <= 23:
            if game.board.has_pieces_on_point(clicked_point, Player.WHITE):
                print(f"Hane {clicked_point+1} seçildi")
                self.selected_point = clicked_point
                self.valid_moves = game.get_valid_moves(clicked_point)
                # GAME STATE DEĞİŞTİRİLMEDİ - main.py'da yapılacak
                print(f"Geçerli hamleler: {[str(m) for m in self.valid_moves]}")
                return None
            else:
                print(f"Hane {clicked_point+1}'de beyaz pul yok")
        elif clicked_point == -2:  # Bar
            if game.board.has_pieces_in_bar(Player.WHITE):
                print("Bar seçildi")
                self.selected_point = -2
                self.valid_moves = game.get_valid_moves()
                # GAME STATE DEĞİŞTİRİLMEDİ - main.py'da yapılacak
                return None
            else:
                print("Bar'da pul yok")
        
        # Geçersiz seçim
        print("Geçersiz seçim")
        self.selected_point = None
        self.valid_moves = []
        return None
    
    def _handle_target_selection(self, game: TavlaGame, clicked_point: int) -> Optional[Move]:
        """Hedef seçimi işlemi - GAME STATE DEĞİŞTİRMEZ"""
        print(f"Hedef seçimi: Tıklanan nokta {clicked_point}")
        print(f"Seçili pul: {self.selected_point}")
        print(f"Geçerli hamleler: {[f'{m.from_point}->{m.to_point}({m.dice_value})' for m in self.valid_moves]}")
        
        # Geçerli hamle mi kontrol et
        for move in self.valid_moves:
            if move.to_point == clicked_point:
                # Geçerli hamle bulundu
                print(f"Geçerli hamle bulundu: {self.selected_point} -> {clicked_point} (zar: {move.dice_value})")
                selected_move = Move(self.selected_point, clicked_point, move.dice_value)
                self.selected_point = None
                self.valid_moves = []
                # GAME STATE DEĞİŞTİRİLMEDİ - main.py'da yapılacak
                return selected_move
        
        print(f"Geçersiz hedef: {clicked_point}")
        
        # Geçersiz hedef, yeni pul seçimine geç
        if clicked_point >= 0 and clicked_point <= 23:
            if game.board.has_pieces_on_point(clicked_point, Player.WHITE):
                print(f"Yeni pul seçildi: {clicked_point}")
                self.selected_point = clicked_point
                self.valid_moves = game.get_valid_moves(clicked_point)
                return None
        elif clicked_point == -2 and game.board.has_pieces_in_bar(Player.WHITE):
            print("Bar seçildi")
            self.selected_point = -2
            self.valid_moves = game.get_valid_moves()
            return None
        
        # Tamamen geçersiz, seçimi sıfırla
        print("Seçim sıfırlandı")
        self.selected_point = None
        self.valid_moves = []
        # GAME STATE DEĞİŞTİRİLMEDİ - main.py'da yapılacak
        return None
    
    def reset_selection(self):
        """Seçimi sıfırla"""
        self.selected_point = None
        self.valid_moves = []


class MenuManager:
    """Menü yönetimi"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors):
        self.screen = screen
        self.colors = colors
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 28)
        
        self.menu_buttons: Dict[str, Button] = {}
        self._create_menu_buttons()
    
    def _create_menu_buttons(self):
        """Menü butonlarını oluştur"""
        center_x = 500
        start_y = 300
        button_height = 50
        button_width = 200
        spacing = 70
        
        # Oyuna başla
        start_rect = pygame.Rect(center_x - button_width//2, start_y, 
                                button_width, button_height)
        self.menu_buttons['start_game'] = Button(start_rect, "Oyuna Başla", None)
        
        # AI zorluk seçimi
        difficulty_y = start_y + spacing
        difficulties = [('Kolay', 'easy'), ('Orta', 'medium'), ('Zor', 'hard'), ('Uzman', 'expert')]
        
        for i, (text, key) in enumerate(difficulties):
            diff_rect = pygame.Rect(center_x - 400 + i * 200, difficulty_y, 
                                   180, button_height)
            self.menu_buttons[f'difficulty_{key}'] = Button(diff_rect, text, None)
        
        # İstatistikleri sıfırla
        reset_rect = pygame.Rect(center_x - button_width//2, difficulty_y + spacing,
                                button_width, button_height)
        self.menu_buttons['reset_stats'] = Button(reset_rect, "İstatistikleri Sıfırla", None)
        
        # Çıkış
        exit_rect = pygame.Rect(center_x - button_width//2, difficulty_y + spacing * 2,
                               button_width, button_height)
        self.menu_buttons['exit'] = Button(exit_rect, "Çıkış", None)
    
    def draw_main_menu(self, selected_difficulty: str = "medium"):
        """Ana menüyü çiz"""
        self.screen.fill(self.colors.BACKGROUND)
        
        # Başlık
        title = self.title_font.render("TAVLA", True, self.colors.BLACK)
        title_rect = title.get_rect(center=(500, 150))
        self.screen.blit(title, title_rect)
        
        # Alt başlık
        subtitle = self.font.render("Klasik Türk Tavlası", True, self.colors.DARK_BROWN)
        subtitle_rect = subtitle.get_rect(center=(500, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Zorluk seviyesi etiketi
        difficulty_label = self.font.render("AI Zorluk Seviyesi:", True, self.colors.BLACK)
        label_rect = difficulty_label.get_rect(center=(500, 340))
        self.screen.blit(difficulty_label, label_rect)
        
        # Butonları çiz
        for button_name, button in self.menu_buttons.items():
            # Seçili zorluk seviyesini vurgula
            if button_name.startswith('difficulty_'):
                difficulty_key = button_name.split('_')[1]
                if difficulty_key == selected_difficulty:
                    button.state = ButtonState.PRESSED
                else:
                    button.state = ButtonState.NORMAL
            
            self._draw_menu_button(button)
    
    def _draw_menu_button(self, button: Button):
        """Menü butonunu çiz"""
        # Buton rengi
        if button.state == ButtonState.PRESSED:
            color = (50, 100, 150)
        elif button.state == ButtonState.HOVER:
            color = self.colors.BUTTON_HOVER
        else:
            color = self.colors.BUTTON_COLOR
        
        # Buton çiz
        pygame.draw.rect(self.screen, color, button.rect, border_radius=8)
        pygame.draw.rect(self.screen, self.colors.BLACK, button.rect, 3, border_radius=8)
        
        # Gölge efekti
        shadow_rect = button.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, (100, 100, 100), shadow_rect, border_radius=8)
        pygame.draw.rect(self.screen, color, button.rect, border_radius=8)
        pygame.draw.rect(self.screen, self.colors.BLACK, button.rect, 3, border_radius=8)
        
        # Metin çiz
        text_surface = self.button_font.render(button.text, True, self.colors.BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=button.rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def handle_menu_click(self, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> Optional[str]:
        """Menü tıklamasını işle"""
        for button_name, button in self.menu_buttons.items():
            if button.is_clicked(mouse_pos, mouse_pressed):
                return button_name
        return None
    
    def update_menu_hover(self, mouse_pos: Tuple[int, int]):
        """Menü hover durumunu güncelle"""
        for button in self.menu_buttons.values():
            if button.rect.collidepoint(mouse_pos) and button.state != ButtonState.PRESSED:
                button.state = ButtonState.HOVER
            elif button.state == ButtonState.HOVER:
                button.state = ButtonState.NORMAL


class NotificationManager:
    """Geliştirilmiş bildirim yöneticisi"""
    
    def __init__(self, screen: pygame.Surface, colors: Colors):
        self.screen = screen
        self.colors = colors
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        self.notifications = []
        self.max_notifications = 8  # Maksimum aynı anda gösterilecek bildirim sayısı
    
    def add_notification(self, message: str, duration: float = 3.0, 
                        color: Tuple[int, int, int] = None, important: bool = False):
        """Bildirim ekle"""
        if color is None:
            color = self.colors.WHITE
        
        import time
        notification = {
            'message': message,
            'start_time': time.time(),
            'duration': duration,
            'color': color,
            'important': important  # Önemli bildirimler daha uzun süre kalır
        }
        
        # Maksimum bildirim sayısını aş, eski olanları sil
        if len(self.notifications) >= self.max_notifications:
            # Önemli olmayanları önce sil
            non_important = [n for n in self.notifications if not n.get('important', False)]
            if non_important:
                self.notifications.remove(non_important[0])
            else:
                self.notifications.pop(0)  # En eskiyi sil
        
        self.notifications.append(notification)
    
    def add_game_log(self, message: str, log_type: str = "info"):
        """Oyun log'u ekle - önceden tanımlanmış renklerle"""
        colors_by_type = {
            "player_move": (100, 255, 100),      # Açık yeşil - oyuncu hamlesi
            "ai_move": (150, 150, 255),          # Açık mavi - AI hamlesi  
            "dice": (255, 255, 100),             # Sarı - zar
            "turn": (255, 200, 100),             # Turuncu - tur değişimi
            "error": (255, 100, 100),            # Kırmızı - hata
            "info": (200, 200, 200),             # Gri - bilgi
            "success": (100, 255, 150),          # Yeşil - başarı
            "warning": (255, 200, 0)             # Turuncu - uyarı
        }
        
        duration_by_type = {
            "player_move": 2.5,
            "ai_move": 2.0,
            "dice": 3.0,
            "turn": 2.5,
            "error": 3.5,
            "info": 2.0,
            "success": 2.0,
            "warning": 3.0
        }
        
        color = colors_by_type.get(log_type, (255, 255, 255))
        duration = duration_by_type.get(log_type, 2.5)
        important = log_type in ["error", "warning", "turn"]
        
        self.add_notification(message, duration, color, important)
    
    def update_notifications(self):
        """Bildirimleri güncelle"""
        import time
        current_time = time.time()
        self.notifications = [n for n in self.notifications 
                             if current_time - n['start_time'] < n['duration']]
    
    def draw_notifications(self):
        """Bildirimleri çiz - Sağ üst köşede dikey liste"""
        import time
        current_time = time.time()
        
        # Sağ üst köşeden başla
        start_x = 520  # Stats panelinin solunda
        start_y = 10
        notification_height = 25
        
        for i, notification in enumerate(self.notifications):
            # Fade out efekti
            elapsed = current_time - notification['start_time']
            progress = elapsed / notification['duration']
            
            # Alpha hesaplama - son %20'de fade out
            if progress > 0.8:
                fade_progress = (progress - 0.8) / 0.2  # 0.8-1.0 arası 0-1'e map et
                alpha = int(255 * (1 - fade_progress))
            else:
                alpha = 255
            
            if alpha > 0:
                y_pos = start_y + (i * notification_height)
                
                # Önemli bildirimlerde arka plan vurgula
                if notification.get('important', False):
                    bg_color = (50, 50, 50, min(200, alpha))
                else:
                    bg_color = (30, 30, 30, min(150, alpha))
                
                # Metin render et
                font = self.font if not notification.get('important', False) else self.font
                text_surface = font.render(notification['message'], True, notification['color'])
                
                # Arka plan kutucuğu
                text_rect = text_surface.get_rect()
                bg_rect = pygame.Rect(start_x - 10, y_pos, min(text_rect.width + 20, 200), notification_height)
                
                # Yarı saydam arka plan
                s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                s.fill(bg_color)
                self.screen.blit(s, bg_rect)
                
                # Kenarlık (önemli bildirimlerde)
                if notification.get('important', False):
                    pygame.draw.rect(self.screen, notification['color'], bg_rect, 2)
                
                # Metin - uzun metinleri kes
                if text_rect.width > 180:
                    truncated_text = notification['message'][:25] + "..."
                    text_surface = font.render(truncated_text, True, notification['color'])
                
                text_with_alpha = text_surface.copy()
                text_with_alpha.set_alpha(alpha)
                text_pos = (start_x, y_pos + (notification_height - text_rect.height) // 2)
                self.screen.blit(text_with_alpha, text_pos)
    
    def clear_all(self):
        """Tüm bildirimleri temizle"""
        self.notifications = []
    
    def add_debug_info(self, game_state: str, current_player: str, moves_left: List):
        """Debug bilgisi ekle"""
        debug_msg = f"Durum: {game_state} | {current_player} | Kalan: {len(moves_left) if moves_left else 0}"
        self.add_notification(debug_msg, 1.5, (150, 150, 150))
