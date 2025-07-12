<<<<<<< HEAD
# Modüler Tavla Oyunu

Modern Python ve Pygame kullanılarak geliştirilmiş, tamamen modüler yapıda klasik Türk Tavlası oyunu.

## Özellikler

### 🎮 Oyun Özellikleri
- Klasik Türk Tavlası kuralları
- İnsan vs AI oyun modu
- 4 farklı AI zorluk seviyesi (Kolay, Orta, Zor, Uzman)
- Gerçek zamanlı oyun istatistikleri
- Modern ve kullanıcı dostu arayüz
- Animasyonlu bildirimler ve efektler

### 🏗️ Teknik Özellikler
- **Modüler Mimari**: Her bileşen ayrı dosyada
- **Gelişmiş AI Stratejileri**: Minimax algoritması ile düşünen AI
- **Temiz Kod Yapısı**: OOP prensipleri ve design patterns
- **Kapsamlı İstatistikler**: Oyun ve AI performans metrikleri
- **Responsive UI**: Dinamik kullanıcı arayüzü

## Dosya Yapısı

```
📁 tavla-game/
├── 📄 main.py              # Ana uygulama
├── 📄 game_logic.py        # Oyun mantığı ve kuralları  
├── 📄 ai_player.py         # AI stratejileri
├── 📄 renderer.py          # Görüntüleme katmanı
├── 📄 user_interface.py    # Kullanıcı arayüzü yönetimi
├── 📄 requirements.txt     # Gerekli kütüphaneler
└── 📄 README.md           # Bu dosya
```

## Kurulum

### 1. Gereksinimleri Yükleyin

=======
# Turkish Tavla (backgammon) Game 🎲

A modern implementation of the traditional Turkish backgammon game (Tavla) built with Python and Pygame.

[Türkçe](#türkçe) | [English](#english)

![image](https://github.com/user-attachments/assets/f86dfe4f-d428-42fb-94a7-dead210aaa18)


## English

### 🎮 Game Features

- **Classic Tavla Rules**: Authentic Turkish backgammon gameplay
- **AI Opponent**: Play against a computer opponent
- **Modern Interface**: Clean, intuitive graphical user interface
- **Real-time Feedback**: Visual highlights for valid moves
- **Interactive Messages**: On-screen notifications and game status
- **Visual Dice**: Animated dice with realistic dot patterns

### 🚀 Getting Started

#### Prerequisites
- Python 3.7 or higher
- Pygame library

#### Installation

1. Clone the repository:
```bash
git clone https://github.com/onder7/Turkish-Tavla-Game-.git
cd turkish-tavla-game
```

2. Install required dependencies:
>>>>>>> 01aa59494936c95a3c19eb20237a68e755a6c0fb
```bash
pip install pygame
```

<<<<<<< HEAD
veya

```bash
pip install -r requirements.txt
```

### 2. Oyunu Başlatın

=======
3. Run the game:
>>>>>>> 01aa59494936c95a3c19eb20237a68e755a6c0fb
```bash
python main.py
```

<<<<<<< HEAD
## Modül Açıklamaları

### 🎯 game_logic.py
**Oyun Mantığı ve Kuralları**
- `TavlaGame`: Ana oyun sınıfı
- `Board`: Tahta ve pul yönetimi
- `Player`: Oyuncu türleri (Enum)
- `GameState`: Oyun durumları
- `Move`: Hamle temsili
- `GameStats`: İstatistik yönetimi

**Temel Sınıflar:**
```python
class TavlaGame:
    def roll_dice()          # Zar atma
    def get_valid_moves()    # Geçerli hamleleri bulma
    def make_move()          # Hamle yapma
    def can_bear_off()       # Pul toplama kontrolü
```

### 🤖 ai_player.py
**AI Stratejileri ve Oyuncu Sınıfları**

**AI Zorluk Seviyeleri:**
- **Kolay AI**: %70 rastgele + %30 açgözlü
- **Orta AI**: Tamamen açgözlü strateji
- **Zor AI**: Minimax algoritması (depth=2)
- **Uzman AI**: Gelişmiş minimax (depth=3)

**Temel Sınıflar:**
```python
class AIStrategy:           # Strateji base class
    def choose_move()       # Hamle seçimi
    
class AdvancedAI:          # Gelişmiş AI
    def _minimax()         # Minimax algoritması
    def _evaluate_position() # Pozisyon değerlendirmesi
```

### 🎨 renderer.py
**Görüntüleme ve Çizim Katmanı**

**Renderer Sınıfları:**
- `BoardRenderer`: Tahta çizimi
- `DiceRenderer`: Zar görselleştirmesi  
- `StatsRenderer`: İstatistik paneli
- `GameRenderer`: Ana render yöneticisi

**Özellikler:**
- Responsive tasarım
- Gerçek zamanlı pul animasyonları
- Vurgulama ve seçim efektleri
- İstatistik görselleştirmesi

### 🖱️ user_interface.py
**Kullanıcı Arayüzü ve Input Yönetimi**

**UI Bileşenleri:**
- `UIManager`: Buton ve panel yönetimi
- `InputHandler`: Fare ve klavye girişleri
- `MenuManager`: Ana menü sistemi
- `NotificationManager`: Bildirim sistemi

**Özellikler:**
- Hover efektleri
- Dinamik buton durumları
- Akıcı menü geçişleri
- Fade-out bildirimleri

## Oyun Kontrolları

### 🎮 Oyun İçi Kontroller
- **Sol Tık**: Pul seçme / Hamle yapma
- **Space**: Zar atma
- **R**: Yeni oyun (oyun bittiğinde)
- **N**: Yeni oyun başlatma
- **ESC**: Ana menüye dönüş

### 🔧 Debug Kontrolleri
- **D**: Debug bilgilerini konsola yazdır
- **V**: Tahta durumu validasyonu
- **H**: Klavye kısayolları yardımı

### 📊 UI Kontrolleri
- **Zar At**: Zar atmak için tıklayın
- **Yeni Oyun**: Oyunu yeniden başlatır
- **AI Zorluk**: Anlık zorluk seviyesi değişimi
- **İstatistikler**: Sağ panelde otomatik güncellenir

## Teknik İyileştirmeler (v2.1)

### 🏗️ **Yeni Point Veri Yapısı**
```python
@dataclass
class Point:
    count: int = 0
    owner: Optional[Player] = None
    
    def can_land(self, player: Player) -> bool
    def is_vulnerable(self) -> bool
    def is_safe(self) -> bool
```

### ✅ **Otomatik Tur Yönetimi**
- Tüm zar değerleri kullanıldığında otomatik tur bitme
- Oynanacak hamle kalmadığında otomatik pas geçme
- Oyun sonu otomatik algılama

### 🔍 **Gelişmiş Debug Sistemi**
- Tahta durumu validasyonu
- Detaylı konsol çıktıları
- Pul sayısı kontrolü
- Canlı oyun istatistikleri

### 📏 **Standart Tavla Pozisyonu Doğrulaması**
```
Başlangıç Pozisyonu:
Hane 24: 2 Beyaz  |  Hane 1: 2 Siyah
Hane 13: 5 Beyaz  |  Hane 12: 5 Siyah  
Hane 8:  3 Beyaz  |  Hane 17: 3 Siyah
Hane 6:  5 Beyaz  |  Hane 19: 5 Siyah
```

## AI Stratejileri Detayı

### 🧠 Minimax Algoritması
Gelişmiş AI'lar minimax algoritması kullanır:

```python
def _minimax(self, game, move, depth, maximizing):
    # Rekursif oyun ağacı araması
    # En iyi hamleyi bulma
    # Rakip hamlelerini öngörme
```

### 📈 Pozisyon Değerlendirmesi
AI hamleleri şu kriterlere göre değerlendirir:
- **Bar'dan Çıkış**: +100 puan
- **Pul Toplama**: +80 puan  
- **Rakip Pul Vurma**: +50 puan
- **Ev Bölgesine Taşıma**: +30 puan
- **İlerleme**: +2×zar_değeri puan
- **Güvenli Hane**: +10 puan

## İstatistikler

### 🏆 Oyun İstatistikleri
- Toplam oyun sayısı
- Kazanma oranları (Beyaz/Siyah)
- Ortalama oyun uzunluğu
- Vurulan pul sayıları

### 🤖 AI İstatistikleri
- Seçili strateji türü
- AI kazanma oranı
- Ortalama düşünme süresi
- Toplam oyun sayısı

## Geliştirme ve Katkı

### 🔧 Yeni AI Stratejisi Ekleme

```python
class YeniAI(AIStrategy):
    def choose_move(self, game):
        # Yeni strateji implementasyonu
        return best_move
    
    def get_name(self):
        return "Yeni AI"

# ai_player.py'ye ekleyin
def create_yeni_ai():
    return AIPlayer(YeniAI())
```

### 🎨 Yeni UI Bileşeni Ekleme

```python
# user_interface.py'de
class YeniUIBileşeni:
    def __init__(self, screen, colors):
        self.screen = screen
        self.colors = colors
    
    def draw(self):
        # Çizim implementasyonu
        pass
```

### 📊 Yeni İstatistik Ekleme

```python
# game_logic.py'de GameStats sınıfına
@dataclass
class GameStats:
    # Mevcut alanlar...
    yeni_metrik: int = 0
    
    @property
    def yeni_hesaplama(self):
        return self.yeni_metrik / self.games_played
```

## Teknik Detaylar

### 🏗️ Mimari Prensipleri
- **Separation of Concerns**: Her modül tek sorumluluğa sahip
- **Dependency Injection**: Gevşek bağlılık
- **Strategy Pattern**: AI stratejileri için
- **Observer Pattern**: UI güncellemeleri için

### ⚡ Performans Optimizasyonları
- Efficient board representation
- Memoization for AI calculations
- Smart rendering updates
- Minimal memory allocation

### 🔒 Kod Kalitesi
- Type hints kullanımı
- Docstring documentation
- Error handling
- Clean code principles

## Sorun Giderme

### ❌ Yaygın Hatalar

**Pygame bulunamadı:**
=======
### 🎯 How to Play

1. **Roll Dice**: Click the "Zar At" (Roll Dice) button to start your turn
2. **Select Piece**: Click on one of your pieces to select it
3. **Make Move**: Click on a valid destination highlighted in green
4. **Win Condition**: Be the first to bear off all 15 pieces

#### Game Rules
- **White pieces** move clockwise (1 → 24)
- **Black pieces** move counter-clockwise (24 → 1)
- Hit opponent pieces to send them to the bar
- Enter pieces from the bar before making other moves
- Bear off pieces when all are in your home board

### 🎨 Game Interface

- **Board**: Traditional tavla board with 24 points
- **Bar**: Center area for hit pieces
- **Bear-off Area**: Right side for collected pieces
- **Dice Area**: Shows current dice rolls
- **Message Panel**: Real-time game feedback
- **Turn Indicator**: Shows whose turn it is

### 🤖 AI Features

- Strategic piece movement
- Bar entry prioritization
- Automatic turn management
- Visual move demonstration

### 🔧 Technical Details

- **Engine**: Python 3.x
- **Graphics**: Pygame
- **Architecture**: Object-oriented design
- **Board Representation**: List-based game state
- **Move Validation**: Real-time legal move checking

### 📋 Controls

- **Mouse**: Click to interact with pieces and board
- **R Key**: Restart game (when game is over)
- **ESC**: Exit game

### 🛠️ Development

#### Project Structure
```
turkish-tavla-game/
├── main.py          # Main game file
├── README.md        # This file
└── requirements.txt # Dependencies
```

#### Key Classes
- `TavlaOyunu`: Main game class handling all game logic
- Board state management
- AI opponent logic
- Pygame rendering system

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🐛 Bug Reports

If you find any bugs or issues, please open an issue on GitHub with:
- Description of the problem
- Steps to reproduce
- Expected behavior
- Screenshots (if applicable)

---

## Türkçe

### 🎮 Oyun Özellikleri

- **Klasik Tavla Kuralları**: Geleneksel Türk tavlası oyun mekaniği
- **AI Rakip**: Bilgisayara karşı oynayın
- **Modern Arayüz**: Temiz ve sezgisel grafik kullanıcı arayüzü
- **Gerçek Zamanlı Geri Bildirim**: Geçerli hamleler için görsel vurgulama
- **Etkileşimli Mesajlar**: Ekran üzerinde bildirimler ve oyun durumu
- **Görsel Zarlar**: Gerçekçi nokta desenleri ile animasyonlu zarlar

### 🚀 Başlangıç

#### Gereksinimler
- Python 3.7 veya üzeri
- Pygame kütüphanesi

#### Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/onder7/Turkish-Tavla-Game-.git
cd turkish-tavla-game
```

2. Gerekli bağımlılıkları yükleyin:
>>>>>>> 01aa59494936c95a3c19eb20237a68e755a6c0fb
```bash
pip install pygame
```

<<<<<<< HEAD
**Font hataları:**
```python
# Sistem font'u kullanın
font = pygame.font.SysFont('Arial', 24)
```

**Performans sorunları:**
- AI depth seviyesini düşürün
- FPS limit'i ayarlayın: `clock.tick(30)`

### 🐛 Debug Modu
```python
# main.py'de debug modunu açın
DEBUG = True

if DEBUG:
    print(f"Current game state: {game.game_state}")
    print(f"Valid moves: {game.get_valid_moves()}")
```

## Lisans

Bu proje MIT lisansı altında geliştirilmiştir. Özgürce kullanabilir, değiştirebilir ve dağıtabilirsiniz.

## Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

---

**Geliştirici:** AI Assistant ile beraber geliştirilen modüler tavla oyunu
**Versiyon:** 2.0.0 (Modüler Sürüm)
**Güncelleme:** 2025 - Tam modüler refactoring
=======
3. Oyunu çalıştırın:
```bash
python main.py
```

### 🎯 Nasıl Oynanır

1. **Zar At**: Turunuzu başlatmak için "Zar At" butonuna tıklayın
2. **Pul Seç**: Oynatmak istediğiniz pulunuza tıklayın
3. **Hamle Yap**: Yeşil renkle vurgulanan geçerli hedefe tıklayın
4. **Kazanma Koşulu**: Tüm 15 pulunuzu ilk toplayan kazanır

#### Oyun Kuralları
- **Beyaz pullar** saat yönünde hareket eder (1 → 24)
- **Siyah pullar** saat yönünün tersine hareket eder (24 → 1)
- Rakip pulları vurarak bar'a gönderin
- Diğer hamleleri yapmadan önce bar'daki pulları oyuna sokun
- Tüm pullarınız ev tahtanızda olduğunda toplayabilirsiniz

### 🎨 Oyun Arayüzü

- **Tahta**: 24 haneli geleneksel tavla tahtası
- **Bar**: Vurulan pullar için merkez alan
- **Toplama Alanı**: Toplanan pullar için sağ taraf
- **Zar Alanı**: Mevcut zar atışlarını gösterir
- **Mesaj Paneli**: Gerçek zamanlı oyun geri bildirimi
- **Tur Göstergesi**: Sıranın kimde olduğunu gösterir

### 🤖 AI Özellikleri

- Stratejik pul hareketi
- Bar girişi önceliklendirmesi
- Otomatik tur yönetimi
- Görsel hamle gösterimi

### 🔧 Teknik Detaylar

- **Motor**: Python 3.x
- **Grafikler**: Pygame
- **Mimari**: Nesne yönelimli tasarım
- **Tahta Temsili**: Liste tabanlı oyun durumu
- **Hamle Doğrulama**: Gerçek zamanlı geçerli hamle kontrolü

### 📋 Kontroller

- **Fare**: Pullar ve tahta ile etkileşim için tıklayın
- **R Tuşu**: Oyunu yeniden başlat (oyun bittiğinde)
- **ESC**: Oyundan çık

### 🛠️ Geliştirme

#### Proje Yapısı
```
turkish-tavla-game/
├── main.py          # Ana oyun dosyası
├── README.md        # Bu dosya
└── requirements.txt # Bağımlılıklar
```

#### Ana Sınıflar
- `TavlaOyunu`: Tüm oyun mantığını işleyen ana oyun sınıfı
- Tahta durum yönetimi
- AI rakip mantığı
- Pygame render sistemi

### 🤝 Katkıda Bulunma

1. Depoyu fork edin
2. Bir özellik dalı oluşturun (`git checkout -b feature/harika-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Harika özellik ekle'`)
4. Dalı push edin (`git push origin feature/harika-ozellik`)
5. Pull Request açın

### 📝 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

### 🐛 Hata Raporları

Herhangi bir hata veya sorun bulursanız, lütfen GitHub'da şunları içeren bir issue açın:
- Problemin açıklaması
- Yeniden üretme adımları
- Beklenen davranış
- Ekran görüntüleri (varsa)

---

### 📸 Screenshots / Ekran Görüntüleri

![image](https://github.com/user-attachments/assets/47289639-6e60-49de-93b8-367ed42a5ba7)

*Modern tavla game interface / Modern tavla oyun arayüzü*

### 🏆 Features Coming Soon / Yakında Gelecek Özellikler

- [ ] Multiplayer support / Çok oyunculu destek
- [ ] Different AI difficulty levels / Farklı AI zorluk seviyeleri
- [ ] Game statistics / Oyun istatistikleri
- [ ] Custom board themes / Özel tahta temaları
- [ ] Sound effects / Ses efektleri
- [ ] Tournament mode / Turnuva modu

### 💡 Credits / Teşekkürler

- Traditional Turkish Tavla rules / Geleneksel Türk tavlası kuralları
- Pygame community / Pygame topluluğu
- Contributors / Katkıda bulunanlar

---

**Enjoy playing Turkish Tavla! / Türk Tavlası oynamanın keyfini çıkarın!** 🎲✨
>>>>>>> 01aa59494936c95a3c19eb20237a68e755a6c0fb
