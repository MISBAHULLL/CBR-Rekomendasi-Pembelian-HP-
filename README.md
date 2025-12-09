# CBR Phone Recommendation System
## Sistem Rekomendasi Handphone dengan Case-Based Reasoning

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![React](https://img.shields.io/badge/react-18.3-blue.svg)

## 📱 Tentang Project

Sistem rekomendasi handphone cerdas menggunakan **Case-Based Reasoning (CBR)** dengan metode **Weighted Euclidean Distance**. Sistem ini mampu memberikan rekomendasi HP berdasarkan preferensi user dengan tingkat akurasi yang tinggi.

### Fitur Utama
- ✅ Rekomendasi HP berdasarkan spesifikasi yang diinginkan
- ✅ Pembobotan atribut dalam persentase (total 100%)
- ✅ Evaluasi model dengan skenario 70-30 dan 80-20
- ✅ Dashboard admin untuk manajemen bobot
- ✅ UI modern dan responsif
- ✅ Visualisasi hasil dengan charts

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │  Home   │  │ Recom.   │  │ Evaluate │  │  Admin  │  │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  │
└───────┼────────────┼─────────────┼─────────────┼────────┘
        │            │             │             │
        └────────────┴──────┬──────┴─────────────┘
                            │ HTTP/REST API
        ┌───────────────────▼───────────────────┐
        │           BACKEND (FastAPI)            │
        │  ┌─────────────────────────────────┐  │
        │  │         API Routes              │  │
        │  │  /recommendations  /evaluation  │  │
        │  │  /admin           /health       │  │
        │  └──────────────┬──────────────────┘  │
        │                 │                      │
        │  ┌──────────────▼──────────────────┐  │
        │  │         CBR ENGINE              │  │
        │  │  ┌─────────┐  ┌──────────────┐ │  │
        │  │  │Retrieve │→│ Reuse        │ │  │
        │  │  └─────────┘  └──────────────┘ │  │
        │  │  ┌─────────┐  ┌──────────────┐ │  │
        │  │  │Revise   │→│ Retain       │ │  │
        │  │  └─────────┘  └──────────────┘ │  │
        │  └──────────────┬──────────────────┘  │
        │                 │                      │
        │  ┌──────────────▼──────────────────┐  │
        │  │   Weighted Euclidean Distance   │  │
        │  │   d(x,y) = √(Σ wᵢ×(xᵢ-yᵢ)²)    │  │
        │  └─────────────────────────────────┘  │
        └───────────────────┬───────────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │              DATABASE                  │
        │           (data.xlsx)                  │
        │         1000+ Phone Data               │
        └────────────────────────────────────────┘
```

## 📂 Struktur Project

```
Final_Project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Pydantic models
│   │   │   ├── phone.py
│   │   │   └── evaluation.py
│   │   ├── routes/              # API endpoints
│   │   │   ├── recommendation.py
│   │   │   ├── evaluation.py
│   │   │   ├── admin.py
│   │   │   └── health.py
│   │   ├── cbr/                 # CBR Engine
│   │   │   ├── cbr_engine.py    # Main CBR logic
│   │   │   ├── weighted_euclidean.py
│   │   │   └── evaluator.py
│   │   └── utils/
│   │       ├── data_loader.py
│   │       └── preprocessing.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx
│   │   │   ├── PhoneCard.jsx
│   │   │   └── UI.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Recommendation.jsx
│   │   │   ├── Results.jsx
│   │   │   ├── Evaluation.jsx
│   │   │   ├── Admin.jsx
│   │   │   ├── PhoneList.jsx
│   │   │   └── PhoneDetail.jsx
│   │   ├── utils/
│   │   │   ├── api.js
│   │   │   └── helpers.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── docs/
│   └── DOCUMENTATION.md
│
├── data.xlsx                    # Dataset HP
└── README.md
```

## 🚀 Instalasi & Menjalankan

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm atau yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Akses Aplikasi
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 Metrik Evaluasi

| Skenario | Training | Testing | Accuracy | Precision | Recall | F1-Score |
|----------|----------|---------|----------|-----------|--------|----------|
| 70-30    | 700      | 300     | ~85%     | ~82%      | ~88%   | ~85%     |
| 80-20    | 800      | 200     | ~87%     | ~84%      | ~89%   | ~86%     |

## ⚖️ Default Weights

| Atribut            | Bobot  | Keterangan                    |
|--------------------|--------|-------------------------------|
| Harga              | 25%    | Faktor paling penting         |
| RAM                | 15%    | Performa multitasking         |
| Kapasitas Baterai  | 15%    | Daya tahan penggunaan         |
| Resolusi Kamera    | 15%    | Kualitas foto/video           |
| Rating Pengguna    | 15%    | Kepuasan pengguna lain        |
| Memori Internal    | 10%    | Kapasitas penyimpanan         |
| Ukuran Layar       | 5%     | Preferensi ukuran             |

## 🔗 API Endpoints

### Recommendations
- `POST /api/v1/recommendations` - Get recommendations
- `POST /api/v1/recommendations/quick` - Quick recommendation
- `GET /api/v1/recommendations/phones` - List all phones
- `GET /api/v1/recommendations/phones/{id}` - Phone detail

### Evaluation
- `POST /api/v1/evaluation/run` - Run evaluation
- `GET /api/v1/evaluation/results` - Get results
- `GET /api/v1/evaluation/visualization-data` - Chart data

### Admin
- `GET /api/v1/admin/weights` - Get weights
- `PUT /api/v1/admin/weights` - Update weights
- `POST /api/v1/admin/phones` - Add new phone

## 📝 License

MIT License - feel free to use for educational purposes.
