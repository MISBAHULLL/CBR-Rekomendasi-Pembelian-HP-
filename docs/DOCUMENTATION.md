# Dokumentasi Lengkap Sistem Rekomendasi HP dengan CBR

## 1. Teori Case-Based Reasoning (CBR)

### 1.1 Pengertian CBR

**Case-Based Reasoning (CBR)** adalah paradigma penyelesaian masalah yang menggunakan pengalaman masa lalu (kasus sebelumnya) untuk menyelesaikan masalah baru. Dalam konteks sistem rekomendasi HP, CBR bekerja dengan:

1. Menyimpan data HP sebagai **kasus (cases)** dalam database
2. Ketika user meminta rekomendasi, sistem mencari kasus yang paling mirip
3. Menggunakan HP yang mirip sebagai rekomendasi

### 1.2 Siklus CBR (R4 Cycle)

```
      ┌──────────────┐
      │   PROBLEM    │ ← Input preferensi user
      └──────┬───────┘
             │
      ┌──────▼───────┐
      │   RETRIEVE   │ ← Cari HP mirip dari database
      └──────┬───────┘
             │
      ┌──────▼───────┐
      │    REUSE     │ ← Gunakan HP tersebut sebagai rekomendasi
      └──────┬───────┘
             │
      ┌──────▼───────┐
      │   REVISE     │ ← Sesuaikan berdasarkan preferensi tambahan
      └──────┬───────┘
             │
      ┌──────▼───────┐
      │   RETAIN     │ ← Simpan feedback untuk pembelajaran
      └──────┬───────┘
             │
      ┌──────▼───────┐
      │   SOLUTION   │ ← Output rekomendasi HP
      └──────────────┘
```

#### RETRIEVE
Mencari kasus-kasus yang relevan dari case base menggunakan similarity measure.

#### REUSE  
Mengadaptasi solusi dari kasus yang ditemukan untuk masalah baru.

#### REVISE
Mengevaluasi dan memperbaiki solusi jika diperlukan.

#### RETAIN
Menyimpan pengalaman baru ke dalam case base untuk digunakan di masa depan.


## 2. Weighted Euclidean Distance

### 2.1 Formula

Weighted Euclidean Distance adalah metode untuk mengukur jarak (ketidakmiripan) antara dua vektor dengan mempertimbangkan bobot pada setiap dimensi.

**Formula:**
```
d(x, y) = √(Σᵢ wᵢ × (xᵢ - yᵢ)²)
```

Dimana:
- `x` = vektor fitur query (input user)
- `y` = vektor fitur case (HP dalam database)  
- `wᵢ` = bobot untuk fitur ke-i
- `xᵢ - yᵢ` = selisih nilai fitur ke-i

### 2.2 Konversi ke Similarity

```
similarity = 1 / (1 + distance)
```

Atau:
```
similarity = 1 - (distance / max_distance)
```

### 2.3 Contoh Perhitungan

**Query User:**
- Harga: 8.000.000
- RAM: 8 GB
- Baterai: 5000 mAh

**Case dalam Database:**
- Harga: 7.500.000
- RAM: 8 GB
- Baterai: 4500 mAh

**Bobot:**
- Harga: 25%
- RAM: 15%
- Baterai: 15%

**Langkah:**
1. Normalisasi nilai ke range 0-1
2. Hitung weighted squared difference untuk setiap atribut
3. Jumlahkan dan akar kuadratkan
4. Konversi ke similarity


## 3. Alasan Pemilihan Metode

### 3.1 Mengapa CBR?

1. **Intuitif** - Mirip cara manusia berpikir (belajar dari pengalaman)
2. **Tidak perlu model** - Berbeda dengan ML tradisional
3. **Incremental learning** - Bisa menambah kasus baru tanpa retrain
4. **Explainable** - Mudah menjelaskan mengapa rekomendasi diberikan

### 3.2 Mengapa Weighted Euclidean?

1. **Fleksibel** - Bobot bisa disesuaikan
2. **Efisien** - Komputasi cepat
3. **Interpretable** - Mudah dipahami
4. **Kontrol** - User/admin bisa mengatur prioritas atribut


## 4. Sistem Pembobotan

### 4.1 Bobot dalam Persentase

Sistem menggunakan bobot dalam **persentase (0-100%)** bukan desimal, dengan aturan:
- Total bobot harus **100%**
- Tidak boleh ada bobot bernilai **0**
- Minimum bobot adalah **1%**

### 4.2 Contoh Pembobotan Optimal

**Untuk Rekomendasi HP Umum:**
| Atribut | Bobot | Alasan |
|---------|-------|--------|
| Harga | 25% | Faktor utama keputusan pembelian |
| RAM | 15% | Performa multitasking |
| Baterai | 15% | Daya tahan penggunaan |
| Kamera | 15% | Kebutuhan fotografi |
| Rating | 15% | Kepuasan pengguna lain |
| Storage | 10% | Kapasitas penyimpanan |
| Layar | 5% | Preferensi sekunder |

### 4.3 Preset Alternatif

**Budget Focused (Hemat):**
- Harga: 40%, RAM: 15%, lainnya: 10%

**Performance (Gaming/Produktivitas):**
- RAM: 30%, Storage: 25%, Harga: 15%

**Photography (Content Creator):**
- Kamera: 35%, Storage: 15%, Baterai: 15%


## 5. Evaluasi Model

### 5.1 Skenario

1. **70% Training - 30% Testing**
   - 700 data untuk training (case base)
   - 300 data untuk testing

2. **80% Training - 20% Testing**
   - 800 data untuk training
   - 200 data untuk testing

### 5.2 Metrik

**Accuracy:** Proporsi prediksi yang benar
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**Precision:** Ketepatan hasil positif
```
Precision = TP / (TP + FP)
```

**Recall:** Kemampuan menemukan semua yang relevan
```
Recall = TP / (TP + FN)
```

**F1-Score:** Harmonic mean precision & recall
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

### 5.3 Confusion Matrix

```
                 Predicted
                 Neg   Pos
Actual  Neg  [  TN  |  FP  ]
        Pos  [  FN  |  TP  ]
```


## 6. Flowchart Sistem

```
┌─────────────────┐
│    START        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User Input      │
│ Preferensi HP   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Normalisasi     │
│ Input (0-1)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RETRIEVE:       │
│ Hitung Similarity│
│ dengan semua HP │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sort by         │
│ Similarity DESC │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ REUSE:          │
│ Ambil Top-K HP  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ REVISE:         │
│ Filter tambahan │
│ (brand, OS)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate        │
│ Explanations    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return          │
│ Recommendations │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     END         │
└─────────────────┘
```


## 7. Contoh Input-Output

### 7.1 Request API

```json
POST /api/v1/recommendations
{
  "input_specs": {
    "max_harga": 8000000,
    "ram": 8,
    "memori_internal": 128,
    "min_baterai": 4500,
    "min_rating": 4.0,
    "preferred_brands": ["Samsung", "Xiaomi"],
    "preferred_os": "Android"
  },
  "top_k": 5,
  "min_similarity": 0.3
}
```

### 7.2 Response

```json
{
  "success": true,
  "total_results": 5,
  "recommendations": [
    {
      "rank": 1,
      "phone": {
        "Id_hp": 42,
        "Nama_hp": "Samsung Galaxy A54",
        "Brand": "Samsung",
        "Harga": 6499000,
        "Ram": 8,
        "Memori_internal": 128,
        "Kapasitas_baterai": 5000,
        "Rating_pengguna": 4.5
      },
      "similarity_score": 0.89,
      "similarity_percentage": 89.0,
      "match_highlights": [
        "✓ Harga sesuai budget",
        "✓ RAM memenuhi kebutuhan",
        "✓ Brand favorit"
      ]
    }
  ]
}
```


## 8. Handle Missing Values

Strategi fallback untuk missing values:

| Tipe Data | Strategi | Contoh |
|-----------|----------|--------|
| Numerik | Median | Harga: median semua HP |
| Kategorikal | Mode | Brand: brand terbanyak |
| String | "Unknown" | Nama: "Unknown" |
| Boolean | True | Stok: True (tersedia) |


## 9. Cara Menambah Data Baru (RETAIN)

### Via API

```json
POST /api/v1/admin/phones
{
  "nama_hp": "Xiaomi 14 Pro",
  "brand": "Xiaomi",
  "harga": 12999000,
  "ram": 12,
  "memori_internal": 256,
  "ukuran_layar": 6.7,
  "resolusi_kamera": "50MP",
  "kapasitas_baterai": 4880,
  "os": "Android",
  "rating_pengguna": 4.7
}
```

### Via Admin Dashboard

1. Buka menu Admin
2. Tab "Tambah HP"
3. Isi form
4. Klik "Tambah HP"

Data akan otomatis ditambahkan ke case base dan bisa langsung digunakan untuk rekomendasi.
