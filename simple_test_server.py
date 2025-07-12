"""
Tavla Multiplayer Sunucu - Eventlet Olmadan
Python 3.12+ uyumlu versiyon
"""
import sys
import os

# Modül kontrolleri
missing_modules = []

try:
    from flask import Flask, request
    print("✅ Flask modülü yüklendi")
except ImportError:
    missing_modules.append("flask")
    print("❌ Flask modülü eksik!")

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    print("✅ Flask-SocketIO modülü yüklendi")
except ImportError:
    missing_modules.append("flask-socketio")
    print("❌ Flask-SocketIO modülü eksik!")

# Eventlet yerine threading kullanacağız
print("ℹ️ Eventlet atlanıyor, threading kullanılacak")

# Eksik modüller varsa çık
if missing_modules:
    print(f"\n❌ Eksik modüller: {', '.join(missing_modules)}")
    print("Lütfen şu komutu çalıştırın:")
    print("pip install flask flask-socketio")
    sys.exit(1)

# Oyun mantığını import etmeye çalış
try:
    from game_logic import TavlaGame, Player, GameState, Move
    print("✅ Oyun modülleri yüklendi")
    GAME_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Oyun modülleri bulunamadı: {e}")
    print("Basit sunucu modunda çalışacak")
    GAME_MODULES_AVAILABLE = False

import uuid
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tavla_2025_no_eventlet'

# Threading backend kullan (eventlet yerine)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    logger=False, 
    engineio_logger=False,
    async_mode='threading'  # Eventlet yerine threading
)

@dataclass
class PlayerInfo:
    username: str
    socket_id: str
    room_id: Optional[str] = None
    color: Optional[str] = None
    ready: bool = False
    connected_at: float = 0

@dataclass 
class GameRoom:
    room_id: str
    players: List[PlayerInfo]
    game_started: bool = False
    created_at: float = 0
    game_state: Optional[dict] = None

# Global değişkenler
rooms: Dict[str, GameRoom] = {}
players: Dict[str, PlayerInfo] = {}
rooms_lock = threading.Lock()

def find_available_room() -> Optional[str]:
    """Uygun oda bul"""
    with rooms_lock:
        for room_id, room in rooms.items():
            if len(room.players) < 2 and not room.game_started:
                return room_id
    return None

def create_room() -> str:
    """Yeni oda oluştur"""
    room_id = str(uuid.uuid4())[:8].upper()
    
    with rooms_lock:
        rooms[room_id] = GameRoom(
            room_id=room_id,
            players=[],
            created_at=time.time()
        )
    
    return room_id

def cleanup_empty_rooms():
    """Boş odaları temizle"""
    with rooms_lock:
        to_remove = []
        current_time = time.time()
        
        for room_id, room in rooms.items():
            # 1 saat eski veya boş odalar
            if (current_time - room.created_at > 3600) or len(room.players) == 0:
                to_remove.append(room_id)
        
        for room_id in to_remove:
            if room_id in rooms:
                del rooms[room_id]
                print(f"🗑️ Oda temizlendi: {room_id}")

@app.route('/')
def index():
    player_count = len(players)
    room_count = len(rooms)
    
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎲 Tavla Multiplayer Sunucu</h1>
            
            <div class="status">
                <h3>✅ Sunucu Durumu: Aktif</h3>
                <p><strong>Bağlı Oyuncu:</strong> {player_count}</p>
                <p><strong>Aktif Oda:</strong> {room_count}</p>
                <p><strong>Sunucu Modu:</strong> Threading (Python 3.12+ uyumlu)</p>
                <p><strong>Oyun Modülleri:</strong> {'✅ Mevcut' if GAME_MODULES_AVAILABLE else '⚠️ Basit mod'}</p>
            </div>
            
            <h3>🚀 Client Başlatma</h3>
            <div class="command">python multiplayer_client.py</div>
            
            <h3>🌐 Web Test</h3>
            <div class="command">http://localhost:5000/test</div>
            
            <h3>📊 Canlı İstatistikler</h3>
            <div id="stats">Yükleniyor...</div>
        </div>
        
        <script>
            function updateStats() {{
                fetch('/stats')
                    .then(r => r.json())
                    .then(data => {{
                        document.getElementById('stats').innerHTML = 
                            `Oyuncu: ${{data.players}} | Oda: ${{data.rooms}} | Zaman: ${{new Date(data.timestamp * 1000).toLocaleTimeString()}}`;
                    }})
                    .catch(e => {{
                        document.getElementById('stats').innerHTML = 'Bağlantı hatası';
                    }});
            }}
            
            updateStats();
            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """

@app.route('/stats')
def stats():
    return {
        'players': len(players),
        'rooms': len(rooms),
        'timestamp': time.time(),
        'game_modules': GAME_MODULES_AVAILABLE
    }

@app.route('/test')
def test_page():
    return """
    <html>
    <head>
        <title>Socket.IO Test</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    </head>
    <body>
        <h1>Socket.IO Bağlantı Testi</h1>
        <div id="status">Bağlanılıyor...</div>
        <button onclick="testMessage()">Test Mesajı Gönder</button>
        <div id="messages"></div>
        
        <script>
            const socket = io();
            
            socket.on('connect', () => {
                document.getElementById('status').innerHTML = '✅ Bağlandı!';
            });
            
            socket.on('disconnect', () => {
                document.getElementById('status').innerHTML = '❌ Bağlantı koptu';
            });
            
            socket.on('test_response', (data) => {
                document.getElementById('messages').innerHTML += 
                    `<p>📨 ${data.username}: ${data.message}</p>`;
            });
            
            function testMessage() {
                socket.emit('test_message', {message: 'Merhaba Sunucu!'});
            }
        </script>
    </body>
    </html>
    """

@socketio.on('connect')
def on_connect():
    print(f"🔗 Yeni bağlantı: {request.sid}")
    
    players[request.sid] = PlayerInfo(
        username=f'Player_{request.sid[:6]}',
        socket_id=request.sid,
        connected_at=time.time()
    )
    
    emit('connected', {
        'message': 'Tavla sunucusuna bağlandınız!',
        'player_id': request.sid,
        'server_time': time.time()
    })
    
    # İstatistikleri güncelle
    emit('server_stats', {
        'total_players': len(players),
        'total_rooms': len(rooms)
    }, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    print(f"🔌 Bağlantı koptu: {request.sid}")
    
    if request.sid in players:
        player = players[request.sid]
        
        # Oyuncuyu odasından çıkar
        if player.room_id and player.room_id in rooms:
            with rooms_lock:
                room = rooms[player.room_id]
                room.players = [p for p in room.players if p.socket_id != request.sid]
                
                # Odadaki diğer oyunculara bildir
                emit('player_left', {
                    'username': player.username,
                    'remaining_players': len(room.players)
                }, room=player.room_id)
                
                print(f"👋 {player.username} {player.room_id} odasından ayrıldı")
        
        del players[request.sid]
    
    # Temizlik
    cleanup_empty_rooms()
    
    # İstatistikleri güncelle
    emit('server_stats', {
        'total_players': len(players),
        'total_rooms': len(rooms)
    }, broadcast=True)

@socketio.on('find_game')
def on_find_game(data):
    username = data.get('username', f'Player_{request.sid[:6]}')
    
    if request.sid not in players:
        emit('error', {'message': 'Oyuncu bulunamadı!'})
        return
    
    print(f"🔍 {username} oyun arıyor...")
    
    # Oyuncu bilgilerini güncelle
    players[request.sid].username = username
    
    # Uygun oda ara veya oluştur
    room_id = find_available_room()
    if not room_id:
        room_id = create_room()
        print(f"🏠 Yeni oda oluşturuldu: {room_id}")
    
    with rooms_lock:
        room = rooms[room_id]
        
        # Oyuncuyu odaya ekle
        player_info = players[request.sid]
        player_info.room_id = room_id
        room.players.append(player_info)
    
    join_room(room_id)
    
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

@socketio.on('ready')
def on_ready():
    if request.sid not in players:
        emit('error', {'message': 'Oyuncu bulunamadı!'})
        return
    
    player = players[request.sid]
    if not player.room_id or player.room_id not in rooms:
        emit('error', {'message': 'Oda bulunamadı!'})
        return
    
    with rooms_lock:
        room = rooms[player.room_id]
        
        # Oyuncuyu hazır olarak işaretle
        for p in room.players:
            if p.socket_id == request.sid:
                p.ready = True
                break
    
    print(f"✅ {player.username} hazır!")
    
    emit('player_ready', {
        'username': player.username,
        'players': [{'username': p.username, 'ready': p.ready} for p in room.players]
    }, room=player.room_id)
    
    # Her iki oyuncu da hazırsa oyunu başlat
    if len(room.players) == 2 and all(p.ready for p in room.players):
        start_game(room)

def start_game(room: GameRoom):
    """Oyunu başlat"""
    with rooms_lock:
        room.game_started = True
        
        # Oyuncu renklerini ata
        import random
        colors = ['beyaz', 'siyah']
        random.shuffle(colors)
        
        for i, player in enumerate(room.players):
            player.color = colors[i]
        
        # Oyun durumunu oluştur
        if GAME_MODULES_AVAILABLE:
            room.game_state = create_real_game_state()
        else:
            room.game_state = create_simple_game_state()
    
    game_data = {
        'game_started': True,
        'players': [
            {'username': p.username, 'color': p.color} 
            for p in room.players
        ],
        'game_state': room.game_state
    }
    
    emit('game_started', game_data, room=room.room_id)
    print(f"🎮 Oyun başladı: {room.room_id}")

def create_simple_game_state():
    """Basit oyun durumu"""
    return {
        'current_player': 'beyaz',
        'game_state': 'waiting_dice',
        'dice_values': [0, 0],
        'moves_left': [],
        'move_count': 0,
        'board': [{'count': 0, 'owner': None} for _ in range(28)],
        'winner': None
    }

def create_real_game_state():
    """Gerçek oyun durumu"""
    game = TavlaGame()
    
    board_data = []
    for i in range(28):
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

@socketio.on('test_message')
def on_test_message(data):
    """Test mesajı handler"""
    message = data.get('message', 'Test mesajı')
    username = players.get(request.sid, PlayerInfo('Bilinmeyen', '')).username
    
    print(f"💬 Test mesajı - {username}: {message}")
    
    emit('test_response', {
        'username': username,
        'message': message,
        'timestamp': time.time()
    }, broadcast=True)

@socketio.on('roll_dice')
def on_roll_dice():
    """Zar atma (basit implementasyon)"""
    if request.sid not in players:
        emit('error', {'message': 'Oyuncu bulunamadı!'})
        return
    
    player = players[request.sid]
    if not player.room_id or player.room_id not in rooms:
        emit('error', {'message': 'Oda bulunamadı!'})
        return
    
    # Basit zar atma
    import random
    dice_result = [random.randint(1, 6), random.randint(1, 6)]
    
    emit('dice_rolled', {
        'player': player.username,
        'dice': dice_result,
        'game_state': rooms[player.room_id].game_state
    }, room=player.room_id)
    
    print(f"🎲 {player.username} zar attı: {dice_result}")

if __name__ == '__main__':
    print("🚀 Tavla Multiplayer Sunucu başlatılıyor...")
    print("📋 Özellikler:")
    print("   ✅ Python 3.12+ uyumlu")
    print("   ✅ Threading backend")
    print("   ✅ Flask-SocketIO")
    print("   ❌ Eventlet (atlandı)")
    if GAME_MODULES_AVAILABLE:
        print("   ✅ Tam oyun mantığı")
    else:
        print("   ⚠️ Basit oyun mantığı")
    
    print("\n🌐 Sunucu adresleri:")
    print("   Ana sayfa: http://localhost:5000")
    print("   Test sayfası: http://localhost:5000/test")
    print("   İstatistikler: http://localhost:5000/stats")
    
    print("\n🔗 Client bağlantısı:")
    print("   python multiplayer_client.py")
    
    print("\n🛑 Durdurmak için: Ctrl+C")
    
    try:
        # Threading backend ile çalıştır
        socketio.run(
            app, 
            debug=False,  # Debug modunu kapat
            host='0.0.0.0', 
            port=5000,
            use_reloader=False,  # Reloader'ı kapat
            log_output=False     # Fazla log'u azalt
        )
    except KeyboardInterrupt:
        print("\n🛑 Sunucu kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Sunucu hatası: {e}")
        import traceback
        traceback.print_exc()
