import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ---------------- APP ----------------
class SimpleImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Foto Editör | DPI - PPI - Resize")
        self.root.geometry("1350x750")

        self.original_img = None
        self.processed_img = None

        self.dpi_value = 300  # varsayılan

        self.build_ui()

    def build_ui(self):
        control = tk.Frame(self.root, width=320)
        control.pack(side="left", fill="y", padx=10)

        view = tk.Frame(self.root)
        view.pack(side="right", expand=True, fill="both")

        # ---------------- FILE ----------------
        tk.Button(control, text="📂 Fotoğraf Aç", command=self.load_image).pack(fill="x", pady=5)

        # ---------------- BASIC ----------------
        self.brightness = tk.Scale(control, from_=-100, to=100,
                                   label="Parlaklık", orient="horizontal",
                                   command=lambda e: self.update())
        self.brightness.pack(fill="x")

        self.contrast = tk.Scale(control, from_=50, to=200,
                                 label="Kontrast", orient="horizontal",
                                 command=lambda e: self.update())
        self.contrast.set(100)
        self.contrast.pack(fill="x")

        self.bg_clean = tk.Scale(control, from_=0, to=255,
                                 label="Arkaplan Temizleme",
                                 orient="horizontal",
                                 command=lambda e: self.update())
        self.bg_clean.pack(fill="x")

        self.face_var = tk.IntVar()
        tk.Checkbutton(control, text="🙂 Yüz Tanıma",
                       variable=self.face_var,
                       command=self.update).pack(pady=5)

        # ---------------- RESIZE ----------------
        tk.Label(control, text="📏 Yeniden Boyutlandır (px)", font=("Arial", 10, "bold")).pack(pady=5)

        size_frame = tk.Frame(control)
        size_frame.pack(fill="x")

        tk.Label(size_frame, text="G:").pack(side="left")
        self.width_entry = tk.Entry(size_frame, width=6)
        self.width_entry.pack(side="left", padx=2)

        tk.Label(size_frame, text="Y:").pack(side="left")
        self.height_entry = tk.Entry(size_frame, width=6)
        self.height_entry.pack(side="left", padx=2)

        tk.Button(control, text="Resize Uygula", command=self.resize_image).pack(fill="x", pady=5)

        # ---------------- DPI / PPI ----------------
        self.dpi_slider = tk.Scale(control, from_=72, to=600,
                                   label="DPI / PPI",
                                   orient="horizontal",
                                   command=self.update_info)
        self.dpi_slider.set(300)
        self.dpi_slider.pack(fill="x")

        self.info_label = tk.Label(control, text="", justify="left")
        self.info_label.pack(pady=10)

        # ---------------- IMAGES ----------------
        self.lbl_original = tk.Label(view)
        self.lbl_original.pack(side="left", padx=10)

        self.lbl_processed = tk.Label(view)
        self.lbl_processed.pack(side="right", padx=10)

    # ---------------- LOAD ----------------
   def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
        )
        if not path:
            return

        self.original_img = cv2.imread(path)

        if self.original_img is None:
            print("Resim okunamadı")
            return

        # 🔥 BU SATIR KRİTİK
        self.processed_img = self.original_img.copy()

        h, w = self.original_img.shape[:2]
        self.width_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(w))
        self.height_entry.insert(0, str(h))

        self.update()


    # ---------------- RESIZE ----------------
    def resize_image(self):
        if self.original_img is None:
            return

        try:
            w = int(self.width_entry.get())
            h = int(self.height_entry.get())
            self.original_img = cv2.resize(self.original_img, (w, h))
            self.update()
        except:
            pass

    # ---------------- UPDATE IMAGE ----------------
    def update(self):
        if self.original_img is None:
            return

        img = self.original_img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        alpha = self.contrast.get() / 100.0
        beta = self.brightness.get()
        gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    def apply_dpi_resample(self):
        if self.original_img is None:
            return

        self.dpi_target = self.dpi_slider.get()
        self.original_img = resample_by_dpi(
            self.original_img,
            self.dpi_original,
            self.dpi_target
        )
        self.dpi_original = self.dpi_target
        self.update()

    def remove_faces(gray):
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(gray, (x, y), (x+w, y+h), 255, -1)
        return gray

        if self.bg_clean.get() > 0:
            _, gray = cv2.threshold(gray, self.bg_clean.get(), 255, cv2.THRESH_BINARY)

        if self.face_var.get():
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            gray_color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            for (x, y, w, h) in faces:
                cv2.rectangle(gray_color, (x, y), (x+w, y+h), (0, 255, 0), 2)
            self.processed_img = gray_color
        else:
            self.processed_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        self.show_images()
        self.update_info()

    # ---------------- INFO ----------------
    def update_info(self, e=None):
        if self.original_img is None:
            return

        dpi = self.dpi_slider.get()
        h, w = self.original_img.shape[:2]

        width_cm = (w / dpi) * 2.54
        height_cm = (h / dpi) * 2.54

        self.info_label.config(
            text=f"Piksel: {w} x {h}\n"
                 f"DPI / PPI: {dpi}\n"
                 f"Fiziksel Ölçü: {width_cm:.2f} x {height_cm:.2f} cm"
        )

    # ---------------- DISPLAY ----------------
    def show_images(self):
        def cv_to_tk(img, size=(520, 520)):
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, size)
            return ImageTk.PhotoImage(Image.fromarray(img))

        self.lbl_original.imgtk = cv_to_tk(self.original_img)
        self.lbl_original.config(image=self.lbl_original.imgtk)

        self.lbl_processed.imgtk = cv_to_tk(self.processed_img)
        self.lbl_processed.config(image=self.lbl_processed.imgtk)


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleImageEditor(root)
    root.mainloop()
