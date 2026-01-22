import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


# ----------------- UTILS -----------------

def adjust_gamma(image, gamma):
    gamma = max(gamma, 0.01)
    inv = 1.0 / gamma
    table = np.array(
        [(i / 255.0) ** inv * 255 for i in range(256)]
    ).astype("uint8")
    return cv2.LUT(image, table)


# ----------------- CORE GRAYSCALE -----------------

def laser_final_grayscale(img, eskiz, alpha_u, beta_u, gamma_u, whitepoint):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    alpha = np.clip(alpha_u + eskiz * 1.8, 1.0, 2.2)
    beta = np.clip(beta_u - eskiz * 30, -60, 10)
    gamma = np.clip(gamma_u - eskiz * 0.25, 0.4, 1.4)

    gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    gray = adjust_gamma(gray, gamma)

    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)

    sketch = np.clip(sketch, 0, 255).astype(np.uint8)
    sketch[sketch > whitepoint] = 255
    sketch = cv2.GaussianBlur(sketch, (3, 3), 0)

    return sketch


# ----------------- LINE ART -----------------

def generate_line_art(gray, strength):
    high = int(80 + strength * 200)
    edges = cv2.Canny(gray, 40, high)
    edges = 255 - edges
    return cv2.GaussianBlur(edges, (3, 3), 0)


# ----------------- DITHERING -----------------

def generate_dither(gray, strength):
    img = gray.astype(np.float32)
    h, w = img.shape

    threshold = np.interp(strength, [0, 1], [160, 90])

    for y in range(h - 1):
        for x in range(1, w - 1):
            old = img[y, x]
            new = 255 if old > threshold else 0
            img[y, x] = new
            err = old - new

            img[y, x + 1] += err * 7 / 16
            img[y + 1, x - 1] += err * 3 / 16
            img[y + 1, x] += err * 5 / 16
            img[y + 1, x + 1] += err * 1 / 16

    return np.clip(img, 0, 255).astype(np.uint8)


# ----------------- GUI -----------------

class PencilLaserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pencil Laser – GRAYSCALE / LINE / DITHER")
        self.root.geometry("1800x950")

        self.image = None

        self.eskiz = tk.DoubleVar(value=0.45)
        self.alpha = tk.DoubleVar(value=1.3)
        self.beta = tk.IntVar(value=-15)
        self.gamma = tk.DoubleVar(value=0.9)
        self.whitepoint = tk.IntVar(value=245)
        self.line_strength = tk.DoubleVar(value=0.5)
        self.dither_strength = tk.DoubleVar(value=0.6)

        self.setup_ui()

    def setup_ui(self):
        top = ttk.LabelFrame(self.root, text=" AYARLAR ")
        top.pack(fill="x", padx=15, pady=10)

        ttk.Button(top, text="RESİM YÜKLE", command=self.load_image).grid(row=0, column=0)

        sliders = [
            ("Eskiz", self.eskiz, 0.05, 0.85),
            ("Alpha", self.alpha, 1.0, 2.2),
            ("Beta", self.beta, -60, 10),
            ("Gamma", self.gamma, 0.4, 1.4),
            ("White", self.whitepoint, 200, 255),
            ("Line", self.line_strength, 0.0, 1.0),
            ("Dither", self.dither_strength, 0.0, 1.0)
        ]

        col = 1
        for name, var, a, b in sliders:
            ttk.Label(top, text=name).grid(row=0, column=col)
            ttk.Scale(top, from_=a, to=b, variable=var,
                      command=self.update_all).grid(row=0, column=col + 1, sticky="ew")
            col += 2

        ttk.Button(top, text="GRAYSCALE KAYDET", command=self.save_gray).grid(row=1, column=10)
        ttk.Button(top, text="LINE ART KAYDET", command=self.save_line).grid(row=1, column=11)
        ttk.Button(top, text="DITHER KAYDET", command=self.save_dither).grid(row=1, column=12)

        top.columnconfigure(tuple(range(14)), weight=1)

        mid = ttk.Frame(self.root)
        mid.pack(fill="both", expand=True, padx=15, pady=10)

        self.p_gray = self.create_panel(mid, "GRAYSCALE", 0)
        self.p_line = self.create_panel(mid, "LINE ART", 1)
        self.p_dither = self.create_panel(mid, "DITHERING", 2)

        mid.columnconfigure((0, 1, 2), weight=1)

    def create_panel(self, parent, title, col):
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=0, column=col, padx=10, sticky="nsew")
        lbl = ttk.Label(frame, text="\n\nBekleniyor...")
        lbl.pack(expand=True)
        return lbl

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.jpeg")])
        if path:
            self.image = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
            self.update_all()

    def update_all(self, e=None):
        if self.image is None:
            return

        gray = laser_final_grayscale(
            self.image,
            self.eskiz.get(),
            self.alpha.get(),
            self.beta.get(),
            self.gamma.get(),
            self.whitepoint.get()
        )

        line = generate_line_art(gray, self.line_strength.get())
        dither = generate_dither(gray, self.dither_strength.get())

        self.show(self.p_gray, gray)
        self.show(self.p_line, line)
        self.show(self.p_dither, dither)

    def show(self, panel, img):
        im = Image.fromarray(img)
        im.thumbnail((520, 520))
        tkimg = ImageTk.PhotoImage(im)
        panel.configure(image=tkimg, text="")
        panel.image = tkimg

    def save_gray(self):
        self.save_img(self.p_gray, "grayscale.png")

    def save_line(self):
        self.save_img(self.p_line, "lineart.png")

    def save_dither(self):
        self.save_img(self.p_dither, "dither.png")

    def save_img(self, panel, default):
        if self.image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default)
        if path:
            cv2.imwrite(path, panel.image._PhotoImage__photo.convert("L"))


if __name__ == "__main__":
    root = tk.Tk()
    PencilLaserApp(root)
    root.mainloop()
