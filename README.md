# 🛡️ WordPress Login Checker + Admin/User Filter

Script Python ini digunakan untuk melakukan pengecekan login ke halaman WordPress (`wp-login.php`) secara otomatis dari list target. Script ini juga memfilter akun berdasarkan level **admin** atau **user** menggunakan scraping terhadap halaman `profile.php`.

---

## 🎯 Fitur Utama

- ✅ Cek kredensial WordPress secara otomatis
- 🔍 Deteksi apakah akun adalah **admin** atau **user**
- 🧠 Deteksi otomatis format baris login (support banyak format)
- ⚡ Asynchronous dengan `asyncio + aiohttp + aiofiles`
- 📥 Hasil disimpan terpisah di:
  - `wp_admin.txt` (akun admin)
  - `wp_user.txt` (akun user)

---

## 📁 Struktur Direktori

```
.
├── checker.py         # Script utama
├── list/              # Folder berisi list target (file .txt)
│   └── target.txt     # Contoh file list target
├── wp_admin.txt       # Output akun admin valid
└── wp_user.txt        # Output akun user valid
```

---

## 📝 Format Input yang Didukung

Script ini mendukung berbagai macam format login:

```
https://domain.com/wp-login.php#admin@password
domain.com admin password
domain.com:admin:password
domain.com|admin|password
```

> Script akan otomatis menambahkan `https://` dan `/wp-login.php` jika tidak ada.

---

## 🚀 Cara Menjalankan

1. **Clone** repository ini atau download file `checker.py`
2. Masukkan list target ke dalam folder `list/` dengan format `.txt`
3. Jalankan script dengan:

```bash
python checker.py
```

---

## 📦 Contoh Output

```
✅ ADMIN: https://example.com/wp-login.php|admin|password123
✅ USER: https://blog.net/wp-login.php|editor|123456
❌ Wrong password: https://fail.com/wp-login.php
❌ Not a WordPress login page: https://notwp.com/
```

---

## 📌 Kebutuhan

- Python 3.8+
- Library: `aiohttp`, `aiofiles`, `colorama`, `beautifulsoup4`
  
Install semua kebutuhan dengan:

```bash
pip install aiohttp aiofiles colorama beautifulsoup4
```

---

## 💡 Tips Tambahan

- Gunakan file list yang bersih dan tidak ada duplikat
- Jalankan script dengan koneksi yang stabil
- Untuk jumlah target besar, bisa gunakan proxy atau split list

---

## 🔒 Disclaimer

> Script ini dibuat untuk tujuan edukasi dan pengujian keamanan sistem milik sendiri. Segala penyalahgunaan bukan tanggung jawab pembuat.


## 🧠 Motivasi

> "Masalah ada untuk diselesaikan — bukan dihindari."

---
