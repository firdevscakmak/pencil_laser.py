import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageFilter, ImageDraw,ImageFont,ImagePalette,ImageMath
import numpy as np
import cv2
import os


class StudioX_FreeEditor(tk.Toplevel):
    def __init__(self, parent, pil_image, callback):
        super().__init__(parent)
        self.title("STUDIO X – Free Crop Editor")
        self.geometry("1200x750")
        self.configure(bg="#000000")

        self.callback = callback

        # -------- IMAGE STATE (EDITÖRE ÖZEL) --------
        self.original = pil_image.convert("RGBA")
        self.preview = self.original.copy()
        self.display_img = None

        # -------- ADJUSTMENTS --------
        self.bright = tk.DoubleVar(value=1.0)
        self.contrast = tk.DoubleVar(value=1.0)
        self.sat = tk.DoubleVar(value=1.0)
        self.rotation = tk.DoubleVar(value=0.0)

        # -------- CROP STATE --------
        self.start = None
        self.crop_box = None  # x1,y1,x2,y2 (label coords)

        self.build_layout()
        self.build_controls()
        self.update_preview()

    # -------------------------------------------------
    def build_layout(self):
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.left = tk.Frame(self, width=240, bg="#151515")
        self.left.grid(row=1, column=0, sticky="ns")
        self.left.grid_propagate(False)

        self.center = tk.Frame(self, bg="#222222")
        self.center.grid(row=1, column=1, sticky="nsew")

    # -------------------------------------------------
    def build_controls(self):
        self.make_slider("Parlaklık", self.bright, 0.2, 2.5)
        self.make_slider("Kontrast", self.contrast, 0.2, 2.5)
        self.make_slider("Doygunluk", self.sat, 0.0, 2.5)
        self.make_slider("Döndür", self.rotation, -180, 180)

        ttk.Button(
            self.left,
            text="✂ KIRP & YÜKLE",
            command=self.finalize
        ).pack(fill="x", padx=10, pady=20)

    def make_slider(self, text, var, f, t):
        tk.Label(
            self.left,
            text=text,
            fg="#39ff14",
            bg="#151515"
        ).pack(anchor="w", padx=10, pady=(10, 0))

        ttk.Scale(
            self.left,
            from_=f,
            to=t,
            variable=var,
            command=lambda e: self.update_preview()
        ).pack(fill="x", padx=10)

    # -------------------------------------------------
    def update_preview(self):
        img = self.original.copy()
        img = ImageEnhance.Brightness(img).enhance(self.bright.get())
        img = ImageEnhance.Contrast(img).enhance(self.contrast.get())
        img = ImageEnhance.Color(img).enhance(self.sat.get())
        img = img.rotate(self.rotation.get(), expand=True)

        self.preview = img
        self.show_image()

    def show_image(self):
        img = self.preview.copy()
        img.thumbnail((900, 650))
        self.display_img = img

        self.tk_img = ImageTk.PhotoImage(img)

        if not hasattr(self, "img_label"):
            self.img_label = tk.Label(self.center, image=self.tk_img, bg="#222222")
            self.img_label.pack(expand=True)

            self.img_label.bind("<ButtonPress-1>", self.start_crop)
            self.img_label.bind("<B1-Motion>", self.drag_crop)
        else:
            self.img_label.configure(image=self.tk_img)

        self.img_label.image = self.tk_img

    # -------------------------------------------------
    def start_crop(self, e):
        self.start = (e.x, e.y)

    def drag_crop(self, e):
        if not self.start:
            return
        self.crop_box = (self.start[0], self.start[1], e.x, e.y)

    # -------------------------------------------------
    def finalize(self):
        if not self.crop_box:
            return

        # 1️⃣ AYARLARI KALICI UYGULA
        base = self.original.copy()
        base = ImageEnhance.Brightness(base).enhance(self.bright.get())
        base = ImageEnhance.Contrast(base).enhance(self.contrast.get())
        base = ImageEnhance.Color(base).enhance(self.sat.get())
        base = base.rotate(self.rotation.get(), expand=True)

        # 2️⃣ SCALE (label → gerçek resim)
        sx = base.width / self.display_img.width
        sy = base.height / self.display_img.height

        x1, y1, x2, y2 = self.crop_box
        x1, x2 = sorted([int(x1 * sx), int(x2 * sx)])
        y1, y2 = sorted([int(y1 * sy), int(y2 * sy)])

        # 3️⃣ SAYDAM ALPHA MASKE
        cv_img = cv2.cvtColor(np.array(base), cv2.COLOR_RGBA2BGRA)
        alpha = np.zeros((base.height, base.width), dtype=np.uint8)
        alpha[y1:y2, x1:x2] = 255
        cv_img[:, :, 3] = alpha

        result = Image.fromarray(
            cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)
        )

        # 4️⃣ ANA PANELE GÖNDER
        self.callback(result)
        self.destroy()


class LazerMasterCyber:

    def receive_from_editor(self, cv_img):
        self.orig_img = cv_img  # RGBA, kırpılmış, saydam
        self.orig_img = Image.open(path).convert("RGBA")
        self.process_image()

    def __init__(self, root):
        self.orig_img = None
        self.ratio = 1.0
        self.res = {}
        self.root = root
        self.root.title("emergent1 LASER MASTER ULTIMATE - CYBER TECH v3.7 - LINE ART")
        self.root.geometry("1600x950")
        self.root.configure(bg="#000000")
        self.orig_img = None
        self.ratio = 1.0
        self.res = {}
       
        # Cascade Dosyası Kontrolü
        cv_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        local_path = "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(local_path if os.path.exists(local_path) else cv_path)

        # ================= TOP PANEL (HEADER) =================
        header_f = tk.Frame(root, bg="#1a1a1a", height=70, highlightthickness=1, highlightbackground="#39ff14")
        header_f.pack(side="top", fill="x", padx=10, pady=(5, 0))
        header_f.pack_propagate(False)

        main_title = tk.Label(header_f, text="emergent1 ULTIMATE - LINE ART ENGINE V3.7", 
                              bg="#1a1a1a", fg="#39ff14", font=('Courier New', 22, 'bold'))
        main_title.pack(expand=True)

        # ================= LEFT PANEL (CONTROLS) =================
        ctrl = tk.Frame(root, width=220, padx=10, pady=10, bg="#050505", 
                        highlightthickness=1, highlightbackground="#39ff14")
        ctrl.pack(side="left", fill="y", padx=(10, 0), pady=10)
        ctrl.pack_propagate(False)

        # 1. Buton için dış çerçeve oluşturuyoruz
        load_frame = tk.Frame(ctrl, bg="#050505", bd=1, 
                            highlightthickness=1, highlightbackground="#39ff14") # Yeşil neon çerçeve
        load_frame.pack(fill="x", pady=(0, 10))

        # 2. Butonu bu çerçevenin (load_frame) içine yerleştiriyoruz
        self.load_btn = tk.Button(load_frame, text="📂 LOAD IMAGE", command=self.load_image, 
                                bg="#1a1a1a", fg="#39ff14", font=('Courier New', 11, 'bold'),
                                relief="flat", 
                                activebackground="#39ff14", # Üzerine gelince yanma efekti
                                activeforeground="#000000",
                                cursor="hand2", 
                                pady=8, 
                                anchor="center", # Metni ortaladık, daha şık durur
                                padx=15)
  
        self.load_btn.pack(fill="x")# Butonu çerçevenin içine tam yayıyoruz

        # ---------- MATERIAL BUTTONS ----------
        tk.Label(ctrl, text="[ MATERIAL ENGINE ]", bg="#050505", fg="#00f2ff", font=('Arial', 10, 'bold')).pack(anchor="w")
        mat_frame = tk.Frame(ctrl, bg="#050505")
        mat_frame.pack(fill="x", pady=5)
        mats = [("WOOD", "#8B4513", "WOOD"), ("METAL", "#708090", "METAL"), 
                ("STONE", "#4F4F4F", "STONE"), ("DEFAULT", "#5C4033", "DEFAULT")]
        self.material_var = tk.StringVar(value="WOOD")
        self.mat_btns = {}
        for i, (name, color, val) in enumerate(mats):
            texture_img = self.create_texture_image(name, color, "#1c1c1c")
            btn = tk.Button(mat_frame, text=name, image=texture_img, compound="center",
                           command=lambda v=val: self.apply_preset(v),
                           fg="#ffffff", font=('Courier New', 8, 'bold'),
                           relief="flat", highlightthickness=1, highlightbackground="#00f2ff",
                           activebackground="#ffffff", cursor="hand2", pady=5)
            btn.texture_img = texture_img 
            btn.grid(row=i//2, column=i%2, sticky="nsew", padx=1, pady=1)
            self.mat_btns[name] = btn
        mat_frame.grid_columnconfigure((0, 1), weight=1)

       
        size_dpi_container = tk.Frame(ctrl, bg="#131212")
        size_dpi_container.pack(fill="x", pady=5)

        # ---------- SIZE KUTUSU (SOL) ----------
       # 1. Önce kapsayıcıyı (container) oluştur
        size_dpi_container = tk.Frame(ctrl, bg="#050505")
        size_dpi_container.pack(fill="x", pady=5)

        # 2. SIZE kutusunu (frame) oluştur
       # ---------- SIZE KUTUSU (SOL) ----------
        size_box = tk.Frame(size_dpi_container, bg="#050505", bd=1, highlightthickness=1, highlightbackground="#850404")
        size_box.pack(side="left", fill="both", expand=True, padx=(0, 2))

        tk.Label(size_box, text="SIZE (mm)", bg="#050505", fg="#00f2ff", font=('Arial', 9, 'bold')).pack(pady=(2,0))

        size_inputs = tk.Frame(size_box, bg="#050505")
        size_inputs.pack(pady=2)

        # 1. Değişkenleri tanımla (Sadece bir kez!)
        self.w_mm = tk.StringVar(value="100")
        self.h_mm = tk.StringVar()

        # 2. Doğrulama kuralını kaydet
        vcmd = (self.root.register(self.validate_numeric), '%P')

        # 3. GENİŞLİK (W) - Tek Seferde Doğru Tanımlama
        tk.Entry(size_inputs, textvariable=self.w_mm, bg="#000000", fg="#00f2ff", width=5, 
                font=('Arial', 8), justify="center", insertbackground="white", 
                validate="key", validatecommand=vcmd).grid(row=0, column=0)

        tk.Label(size_inputs, text="x", bg="#050505", fg="#00f2ff", font=('Arial', 9)).grid(row=0, column=1, padx=1)

        # 4. YÜKSEKLİK (H) - Tek Seferde Doğru Tanımlama
        tk.Entry(size_inputs, textvariable=self.h_mm, bg="#000000", fg="#00f2ff", width=5, 
                font=('Arial', 8), justify="center", insertbackground="white",
                validate="key", validatecommand=vcmd).grid(row=0, column=2)

        # ---------- DPI KUTUSU (SAĞ) ---------- (Zaten doğru çalışıyor demiştin)
        dpi_box = tk.Frame(size_dpi_container, bg="#050505", bd=1, highlightthickness=1, highlightbackground="#850404")
        dpi_box.pack(side="left", fill="both", expand=True, padx=(2, 0))

        tk.Label(dpi_box, text=" DPI ", bg="#050505", fg="#39ff14", font=('Arial', 8, 'bold')).pack(pady=(2,0))

        self.dpi_var = tk.StringVar(value="250")
        tk.Entry(dpi_box, textvariable=self.dpi_var, bg="#000000", fg="#39ff14", width=8, 
                font=('Arial', 8), justify="center", insertbackground="white",
                validate="key", validatecommand=vcmd).pack(pady=2)
                # Takipçiler (Trace) aynı kalıyor
        self.w_mm.trace_add("write", self.sync_h); self.h_mm.trace_add("write", self.sync_w)
        self.dpi_var.trace_add("write", lambda *_: self.process())

        # ---------- SLIDERS ----------
        self.neg_var = tk.BooleanVar(value=False)
        tk.Checkbutton(ctrl, text="INVERT COLORS", variable=self.neg_var, bg="#050505", fg="#ff0055", 
                       selectcolor="#000000", activebackground="#050505", font=('Arial', 9, 'bold'),
                       command=self.process).pack(anchor="w", pady=2)

        self.bright_s = self.make_slider(ctrl, "BRIGHTNESS", 0.1, 4.0, 1.2)
        self.contrast_s = self.make_slider(ctrl, "CONTRAST", 0.1, 2.0, 0.95)
        self.sketch_s = self.make_slider(ctrl, "SKETCH DEPTH", 3, 35, 25, 1)
        self.bg_strength = self.make_slider(ctrl, "BG CLEANER", 0, 100, 51, 1)
        self.face_blur_s = self.make_slider(ctrl, "FACE SMOOTH", 1, 50, 5, 1)

        # ================= EXPORT PANEL (RIGHT) =================
        export_f = tk.Frame(root, width=220, padx=10, pady=10, bg="#050505", 
                            highlightthickness=1, highlightbackground="#39ff14")
        export_f.pack(side="right", fill="y", padx=(0, 10), pady=10)
        export_f.pack_propagate(False)

        tk.Label(export_f, text="EXPORT PANEL", bg="#050505", fg="#39ff14", font=('Courier New', 13, 'bold')).pack(pady=(0, 10))
        # export_f içine butonlu çerçeveleri ekliyoruz
        self.neon_frame(export_f, "💾 SAVE GRAY", lambda: self.save("gray"), "#00f2ff", "#1a1a1a").pack(fill="x", pady=5)
        self.neon_frame(export_f, "💾 SAVE DITHER", lambda: self.save("gray_d"), "#00f2ff", "#1a1a1a").pack(fill="x", pady=5)
        self.neon_frame(export_f, "💾 SAVE SKETCH", lambda: self.save("sketch"), "#39ff14", "#1a1a1a").pack(fill="x", pady=5)
        self.neon_frame(export_f, "💾 SAVE LINE ART", lambda: self.save("line_art"), "#39ff14", "#1a1a1a").pack(fill="x", pady=5)

        tk.Label(export_f, text="[ ANALYSIS ]", bg="#050505", fg="#00f2ff", font=('Courier New', 12, 'bold')).pack(anchor="w", pady=(15, 2))
        self.info = tk.Label(export_f, bg="#000000", fg="#00f2ff", font=('Consolas', 11),
                            highlightbackground="#39ff14", highlightthickness=2, height=10, relief="flat", justify="left", anchor="nw")
        self.info.pack(fill="both", expand=True)

        # ================= CENTER PANEL (PREVIEWS) =================
        self.view = tk.Frame(root, bg="#000000")
        self.view.pack(expand=True, fill="both", padx=5, pady=5)
        self.panels = {}
        names = [("gray","GRAYSCALE", "#00f2ff"), 
                 ("gray_d","GRAY DITHER", "#00f2ff"),
                 ("sketch","SKETCH MODE", "#39ff14"), 
                 ("line_art","LINE ART MODE", "#39ff14")
                 ]

        for i,(k,t, color) in enumerate(names):
            f = tk.Frame(self.view, bg="#000000", highlightthickness=1, highlightbackground="#1a1a1a")
            f.grid(row=i//2, column=i%2, sticky="nsew", padx=3, pady=3)
            tk.Label(f, text=t, bg="#000000", fg=color, font=('Courier New', 10, 'bold')).pack()
            lbl = tk.Label(f, bg="#020202")
            lbl.pack(expand=True, fill="both")
            self.panels[k] = lbl
        # BU İKİ SATIRI EKLE:
            lbl.bind("<Enter>", lambda e, key=k: self.set_active_panel(key))
            lbl.bind("<Leave>", lambda e: self.set_active_panel(None))
        self.view.grid_columnconfigure((0,1), weight=1); self.view.grid_rowconfigure((0,1), weight=1)

    def validate_numeric(self, P):
            # P, kutunun o anki halidir
        if P == "": return True # Silmeye izin ver
            # Sadece rakam ve maksimum 3 karakter (999)
        if P.isdigit() and len(P) <= 3:
            return True
        return False

    def create_texture_image(self, name, c1, c2):#materyal butonları için degrade doku oluşturur.
        img = Image.new("RGB", (115, 35), c1); 
        draw = ImageDraw.Draw(img)
        r1, g1, b1 = self.hex_to_rgb(c1); r2, g2, b2 = self.hex_to_rgb(c2)
        for y in range(35):
            r, g, b = int(r1+(r2-r1)*(y/35)), int(g1+(g2-g1)*(y/35)), int(b1+(b2-b1)*(y/35))
            for x in range(115):
                noise = np.random.randint(-15, 15)
                if name == "WOOD" and (x+y*2)%25 < 2: noise = -35
                elif name == "METAL" and y%2 == 0: noise = 8
                elif name == "STONE" and np.random.rand() > 0.92: noise = 40
                draw.point((x,y), fill=(max(0,min(255,r+noise)), max(0,min(255,g+noise)), max(0,min(255,b+noise))))
        return ImageTk.PhotoImage(img)

    def hex_to_rgb(self, hex_color):#hex renk kodunu RGB tuple'a çevirir.
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def btn_neon(self, parent, text, cmd, color, fg):#neon stilde buton oluşturur
        return tk.Button(parent, text=text, command=cmd, bg=fg, fg=color, font=('Courier New', 10, 'bold'), relief="flat",
                    highlightthickness=2,
                    highlightbackground=color, 
                    activebackground=color, cursor="hand2", pady=8, padx=15, anchor="w")
    
    def neon_frame(self, parent, text, cmd, color, bg_color):
        # Dış çerçeve
        frame = tk.Frame(
            parent,
            bg=bg_color,
            highlightthickness=2,
            highlightbackground=color
        )
        # Butonu doğrudan burada oluşturup frame'e bağla
        btn = self.btn_neon(frame, text, cmd, color, bg_color)
        btn.pack(fill="x", padx=2, pady=2)
        
        return frame
 
    def make_slider(self, parent, text, f, t, start, res=0.05):
    # Çerçeveyi daraltmak için pady değerini 1'e düşürdük
        frame = tk.Frame(parent, bg="#050505", bd=1, 
                        highlightthickness=1, highlightbackground="#850404") # Kırmızı neon tonu
        frame.pack(fill="x", pady=5, padx=2) 

        # Yazıyı sola alıp dikey boşluğunu (pady) sıfırladık
        tk.Label(frame, text=text, bg="#050505", fg="#e5efef", 
                font=('Arial', 9, 'bold')).pack(anchor="w", padx=5, pady=(3, 0))

        # Sürgünün kalınlığını (width) ve fontunu küçülttük
        s = tk.Scale(frame, from_=f, to=t, resolution=res, orient="horizontal", 
                    bg="#050505", fg="#39ff14", troughcolor="#111111", 
                    highlightthickness=1, command=lambda *_: self.process(), 
                    font=('Arial', 8), showvalue=True,
                    width=13,         # Sürgü çubuğunun kalınlığı (Standartı 15'tir, 8 yaptık)
                    sliderlength=20) # Kaydıraç parçasının boyu
        
        s.set(start)
        s.pack(fill="x", padx=1, pady=(0, 2))
        
        return s

    def apply_preset(self, mat):#materyal butonlara default ayarları uygulanır.
        self.material_var.set(mat); ps = {"WOOD":(0.9,1.15,35,11,5), 
         "DEFAULT":(1.0,1.0,25,45,5), 
         "METAL":(0.9,1.0,35,76,5), 
         "STONE":(1.3,0.75,35,100,5)}
        b,c,s,bg,d = ps[mat]; 
        self.bright_s.set(b); 
        self.contrast_s.set(c); 
        self.sketch_s.set(s); 
        self.bg_strength.set(bg);
        self.face_blur_s.set(d); 
        self.process()

    def sync_h(self, *_):# w değiştiğinde h yi günceller
        try:
            val_str = self.w_mm.get()
            if self.orig_img and val_str and val_str.isdigit():
                val = int(round(float(val_str) / self.ratio))
                # trace döngüsünü kırmasın diye geçici olarak trace'i devre dışı bırakabilir veya sadece set edebilirsin
                self.h_mm.set(str(val))
                self.process()
        except: pass
 
    def sync_w(self, *_):# h değiştiğinde w yi günceller
        try:
            if self.orig_img and self.h_mm.get().isdigit():
                val = int(round(float(self.h_mm.get()) * self.ratio))
                if self.w_mm.get() != str(val):
                    self.w_mm.set(str(val))
                self.process()
        except: pass

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return

        img = Image.open(path)

        StudioX_FreeEditor(
            self.root,
            img,
            self.receive_from_editor
        )
    def receive_from_editor(self, img):
        self.orig_img = img.convert("RGBA")
        self.process_image()

    def detect_and_clean_faces(self, pil_img):#yüz algılama ve blurlaştırma fonksiyonu
        if not self.face_cascade: return pil_img
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR); gray_cv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_cv, 1.1, 5, minSize=(30, 30))
        b_val = int(self.face_blur_s.get()); b_val = b_val if b_val % 2 != 0 else b_val + 1
        for (x, y, w, h) in faces:
            roi = cv_img[y:y+h, x:x+w]; roi = cv2.GaussianBlur(roi, (b_val, b_val), 0); cv_img[y:y+h, x:x+w] = roi
        return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

    def process(self):# resim işleme fonksiyonu.
        if not isinstance(self.orig_img, Image.Image):
                print("HATA: orig_img PIL Image değil!", type(self.orig_img))
                return   
        cv_img = cv2.cvtColor(
            np.array(self.orig_img),
            cv2.COLOR_RGBA2BGRA
        )
        if not self.orig_img: return
        try:
            dpi = float(self.dpi_var.get() or 250); px_w = int((float(self.w_mm.get() or 100)/25.4)*dpi); px_h = int(px_w/self.ratio)
            work = self.orig_img.resize((px_w, px_h), Image.Resampling.LANCZOS); 
            work = self.detect_and_clean_faces(work)
            base = work.convert("L"); 
            base = ImageEnhance.Brightness(base).enhance(self.bright_s.get()); 
            base = ImageEnhance.Contrast(base).enhance(self.contrast_s.get())
            if self.neg_var.get(): base = ImageOps.invert(base)

            # ... (resizing ve face_blur işlemleri bittikten sonra) ...

            #work = self.detect_and_clean_faces(work)
            bas = work.convert("L") # Siyah-beyaza çevir

            # 1. Önce Resme Varsayılan (Default) Bir Artış Uygula
            # Örneğin: Parlaklığı %20, Kontrastı %30 sabit artırıyoruz.
            default_bright = 1.0 
            default_contrast = 1.5
            # 2. Sürgü Değerleriyle Birleştirerek Uygula
            # Sürgü 1.0 (orta) konumundayken resim senin verdiğin default değerde görünür.
            bas = ImageEnhance.Brightness(bas).enhance(default_bright * self.bright_s.get())
            bas = ImageEnhance.Contrast(bas).enhance(default_contrast * self.contrast_s.get())

            # Invert kontrolü
            if self.neg_var.get():
                bas = ImageOps.invert(bas)

            gri = bas  # Senin istediğin 'gri' artık saf siyah-beyaz ve slider etkisinde olan resim
            #=========================
            #Gri tonlamadan dithere dönüştürme
            dither = gri.convert("1")# pillowun dithering fonksiyonu.
            #=========================

            # Sketch Moda geçiş: gray scale with bg cleaner skech oluşturmak için orijinal resmi yeniden işliyoruz. 
            np_img = np.array(base); strg = self.bg_strength.get(); block = int(11 + strg//5*2)
            th = cv2.adaptiveThreshold(np_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block|1, 5)
            gray = Image.fromarray((np_img*(1-strg/100) + th*(strg/100)).astype(np.uint8))
            
            # Sketch Mode
            inv = ImageOps.invert(gray)
            sketch = Image.blend(gray, inv.filter(ImageFilter.GaussianBlur(self.sketch_s.get())), 0.3)
            sketch = ImageEnhance.Contrast(sketch).enhance(3.0)
            #=========================
            # --- YENİ: LINE ART ENGINE (Sketch üzerinden türetilir) ---
            # Sketch görüntüsünü OpenCV ile işle
            cv_sketch = np.array(sketch)#numpy arraya çevir.
            # Keskinleştirme ve eşikleme (Lazer için saf siyah-beyaz çizgi)
            _, line_art_np = cv2.threshold(cv_sketch, 110, 255, cv2.THRESH_BINARY)
            line_art = Image.fromarray(line_art_np)
            
            self.res = {
                "gray": gri, #gri tonlama
                "gray_d": dither,# dither modu
                "sketch": sketch,# eskiz modu 
                "line_art": line_art # yeni line art modu
            }
            
            for k, lbl in self.panels.items():#görselleri panelde gösterir.
                im = self.res[k].copy(); im.thumbnail((550, 450))# Görseli panel boyutuna göre sınırlar
                tk_im = ImageTk.PhotoImage(im);# Label üzerine resmi basar
                lbl.config(image=tk_im); lbl.image = tk_im # Çöp toplayıcısının (Garbage Collector) resmi silmemesi için referans tutar
            self.info.config(text=f"> STATUS: READY\n> SIZE: {px_w}x{px_h}\n> ENGINE: V3.7_LINE_ART")
        except Exception as e: print(e)

    def save(self, key):
        if key in self.res:
            p = filedialog.asksaveasfilename(defaultextension=".png")
            if p: self.res[key].save(p, dpi=(int(self.dpi_var.get() or 250),)*2); messagebox.showinfo("OK", f"{key.upper()} EXPORTED")

    def validate_numeric(self, P):
    # Eğer kutu boşaltılıyorsa izin ver
        if P == "": return True
    # Sadece rakam girilsin VE maksimum 3 basamak olsun
        if P.isdigit() and len(P) <= 3:
            return True
        return False

    def set_active_panel(self, key):
            self.active_panel_key = key

    
if __name__ == "__main__":
    root = tk.Tk()
    app = LazerMasterCyber(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        app = LazerMasterCyber() # Sizin sınıf adınız
        app.mainloop()
    except Exception as e:
        print(f"KRİTİK HATA: {e}")
        input("Kapatmak için Enter'a basın...") # Konsolun hemen kapanmaması için
