"""
Tavla Multiplayer Sunucu - Flask-SocketIO (Python 3.12+ Uyumlu)
"""
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import time

# Oyun mantığını import et
try:
    from game_logic import TavlaGame, Player, GameState, Move
    GAME_LOGIC_AVAILABLE = True
    print("✅ Oyun mantığı modülleri yüklendi")
except ImportError as e:
    GAME_LOGIC_AVAILABLE = False
    print(f"⚠️ Oyun mantığı bulunamadı: {e}")
    print("Sunucu basit modda çalışacak")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tavla_secret_key_2025'

# Threading backend kullan (Eventlet yerine)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',  # Eventlet yerine threading
    logger=False,
    engineio_logger=False
)

class RoomState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"

@dataclass
class PlayerInfo:
    id: str
    username: str
    socket_id: str
    ready: bool = False
    connected: bool = True
    role: Optional[str] = None  # 'WHITE' veya 'BLACK'

@dataclass
class GameRoom:
    room_id: str
    players: List[PlayerInfo]
    game: Optional[object]  # TavlaGame veya dict
    state: RoomState
    created_at: float
    spectators: List[str]  # Sadece izleyici socket_id'leri
    
    def add_player(self, player: PlayerInfo) -> bool:
        """Oyuncu ekle"""
        if len(self.players) >= 2:
            return False
        self.players.append(player)
        return True
    
    def remove_player(self, socket_id: str) -> bool:
        """Oyuncu çıkar"""
        for player in self.players:
            if player.socket_id == socket_id:
                self.players.remove(player)
                return True
        return False
    
    def get_player_by_socket(self, socket_id: str) -> Optional[PlayerInfo]:
        """Socket ID'ye göre oyuncu bul"""
        for player in self.players:
            if player.socket_id == socket_id:
                return player
        return None
    
    def is_full(self) -> bool:
        """Oda dolu mu?"""
        return len(self.players) >= 2
    
    def both_ready(self) -> bool:
        """Her iki oyuncu da hazır mı?"""
        return len(self.players) == 2 and all(p.ready for p in self.players)

# Global değişkenler
game_rooms: Dict[str, GameRoom] = {}
player_to_room: Dict[str, str] = {}  # socket_id -> room_id

def create_room() -> str:
    """Yeni oda oluştur"""
    room_id = str(uuid.uuid4())[:8].upper()
    game_rooms[room_id] = GameRoom(
        room_id=room_id,
        players=[],
        game=None,
        state=RoomState.WAITING,
        created_at=time.time(),
        spectators=[]
    )
    return room_id

def find_available_room() -> Optional[str]:
    """Uygun oda bul"""
    for room_id, room in game_rooms.items():
        if not room.is_full() and room.state == RoomState.WAITING:
            return room_id
    return None

def cleanup_old_rooms():
    """Eski odaları temizle"""
    current_time = time.time()
    to_remove = []
    
    for room_id, room in game_rooms.items():
        # 1 saat eski odaları sil
        if current_time - room.created_at > 3600:
            to_remove.append(room_id)
        # Boş odaları sil
        elif len(room.players) == 0 and len(room.spectators) == 0:
            to_remove.append(room_id)
    
    for room_id in to_remove:
        if room_id in game_rooms:
            del game_rooms[room_id]
            print(f"🗑️ Oda temizlendi: {room_id}")

def serialize_game_state(game) -> dict:
    """Oyun durumunu serialize et"""
    if not game:
        return None
    
    if GAME_LOGIC_AVAILABLE and hasattr(game, 'board'):
        # Gerçek TavlaGame objesi
        board_data = []
        for i in range(28):  # 24 normal + 2 bar + 2 home
            point = game.board.points[i]
            board_data.append({
                'count': point.count,
                'owner': point.owner.value if point.owner else None
            })
        
        return {
            'current_player': game.current_player.value,
            'game_state': game.game_state.value,
            'dice_values': game.dice_values,
            'moves_left': game.moves_left,
            'move_count': game.move_count,
            'board': board_data,
            'winner': game.winner.value if game.winner else None
        }
    else:
        # Basit dict objesi
        return game

def create_simple_game_state():
    """Basit oyun durumu (game_logic.py olmadan)"""
    return {
        'current_player': 'beyaz',
        'game_state': 'waiting_dice',
        'dice_values': [0, 0],
        'moves_left': [],
        'move_count': 0,
        'board': [{'count': 0, 'owner': None} for _ in range(28)],
        'winner': None
    }

@app.route('/')
def index():
    player_count = len(player_to_room)
    room_count = len(game_rooms)
    
    return f"""
    <html>
    <head>
        <title>Tavla Multiplayer Sunucu</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            .status {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .command {{ background: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }}
            h1 {{ color: #2c3e50; }}
            .stats {{ background: #f8f9fa; padding: 10px; border-left: 4px solid #007bff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎲 Tavla Multiplayer Sunucu</h1>
            
            <div class="status">
                <h3>✅ Sunucu Aktif</h3>
                <div class="stats">
                    <p><strong>Bağlı Oyuncu:</strong> {player_count}</p>
                    <p><strong>Aktif Oda:</strong> {room_count}</p>
                    <p><strong>Backend:</strong> Threading (Python 3.12+ uyumlu)</p>
                    <p><strong>Oyun Mantığı:</strong> {'✅ Tam' if GAME_LOGIC_AVAILABLE else '⚠️ Basit'}</p>
                    <p><strong>Sunucu Zamanı:</strong> {time.strftime('%H:%M:%S')}</p>
                </div>
            </div>
            
            <h3>🚀 Client Bağlantısı</h3>
            <div class="command">python multiplayer_client.py</div>
            
            <h3>📊 API Endpoints</h3>
            <ul>
                <li><a href="/stats">İstatistikler</a> - JSON formatında</li>
                <li><a href="/rooms">Aktif Odalar</a> - Oda listesi</li>
            </ul>
            
            <div id="live-stats">
                <h3>🔴 Canlı İstatistikler</h3>
                <div id="stats-content">Yükleniyor...</div>
            </div>
        </div>
        
        <script>
            function updateStats() {{
                fetch('/stats')
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('stats-content').innerHTML = 
                            `<p>Oyuncu: ${{data.players}} | Oda: ${{data.rooms}} | Uptime: ${{Math.floor(data.uptime/60)}}dk</p>`;
                    }})
                    .catch(e => {{
                        document.getElementById('stats-content').innerHTML = '<p style="color:red;">Bağlantı hatası</p>';
                    }});
            }}
            
            updateStats();
            setInterval(updateStats, 5000);
        </script>
    </body>
    </html>
    """

@app.route('/stats')
def stats():
    return {
        'players': len(player_to_room),
        'rooms': len(game_rooms),
        'uptime': time.time() - app.start_time,
        'game_logic_available': GAME_LOGIC_AVAILABLE,
        'timestamp': time.time()
    }

@app.route('/rooms')
def rooms_info():
    rooms_data = []
    for room_id, room in game_rooms.items():
        rooms_data.append({
            'room_id': room_id,
            'player_count': len(room.players),
            'state': room.state.value,
            'spectator_count': len(room.spectators),
            'players': [p.username for p in room.players]
        })
    
    return {'rooms': rooms_data, 'total': len(rooms_data)}

@socketio.on('connect')
def on_connect():
    print(f"🔗 Yeni bağlantı: {request.sid}")
    emit('connected', {
        'message': 'Tavla Multiplayer Sunucusuna bağlandınız!',
        'server_info': {
            'game_logic': GAME_LOGIC_AVAILABLE,
            'backend': 'threading',
            'version': '2.0'
        }
    })

@socketio.on('disconnect')
def on_disconnect():
    print(f"🔌 Bağlantı koptu: {request.sid}")
    
    # Oyuncuyu odasından çıkar
    if request.sid in player_to_room:
        room_id = player_to_room[request.sid]
        if room_id in game_rooms:
            room = game_rooms[room_id]
            
            # Oyuncu mu yoksa izleyici mi?
            player = room.get_player_by_socket(request.sid)
            if player:
                player.connected = False
                print(f"👋 {player.username} {room_id} odasından ayrıldı")
                
                # Oyun devam ediyorsa diğer oyuncuya bildir
                if room.state == RoomState.PLAYING:
                    emit('opponent_disconnected', 
                         {'message': f'{player.username} bağlantısını kaybetti'},
                         room=room_id)
                else:
                    room.remove_player(request.sid)
                    
                    # Odadaki diğer oyunculara bildir
                    emit('player_left', {
                        'username': player.username,
                        'remaining_players': len(room.players)
                    }, room=room_id)
            else:
                # İzleyici çıkarma
                if request.sid in room.spectators:
                    room.spectators.remove(request.sid)
            
            leave_room(room_id)
        
        del player_to_room[request.sid]
    
    cleanup_old_rooms()

@socketio.on('find_game')
def on_find_game(data):
    """Oyun ara"""
    username = data.get('username', f'Player_{request.sid[:6]}')
    
    # Önce mevcut odayı kontrol et
    if request.sid in player_to_room:
        emit('error', {'message': 'Zaten bir oyundasınız!'})
        return
    
    print(f"🔍 {username} oyun arıyor...")
    
    # Uygun oda ara
    room_id = find_available_room()
    if not room_id:
        room_id = create_room()
        print(f"🏠 Yeni oda oluşturuldu: {room_id}")
    
    room = game_rooms[room_id]
    player = PlayerInfo(
        id=str(uuid.uuid4()),
        username=username,
        socket_id=request.sid
    )
    
    if room.add_player(player):
        join_room(room_id)
        player_to_room[request.sid] = room_id
        
        emit('joined_room', {
            'room_id': room_id,
            'player_count': len(room.players),
            'players': [{'username': p.username, 'ready': p.ready} for p in room.players]
        })
        
        # Odadaki diğer oyunculara bildir
        emit('player_joined', {
            'username': username,
            'player_count': len(room.players)
        }, room=room_id, include_self=False)
        
        print(f"👤 {username} {room_id} odasına katıldı ({len(room.players)}/2)")
    else:
        emit('error', {'message': 'Oda dolu!'})

@socketio.on('ready')
def on_ready():
    """Oyuncu hazır"""
    if request.sid not in player_to_room:
        emit('error', {'message': 'Önce bir odaya katılın!'})
        return
    
    room_id = player_to_room[request.sid]
    room = game_rooms[room_id]
    player = room.get_player_by_socket(request.sid)
    
    if player:
        player.ready = True
        print(f"✅ {player.username} hazır!")
        
        emit('player_ready', {
            'username': player.username,
            'players': [{'username': p.username, 'ready': p.ready} for p in room.players]
        }, room=room_id)
        
        # Her iki oyuncu da hazırsa oyunu başlat
        if room.both_ready():
            start_game(room)

def start_game(room: GameRoom):
    """Oyunu başlat"""
    if GAME_LOGIC_AVAILABLE:
        room.game = TavlaGame()
    else:
        room.game = create_simple_game_state()
    
    room.state = RoomState.PLAYING
    
    # Oyuncu rollerini ata (rastgele)
    import random
    random.shuffle(room.players)
    
    if GAME_LOGIC_AVAILABLE:
        room.players[0].role = Player.WHITE  # İlk oyuncu beyaz
        room.players[1].role = Player.BLACK  # İkinci oyuncu siyah
        
        game_data = {
            'game_started': True,
            'players': [
                {'username': p.username, 'color': p.role.value} 
                for p in room.players
            ],
            'game_state': serialize_game_state(room.game)
        }
    else:
        # Basit mod
        colors = ['beyaz', 'siyah']
        for i, player in enumerate(room.players):
            player.role = colors[i]
        
        game_data = {
            'game_started': True,
            'players': [
                {'username': p.username, 'color': p.role} 
                for p in room.players
            ],
            'game_state': room.game
        }
    
    emit('game_started', game_data, room=room.room_id)
    print(f"🎮 Oyun başladı: {room.room_id}")

@socketio.on('roll_dice')
def on_roll_dice():
    """Zar at"""
    if request.sid not in player_to_room:
        emit('error', {'message': 'Oyunda değilsiniz!'})
        return
    
    room_id = player_to_room[request.sid]
    room = game_rooms[room_id]
    
    if not room.game or room.state != RoomState.PLAYING:
        emit('error', {'message': 'Oyun başlamamış!'})
        return
    
    player = room.get_player_by_socket(request.sid)
    if not player:
        emit('error', {'message': 'Oyuncu bulunamadı!'})
        return
    
    # Sıra kontrolü
    if GAME_LOGIC_AVAILABLE:
        if hasattr(room.game, 'current_player'):
            if player.role != room.game.current_player:
                emit('error', {'message': 'Sizin sıranız değil!'})
                return
            
            if room.game.game_state != GameState.WAITING_DICE:
                emit('error', {'message': 'Zar atma sırası değil!'})
                return
            
            # Zar at
            dice_result = room.game.roll_dice()
        else:
            emit('error', {'message': 'Oyun durumu hatası!'})
            return
    else:
        # Basit mod - sadece rastgele zar
        import random
        dice_result = (random.randint(1, 6), random.randint(1, 6))
        room.game['dice_values'] = list(dice_result)
    
    # Tüm oyunculara gönder
    emit('dice_rolled', {
        'player': player.username,
        'dice': dice_result,
        'game_state': serialize_game_state(room.game)
    }, room=room_id)
    
    print(f"🎲 {player.username} zar attı: {dice_result}")

@socketio.on('make_move')
def on_make_move(data):
    """Hamle yap"""
    if request.sid not in player_to_room:
        emit('error', {'message': 'Oyunda değilsiniz!'})
        return
    
    room_id = player_to_room[request.sid]
    room = game_rooms[room_id]
    
    if not room.game or room.state != RoomState.PLAYING:
        emit('error', {'message': 'Oyun başlamamış!'})
        return
    
    player = room.get_player_by_socket(request.sid)
    if not player:
        emit('error', {'message': 'Oyuncu bulunamadı!'})
        return
    
    # Sıra kontrolü
    if GAME_LOGIC_AVAILABLE and hasattr(room.game, 'current_player'):
        if player.role != room.game.current_player:
            emit('error', {'message': 'Sizin sıranız değil!'})
            return
    
    # Hamleyi parse et
    try:
        if GAME_LOGIC_AVAILABLE:
            move = Move(
                from_point=data['from_point'],
                to_point=data['to_point'],
                dice_value=data['dice_value']
            )
            
            # Hamleyi yap
            if room.game.make_move(move):
                # Başarılı hamle
                game_over = room.game.game_state == GameState.GAME_OVER
                
                emit('move_made', {
                    'player': player.username,
                    'move': {
                        'from_point': move.from_point,
                        'to_point': move.to_point,
                        'dice_value': move.dice_value
                    },
                    'game_state': serialize_game_state(room.game),
                    'game_over': game_over
                }, room=room_id)
                
                print(f"♟️ {player.username} hamle yaptı: {move}")
                
                # Oyun bittiyse
                if game_over:
                    room.state = RoomState.FINISHED
                    winner_name = next(p.username for p in room.players if p.role == room.game.winner)
                    emit('game_over', {
                        'winner': winner_name,
                        'winner_color': room.game.winner.value
                    }, room=room_id)
                    print(f"🏆 Oyun bitti: {winner_name} kazandı!")
            else:
                emit('error', {'message': 'Geçersiz hamle!'})
        else:
            # Basit mod - hamleyi kabul et
            emit('move_made', {
                'player': player.username,
                'move': data,
                'game_state': room.game,
                'game_over': False
            }, room=room_id)
            
    except KeyError:
        emit('error', {'message': 'Geçersiz hamle formatı!'})
    except Exception as e:
        emit('error', {'message': f'Hamle hatası: {str(e)}'})

@socketio.on('spectate')
def on_spectate(data):
    """Oyunu izle"""
    room_id = data.get('room_id')
    
    if room_id not in game_rooms:
        emit('error', {'message': 'Oda bulunamadı!'})
        return
    
    room = game_rooms[room_id]
    join_room(room_id)
    room.spectators.append(request.sid)
    player_to_room[request.sid] = room_id
    
    emit('spectating', {
        'room_id': room_id,
        'game_state': serialize_game_state(room.game) if room.game else None,
        'players': [{'username': p.username} for p in room.players]
    })
    
    print(f"👁️ İzleyici {room_id} odasına katıldı")

@socketio.on('get_rooms')
def on_get_rooms():
    """Mevcut odaları listele"""
    rooms_data = []
    for room_id, room in game_rooms.items():
        rooms_data.append({
            'room_id': room_id,
            'player_count': len(room.players),
            'state': room.state.value,
            'spectator_count': len(room.spectators)
        })
    
    emit('rooms_list', {'rooms': rooms_data})

if __name__ == '__main__':
    # Başlangıç zamanını kaydet
    app.start_time = time.time()
    
    print("🚀 Tavla Multiplayer Sunucu başlatılıyor...")
    print("📋 Özellikler:")
    print("   ✅ Python 3.12+ uyumlu")
    print("   ✅ Threading backend (Eventlet yerine)")
    print("   ✅ Flask-SocketIO")
    if GAME_LOGIC_AVAILABLE:
        print("   ✅ Tam oyun mantığı")
    else:
        print("   ⚠️ Basit oyun mantığı")
    
    print("\n🌐 Sunucu adresleri:")
    print("   Ana sayfa: http://localhost:5000")
    print("   İstatistikler: http://localhost:5000/stats")
    print("   Odalar: http://localhost:5000/rooms")
    
    print("\n🔗 Client bağlantısı:")
    print("   python multiplayer_client.py")
    
    print("\n🛑 Durdurmak için: Ctrl+C")
    
    try:
        socketio.run(
            app, 
            debug=False,  # Debug modunu kapat (threading için)
            host='0.0.0.0', 
            port=5000,
            use_reloader=False  # Threading ile reloader uyumsuz
        )
    except KeyboardInterrupt:
        print("\n🛑 Sunucu kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Sunucu hatası: {e}")
        import traceback
        traceback.print_exc()
