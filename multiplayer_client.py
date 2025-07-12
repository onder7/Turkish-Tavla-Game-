"""
Tavla Multiplayer İstemci - Pygame + SocketIO
"""
import pygame
import socketio
import threading
import json
import time
from typing import Optional, Dict, List
from enum import Enum

# Mevcut oyun modüllerini import et
from game_logic import TavlaGame, Player, GameState, Move
from renderer import GameRenderer, Layout, Colors
from user_interface import UIManager, InputHandler, NotificationManager

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    IN_LOBBY = "in_lobby"
    IN_ROOM = "in_room"
    PLAYING = "playing"

class MultiplayerClient:
    """Multiplayer istemci sınıfı"""
    
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.socket = socketio.Client()
        self.connection_state = ConnectionState.DISCONNECTED
        
        # Oyun verileri
        self.username = ""
        self.room_id = ""
        self.player_color = None
        self.opponent_name = ""
        self.game_state_data = None
        self.is_my_turn = False
        
        # Socket event'lerini bağla
        self._setup_socket_events()
        
        # Pygame ve UI
        self.setup_ui()
        
    def setup_ui(self):
        """UI'yi başlat"""
        pygame.init()
        self.layout = Layout()
        self.colors = Colors()
        self.screen = pygame.display.set_mode((self.layout.WINDOW_WIDTH, self.layout.WINDOW_HEIGHT))
        pygame.display.set_caption("Tavla Multiplayer")
        self.clock = pygame.time.Clock()
        
        self.renderer = GameRenderer(self.screen)
        self.notification_manager = NotificationManager(self.screen, self.colors)
        self.ui_manager = UIManager(self.screen, self.layout, self.colors)
        self.input_handler = InputHandler(self.layout)
        
        # Local game instance (sync edilecek)
        self.local_game = None
        
    def _setup_socket_events(self):
        """Socket event handler'larını ayarla"""
        
        @self.socket.event
        def connect():
            print("Sunucuya bağlandı!")
            self.connection_state = ConnectionState.CONNECTED
            self.notification_manager.add_game_log("Sunucuya bağlandı!", "success")
        
        @self.socket.event
        def disconnect():
            print("Sunucu bağlantısı koptu!")
            self.connection_state = ConnectionState.DISCONNECTED
            self.notification_manager.add_game_log("Bağlantı koptu!", "error")
        
        @self.socket.event
        def connected(data):
            print(f"Hoş geldiniz: {data['message']}")
        
        @self.socket.event
        def joined_room(data):
            self.room_id = data['room_id']
            self.connection_state = ConnectionState.IN_ROOM
            player_count = data['player_count']
            
            self.notification_manager.add_game_log(f"Oda: {self.room_id} ({player_count}/2)", "success")
            
            if player_count == 2:
                self.notification_manager.add_game_log("Hazır olmak için 'R' tuşuna basın", "info")
        
        @self.socket.event
        def player_joined(data):
            username = data['username']
            player_count = data['player_count']
            self.notification_manager.add_game_log(f"{username} katıldı ({player_count}/2)", "info")
        
        @self.socket.event
        def player_ready(data):
            players = data['players']
            ready_count = sum(1 for p in players if p['ready'])
            self.notification_manager.add_game_log(f"Hazır oyuncu: {ready_count}/2", "info")
        
        @self.socket.event
        def game_started(data):
            self.connection_state = ConnectionState.PLAYING
            players = data['players']
            
            # Kendi rengimi bul
            for player_data in players:
                if player_data['username'] == self.username:
                    self.player_color = Player.WHITE if player_data['color'] == 'beyaz' else Player.BLACK
                else:
                    self.opponent_name = player_data['username']
            
            # Local game'i sync et
            self._sync_game_state(data['game_state'])
            
            color_text = "Beyaz" if self.player_color == Player.WHITE else "Siyah"
            self.notification_manager.add_game_log(f"Oyun başladı! Sen {color_text}sın", "success")
            self.notification_manager.add_game_log(f"Rakip: {self.opponent_name}", "info")
        
        @self.socket.event
        def dice_rolled(data):
            player = data['player']
            dice = data['dice']
            
            self._sync_game_state(data['game_state'])
            
            if player == self.username:
                self.notification_manager.add_game_log(f"Sen zar attın: {dice[0]}-{dice[1]}", "dice")
            else:
                self.notification_manager.add_game_log(f"{player} zar attı: {dice[0]}-{dice[1]}", "dice")
        
        @self.socket.event
        def move_made(data):
            player = data['player']
            move_data = data['move']
            
            self._sync_game_state(data['game_state'])
            
            move_str = f"P{move_data['from_point']+1} -> P{move_data['to_point']+1}"
            if player == self.username:
                self.notification_manager.add_game_log(f"Sen: {move_str}", "player_move")
            else:
                self.notification_manager.add_game_log(f"{player}: {move_str}", "ai_move")
        
        @self.socket.event
        def game_over(data):
            winner = data['winner']
            if winner == self.username:
                self.notification_manager.add_game_log("KAZANDIN! 🎉", "success")
            else:
                self.notification_manager.add_game_log(f"{winner} kazandı", "warning")
            
            self.connection_state = ConnectionState.IN_ROOM
        
        @self.socket.event
        def error(data):
            print(f"Hata: {data['message']}")
            self.notification_manager.add_game_log(f"Hata: {data['message']}", "error")
        
        @self.socket.event
        def opponent_disconnected(data):
            self.notification_manager.add_game_log(data['message'], "warning")
    
    def _sync_game_state(self, game_state_data):
        """Sunucudan gelen game state'i local game ile sync et"""
        if not game_state_data:
            return
        
        # Yeni local game oluştur
        self.local_game = TavlaGame()
        
        # Board state'ini sync et
        for i, point_data in enumerate(game_state_data['board']):
            point = self.local_game.board.points[i]
            point.count = point_data['count']
            if point_data['owner']:
                point.owner = Player.WHITE if point_data['owner'] == 'beyaz' else Player.BLACK
            else:
                point.owner = None
        
        # Game state'ini sync et
        self.local_game.current_player = Player.WHITE if game_state_data['current_player'] == 'beyaz' else Player.BLACK
        self.local_game.game_state = GameState(game_state_data['game_state'])
        self.local_game.dice_values = game_state_data['dice_values']
        self.local_game.moves_left = game_state_data['moves_left']
        self.local_game.move_count = game_state_data['move_count']
        
        if game_state_data['winner']:
            self.local_game.winner = Player.WHITE if game_state_data['winner'] == 'beyaz' else Player.BLACK
        
        # Sıra kontrolü
        self.is_my_turn = (self.local_game.current_player == self.player_color)
        
        self.game_state_data = game_state_data
    
    def connect_to_server(self, username: str):
        """Sunucuya bağlan"""
        self.username = username
        
        try:
            self.connection_state = ConnectionState.CONNECTING
            self.notification_manager.add_game_log("Sunucuya bağlanılıyor...", "info")
            
            self.socket.connect(self.server_url)
            return True
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
            self.connection_state = ConnectionState.DISCONNECTED
            self.notification_manager.add_game_log(f"Bağlantı hatası: {e}", "error")
            return False
    
    def find_game(self):
        """Oyun ara"""
        if self.connection_state != ConnectionState.CONNECTED:
            self.notification_manager.add_game_log("Önce sunucuya bağlanın!", "error")
            return
        
        self.socket.emit('find_game', {'username': self.username})
        self.notification_manager.add_game_log("Oyun aranıyor...", "info")
    
    def ready_up(self):
        """Hazır ol"""
        if self.connection_state != ConnectionState.IN_ROOM:
            return
        
        self.socket.emit('ready')
        self.notification_manager.add_game_log("Hazırsın! Rakip bekleniyor...", "success")
    
    def roll_dice(self):
        """Zar at"""
        if (self.connection_state != ConnectionState.PLAYING or 
            not self.is_my_turn or 
            not self.local_game or 
            self.local_game.game_state != GameState.WAITING_DICE):
            return
        
        self.socket.emit('roll_dice')
    
    def make_move(self, move: Move):
        """Hamle yap"""
        if (self.connection_state != ConnectionState.PLAYING or 
            not self.is_my_turn or 
            not self.local_game):
            return
        
        self.socket.emit('make_move', {
            'from_point': move.from_point,
            'to_point': move.to_point,
            'dice_value': move.dice_value
        })
    
    def handle_events(self):
        """Pygame event'lerini işle"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_c:  # Connect
                    if self.connection_state == ConnectionState.DISCONNECTED:
                        username = f"Player_{int(time.time()) % 1000}"
                        self.connect_to_server(username)
                
                elif event.key == pygame.K_f:  # Find game
                    self.find_game()
                
                elif event.key == pygame.K_r:  # Ready
                    self.ready_up()
                
                elif event.key == pygame.K_SPACE:  # Roll dice
                    self.roll_dice()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol click
                    self._handle_mouse_click(pygame.mouse.get_pos())
        
        return True
    
    def _handle_mouse_click(self, mouse_pos):
        """Mouse tıklamasını işle"""
        if (self.connection_state != ConnectionState.PLAYING or 
            not self.is_my_turn or 
            not self.local_game):
            return
        
        # Zar at butonunu kontrol et
        if self.ui_manager.handle_button_click('roll_dice'):
            self.roll_dice()
            return
        
        # Tahta tıklaması
        if self.local_game.current_player == self.player_color:
            if self.local_game.game_state == GameState.SELECTING_PIECE:
                move = self.input_handler.handle_board_click(self.local_game, mouse_pos)
                if move:
                    self.make_move(move)
                elif self.input_handler.selected_point is not None:
                    self.local_game.game_state = GameState.SELECTING_TARGET
            
            elif self.local_game.game_state == GameState.SELECTING_TARGET:
                move = self.input_handler.handle_board_click(self.local_game, mouse_pos)
                if move:
                    self.make_move(move)
                else:
                    if self.input_handler.selected_point is None:
                        self.local_game.game_state = GameState.SELECTING_PIECE
    
    def render(self):
        """Ekranı çiz"""
        self.screen.fill(self.colors.BACKGROUND)
        
        if self.connection_state == ConnectionState.PLAYING and self.local_game:
            # Oyun ekranını çiz
            self.renderer.render_game(
                game=self.local_game,
                selected_point=self.input_handler.selected_point,
                valid_moves=self.input_handler.valid_moves,
                ai_info=None
            )
            
            # UI paneli
            self.ui_manager.draw_ui_panel(self.local_game)
            
            # Sıra göstergesi
            if self.is_my_turn:
                turn_text = self.renderer.board_renderer.font.render(
                    "SENİN SIRAN", True, (0, 255, 0)
                )
            else:
                turn_text = self.renderer.board_renderer.font.render(
                    f"{self.opponent_name}'İN SIRASI", True, (255, 100, 100)
                )
            
            self.screen.blit(turn_text, (400, 30))
        
        else:
            # Bağlantı durumu ekranı
            self._draw_connection_screen()
        
        # Bildirimleri çiz
        self.notification_manager.update_notifications()
        self.notification_manager.draw_notifications()
        
        pygame.display.flip()
    
    def _draw_connection_screen(self):
        """Bağlantı ekranını çiz"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        # Başlık
        title = font.render("TAVLA MULTIPLAYER", True, self.colors.BLACK)
        title_rect = title.get_rect(center=(500, 200))
        self.screen.blit(title, title_rect)
        
        # Durum
        status_text = {
            ConnectionState.DISCONNECTED: "Bağlantı Yok",
            ConnectionState.CONNECTING: "Bağlanılıyor...",
            ConnectionState.CONNECTED: "Bağlandı - Oyun Aranıyor",
            ConnectionState.IN_LOBBY: "Lobide",
            ConnectionState.IN_ROOM: f"Odada: {self.room_id}",
            ConnectionState.PLAYING: "Oyunda"
        }
        
        status = small_font.render(status_text.get(self.connection_state, "Bilinmeyen"), 
                                 True, self.colors.DARK_BROWN)
        status_rect = status.get_rect(center=(500, 250))
        self.screen.blit(status, status_rect)
        
        # Kontroller
        controls = [
            "C - Sunucuya Bağlan",
            "F - Oyun Ara", 
            "R - Hazır Ol",
            "SPACE - Zar At",
            "ESC - Çıkış"
        ]
        
        y_start = 320
        for i, control in enumerate(controls):
            control_text = small_font.render(control, True, self.colors.BLACK)
            control_rect = control_text.get_rect(center=(500, y_start + i * 30))
            self.screen.blit(control_text, control_rect)
        
        # Bağlantı bilgileri
        if self.connection_state in [ConnectionState.IN_ROOM, ConnectionState.PLAYING]:
            info = small_font.render(f"Kullanıcı: {self.username}", True, self.colors.DARK_BROWN)
            info_rect = info.get_rect(center=(500, 500))
            self.screen.blit(info, info_rect)
            
            if self.opponent_name:
                opponent = small_font.render(f"Rakip: {self.opponent_name}", True, self.colors.DARK_BROWN)
                opponent_rect = opponent.get_rect(center=(500, 530))
                self.screen.blit(opponent, opponent_rect)
    
    def run(self):
        """Ana döngü"""
        print("Multiplayer client başlatılıyor...")
        print("Kontroller:")
        print("C - Sunucuya bağlan")
        print("F - Oyun ara")
        print("R - Hazır ol")
        print("SPACE - Zar at")
        print("ESC - Çıkış")
        
        running = True
        while running:
            running = self.handle_events()
            self.render()
            self.clock.tick(60)
        
        # Temizlik
        if self.socket.connected:
            self.socket.disconnect()
        
        pygame.quit()

def main():
    """Ana fonksiyon"""
    import sys
    
    server_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    
    print(f"Sunucu: {server_url}")
    
    client = MultiplayerClient(server_url)
    client.run()

if __name__ == "__main__":
    main()
