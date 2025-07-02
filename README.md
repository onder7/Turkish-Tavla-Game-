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
git clone https://github.com/yourusername/turkish-tavla-game.git
cd turkish-tavla-game
```

2. Install required dependencies:
```bash
pip install pygame
```

3. Run the game:
```bash
python main.py
```

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
git clone https://github.com/kullaniciadi/turkish-tavla-game.git
cd turkish-tavla-game
```

2. Gerekli bağımlılıkları yükleyin:
```bash
pip install pygame
```

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
