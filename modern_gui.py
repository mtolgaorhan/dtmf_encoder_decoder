import customtkinter as ctk
from tkinter import filedialog, messagebox
from main import encode_text, decode_wav, load_frequency_map

# Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DTMFApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DTMF Türkçe Encoder / Decoder")
        self.geometry("650x600")

        # Başlık
        title = ctk.CTkLabel(self, text="DTMF Türkçe Metin ↔ Ses Uygulaması",
                             font=("Segoe UI", 22, "bold"))
        title.pack(pady=20)

        # Metin giriş alanı
        self.text_entry = ctk.CTkEntry(self, width=400, placeholder_text="Metin giriniz...")
        self.text_entry.pack(pady=10)

        encode_btn = ctk.CTkButton(self, text="Encode Et ve encoded.wav Üret", command=self.encode_action)
        encode_btn.pack(pady=10)

        # WAV seçme
        self.wav_entry = ctk.CTkEntry(self, width=400, placeholder_text="WAV dosyası seç...")
        self.wav_entry.pack(pady=10)

        wav_btn = ctk.CTkButton(self, text="WAV Seç", command=self.select_wav)
        wav_btn.pack(pady=5)

        # JSON seçme
        self.json_entry = ctk.CTkEntry(self, width=400, placeholder_text="JSON frekans tablosu seç...")
        self.json_entry.pack(pady=10)

        json_btn = ctk.CTkButton(self, text="JSON Seç", command=self.select_json)
        json_btn.pack(pady=5)

        decode_btn = ctk.CTkButton(self, text="Decode Et", command=self.decode_action)
        decode_btn.pack(pady=15)

        # Çıktı alanı
        self.output_text = ctk.CTkTextbox(self, width=500, height=150)
        self.output_text.pack(pady=10)

    def encode_action(self):
        text = self.text_entry.get()
        if not text:
            messagebox.showerror("Hata", "Metin boş olamaz!")
            return

        encode_text(text, "encoded.wav", play=True)
        messagebox.showinfo("Başarılı", "encoded.wav oluşturuldu ve ses çalındı!")

    def decode_action(self):
        wav_file = self.wav_entry.get()
        json_file = self.json_entry.get()

        if not wav_file or not json_file:
            messagebox.showerror("Hata", "WAV ve JSON dosyaları seçilmeli!")
            return

        try:
            freqmap = load_frequency_map(json_file)
            text = decode_wav(wav_file, freqmap)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("end", text)
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def select_wav(self):
        file = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file:
            self.wav_entry.delete(0, "end")
            self.wav_entry.insert(0, file)

    def select_json(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file:
            self.json_entry.delete(0, "end")
            self.json_entry.insert(0, file)


if __name__ == "__main__":
    app = DTMFApp()
    app.mainloop()