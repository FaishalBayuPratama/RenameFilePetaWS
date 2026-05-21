# RenameFilePetaWS

Alat berbasis web untuk pemrosesan otomatis file peta geospasial, dibangun menggunakan Flask. Menggunakan teknologi OCR untuk secara otomatis mengganti nama file gambar peta berdasarkan nomor registrasinya, serta mengonversi file peta PDF ke format JPG.

Dibangun selama magang di BPS Kabupaten Sidoarjo untuk menyederhanakan alur kerja data geospasial.

---

## Anggota Tim

| No | Nama | NIM |
|----|------|-----|
| 1 | Faishal Bayu Pratama | 23031554092 |
| 2 | Iqbal Wahyufirmansyah | 23031554106 |
| 3 | Yogi Ramadhani | 23031554198 |
| 4 | Muhammad Dafa Alvian Ramadhani | 23031554017 |
| 5 | Muhammad Alif Mahbubi | 23031554031 |

---

## Fitur

**Rename Peta**
- Mendeteksi otomatis nomor registrasi 10–16 digit dari gambar peta menggunakan OCR
- Mengganti nama file berdasarkan nomor yang terdeteksi (contoh: `1234567890.jpg`)
- File yang nomornya tidak terdeteksi akan diberi nama `Anomali_1.jpg`, `Anomali_2.jpg`, dst.
- Mendukung unggahan file ZIP atau beberapa file gambar sekaligus
- Menghasilkan ZIP berisi file yang sudah diganti namanya beserta laporan pemrosesan lengkap

**Konversi PDF ke JPG**
- Mengonversi setiap halaman file PDF peta menjadi gambar JPG berkualitas tinggi (300 DPI)
- Menghasilkan semua halaman dalam satu file ZIP yang bisa diunduh

---

## Teknologi yang Digunakan

- **Backend:** Python, Flask
- **OCR:** EasyOCR (mendukung Bahasa Indonesia dan Inggris)
- **Pemrosesan PDF:** pdf2image, Poppler
- **Pemrosesan Gambar:** Pillow (PIL)
- **Frontend:** HTML, Tailwind CSS

---

## Persyaratan

- Python 3.11+
- Poppler (untuk konversi PDF)

Instalasi dependensi Python:

```bash
pip install flask easyocr pdf2image Pillow werkzeug
```

Instalasi Poppler di Windows:
1. Unduh dari [https://github.com/oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases)
2. Ekstrak dan catat lokasi folder `bin`
3. Perbarui `POPPLER_PATH` di file `coba flask.py` sesuai dengan lokasi instalasi kamu

---

## Cara Menjalankan

**Opsi 1: Manual**

```bash
python "coba flask.py"
```

Kemudian buka browser dan akses `http://localhost:5000`

**Opsi 2: Menggunakan file batch**

Edit file `jalankan_web.bat` sesuai dengan lokasi Python dan proyek di komputermu, lalu klik dua kali untuk menjalankan.

---

## Struktur Proyek

```
RenameFilePetaWS-main/
├── coba flask.py       # Aplikasi Flask utama
├── index.html          # Halaman utama
├── rename.html         # Halaman rename peta
├── convert.html        # Halaman konversi PDF ke JPG
├── result.html         # Halaman hasil pemrosesan
├── style.css           # Gaya kustom
└── jalankan_web.bat    # File batch Windows untuk menjalankan aplikasi
```

---

## Cara Penggunaan

### Rename File Peta
1. Buka halaman **Rename Peta**
2. Unggah file ZIP berisi gambar peta, atau pilih beberapa file gambar (JPG, PNG, JPEG)
3. Klik **Proses**
4. Lihat laporan pemrosesan dan unduh file yang sudah diganti namanya dalam format ZIP

### Konversi PDF ke JPG
1. Buka halaman **Convert PDF**
2. Unggah file PDF (maks. 5 GB)
3. Klik **Proses**
4. Unduh halaman JPG hasil konversi dalam format ZIP

---

## Catatan

- Akurasi OCR bergantung pada kualitas gambar. Gambar yang jernih dan beresolusi tinggi menghasilkan hasil yang lebih baik.
- File yang gagal dideteksi nomornya oleh OCR akan disimpan sebagai `Anomali_N` dan bisa diganti namanya secara manual.
- Aplikasi ini ditujukan untuk penggunaan lokal. Untuk deployment ke produksi, ganti secret key di `app.secret_key` dan konfigurasikan server yang sesuai.
