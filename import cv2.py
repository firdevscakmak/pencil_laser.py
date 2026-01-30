"#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
================================================================================
                    GÖRÜNTÜ İŞLEME MASAÜSTÜ UYGULAMASI
================================================================================
Bu uygulama, yüklenen görselleri farklı sanatsal stillere dönüştürür:
- Gri Skala (Grayscale)
- Dither Efekti
- Karakalem Sketch
- Line Art (Çizgi Sanatı)

Geliştirici: Image Processing Studio
Versiyon: 1.0
================================================================================
\"\"\"

# =============================================================================
# BÖLÜM 1: KÜTÜPHANE İMPORTLARI
# Bu bölümde uygulamanın çalışması için gereken tüm kütüphaneler yüklenir
# =============================================================================

import sys  # Python sistem işlemleri için
import os  # Dosya ve klasör işlemleri için
import numpy as np  # Sayısal hesaplamalar ve dizi işlemleri için
from PIL import Image, ImageFilter, ImageOps, ImageEnhance  # Görüntü işleme için
import cv2  # OpenCV - gelişmiş görüntü işleme için

# PyQt5 - Masaüstü arayüz oluşturmak için
from PyQt5.QtWidgets import (
    QApplication,  # Ana uygulama sınıfı
    QMainWindow,  # Ana pencere sınıfı
    QWidget,  # Temel widget sınıfı
    QVBoxLayout,  # Dikey düzen yöneticisi
    QHBoxLayout,  # Yatay düzen yöneticisi
    QGridLayout,  # Izgara düzen yöneticisi
    QLabel,  # Metin ve görüntü etiketi
    QPushButton,  # Buton widget'ı
    QSlider,  # Kaydırıcı widget'ı
    QCheckBox,  # Onay kutusu widget'ı
    QComboBox,  # Açılır liste widget'ı
    QLineEdit,  # Tek satırlık metin girişi
    QFileDialog,  # Dosya seçim penceresi
    QGroupBox,  # Gruplandırma kutusu
    QFrame,  # Çerçeve widget'ı
    QScrollArea,  # Kaydırılabilir alan
    QSpinBox,  # Sayı girişi widget'ı
    QDoubleSpinBox,  # Ondalıklı sayı girişi
    QMessageBox,  # Mesaj kutusu
    QSplitter,  # Bölücü widget
    QSizePolicy,  # Boyut politikası
    QProgressBar,  # İlerleme çubuğu
)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal  # Qt temel sınıfları
from PyQt5.QtGui import (
    QPixmap,  # Görüntü taşıyıcı
    QImage,  # Qt görüntü sınıfı
    QFont,  # Yazı tipi
    QPalette,  # Renk paleti
    QColor,  # Renk sınıfı
    QIcon,  # İkon sınıfı
    QPainter,  # Çizim sınıfı
    QLinearGradient,  # Doğrusal gradyan
    QBrush,  # Fırça sınıfı
    QPen,  # Kalem sınıfı
)

# Arkaplan kaldırma için rembg kütüphanesi
# =============================================================================
# ARKA PLAN KALDIRMA VE SVG DESTEĞİ (GÜVENLİ MOD)
# Python 3.14 uyumluluğu için kütüphane kontrolleri devre dışı bırakıldı
# =============================================================================

REMBG_AVAILABLE = False
POTRACE_AVAILABLE = False

# Programın hata vermemesi için boş fonksiyon tanımlıyoruz
def remove_background(image, *args, **kwargs):
    return image

print("Bilgi: Python 3.14 uyumluluğu için rembg devre dışı bırakıldı, uygulama başlatılıyor...")

# SVG dışa aktarma için
try:
    import potrace  # Bitmap'ten vektör dönüşümü için
    POTRACE_AVAILABLE = True
except ImportError:
    POTRACE_AVAILABLE = False
    print(\"Uyarı: potrace kütüphanesi yüklü değil. SVG export için 'pip install potracer' gerekli.\")


# =============================================================================
# BÖLÜM 2: RENK VE STİL TANIMLARI
# Bu bölümde uygulamanın görsel teması tanımlanır
# =============================================================================

# 3D görünümlü koyu tema renkleri
COLORS = {
    'bg_dark': '#1a1a2e',  # Ana arkaplan - koyu lacivert
    'bg_medium': '#16213e',  # Orta ton arkaplan
    'bg_light': '#0f3460',  # Açık arkaplan
    'accent': '#e94560',  # Vurgu rengi - kırmızı
    'accent_hover': '#ff6b6b',  # Hover durumu
    'text_primary': '#ffffff',  # Ana metin - beyaz
    'text_secondary': '#a0a0a0',  # İkincil metin - gri
    'border': '#3a3a5c',  # Kenarlık rengi
    'success': '#4ecca3',  # Başarı rengi - yeşil
    'warning': '#ffc107',  # Uyarı rengi - sarı
    'panel_bg': '#252542',  # Panel arkaplanı
    'button_3d_light': '#3d3d6b',  # 3D buton açık ton
    'button_3d_dark': '#1a1a35',  # 3D buton koyu ton
}

# Materyal preset renkleri
MATERIAL_COLORS = {
    'wood': {'primary': '#8B4513', 'secondary': '#D2691E', 'name': 'Wood'},  # Ahşap
    'metal': {'primary': '#708090', 'secondary': '#C0C0C0', 'name': 'Metal'},  # Metal
    'leather': {'primary': '#8B0000', 'secondary': '#A52A2A', 'name': 'Leather'},  # Deri
    'stone': {'primary': '#696969', 'secondary': '#A9A9A9', 'name': 'Stone'},  # Taş
}


# =============================================================================
# BÖLÜM 3: ANA STİL ŞABLONU (QSS - Qt Style Sheet)
# Bu bölümde uygulamanın CSS benzeri stilleri tanımlanır
# =============================================================================

MAIN_STYLE = f\"\"\"
/* Ana pencere stili */
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}

/* Genel widget stili */
QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

/* Grup kutusu stili - 3D görünüm */
QGroupBox {{
    background-color: {COLORS['panel_bg']};
    border: 2px solid {COLORS['border']};
    border-radius: 10px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: bold;
    font-size: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px 15px;
    background-color: {COLORS['accent']};
    border-radius: 5px;
    color: white;
}}

/* 3D Buton stili */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['button_3d_light']},
        stop:0.5 {COLORS['bg_medium']},
        stop:1 {COLORS['button_3d_dark']});
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 20px;
    color: {COLORS['text_primary']};
    font-weight: bold;
    font-size: 11px;
    min-height: 20px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['accent_hover']},
        stop:0.5 {COLORS['accent']},
        stop:1 #c73e54);
    border-color: {COLORS['accent']};
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['button_3d_dark']},
        stop:0.5 {COLORS['bg_medium']},
        stop:1 {COLORS['button_3d_light']});
    padding-top: 12px;
    padding-bottom: 8px;
}}

/* Kaydırıcı stili */
QSlider::groove:horizontal {{
    border: 1px solid {COLORS['border']};
    height: 8px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['button_3d_dark']},
        stop:1 {COLORS['bg_medium']});
    border-radius: 4px;
}}

QSlider::handle:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['accent_hover']},
        stop:0.5 {COLORS['accent']},
        stop:1 #c73e54);
    border: 2px solid {COLORS['text_primary']};
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {COLORS['success']};
}}

/* Metin girişi stili */
QLineEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_medium']};
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    color: {COLORS['text_primary']};
    font-size: 12px;
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['accent']};
}}

/* Açılır liste stili */
QComboBox {{
    background-color: {COLORS['bg_medium']};
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    color: {COLORS['text_primary']};
    font-size: 12px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_medium']};
    border: 2px solid {COLORS['accent']};
    selection-background-color: {COLORS['accent']};
    color: {COLORS['text_primary']};
}}

/* Onay kutusu stili */
QCheckBox {{
    spacing: 10px;
    font-size: 12px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['bg_medium']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border-color: {COLORS['accent']};
}}

/* Etiket stili */
QLabel {{
    color: {COLORS['text_primary']};
    font-size: 11px;
}}

/* Kaydırma alanı stili */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

/* İlerleme çubuğu stili */
QProgressBar {{
    border: 2px solid {COLORS['border']};
    border-radius: 5px;
    text-align: center;
    background-color: {COLORS['bg_medium']};
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 3px;
}}
\"\"\"


# =============================================================================
# BÖLÜM 4: GÖRÜNTÜ İŞLEME FONKSİYONLARI
# Bu bölümde tüm görüntü dönüşüm algoritmaları tanımlanır
# =============================================================================

class ImageProcessor:
    \"\"\"
    Görüntü işleme sınıfı - Tüm görüntü dönüşümlerini içerir
    \"\"\"
    
    def __init__(self):
        \"\"\"Sınıf başlatıcı - varsayılan değerleri ayarlar\"\"\"
        self.original_image = None  # Orijinal görüntü
        self.processed_images = {}  # İşlenmiş görüntüler sözlüğü
        
        # İşlem parametreleri
        self.contrast = 1.0  # Kontrast değeri (0.5-2.0)
        self.brightness = 1.0  # Parlaklık değeri (0.5-2.0)
        self.bg_removal = 0  # Arkaplan temizleme seviyesi (0-100)
        self.face_detection = 0  # Yüz algılama seviyesi (0-100)
        self.pencil_hardness = 2  # Kalem sertliği (H-6H = 0-6)
        self.invert_colors = False  # Renk ters çevirme
        self.beam_diameter = 0.25  # Işın çapı (0.15-0.4)
        self.target_dpi = 300  # Hedef DPI değeri
    
    def load_image(self, filepath):
        \"\"\"
        Görüntü yükleme fonksiyonu
        
        Parametreler:
            filepath: Görüntü dosyasının yolu
        
        Döndürür:
            bool: Yükleme başarılı ise True
        \"\"\"
        try:
            # PIL ile görüntüyü aç
            self.original_image = Image.open(filepath)
            
            # RGBA moduna dönüştür (şeffaflık desteği için)
            if self.original_image.mode != 'RGBA':
                self.original_image = self.original_image.convert('RGBA')
            
            return True
        except Exception as e:
            print(f\"Görüntü yükleme hatası: {e}\")
            return False
    
    def apply_dpi_ppi(self, image, target_dpi):
        \"\"\"
        DPI/PPI değerlerini eşitle ve ayarla
        
        Parametreler:
            image: PIL Image nesnesi
            target_dpi: Hedef DPI değeri
        
        Döndürür:
            PIL Image: DPI ayarlanmış görüntü
        \"\"\"
        # Görüntünün DPI bilgisini ayarla
        image.info['dpi'] = (target_dpi, target_dpi)
        return image
    
    def resize_image(self, image, width=None, height=None):
        \"\"\"
        Görüntüyü yeniden boyutlandır
        
        Parametreler:
            image: PIL Image nesnesi
            width: Hedef genişlik (piksel)
            height: Hedef yükseklik (piksel)
        
        Döndürür:
            PIL Image: Boyutlandırılmış görüntü
        \"\"\"
        if width is None and height is None:
            return image
        
        orig_width, orig_height = image.size
        
        # En-boy oranını koru
        if width and not height:
            ratio = width / orig_width
            height = int(orig_height * ratio)
        elif height and not width:
            ratio = height / orig_height
            width = int(orig_width * ratio)
        
        # Yüksek kaliteli yeniden boyutlandırma
        return image.resize((width, height), Image.Resampling.LANCZOS)
    
    def adjust_contrast_brightness(self, image):
        \"\"\"
        Kontrast ve parlaklık ayarla
        
        Parametreler:
            image: PIL Image nesnesi
        
        Döndürür:
            PIL Image: Ayarlanmış görüntü
        \"\"\"
        # RGB'ye dönüştür (enhance için gerekli)
        if image.mode == 'RGBA':
            # Alpha kanalını ayır
            r, g, b, a = image.split()
            rgb_image = Image.merge('RGB', (r, g, b))
        else:
            rgb_image = image.convert('RGB')
            a = None
        
        # Kontrast ayarla
        enhancer = ImageEnhance.Contrast(rgb_image)
        rgb_image = enhancer.enhance(self.contrast)
        
        # Parlaklık ayarla
        enhancer = ImageEnhance.Brightness(rgb_image)
        rgb_image = enhancer.enhance(self.brightness)
        
        # Alpha kanalını geri ekle
        if a is not None:
            r, g, b = rgb_image.split()
            return Image.merge('RGBA', (r, g, b, a))
        
        return rgb_image
    
    def remove_background_ai(self, image, strength):
        \"\"\"
        AI destekli arkaplan kaldırma (rembg kullanarak)
        
        Parametreler:
            image: PIL Image nesnesi
            strength: Kaldırma gücü (0-100)
        
        Döndürür:
            PIL Image: Arkaplanı kaldırılmış görüntü
        \"\"\"
        if strength == 0 or not REMBG_AVAILABLE:
            return image
        
        try:
            # rembg ile arkaplanı kaldır
            result = remove_background(image)
            
            # Orijinal ile karıştır (strength'e göre)
            alpha = strength / 100.0
            
            # Her iki görüntüyü de RGBA'ya dönüştür
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            if result.mode != 'RGBA':
                result = result.convert('RGBA')
            
            # Karıştır
            blended = Image.blend(image, result, alpha)
            return blended
            
        except Exception as e:
            print(f\"Arkaplan kaldırma hatası: {e}\")
            return image
    
    def detect_and_enhance_face(self, image, strength):
        \"\"\"
        Yüz algılama ve iyileştirme (OpenCV kullanarak)
        
        Parametreler:
            image: PIL Image nesnesi
            strength: İyileştirme gücü (0-100)
        
        Döndürür:
            PIL Image: Yüz iyileştirilmiş görüntü
        \"\"\"
        if strength == 0:
            return image
        
        try:
            # PIL'den OpenCV formatına dönüştür
            cv_image = np.array(image.convert('RGB'))
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
            
            # Gri tonlamaya dönüştür (yüz algılama için)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Yüz algılayıcı yükle
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Yüzleri algıla
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            # Her yüz için iyileştirme uygula
            for (x, y, w, h) in faces:
                # Yüz bölgesini al
                face_region = cv_image[y:y+h, x:x+w]
                
                # Yumuşatma uygula (gürültü azaltma)
                smoothing = int(strength / 10) * 2 + 1  # Tek sayı olmalı
                if smoothing > 1:
                    face_region = cv2.bilateralFilter(
                        face_region, smoothing, 75, 75
                    )
                
                # Bölgeyi geri yerleştir
                cv_image[y:y+h, x:x+w] = face_region
            
            # OpenCV'den PIL'e dönüştür
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            result = Image.fromarray(cv_image)
            
            # Orijinal alpha kanalını koru
            if image.mode == 'RGBA':
                r, g, b = result.split()
                _, _, _, a = image.split()
                result = Image.merge('RGBA', (r, g, b, a))
            
            return result
            
        except Exception as e:
            print(f\"Yüz algılama hatası: {e}\")
            return image
    
    def convert_to_grayscale(self, image):
        \"\"\"
        Gri tonlamaya dönüştür
        
        Parametreler:
            image: PIL Image nesnesi
        
        Döndürür:
            PIL Image: Gri tonlamalı görüntü
        \"\"\"
        # Luminosity yöntemiyle gri tonlama
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb = Image.merge('RGB', (r, g, b))
            gray = rgb.convert('L')
            # Gri görüntüyü RGB olarak geri dönüştür (görüntüleme için)
            gray_rgb = gray.convert('RGB')
            r, g, b = gray_rgb.split()
            return Image.merge('RGBA', (r, g, b, a))
        else:
            return image.convert('L').convert('RGB')
    
    def apply_dithering(self, image):
        \"\"\"
        Floyd-Steinberg dithering uygula
        
        Parametreler:
            image: PIL Image nesnesi
        
        Döndürür:
            PIL Image: Dither efektli görüntü
        \"\"\"
        # Önce gri tonlamaya dönüştür
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb = Image.merge('RGB', (r, g, b))
            gray = rgb.convert('L')
        else:
            gray = image.convert('L')
        
        # 1-bit dithering uygula
        dithered = gray.convert('1')  # Floyd-Steinberg otomatik uygulanır
        
        # Tekrar RGB'ye dönüştür (görüntüleme için)
        dithered_rgb = dithered.convert('RGB')
        
        # Alpha kanalını koru
        if image.mode == 'RGBA':
            r, g, b = dithered_rgb.split()
            return Image.merge('RGBA', (r, g, b, a))
        
        return dithered_rgb
    
    def create_pencil_sketch(self, image, hardness):
        \"\"\"
        Karakalem sketch efekti oluştur
        
        Parametreler:
            image: PIL Image nesnesi
            hardness: Kalem sertliği (0-6, H'den 6H'ye)
        
        Döndürür:
            PIL Image: Karakalem efektli görüntü
        \"\"\"
        # PIL'den OpenCV formatına dönüştür
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb = Image.merge('RGB', (r, g, b))
        else:
            rgb = image.convert('RGB')
            a = None
        
        cv_image = np.array(rgb)
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        
        # Gri tonlamaya dönüştür
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Ters çevir
        inverted = cv2.bitwise_not(gray)
        
        # Kalem sertliğine göre bulanıklaştırma ayarla
        # Yumuşak kalem (H) = daha fazla bulanıklık
        # Sert kalem (6H) = daha az bulanıklık
        blur_amount = max(21 - (hardness * 3), 3)
        if blur_amount % 2 == 0:
            blur_amount += 1  # Tek sayı olmalı
        
        blurred = cv2.GaussianBlur(inverted, (blur_amount, blur_amount), 0)
        
        # Renk soldurma ile birleştir
        sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
        
        # Kontrast ayarla (sert kalemler için)
        alpha = 1.0 + (hardness * 0.1)  # 1.0 - 1.6 arası
        sketch = cv2.convertScaleAbs(sketch, alpha=alpha, beta=0)
        
        # RGB'ye dönüştür
        sketch_rgb = cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB)
        result = Image.fromarray(sketch_rgb)
        
        # Alpha kanalını geri ekle
        if a is not None:
            r, g, b = result.split()
            result = Image.merge('RGBA', (r, g, b, a))
        
        return result
    
    def create_line_art(self, image, beam_diameter):
        \"\"\"
        Line art (çizgi sanatı) efekti oluştur
        
        Parametreler:
            image: PIL Image nesnesi
            beam_diameter: Işın çapı (çizgi kalınlığı) 0.15-0.4
        
        Döndürür:
            PIL Image: Line art efektli görüntü
        \"\"\"
        # PIL'den OpenCV formatına dönüştür
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb = Image.merge('RGB', (r, g, b))
        else:
            rgb = image.convert('RGB')
            a = None
        
        cv_image = np.array(rgb)
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        
        # Gri tonlamaya dönüştür
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Işın çapına göre kenar algılama parametreleri
        # Küçük çap = daha ince çizgiler, daha fazla detay
        # Büyük çap = daha kalın çizgiler, daha az detay
        threshold_ratio = beam_diameter / 0.4  # 0.375 - 1.0 arası
        
        low_threshold = int(50 * threshold_ratio)
        high_threshold = int(150 * threshold_ratio)
        
        # Canny kenar algılama
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        
        # Çizgileri kalınlaştır (beam_diameter'a göre)
        kernel_size = max(1, int(beam_diameter * 5))
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Ters çevir (beyaz arkaplan, siyah çizgiler)
        edges = cv2.bitwise_not(edges)
        
        # RGB'ye dönüştür
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        result = Image.fromarray(edges_rgb)
        
        # Alpha kanalını geri ekle
        if a is not None:
            r, g, b = result.split()
            result = Image.merge('RGBA', (r, g, b, a))
        
        return result
    
    def apply_invert(self, image):
        \"\"\"
        Renkleri ters çevir
        
        Parametreler:
            image: PIL Image nesnesi
        
        Döndürür:
            PIL Image: Renkleri ters çevrilmiş görüntü
        \"\"\"
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb = Image.merge('RGB', (r, g, b))
            inverted = ImageOps.invert(rgb)
            r, g, b = inverted.split()
            return Image.merge('RGBA', (r, g, b, a))
        else:
            return ImageOps.invert(image.convert('RGB'))
    
    def process_all(self):
        \"\"\"
        Tüm işlemleri uygula ve 4 farklı çıktı oluştur
        
        Döndürür:
            dict: 4 işlenmiş görüntü içeren sözlük
        \"\"\"
        if self.original_image is None:
            return None
        
        # Temel işlemleri uygula
        processed = self.original_image.copy()
        
        # Kontrast ve parlaklık
        processed = self.adjust_contrast_brightness(processed)
        
        # Arkaplan kaldırma
        if self.bg_removal > 0:
            processed = self.remove_background_ai(processed, self.bg_removal)
        
        # Yüz algılama ve iyileştirme
        if self.face_detection > 0:
            processed = self.detect_and_enhance_face(processed, self.face_detection)
        
        # 4 farklı çıktı oluştur
        results = {}
        
        # 1. Gri Skala
        grayscale = self.convert_to_grayscale(processed)
        if self.invert_colors:
            grayscale = self.apply_invert(grayscale)
        results['grayscale'] = grayscale
        
        # 2. Dither
        dithered = self.apply_dithering(processed)
        if self.invert_colors:
            dithered = self.apply_invert(dithered)
        results['dither'] = dithered
        
        # 3. Karakalem Sketch
        sketch = self.create_pencil_sketch(processed, self.pencil_hardness)
        if self.invert_colors:
            sketch = self.apply_invert(sketch)
        results['sketch'] = sketch
        
        # 4. Line Art
        line_art = self.create_line_art(processed, self.beam_diameter)
        if self.invert_colors:
            line_art = self.apply_invert(line_art)
        results['line_art'] = line_art
        
        self.processed_images = results
        return results
    
    def get_image_stats(self, image):
        \"\"\"
        Görüntü istatistiklerini hesapla
        
        Parametreler:
            image: PIL Image nesnesi
        
        Döndürür:
            dict: Görüntü istatistikleri
        \"\"\"
        if image is None:
            return None
        
        # Numpy dizisine dönüştür
        img_array = np.array(image)
        
        stats = {
            'width': image.size[0],
            'height': image.size[1],
            'mode': image.mode,
            'channels': len(image.getbands()),
            'min_pixel': int(np.min(img_array)),
            'max_pixel': int(np.max(img_array)),
            'mean_pixel': round(float(np.mean(img_array)), 2),
            'std_pixel': round(float(np.std(img_array)), 2),
        }
        
        # DPI bilgisi
        try:
            stats['dpi'] = image.info.get('dpi', (72, 72))
        except:
            stats['dpi'] = (72, 72)
        
        return stats
    
    def save_image(self, image, filepath, format='PNG'):
        \"\"\"
        Görüntüyü kaydet
        
        Parametreler:
            image: PIL Image nesnesi
            filepath: Kayıt yolu
            format: Dosya formatı ('PNG' veya 'SVG')
        
        Döndürür:
            bool: Kayıt başarılı ise True
        \"\"\"
        try:
            if format.upper() == 'SVG':
                return self.save_as_svg(image, filepath)
            else:
                # PNG olarak kaydet
                if image.mode == 'RGBA':
                    image.save(filepath, 'PNG', dpi=(self.target_dpi, self.target_dpi))
                else:
                    image.convert('RGB').save(filepath, 'PNG', dpi=(self.target_dpi, self.target_dpi))
                return True
        except Exception as e:
            print(f\"Kayıt hatası: {e}\")
            return False
    
    def save_as_svg(self, image, filepath):
        \"\"\"
        Görüntüyü SVG olarak kaydet (vektör dönüşümü)
        
        Parametreler:
            image: PIL Image nesnesi
            filepath: Kayıt yolu
        
        Döndürür:
            bool: Kayıt başarılı ise True
        \"\"\"
        try:
            # Siyah beyaza dönüştür
            if image.mode != 'L':
                bw = image.convert('L')
            else:
                bw = image
            
            # Eşikleme uygula
            threshold = 128
            bw = bw.point(lambda x: 0 if x < threshold else 255, '1')
            
            # SVG oluştur (basit yöntem - potrace olmadan)
            width, height = bw.size
            pixels = list(bw.getdata())
            
            svg_content = f'''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">
<rect width=\"100%\" height=\"100%\" fill=\"white\"/>
'''
            # Siyah pikselleri dikdörtgen olarak ekle
            for y in range(height):
                for x in range(width):
                    if pixels[y * width + x] == 0:  # Siyah piksel
                        svg_content += f'<rect x=\"{x}\" y=\"{y}\" width=\"1\" height=\"1\" fill=\"black\"/>
'
            
            svg_content += '</svg>'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            return True
            
        except Exception as e:
            print(f\"SVG kayıt hatası: {e}\")
            return False


# =============================================================================
# BÖLÜM 5: ÖZEL WİDGET SINIFLARI
# Bu bölümde uygulamaya özel widget'lar tanımlanır
# =============================================================================

class ImagePanel(QLabel):
    \"\"\"
    Görüntü gösterim paneli - 3D çerçeveli
    \"\"\"
    
    def __init__(self, title=\"Image\"):
        \"\"\"
        Panel başlatıcı
        
        Parametreler:
            title: Panel başlığı
        \"\"\"
        super().__init__()
        self.title = title
        self.current_image = None
        
        # Panel stilini ayarla
        self.setStyleSheet(f\"\"\"
            QLabel {{
                background-color: {COLORS['bg_medium']};
                border: 3px solid {COLORS['border']};
                border-radius: 10px;
                padding: 5px;
            }}
        \"\"\")
        
        # Minimum boyut
        self.setMinimumSize(250, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setText(f\"[{title}]
No Image\")
        
        # Boyut politikası
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_image(self, pil_image):
        \"\"\"
        PIL görüntüsünü panele yükle
        
        Parametreler:
            pil_image: PIL Image nesnesi
        \"\"\"
        if pil_image is None:
            self.setText(f\"[{self.title}]
No Image\")
            self.current_image = None
            return
        
        self.current_image = pil_image
        
        # PIL'den QPixmap'e dönüştür
        if pil_image.mode == 'RGBA':
            data = pil_image.tobytes('raw', 'RGBA')
            qimage = QImage(data, pil_image.size[0], pil_image.size[1], 
                          QImage.Format_RGBA8888)
        else:
            rgb_image = pil_image.convert('RGB')
            data = rgb_image.tobytes('raw', 'RGB')
            qimage = QImage(data, rgb_image.size[0], rgb_image.size[1],
                          QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qimage)
        
        # Panel boyutuna sığdır
        scaled_pixmap = pixmap.scaled(
            self.size() - QSize(20, 20),  # Kenar boşlukları için
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event):
        \"\"\"Yeniden boyutlandırma olayını işle\"\"\"
        super().resizeEvent(event)
        if self.current_image:
            self.set_image(self.current_image)


class MaterialButton(QPushButton):
    \"\"\"
    Materyal seçim butonu - 3D görünümlü
    \"\"\"
    
    def __init__(self, material_type, parent=None):
        \"\"\"
        Buton başlatıcı
        
        Parametreler:
            material_type: Materyal türü ('wood', 'metal', 'leather', 'stone')
            parent: Üst widget
        \"\"\"
        super().__init__(parent)
        self.material_type = material_type
        self.material_info = MATERIAL_COLORS[material_type]
        
        # Buton metnini ayarla
        self.setText(self.material_info['name'])
        
        # Özel stil uygula
        self.setStyleSheet(f\"\"\"
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.material_info['secondary']},
                    stop:0.5 {self.material_info['primary']},
                    stop:1 {self._darken_color(self.material_info['primary'])});
                border: 3px solid {self._darken_color(self.material_info['primary'])};
                border-radius: 10px;
                padding: 15px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
                min-height: 60px;
                text-shadow: 1px 1px 2px black;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._lighten_color(self.material_info['secondary'])},
                    stop:0.5 {self.material_info['secondary']},
                    stop:1 {self.material_info['primary']});
                border-color: {COLORS['accent']};
            }}
            QPushButton:pressed {{
                padding-top: 17px;
                padding-bottom: 13px;
            }}
        \"\"\")
        
        # Boyut ayarı
        self.setMinimumSize(100, 70)
    
    def _darken_color(self, hex_color):
        \"\"\"Rengi koyulaştır\"\"\"
        color = QColor(hex_color)
        return color.darker(130).name()
    
    def _lighten_color(self, hex_color):
        \"\"\"Rengi açıklaştır\"\"\"
        color = QColor(hex_color)
        return color.lighter(130).name()


class StatsPanel(QGroupBox):
    \"\"\"
    Görüntü istatistikleri paneli
    \"\"\"
    
    def __init__(self, title=\"Image Statistics\"):
        \"\"\"Panel başlatıcı\"\"\"
        super().__init__(title)
        
        # Layout oluştur
        layout = QGridLayout()
        layout.setSpacing(5)
        
        # İstatistik etiketleri
        self.labels = {}
        stats_items = [
            ('dimensions', 'Dimensions:'),
            ('mode', 'Color Mode:'),
            ('channels', 'Channels:'),
            ('dpi', 'DPI:'),
            ('min_max', 'Min/Max Pixel:'),
            ('mean', 'Mean Pixel:'),
            ('std', 'Std Dev:'),
        ]
        
        for i, (key, text) in enumerate(stats_items):
            label = QLabel(text)
            label.setStyleSheet(f\"color: {COLORS['text_secondary']}; font-weight: bold;\")
            value = QLabel(\"-\")
            value.setStyleSheet(f\"color: {COLORS['success']};\")
            
            layout.addWidget(label, i, 0)
            layout.addWidget(value, i, 1)
            self.labels[key] = value
        
        self.setLayout(layout)
    
    def update_stats(self, stats):
        \"\"\"
        İstatistikleri güncelle
        
        Parametreler:
            stats: İstatistik sözlüğü
        \"\"\"
        if stats is None:
            for label in self.labels.values():
                label.setText(\"-\")
            return
        
        self.labels['dimensions'].setText(f\"{stats['width']} x {stats['height']} px\")
        self.labels['mode'].setText(stats['mode'])
        self.labels['channels'].setText(str(stats['channels']))
        self.labels['dpi'].setText(f\"{stats['dpi'][0]} x {stats['dpi'][1]}\")
        self.labels['min_max'].setText(f\"{stats['min_pixel']} / {stats['max_pixel']}\")
        self.labels['mean'].setText(str(stats['mean_pixel']))
        self.labels['std'].setText(str(stats['std_pixel']))


# =============================================================================
# BÖLÜM 6: ANA PENCERE SINIFI
# Bu bölümde uygulamanın ana penceresi ve tüm bileşenleri tanımlanır
# =============================================================================

class MainWindow(QMainWindow):
    \"\"\"
    Ana uygulama penceresi
    \"\"\"
    
    def __init__(self):
        \"\"\"Ana pencere başlatıcı\"\"\"
        super().__init__()
        
        # Görüntü işlemci oluştur
        self.processor = ImageProcessor()
        
        # Pencere ayarları
        self.setWindowTitle(\"Image Processing Studio - Professional Edition\")
        self.setMinimumSize(1400, 900)
        
        # Ana stil uygula
        self.setStyleSheet(MAIN_STYLE)
        
        # Arayüzü oluştur
        self.setup_ui()
        
        # Pencereyi ortala
        self.center_window()
    
    def center_window(self):
        \"\"\"Pencereyi ekranın ortasına konumlandır\"\"\"
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def setup_ui(self):
        \"\"\"Ana arayüzü oluştur\"\"\"
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout (yatay)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Sol panel (kontroller)
        left_panel = self.create_left_panel()
        left_panel.setMaximumWidth(350)
        
        # Orta panel (4 görüntü penceresi)
        center_panel = self.create_center_panel()
        
        # Sağ panel (istatistikler ve materyal)
        right_panel = self.create_right_panel()
        right_panel.setMaximumWidth(300)
        
        # Layout'a ekle
        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel, stretch=1)
        main_layout.addWidget(right_panel)
    
    def create_left_panel(self):
        \"\"\"Sol kontrol panelini oluştur\"\"\"
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # === GÖRÜNTÜ YÜKLEME GRUBU ===
        load_group = QGroupBox(\"📁 Image Loading\")
        load_layout = QVBoxLayout()
        
        # Yükle butonu
        self.load_btn = QPushButton(\"Load Image\")
        self.load_btn.setMinimumHeight(50)
        self.load_btn.clicked.connect(self.load_image)
        load_layout.addWidget(self.load_btn)
        
        # Dosya adı etiketi
        self.file_label = QLabel(\"No file loaded\")
        self.file_label.setStyleSheet(f\"color: {COLORS['text_secondary']}; font-style: italic;\")
        load_layout.addWidget(self.file_label)
        
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)
        
        # === BOYUT AYARLARI GRUBU ===
        size_group = QGroupBox(\"📐 Size Settings\")
        size_layout = QGridLayout()
        
        # Genişlik
        size_layout.addWidget(QLabel(\"Width (px):\"), 0, 0)
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 10000)
        self.width_input.setValue(0)
        self.width_input.setSpecialValueText(\"Auto\")
        self.width_input.valueChanged.connect(self.on_settings_changed)
        size_layout.addWidget(self.width_input, 0, 1)
        
        # Yükseklik
        size_layout.addWidget(QLabel(\"Height (px):\"), 1, 0)
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 10000)
        self.height_input.setValue(0)
        self.height_input.setSpecialValueText(\"Auto\")
        self.height_input.valueChanged.connect(self.on_settings_changed)
        size_layout.addWidget(self.height_input, 1, 1)
        
        # DPI
        size_layout.addWidget(QLabel(\"DPI:\"), 2, 0)
        self.dpi_input = QSpinBox()
        self.dpi_input.setRange(72, 1200)
        self.dpi_input.setValue(300)
        self.dpi_input.valueChanged.connect(self.on_settings_changed)
        size_layout.addWidget(self.dpi_input, 2, 1)
        
        # Işın çapı
        size_layout.addWidget(QLabel(\"Beam Diameter:\"), 3, 0)
        self.beam_combo = QComboBox()
        beam_values = [0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35, 0.40]
        for val in beam_values:
            self.beam_combo.addItem(f\"{val:.2f} mm\", val)
        self.beam_combo.setCurrentIndex(4)  # 0.25 varsayılan
        self.beam_combo.currentIndexChanged.connect(self.on_settings_changed)
        size_layout.addWidget(self.beam_combo, 3, 1)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # === İŞLEM AYARLARI GRUBU ===
        process_group = QGroupBox(\"⚙️ Processing Settings\")
        process_layout = QVBoxLayout()
        
        # Kontrast slider
        process_layout.addWidget(QLabel(\"Contrast:\"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(50, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.on_slider_changed)
        self.contrast_label = QLabel(\"1.00\")
        contrast_row = QHBoxLayout()
        contrast_row.addWidget(self.contrast_slider)
        contrast_row.addWidget(self.contrast_label)
        process_layout.addLayout(contrast_row)
        
        # Parlaklık slider
        process_layout.addWidget(QLabel(\"Brightness:\"))
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(50, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.on_slider_changed)
        self.brightness_label = QLabel(\"1.00\")
        brightness_row = QHBoxLayout()
        brightness_row.addWidget(self.brightness_slider)
        brightness_row.addWidget(self.brightness_label)
        process_layout.addLayout(brightness_row)
        
        # Arkaplan temizleme slider
        process_layout.addWidget(QLabel(\"Background Removal:\"))
        self.bg_slider = QSlider(Qt.Horizontal)
        self.bg_slider.setRange(0, 100)
        self.bg_slider.setValue(0)
        self.bg_slider.valueChanged.connect(self.on_slider_changed)
        self.bg_label = QLabel(\"0%\")
        bg_row = QHBoxLayout()
        bg_row.addWidget(self.bg_slider)
        bg_row.addWidget(self.bg_label)
        process_layout.addLayout(bg_row)
        
        # Yüz algılama slider
        process_layout.addWidget(QLabel(\"Face Detection/Enhancement:\"))
        self.face_slider = QSlider(Qt.Horizontal)
        self.face_slider.setRange(0, 100)
        self.face_slider.setValue(0)
        self.face_slider.valueChanged.connect(self.on_slider_changed)
        self.face_label = QLabel(\"0%\")
        face_row = QHBoxLayout()
        face_row.addWidget(self.face_slider)
        face_row.addWidget(self.face_label)
        process_layout.addLayout(face_row)
        
        # Kalem sertliği slider
        process_layout.addWidget(QLabel(\"Pencil Hardness:\"))
        self.pencil_slider = QSlider(Qt.Horizontal)
        self.pencil_slider.setRange(0, 6)
        self.pencil_slider.setValue(2)
        self.pencil_slider.valueChanged.connect(self.on_slider_changed)
        self.pencil_label = QLabel(\"2H\")
        pencil_row = QHBoxLayout()
        pencil_row.addWidget(self.pencil_slider)
        pencil_row.addWidget(self.pencil_label)
        process_layout.addLayout(pencil_row)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        # === RENK AYARLARI ===
        color_group = QGroupBox(\"🎨 Color Settings\")
        color_layout = QVBoxLayout()
        
        # Invert checkbox
        self.invert_checkbox = QCheckBox(\"Invert Colors\")
        self.invert_checkbox.stateChanged.connect(self.on_settings_changed)
        color_layout.addWidget(self.invert_checkbox)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # İşle butonu
        self.process_btn = QPushButton(\"🔄 Process Image\")
        self.process_btn.setMinimumHeight(50)
        self.process_btn.setStyleSheet(f\"\"\"
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['success']},
                    stop:1 #3ba882);
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5eecc3,
                    stop:1 {COLORS['success']});
            }}
        \"\"\")
        self.process_btn.clicked.connect(self.process_image)
        layout.addWidget(self.process_btn)
        
        # Boşluk ekle
        layout.addStretch()
        
        return panel
    
    def create_center_panel(self):
        \"\"\"Orta görüntü panelini oluştur (4 pencere)\"\"\"
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setSpacing(10)
        
        # 4 görüntü paneli oluştur
        self.image_panels = {}
        
        # 1. Grayscale (Sol üst)
        self.image_panels['grayscale'] = ImagePanel(\"Grayscale\")
        layout.addWidget(self.image_panels['grayscale'], 0, 0)
        
        # 2. Dither (Sağ üst)
        self.image_panels['dither'] = ImagePanel(\"Dither\")
        layout.addWidget(self.image_panels['dither'], 0, 1)
        
        # 3. Sketch (Sol alt)
        self.image_panels['sketch'] = ImagePanel(\"Pencil Sketch\")
        layout.addWidget(self.image_panels['sketch'], 1, 0)
        
        # 4. Line Art (Sağ alt)
        self.image_panels['line_art'] = ImagePanel(\"Line Art\")
        layout.addWidget(self.image_panels['line_art'], 1, 1)
        
        return panel
    
    def create_right_panel(self):
        \"\"\"Sağ paneli oluştur (istatistikler ve materyal)\"\"\"
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # === İSTATİSTİK PANELİ ===
        self.stats_panel = StatsPanel(\"📊 Image Statistics\")
        layout.addWidget(self.stats_panel)
        
        # === MATERYAL ÖN AYARLARI ===
        material_group = QGroupBox(\"🎯 Material Presets\")
        material_layout = QGridLayout()
        material_layout.setSpacing(10)
        
        # 4 materyal butonu
        self.material_buttons = {}
        materials = ['wood', 'metal', 'leather', 'stone']
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for material, pos in zip(materials, positions):
            btn = MaterialButton(material)
            btn.clicked.connect(lambda checked, m=material: self.apply_material_preset(m))
            self.material_buttons[material] = btn
            material_layout.addWidget(btn, pos[0], pos[1])
        
        material_group.setLayout(material_layout)
        layout.addWidget(material_group)
        
        # === KAYIT BUTONLARI ===
        save_group = QGroupBox(\"💾 Save Images\")
        save_layout = QGridLayout()
        
        # Her panel için kayıt butonu
        save_buttons = [
            ('grayscale', 'Save Grayscale'),
            ('dither', 'Save Dither'),
            ('sketch', 'Save Sketch'),
            ('line_art', 'Save Line Art'),
        ]
        
        self.save_buttons = {}
        for i, (key, text) in enumerate(save_buttons):
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, k=key: self.save_image(k))
            self.save_buttons[key] = btn
            save_layout.addWidget(btn, i // 2, i % 2)
        
        # Tümünü kaydet butonu
        save_all_btn = QPushButton(\"💾 Save All\")
        save_all_btn.setStyleSheet(f\"\"\"
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['warning']},
                    stop:1 #cc9900);
            }}
        \"\"\")
        save_all_btn.clicked.connect(self.save_all_images)
        save_layout.addWidget(save_all_btn, 2, 0, 1, 2)
        
        save_group.setLayout(save_layout)
        layout.addWidget(save_group)
        
        # Format seçimi
        format_group = QGroupBox(\"📄 Export Format\")
        format_layout = QHBoxLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItem(\"PNG\", \"PNG\")
        self.format_combo.addItem(\"SVG (Vector)\", \"SVG\")
        format_layout.addWidget(self.format_combo)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Boşluk ekle
        layout.addStretch()
        
        return panel
    
    # =========================================================================
    # BÖLÜM 7: OLAY İŞLEYİCİ FONKSİYONLAR
    # Bu bölümde kullanıcı etkileşimlerine yanıt veren fonksiyonlar tanımlanır
    # =========================================================================
    
    def load_image(self):
        \"\"\"Görüntü yükle diyaloğunu aç\"\"\"
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            \"Select Image\",  # Diyalog başlığı
            \"\",  # Başlangıç dizini
            \"Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.gif);;All Files (*)\"
        )
        
        if filepath:
            # Görüntüyü yükle
            if self.processor.load_image(filepath):
                # Dosya adını göster
                filename = os.path.basename(filepath)
                self.file_label.setText(f\"📎 {filename}\")
                
                # Boyut bilgilerini güncelle
                img = self.processor.original_image
                self.width_input.blockSignals(True)
                self.height_input.blockSignals(True)
                self.width_input.setValue(img.size[0])
                self.height_input.setValue(img.size[1])
                self.width_input.blockSignals(False)
                self.height_input.blockSignals(False)
                
                # İstatistikleri güncelle
                stats = self.processor.get_image_stats(img)
                self.stats_panel.update_stats(stats)
                
                # Otomatik işle
                self.process_image()
            else:
                QMessageBox.warning(self, \"Error\", \"Failed to load image!\")
    
    def on_slider_changed(self, value):
        \"\"\"Slider değeri değiştiğinde\"\"\"
        # Etiketleri güncelle
        self.contrast_label.setText(f\"{self.contrast_slider.value() / 100:.2f}\")
        self.brightness_label.setText(f\"{self.brightness_slider.value() / 100:.2f}\")
        self.bg_label.setText(f\"{self.bg_slider.value()}%\")
        self.face_label.setText(f\"{self.face_slider.value()}%\")
        
        # Kalem sertliği etiketi
        hardness_labels = ['H', '2H', '3H', '4H', '5H', '6H', '7H']
        self.pencil_label.setText(hardness_labels[self.pencil_slider.value()])
    
    def on_settings_changed(self):
        \"\"\"Ayarlar değiştiğinde (otomatik işleme için)\"\"\"
        pass  # Manuel işleme tercih edildi
    
    def process_image(self):
        \"\"\"Görüntüyü işle ve panelleri güncelle\"\"\"
        if self.processor.original_image is None:
            QMessageBox.warning(self, \"Warning\", \"Please load an image first!\")
            return
        
        # Parametreleri güncelle
        self.processor.contrast = self.contrast_slider.value() / 100
        self.processor.brightness = self.brightness_slider.value() / 100
        self.processor.bg_removal = self.bg_slider.value()
        self.processor.face_detection = self.face_slider.value()
        self.processor.pencil_hardness = self.pencil_slider.value()
        self.processor.invert_colors = self.invert_checkbox.isChecked()
        self.processor.beam_diameter = self.beam_combo.currentData()
        self.processor.target_dpi = self.dpi_input.value()
        
        # Boyutlandırma
        width = self.width_input.value() if self.width_input.value() > 0 else None
        height = self.height_input.value() if self.height_input.value() > 0 else None
        
        if width or height:
            self.processor.original_image = self.processor.resize_image(
                self.processor.original_image, width, height
            )
        
        # İşle
        results = self.processor.process_all()
        
        if results:
            # Panelleri güncelle
            for key, panel in self.image_panels.items():
                if key in results:
                    panel.set_image(results[key])
            
            # İstatistikleri güncelle (grayscale için)
            stats = self.processor.get_image_stats(results['grayscale'])
            self.stats_panel.update_stats(stats)
    
    def apply_material_preset(self, material):
        \"\"\"
        Materyal ön ayarını uygula
        
        Parametreler:
            material: Materyal türü ('wood', 'metal', 'leather', 'stone')
        \"\"\"
        # Materyal bazlı varsayılan değerler
        presets = {
            'wood': {  # Ahşap - Yumuşak, doğal görünüm
                'contrast': 110,
                'brightness': 105,
                'bg_removal': 0,
                'face_detection': 0,
                'pencil_hardness': 2,
                'beam': 4,  # 0.25
            },
            'metal': {  # Metal - Yüksek kontrast, keskin
                'contrast': 140,
                'brightness': 95,
                'bg_removal': 50,
                'face_detection': 0,
                'pencil_hardness': 5,
                'beam': 2,  # 0.20
            },
            'leather': {  # Deri - Orta kontrast, sıcak
                'contrast': 120,
                'brightness': 100,
                'bg_removal': 30,
                'face_detection': 20,
                'pencil_hardness': 3,
                'beam': 5,  # 0.28
            },
            'stone': {  # Taş - Düşük kontrast, mat
                'contrast': 90,
                'brightness': 110,
                'bg_removal': 70,
                'face_detection': 0,
                'pencil_hardness': 4,
                'beam': 6,  # 0.30
            },
        }
        
        preset = presets.get(material, presets['wood'])
        
        # Değerleri uygula (sinyalleri blokla)
        self.contrast_slider.blockSignals(True)
        self.brightness_slider.blockSignals(True)
        self.bg_slider.blockSignals(True)
        self.face_slider.blockSignals(True)
        self.pencil_slider.blockSignals(True)
        self.beam_combo.blockSignals(True)
        
        self.contrast_slider.setValue(preset['contrast'])
        self.brightness_slider.setValue(preset['brightness'])
        self.bg_slider.setValue(preset['bg_removal'])
        self.face_slider.setValue(preset['face_detection'])
        self.pencil_slider.setValue(preset['pencil_hardness'])
        self.beam_combo.setCurrentIndex(preset['beam'])
        
        self.contrast_slider.blockSignals(False)
        self.brightness_slider.blockSignals(False)
        self.bg_slider.blockSignals(False)
        self.face_slider.blockSignals(False)
        self.pencil_slider.blockSignals(False)
        self.beam_combo.blockSignals(False)
        
        # Etiketleri güncelle
        self.on_slider_changed(0)
        
        # Görüntüyü işle
        self.process_image()
        
        # Bilgi mesajı
        QMessageBox.information(
            self, 
            \"Preset Applied\", 
            f\"{MATERIAL_COLORS[material]['name']} preset has been applied!\"
        )
    
    def save_image(self, image_type):
        \"\"\"
        Tek bir görüntüyü kaydet
        
        Parametreler:
            image_type: Görüntü türü ('grayscale', 'dither', 'sketch', 'line_art')
        \"\"\"
        if image_type not in self.processor.processed_images:
            QMessageBox.warning(self, \"Warning\", \"Please process an image first!\")
            return
        
        # Format seç
        format_type = self.format_combo.currentData()
        ext = format_type.lower()
        
        # Kayıt diyaloğu
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            f\"Save {image_type.replace('_', ' ').title()}\",
            f\"{image_type}.{ext}\",
            f\"{format_type} Files (*.{ext});;All Files (*)\"
        )
        
        if filepath:
            image = self.processor.processed_images[image_type]
            if self.processor.save_image(image, filepath, format_type):
                QMessageBox.information(self, \"Success\", f\"Image saved to:
{filepath}\")
            else:
                QMessageBox.warning(self, \"Error\", \"Failed to save image!\")
    
    def save_all_images(self):
        \"\"\"Tüm görüntüleri kaydet\"\"\"
        if not self.processor.processed_images:
            QMessageBox.warning(self, \"Warning\", \"Please process an image first!\")
            return
        
        # Klasör seç
        folder = QFileDialog.getExistingDirectory(self, \"Select Save Folder\")
        
        if folder:
            format_type = self.format_combo.currentData()
            ext = format_type.lower()
            
            success_count = 0
            for image_type, image in self.processor.processed_images.items():
                filepath = os.path.join(folder, f\"{image_type}.{ext}\")
                if self.processor.save_image(image, filepath, format_type):
                    success_count += 1
            
            QMessageBox.information(
                self, 
                \"Complete\", 
                f\"Saved {success_count}/4 images to:
{folder}\"
            )


# =============================================================================
# BÖLÜM 8: UYGULAMA BAŞLATICI
# Bu bölümde uygulama başlatma kodu bulunur
# =============================================================================

def main():
    \"\"\"Ana fonksiyon - uygulamayı başlatır\"\"\"
    # Yüksek DPI desteği
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Uygulama oluştur
    app = QApplication(sys.argv)
    
    # Font ayarı
    font = QFont(\"Segoe UI\", 10)
    app.setFont(font)
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    # Uygulama döngüsünü başlat
    sys.exit(app.exec_())


# Uygulama doğrudan çalıştırıldığında
if __name__ == \"__main__\":
    main()
"
