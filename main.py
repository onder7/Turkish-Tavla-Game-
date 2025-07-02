import pygame
import sys
import random
import time

# Pygame'i başlat
pygame.init()

# Font'u başlat
pygame.font.init()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 48)

# Pencere boyutları
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Renkler
BACKGROUND_COLOR = (222, 184, 135)
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


class TavlaOyunu:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tavla")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.board_x, self.board_y = 50, 50
        self.board_width, self.board_height = 600, 400
        self.triangle_width, self.triangle_height = 40, 150
        self.bar_width = 40
        self.pul_radius = 15
        
        self.board = self.initialize_board()
        self.dice_values = [0, 0]
        self.moves_left = []
        self.current_player = 'beyaz'
        self.ai_enabled = True
        self.selected_hane = None
        self.valid_moves = []
        self.game_state = 'waiting_dice'
        self.winner = None
        
        self.dice_button = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 200, 120, 40)
        self.dice_area = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 150, 120, 80)
        self.mouse_pos = (0, 0)
        self.button_hover = False

    def initialize_board(self):
        """Standart tavla başlangıç pozisyonu"""
        # 28 elemanlı liste (24 hane + beyaz bar[24], siyah bar[25] + beyaz toplama[26], siyah toplama[27])
        board = [[] for _ in range(28)]
        
        # Beyaz pullar (saat yönünde hareket eder: 0->23)
        board[0] = [2, 'beyaz']   # 2 beyaz pul
        board[11] = [5, 'beyaz']  # 5 beyaz pul
        board[16] = [3, 'beyaz']  # 3 beyaz pul
        board[18] = [5, 'beyaz']  # 5 beyaz pul
        
        # Siyah pullar (saat yönünün tersine hareket eder: 23->0)
        board[23] = [2, 'siyah']  # 2 siyah pul
        board[12] = [5, 'siyah']  # 5 siyah pul
        board[7] = [3, 'siyah']   # 3 siyah pul
        board[5] = [5, 'siyah']   # 5 siyah pul
        
        return board

    def count_pieces_in_home(self, player):
        home_index = 26 if player == 'beyaz' else 27
        return self.board[home_index][0] if self.board[home_index] else 0

    def can_bear_off(self, player):
        if self.has_pieces_in_bar(player):
            return False
        total_pieces = 0
        home_range = range(18, 24) if player == 'beyaz' else range(0, 6)
        for i in range(24):
            if self.board[i] and self.board[i][1] == player:
                if i not in home_range:
                    return False
                total_pieces += self.board[i][0]
        
        total_pieces += self.count_pieces_in_home(player)
        return total_pieces == 15

    def check_winner(self):
        if self.count_pieces_in_home('beyaz') >= 15:
            self.winner = 'beyaz'
            self.game_state = 'game_over'
        elif self.count_pieces_in_home('siyah') >= 15:
            self.winner = 'siyah'
            self.game_state = 'game_over'

    def handle_events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.button_hover = self.dice_button.collidepoint(self.mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_state == 'game_over':
                    self.restart_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                is_player_turn = not self.ai_enabled or self.current_player == 'beyaz'
                if self.dice_button.collidepoint(event.pos) and is_player_turn:
                    self.roll_dice()
                elif is_player_turn:
                    self.handle_board_click(event.pos)

    def update(self):
        is_ai_turn = self.ai_enabled and self.current_player == 'siyah' and self.game_state != 'game_over'
        if is_ai_turn and self.game_state == 'waiting_dice':
            print("AI zar atmak için bekliyor...")
            self.draw()  # Ekranda bekleme yazısını göstermek için
            time.sleep(1.0)
            self.roll_dice()
            if self.moves_left and not self.get_all_possible_moves():
                print("AI'nın oynayacak hamlesi yok. Turu bitiriyor.")
                self.draw()
                time.sleep(1.5)
                self.end_turn()
            elif self.moves_left:
                self.ai_play_turn()
        
        if self.game_state != 'game_over':
            self.check_winner()

    def restart_game(self):
        self.__init__()
        print("Oyun yeniden başlatıldı!")

    def roll_dice(self):
        if self.game_state != 'waiting_dice':
            return
        self.dice_values = [random.randint(1, 6), random.randint(1, 6)]
        if self.dice_values[0] == self.dice_values[1]:
            self.moves_left = [self.dice_values[0]] * 4
        else:
            self.moves_left = self.dice_values[:]
        
        self.game_state = 'selecting_piece'
        print(f"Zarlar: {self.dice_values[0]}-{self.dice_values[1]}, Hamleler: {self.moves_left}")
        
        if self.current_player == 'beyaz' and not self.get_all_possible_moves():
            print("Oynayacak geçerli hamleniz yok. Tur atlanıyor.")
            self.draw()
            time.sleep(1.5)
            self.end_turn()

    def handle_board_click(self, mouse_pos):
        clicked_hane = self.get_clicked_hane(mouse_pos)
        
        # Tahta dışına veya geçersiz bir alana tıklanırsa seçimi sıfırla
        if clicked_hane is None:
            self.selected_hane = None
            self.valid_moves = []
            self.game_state = 'selecting_piece'
            return

        if self.game_state == 'selecting_piece':
            self.select_piece(clicked_hane)
        elif self.game_state == 'selecting_target':
            move_to_execute = None
            for target, move_val in self.valid_moves:
                if target == clicked_hane:
                    move_to_execute = (target, move_val)
                    break
            
            if move_to_execute:
                self.move_piece(move_to_execute[0], move_to_execute[1])
            else:  # Geçersiz bir hedefe tıklandı
                print("Geçersiz hedef. Tekrar pul seçin.")
                self.selected_hane = None
                self.valid_moves = []
                self.game_state = 'selecting_piece'

    def get_clicked_hane(self, mouse_pos):
        mx, my = mouse_pos
        
        # Sağdaki toplama alanı için tıklama kontrolü
        bear_off_rect = pygame.Rect(self.board_x + self.board_width + 10, self.board_y, 60, self.board_height)
        if bear_off_rect.collidepoint(mouse_pos):
            return -1  # -1, toplama alanı anlamına gelsin
        
        # Bar alanı kontrolü
        bar_rect = pygame.Rect(self.board_x + 6 * self.triangle_width, self.board_y, self.bar_width, self.board_height)
        if bar_rect.collidepoint(mouse_pos):
            return -2  # -2, bar anlamına gelsin
            
        for hane_index in range(24):
            tri_x, tri_y, point_up = self.get_triangle_position(hane_index)
            # Basit bir dikdörtgen çarpışma tespiti
            triangle_rect = pygame.Rect(tri_x, tri_y - self.triangle_height if point_up else tri_y, 
                                      self.triangle_width, self.triangle_height)
            if triangle_rect.collidepoint(mouse_pos):
                return hane_index
        return None

    def select_piece(self, hane_index):
        if self.has_pieces_in_bar(self.current_player):
            print("Bar'da pulunuz var! Önce oyuna girin.")
            self.selected_hane = -2  # -2, bar anlamına gelsin
            self.valid_moves = self.get_bar_entry_moves()
            self.game_state = 'selecting_target'
            return

        if hane_index == -2:  # Bar'a tıklandı
            if self.has_pieces_in_bar(self.current_player):
                self.selected_hane = -2
                self.valid_moves = self.get_bar_entry_moves()
                self.game_state = 'selecting_target'
            return

        hane = self.board[hane_index]
        if not hane or hane[1] != self.current_player:
            return

        self.selected_hane = hane_index
        self.valid_moves = self.calculate_valid_moves(hane_index)
        self.game_state = 'selecting_target'

    def calculate_valid_moves(self, from_hane):
        valid_moves = []
        unique_dice = sorted(list(set(self.moves_left)), reverse=True)
        
        for move_value in unique_dice:
            target_hane = self.get_target_hane(from_hane, move_value)
            if target_hane is not None and self.is_valid_move(target_hane):
                valid_moves.append((target_hane, move_value))
            elif self.can_bear_off_logic(from_hane, move_value):
                valid_moves.append((-1, move_value))
        return valid_moves

    def get_highest_piece_in_home(self, player):
        if player == 'beyaz':
            for i in range(23, 17, -1):  # 23'ten 18'e kadar geriye doğru
                if self.board[i] and self.board[i][1] == 'beyaz':
                    return i
        else:
            for i in range(0, 6):  # 0'dan 5'e kadar
                if self.board[i] and self.board[i][1] == 'siyah':
                    return i
        return -1  # Hata veya evde pul yok durumu

    def can_bear_off_logic(self, from_hane, move_value):
        if not self.can_bear_off(self.current_player):
            return False
        
        if self.current_player == 'beyaz':
            if from_hane + move_value == 24: 
                return True
            if from_hane + move_value > 24 and from_hane == self.get_highest_piece_in_home('beyaz'): 
                return True
        else:
            if from_hane - move_value == -1: 
                return True
            if from_hane - move_value < -1 and from_hane == self.get_highest_piece_in_home('siyah'): 
                return True
        return False

    def get_target_hane(self, from_hane, move_value):
        if self.current_player == 'beyaz':
            target = from_hane + move_value
            return target if target < 24 else None
        else:
            target = from_hane - move_value
            return target if target >= 0 else None

    def is_valid_move(self, to_hane):
        target_hane = self.board[to_hane]
        return not target_hane or target_hane[1] == self.current_player or target_hane[0] == 1

    def has_pieces_in_bar(self, player):
        bar_index = 24 if player == 'beyaz' else 25
        return self.board[bar_index] and self.board[bar_index][0] > 0

    def get_bar_entry_moves(self):
        valid_entries = []
        unique_dice = sorted(list(set(self.moves_left)), reverse=True)
        for move_value in unique_dice:
            entry_hane = (move_value - 1) if self.current_player == 'beyaz' else (24 - move_value)
            if self.is_valid_move(entry_hane):
                valid_entries.append((entry_hane, move_value))
        return valid_entries

    def move_piece(self, target_hane, move_value):
        from_hane = self.selected_hane

        if from_hane == -2:  # Bar'dan giriş
            self.execute_bar_entry(target_hane, move_value)
        elif target_hane == -1:  # Pul toplama
            self.execute_bear_off(from_hane, move_value)
        else:  # Normal hamle
            self.execute_move(from_hane, target_hane, move_value)

        self.selected_hane = None
        self.valid_moves = []
        
        if not self.moves_left:
            if self.current_player == 'beyaz': 
                self.end_turn()
        else:
            if self.current_player == 'beyaz':
                self.game_state = 'selecting_piece'
                if not self.get_all_possible_moves():
                    print("Oynayacak başka geçerli hamleniz yok. Tur atlanıyor.")
                    self.draw()
                    time.sleep(1.5)
                    self.end_turn()

    def execute_bar_entry(self, target_hane, move_value):
        bar_index = 24 if self.current_player == 'beyaz' else 25
        self.board[bar_index][0] -= 1
        if self.board[bar_index][0] == 0: 
            self.board[bar_index] = []
        self.execute_common_move_logic(target_hane, move_value)

    def execute_bear_off(self, from_hane, move_value):
        home_index = 26 if self.current_player == 'beyaz' else 27
        self.board[from_hane][0] -= 1
        if self.board[from_hane][0] == 0: 
            self.board[from_hane] = []
        
        if not self.board[home_index]: 
            self.board[home_index] = [1, self.current_player]
        else: 
            self.board[home_index][0] += 1
        
        self.moves_left.remove(move_value)

    def execute_move(self, from_hane, to_hane, move_value):
        self.board[from_hane][0] -= 1
        if self.board[from_hane][0] == 0: 
            self.board[from_hane] = []
        self.execute_common_move_logic(to_hane, move_value)

    def execute_common_move_logic(self, to_hane, move_value):
        if self.board[to_hane] and self.board[to_hane][1] != self.current_player:
            self.hit_opponent_piece(to_hane)
        
        if not self.board[to_hane]: 
            self.board[to_hane] = [1, self.current_player]
        else: 
            self.board[to_hane][0] += 1
        
        self.moves_left.remove(move_value)

    def hit_opponent_piece(self, hane_index):
        opponent_color = self.board[hane_index][1]
        opponent_bar_index = 24 if opponent_color == 'beyaz' else 25
        self.board[hane_index] = []
        if not self.board[opponent_bar_index]:
            self.board[opponent_bar_index] = [1, opponent_color]
        else:
            self.board[opponent_bar_index][0] += 1
        print(f"Rakip pul vuruldu! {opponent_color} pul bar'a gönderildi.")

    def end_turn(self):
        self.current_player = 'siyah' if self.current_player == 'beyaz' else 'beyaz'
        self.game_state = 'waiting_dice'
        self.dice_values = [0, 0]
        self.selected_hane = None
        self.valid_moves = []
        print("-" * 20 + f"\nTur bitti. Sıra: {self.current_player}")

    def ai_play_turn(self):
        print("AI turuna başlıyor...")
        self.draw()
        time.sleep(0.5)

        while self.moves_left:
            possible_moves = self.get_all_possible_moves()
            if not possible_moves:
                print("AI için oynanacak geçerli hamle kalmadı.")
                break

            # Basit Strateji: Önce bar'daki pulu oyna, sonra en uzaktaki pulu oyna
            possible_moves.sort(key=lambda move: move[0], reverse=True)
            from_hane, to_hane, move_value = possible_moves[0]
            
            print(f"AI oynuyor: Hane {from_hane+1 if from_hane!=-2 else 'Bar'} -> Hane {to_hane+1 if to_hane!=-1 else 'Toplama'} ({move_value} zarı ile)")
            
            self.selected_hane = from_hane
            self.move_piece(to_hane, move_value)
            
            self.draw()
            time.sleep(1.0)

        print("AI turunu tamamladı.")
        self.end_turn()

    def get_all_possible_moves(self):
        """Tüm geçerli hamleleri (from, to, move_val) formatında bir liste olarak döndürür."""
        possible_moves = []
        
        # 1. ÖNCELİK: Eğer bar'da pul varsa, sadece giriş hamleleri mümkündür.
        if self.has_pieces_in_bar(self.current_player):
            entry_options = self.get_bar_entry_moves()  # Bu fonksiyon [(hedef_hane, zar_degeri), ...] döndürür.
            for target, move_val in entry_options:
                # Hamle formatını doğru şekilde oluştur: (-2 bar'ı temsil eder)
                possible_moves.append((-2, target, move_val))
            return possible_moves

        # 2. Bar'da pul yoksa, tahtadaki tüm pullar için hamleleri hesapla.
        for hane_index in range(24):
            # Sadece mevcut oyuncunun pullarının olduğu haneleri kontrol et
            if self.board[hane_index] and self.board[hane_index][1] == self.current_player:
                valid_moves_for_piece = self.calculate_valid_moves(hane_index)
                for target, move_val in valid_moves_for_piece:
                    possible_moves.append((hane_index, target, move_val))
                    
        return possible_moves

    # --- ÇİZİM FONKSİYONLARI ---

    def get_pul_color(self, renk):
        return PLAYER1_COLOR if renk == 'beyaz' else PLAYER2_COLOR

    def get_triangle_position(self, hane_index):
        """
        Standart tavla düzenine göre hane pozisyonlarını hesaplar.
        Hane numaralandırması:
        
        13 14 15 16 17 18 | 19 20 21 22 23 24
        12 11 10  9  8  7 |  6  5  4  3  2  1
        
        Beyaz pullar 1->24 yönünde hareket eder
        Siyah pullar 24->1 yönünde hareket eder
        """
        
        if hane_index <= 11:  # Alt sıra (1-12)
            point_up = True
            y = self.board_y + self.board_height
            col = 11 - hane_index  # Ters sıralama
        else:  # Üst sıra (13-24)
            point_up = False
            y = self.board_y
            col = hane_index - 12  # Normal sıralama
        
        # X koordinatını hesapla
        x = self.board_x + col * self.triangle_width
        
        # Ortadaki bar'ı hesaba kat
        if col >= 6:
            x += self.bar_width
                
        return x, y, point_up

    def draw_triangle(self, x, y, width, height, color, point_up=True):
        if point_up: 
            points = [(x, y), (x + width, y), (x + width // 2, y - height)]
        else: 
            points = [(x, y), (x + width, y), (x + width // 2, y + height)]
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, BOARD_BORDER, points, 2)
    
    def draw_board(self):
        # Ana tahta çerçevesi
        pygame.draw.rect(self.screen, BOARD_BORDER, 
                        (self.board_x - 5, self.board_y - 5, 
                         self.board_width + 10, self.board_height + 10), 0, 10)
        pygame.draw.rect(self.screen, BACKGROUND_COLOR, 
                        (self.board_x, self.board_y, self.board_width, self.board_height))
        
        # Üçgenleri çiz
        for i in range(24):
            # Renk hesaplama: her 2 üçgende bir renk değiştir
            color = DARK_BROWN if (i // 2) % 2 == 0 else LIGHT_BROWN
            
            x, y, point_up = self.get_triangle_position(i)
            self.draw_triangle(x, y, self.triangle_width, self.triangle_height, color, point_up)
            
            # Hane numaralarını çiz (geliştirme amaçlı)
            number_text = small_font.render(str(i + 1), True, WHITE)
            text_x = x + self.triangle_width // 2 - number_text.get_width() // 2
            text_y = y - 20 if point_up else y + self.triangle_height + 5
            self.screen.blit(number_text, (text_x, text_y))

        # Bar alanını çiz
        bar_x = self.board_x + 6 * self.triangle_width
        pygame.draw.rect(self.screen, BOARD_BORDER, 
                        (bar_x, self.board_y, self.bar_width, self.board_height))
        
    def draw_pul(self, x, y, color):
        pygame.draw.circle(self.screen, PUL_BORDER, (int(x), int(y)), self.pul_radius+1)
        pygame.draw.circle(self.screen, color, (int(x), int(y)), self.pul_radius)
    
    def draw_pieces(self):
        for hane_index in range(24):
            if not self.board[hane_index]: 
                continue
            
            pul_sayisi, renk = self.board[hane_index]
            pul_color = self.get_pul_color(renk)
            x, y, point_up = self.get_triangle_position(hane_index)
            center_x = x + self.triangle_width // 2

            for i in range(min(pul_sayisi, 5)):  # Maksimum 5 pul çiz
                # Pulların üst üste binme mesafesi
                offset = i * (self.pul_radius * 1.6) 
                
                if point_up: 
                    pul_y = y - self.pul_radius - offset
                else: 
                    pul_y = y + self.pul_radius + offset
                    
                self.draw_pul(center_x, pul_y, pul_color)
            
            # 5'ten fazla pul varsa sayıyı yaz
            if pul_sayisi > 5:
                text = small_font.render(str(pul_sayisi), True, WHITE)
                text_x = center_x - text.get_width() // 2
                text_y = y - 60 if point_up else y + self.triangle_height + 20
                self.screen.blit(text, (text_x, text_y))
                
        self.draw_bar_pieces()
    
    def draw_bar_pieces(self):
        bar_x = self.board_x + 6 * self.triangle_width + self.bar_width // 2
        
        # Beyaz pullar bar'da (alt kısım)
        if self.board[24]:
            pul_sayisi, renk = self.board[24]
            pul_color = self.get_pul_color(renk)
            for i in range(min(pul_sayisi, 5)):
                pul_y = self.board_y + self.board_height - 30 - (i * self.pul_radius * 2)
                self.draw_pul(bar_x, pul_y, pul_color)
            if pul_sayisi > 5:
                text = small_font.render(str(pul_sayisi), True, WHITE)
                self.screen.blit(text, (bar_x - 10, self.board_y + self.board_height - 120))
        
        # Siyah pullar bar'da (üst kısım)
        if self.board[25]:
            pul_sayisi, renk = self.board[25]
            pul_color = self.get_pul_color(renk)
            for i in range(min(pul_sayisi, 5)):
                pul_y = self.board_y + 30 + (i * self.pul_radius * 2)
                self.draw_pul(bar_x, pul_y, pul_color)
            if pul_sayisi > 5:
                text = small_font.render(str(pul_sayisi), True, WHITE)
                self.screen.blit(text, (bar_x - 10, self.board_y + 120))
    
    def draw_highlights(self):
        if self.selected_hane is not None:
            if self.selected_hane == -2:  # Bar seçiliyse
                bar_x = self.board_x + 6 * self.triangle_width
                bar_rect = pygame.Rect(bar_x, self.board_y, self.bar_width, self.board_height)
                pygame.draw.rect(self.screen, SELECTED_COLOR, bar_rect, 4)
            else:  # Bir hane seçiliyse
                x, y, point_up = self.get_triangle_position(self.selected_hane)
                points = [(x, y), (x + self.triangle_width, y), 
                         (x + self.triangle_width // 2, y - self.triangle_height if point_up else y + self.triangle_height)]
                pygame.draw.polygon(self.screen, SELECTED_COLOR, points, 4)

        for target, move_val in self.valid_moves:
            if target == -1:  # Toplama alanı
                bear_off_rect = pygame.Rect(self.board_x + self.board_width + 10, self.board_y, 60, self.board_height)
                pygame.draw.rect(self.screen, VALID_MOVE_COLOR, bear_off_rect, 3)
            else:
                x, y, point_up = self.get_triangle_position(target)
                points = [(x, y), (x + self.triangle_width, y), 
                         (x + self.triangle_width // 2, y - self.triangle_height if point_up else y + self.triangle_height)]
                pygame.draw.polygon(self.screen, VALID_MOVE_COLOR, points, 3)
    
    def draw_bear_off_areas(self):
        area_rect = pygame.Rect(self.board_x + self.board_width + 10, self.board_y, 60, self.board_height)
        pygame.draw.rect(self.screen, BOARD_BORDER, area_rect, 2)
        pygame.draw.line(self.screen, BOARD_BORDER, 
                        (area_rect.left, area_rect.centery), (area_rect.right, area_rect.centery), 2)
        
        # Siyah toplama alanı (üst)
        siyah_count = self.count_pieces_in_home('siyah')
        if siyah_count > 0:
            text = big_font.render(str(siyah_count), True, self.get_pul_color('siyah'))
            y_pos = area_rect.y + 50
            self.screen.blit(text, text.get_rect(center=(area_rect.centerx, y_pos)))
        
        # Beyaz toplama alanı (alt)
        beyaz_count = self.count_pieces_in_home('beyaz')
        if beyaz_count > 0:
            text = big_font.render(str(beyaz_count), True, self.get_pul_color('beyaz'))
            y_pos = area_rect.y + area_rect.height - 50
            self.screen.blit(text, text.get_rect(center=(area_rect.centerx, y_pos)))

    def draw_single_die(self, x, y, value, size=40):
        pygame.draw.rect(self.screen, DICE_COLOR, (x, y, size, size), border_radius=5)
        pygame.draw.rect(self.screen, DICE_BORDER, (x, y, size, size), 2, border_radius=5)
        dots_pos = {
            1: [(0.5, 0.5)], 
            2: [(0.25, 0.25), (0.75, 0.75)],
            3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
            4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
            5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
            6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)]
        }
        if value in dots_pos:
            for dx, dy in dots_pos[value]:
                pygame.draw.circle(self.screen, DICE_DOT, (int(x + dx*size), int(y + dy*size)), 4)

    def draw_ui(self):
        # Zar at butonu
        button_active = self.game_state == 'waiting_dice' and (not self.ai_enabled or self.current_player == 'beyaz')
        button_color = BUTTON_HOVER if self.button_hover and button_active else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color if button_active else (100, 100, 100), self.dice_button, border_radius=10)
        button_text = font.render("Zar At", True, BUTTON_TEXT)
        self.screen.blit(button_text, button_text.get_rect(center=self.dice_button.center))
        
        # Atılan zarlar
        if self.dice_values[0] > 0:
            self.draw_single_die(self.dice_area.x + 0, self.dice_area.y + 10, self.dice_values[0])
            self.draw_single_die(self.dice_area.x + 50, self.dice_area.y + 10, self.dice_values[1])
        
        # Sıra kimde bilgisi
        player_name = "Sıra: Beyaz (Sen)" if self.current_player == 'beyaz' else "Sıra: Siyah (AI)"
        player_surface = font.render(player_name, True, BLACK)
        self.screen.blit(player_surface, (50, 15))
        
        # Kalan hamle sayısı
        if self.moves_left:
            moves_text = f"Kalan hamleler: {self.moves_left}"
            moves_surface = small_font.render(moves_text, True, BLACK)
            self.screen.blit(moves_surface, (50, 480))

        # Oyun durumu bilgisi
        if self.game_state == 'selecting_piece':
            status_text = "Oynatmak istediğiniz pulu seçin"
        elif self.game_state == 'selecting_target':
            status_text = "Hedefe tıklayın"
        elif self.game_state == 'waiting_dice':
            status_text = "Zar atmak için butona tıklayın" if self.current_player == 'beyaz' else "AI düşünüyor..."
        else:
            status_text = ""
            
        if status_text:
            status_surface = small_font.render(status_text, True, BLACK)
            self.screen.blit(status_surface, (50, 500))

        # Oyun bitti ekranı
        if self.game_state == 'game_over':
            winner_name = "BEYAZ (SEN)" if self.winner == 'beyaz' else "SİYAH (AI)"
            win_text = f"{winner_name} KAZANDI!"
            
            s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 128))  # Yarı saydam siyah arka plan
            self.screen.blit(s, (0, 0))

            win_surface = big_font.render(win_text, True, WIN_COLOR)
            win_rect = win_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(win_surface, win_rect)

            restart_text = font.render("Yeniden başlatmak için 'R' tuşuna basın", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
            self.screen.blit(restart_text, restart_rect)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_board()
        self.draw_bear_off_areas()
        self.draw_pieces()
        self.draw_highlights()
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    oyun = TavlaOyunu()
    oyun.run()
