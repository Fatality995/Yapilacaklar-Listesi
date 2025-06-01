import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os

DOSYA_ADI = "gorevler.json"

class Yapilacaklar:
    def __init__(self, root):
        self.root = root
        self.root.title("🗒️ Yapılacaklar Listesi")
        self.root.geometry("500x600")
        self.gorevler = []

        # Üst Giriş Alanı
        self.entry = tk.Entry(root, font=("Arial", 12))
        self.entry.pack(pady=(10, 5), padx=10, fill="x")

        self.date_entry = tk.Entry(root, font=("Arial", 12))
        self.date_entry.insert(0, "İsteğe bağlı: yyyy-aa-gg")
        self.date_entry.pack(padx=10, fill="x")
        self.date_entry.bind("<FocusIn>", self.clear_date_placeholder)

        self.ekle_btn = tk.Button(root, text="➕ Görev Ekle", command=self.gorev_ekle)
        self.ekle_btn.pack(pady=5)

        # Arama Girişi
        self.ara_entry = tk.Entry(root, font=("Arial", 12), fg="gray")
        self.ara_entry.pack(pady=5, padx=10, fill="x")
        self.ara_entry.insert(0, "Görev ara...")
        self.ara_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.ara_entry.bind("<FocusOut>", self.restore_search_placeholder)
        self.ara_entry.bind("<KeyRelease>", self.gorev_filtrele)

        # Liste Alanı
        self.liste_frame = tk.Frame(root)
        self.liste_frame.pack(padx=10, fill="both", expand=True)

        self.canvas = tk.Canvas(self.liste_frame)
        self.scrollbar = tk.Scrollbar(self.liste_frame, orient="vertical", command=self.canvas.yview)
        self.gorevler_frame = tk.Frame(self.canvas)

        self.gorevler_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.gorevler_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.gorev_yukle()

    def clear_date_placeholder(self, event):
        if self.date_entry.get() == "İsteğe bağlı: yyyy-aa-gg":
            self.date_entry.delete(0, tk.END)

    def clear_search_placeholder(self, event):
        if self.ara_entry.get() == "Görev ara...":
            self.ara_entry.delete(0, tk.END)
            self.ara_entry.config(fg="black")

    def restore_search_placeholder(self, event):
        if self.ara_entry.get() == "":
            self.ara_entry.insert(0, "Görev ara...")
            self.ara_entry.config(fg="gray")

    def gorev_ekle(self):
        metin = self.entry.get().strip()
        tarih = self.date_entry.get().strip()

        if not metin:
            messagebox.showwarning("Uyarı", "Lütfen bir görev girin.")
            return

        # Tarih kontrolü sadece girilmişse yapılır
        if tarih and tarih != "İsteğe bağlı: yyyy-aa-gg":
            try:
                datetime.strptime(tarih, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Hatalı tarih", "Tarih formatı: yyyy-aa-gg")
                return
        else:
            tarih = ""

        self.gorev_olustur(metin, tarih, tamamlandi=False)
        self.entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, "İsteğe bağlı: yyyy-aa-gg")
        self.gorev_kaydet()

    def gorev_olustur(self, metin, tarih="", tamamlandi=False):
        frame = tk.Frame(self.gorevler_frame)
        var = tk.BooleanVar(value=tamamlandi)
        yazi = f"{metin} [{tarih}]" if tarih else metin
        check = tk.Checkbutton(frame, text=yazi, variable=var, onvalue=True, offvalue=False,
                               font=("Arial", 11), anchor="w", justify="left", command=self.gorev_kaydet)
        check.pack(side="left", fill="x", expand=True)

        sil_btn = tk.Button(frame, text="🗑️", command=lambda: self.gorev_sil(frame))
        sil_btn.pack(side="right")

        frame.pack(fill="x", pady=2)

        self.gorevler.append((frame, check, var, metin, tarih))

    def gorev_sil(self, frame):
        for i, (f, _, _, _, _) in enumerate(self.gorevler):
            if f == frame:
                f.destroy()
                self.gorevler.pop(i)
                break
        self.gorev_kaydet()

    def gorev_filtrele(self, event=None):
        arama = self.ara_entry.get().strip().lower()
        if arama == "görev ara...":
            arama = ""

        for frame, check, _, metin, tarih in self.gorevler:
            yazi = f"{metin} [{tarih}]" if tarih else metin
            if arama in yazi.lower():
                frame.pack(fill="x", pady=2)
            else:
                frame.pack_forget()

    def gorev_kaydet(self):
        veri = []
        for _, _, var, metin, tarih in self.gorevler:
            veri.append({"metin": metin, "tarih": tarih, "tamamlandi": var.get()})
        with open(DOSYA_ADI, "w", encoding="utf-8") as f:
            json.dump(veri, f, indent=4)

    def gorev_yukle(self):
        if os.path.exists(DOSYA_ADI):
            with open(DOSYA_ADI, "r", encoding="utf-8") as f:
                try:
                    veri = json.load(f)
                    for g in veri:
                        self.gorev_olustur(g["metin"], g.get("tarih", ""), g.get("tamamlandi", False))
                except:
                    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = Yapilacaklar(root)
    root.mainloop()
