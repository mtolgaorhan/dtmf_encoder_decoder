import os
print("ÇALIŞAN KLASÖR:", os.getcwd())

# -*- coding: utf-8 -*-
"""
DTMF-benzeri Türkçe Metin ↔ Ses (WAV) Dönüştürücü
FINAL - SES DESTEKLİ + JSON DESTEKLİ
"""

import numpy as np
from scipy.io.wavfile import write, read
import json



# ============================================================
#   SES ÇALMA MODÜLÜ (sounddevice)
# ============================================================

try:
    import sounddevice as sd
    HAS_SD = True
except ImportError:
    HAS_SD = False

print("SES DURUMU:", "VAR" if HAS_SD else "YOK")



# ============================================================
#   GENEL PARAMETRELER
# ============================================================

FS = 44100
DURATION = 0.04  # 40 ms

LOW_FREQS = [600, 700, 800, 900, 1000, 1100]
HIGH_FREQS = [1300, 1500, 1700, 1900, 2100]

CHARS = [
    'A','B','C','Ç','D','E','F','G','Ğ','H',
    'I','İ','J','K','L','M','N','O','Ö','P',
    'R','S','Ş','T','U','Ü','V','Y','Z',' '
]



# ============================================================
#   JSON FREKANS TABLOSU YÜKLEME
# ============================================================

def load_frequency_map(json_file):
    """Başka grubun JSON frekans tablosunu yükler."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    freq_map = {}
    for ch, pair in data.items():
        freq_map[ch] = (int(pair[0]), int(pair[1]))

    return freq_map



# ============================================================
#   FREKANS TABLOSU (ENCODER İÇİN)
# ============================================================

def build_frequency_map():
    freq_map = {}
    idx = 0
    for lf in LOW_FREQS:
        for hf in HIGH_FREQS:
            freq_map[CHARS[idx]] = (lf, hf)
            idx += 1
    return freq_map

FREQ_MAP = build_frequency_map()



# ============================================================
#   ENCODING (METİN → SES)
# ============================================================

def _tone_for_char(ch):
    """Tek karakter için DTMF benzeri ton üret."""
    f1, f2 = FREQ_MAP[ch]
    t = np.linspace(0, DURATION, int(FS * DURATION), endpoint=False)
    return np.sin(2*np.pi*f1*t) + np.sin(2*np.pi*f2*t)

def encode_text_to_signal(text):
    text = text.upper()
    tones = [_tone_for_char(ch) for ch in text]
    signal = np.concatenate(tones)
    return signal / np.max(np.abs(signal))


def save_signal(signal, filename="encoded.wav"):
    write(filename, FS, (signal * 32767).astype(np.int16))


def play_signal(signal, fs=FS):
    """Hoparlör üzerinden sinyal çal."""
    if not HAS_SD:
        print("sounddevice yok → ses çalınmayacak.")
        return
    sd.play(signal, fs)
    sd.wait()


def encode_text(text, filename="encoded.wav", play=True):
    """Metni encoding → WAV üret → opsiyonel olarak çal."""
    signal = encode_text_to_signal(text)
    save_signal(signal, filename)
    if play:
        play_signal(signal)
    return signal



# ============================================================
#   DECODING (SES → METİN)
# ============================================================

def _nearest_freq(target, candidates):
    """Bir frekansa en yakın listedeki frekansı döndürür."""
    return min(candidates, key=lambda x: abs(x - target))


def decode_wav(filename, freq_map):
    """JSON frekans tablosu ile WAV dosyasını çözer."""
    fs, data = read(filename)

    # Stereo ise mono'ya çevir
    if data.ndim > 1:
        data = data.mean(axis=1)

    data = data.astype(float)
    data /= np.max(np.abs(data))

    samples = int(FS * DURATION)

    # JSON tablosundaki low/high frekans grupları
    low_freqs = sorted({pair[0] for pair in freq_map.values()})
    high_freqs = sorted({pair[1] for pair in freq_map.values()})

    # Reverse map
    reverse_map = {v: k for k, v in freq_map.items()}

    decoded = []

    for i in range(0, len(data), samples):
        frame = data[i:i + samples]
        if len(frame) < samples:
            continue

        # Windowing
        frame = frame * np.hamming(len(frame))

        # FFT
        spectrum = np.abs(np.fft.rfft(frame))
        freqs = np.fft.rfftfreq(len(frame), 1/fs)
        spectrum[0] = 0

        peak_idx = np.argsort(spectrum)[-2:]
        peak_freqs = sorted(freqs[peak_idx])

        f1, f2 = peak_freqs

        f1_low = _nearest_freq(f1, low_freqs)
        f2_high = _nearest_freq(f2, high_freqs)

        # Tolerans (120 Hz önemli!)
        if abs(f1 - f1_low) > 120 or abs(f2 - f2_high) > 120:
            decoded.append("?")
            continue

        ch = reverse_map.get((f1_low, f2_high), "?")
        decoded.append(ch)

    return "".join(decoded)



# ============================================================
#   MENÜ
# ============================================================

if __name__ == "__main__":
    print("\nDTMF Türkçe Encoding / Decoding")
    print("------------------------------------")
    print("1) Metni sese dönüştür (encoding)")
    print("2) WAV dosyasını metne dönüştür (JSON ile decoding)")
    print("3) Çıkış\n")

    secim = input("Seçiminiz: ")

    if secim == "1":
        text = input("Metni girin:\n> ")
        encode_text(text, "encoded.wav", play=True)
        print("\nencoded.wav oluşturuldu!")

    elif secim == "2":
        wav = input("Çözülecek WAV dosyası:\n> ")
        js = input("Frekans tablosu (JSON dosyası):\n> ")

        freqmap = load_frequency_map(js)
        metin = decode_wav(wav, freq_map=freqmap)

        print("\nÇÖZÜLEN METİN:\n", metin)

    else:
        print("Çıkış yapıldı.")