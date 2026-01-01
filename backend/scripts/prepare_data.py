"""
Script persiapan dataset - load, label, preprocess, dan split data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.preprocessing import DataPreprocessor


def add_label_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menambahkan kolom label berdasarkan karakteristik HP.
    
    Kategori:
    - Gaming: RAM >= 8GB AND Kapasitas_baterai >= 5000 AND Harga >= 5,000,000
    - Photographer: Resolusi_kamera (MP) >= 48 AND Rating >= 4.0
    - Daily: Semua HP lainnya (penggunaan sehari-hari)
    
    Args:
        df: DataFrame dengan data HP
        
    Returns:
        DataFrame dengan kolom 'Label' tambahan
    """
    def parse_camera_mp(resolution):
        """Parse resolusi kamera ke nilai MP."""
        if pd.isna(resolution):
            return 0
        resolution_str = str(resolution).upper()
        # Extract MP value
        import re
        match = re.search(r'(\d+)\s*MP', resolution_str)
        if match:
            return int(match.group(1))
        # Try to extract just number
        match = re.search(r'(\d+)', resolution_str)
        if match:
            return int(match.group(1))
        return 0
    
    def determine_label(row):
        """
        Menentukan label berdasarkan spesifikasi HP.
        
        Menggunakan kombinasi harga dan spesifikasi untuk klasifikasi yang lebih akurat:
        - Gaming: HP dengan spesifikasi tinggi (RAM >= 8, baterai >= 5000) DAN harga premium
        - Photographer: HP dengan kamera bagus (>= 48MP) DAN rating tinggi
        - Daily: HP budget hingga mid-range untuk penggunaan sehari-hari
        """
        ram = row.get('Ram', 0) or 0
        baterai = row.get('Kapasitas_baterai', 0) or 0
        harga = row.get('Harga', 0) or 0
        rating = row.get('Rating_pengguna', 0) or 0
        storage = row.get('Memori_internal', 0) or 0
        
        # Parse kamera
        kamera_mp = parse_camera_mp(row.get('Resolusi_kamera', ''))
        
        # Gaming: High-end specs focused
        # RAM tinggi + Baterai besar + Storage besar = Gaming oriented
        gaming_score = 0
        if ram >= 8:
            gaming_score += 2
        if baterai >= 5000:
            gaming_score += 1
        if storage >= 256:
            gaming_score += 1
        if harga >= 7000000:  # Premium price
            gaming_score += 1
        
        if gaming_score >= 4:
            return 'Gaming'
        
        # Photographer: Camera focused
        # Kamera bagus + Rating tinggi = Photography oriented
        photo_score = 0
        if kamera_mp >= 64:
            photo_score += 2
        elif kamera_mp >= 48:
            photo_score += 1
        if rating >= 4.3:
            photo_score += 1
        if harga >= 5000000:  # Mid to premium
            photo_score += 1
            
        if photo_score >= 3 and gaming_score < 4:
            return 'Photographer'
        
        # Daily: Everything else (Budget to mid-range)
        return 'Daily'
    
    df['Label'] = df.apply(determine_label, axis=1)
    return df


def save_raw_data(df: pd.DataFrame, output_path: Path) -> None:
    """Simpan data mentah ke CSV."""
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[OK] Raw data saved to: {output_path}")
    print(f"  - Total records: {len(df)}")
    print(f"  - Labels distribution:")
    for label, count in df['Label'].value_counts().items():
        print(f"    - {label}: {count}")


def preprocess_and_save(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """Preprocess data dan simpan ke CSV."""
    preprocessor = DataPreprocessor()
    
    # Handle missing values dan normalisasi
    df_clean = preprocessor.handle_missing_values(df.copy())
    df_clean = preprocessor.add_camera_numeric(df_clean)
    
    # Fit dan transform untuk normalisasi
    preprocessor.fit(df_clean)
    
    # Simpan data clean (tanpa normalisasi untuk readability)
    df_clean.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[OK] Clean data saved to: {output_path}")
    
    return df_clean


def split_and_save(df: pd.DataFrame, output_dir: Path, train_ratio: float, random_state: int = 42) -> tuple:
    """Split data dan simpan ke CSV."""
    from sklearn.model_selection import train_test_split
    
    train_df, test_df = train_test_split(
        df, 
        train_size=train_ratio, 
        random_state=random_state,
        stratify=df['Label']  # Stratified split untuk menjaga distribusi label
    )
    
    scenario_name = f"{int(round(train_ratio * 100))}-{int(round((1 - train_ratio) * 100))}"
    
    train_path = output_dir / f"train_{scenario_name}.csv"
    test_path = output_dir / f"test_{scenario_name}.csv"
    
    train_df.to_csv(train_path, index=False, encoding='utf-8')
    test_df.to_csv(test_path, index=False, encoding='utf-8')
    
    print(f"[OK] Split {scenario_name} saved:")
    print(f"  - Training: {train_path} ({len(train_df)} records)")
    print(f"  - Testing: {test_path} ({len(test_df)} records)")
    
    return train_df, test_df


def main():
    """Main function untuk menjalankan persiapan data."""
    print("=" * 60)
    print("CBR Phone Recommendation - Data Preparation")
    print("=" * 60)
    print()
    
    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    data_xlsx = base_dir / "data.xlsx"
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    
    # Create directories if not exist
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Base directory: {base_dir}")
    print(f"Dataset: {data_xlsx}")
    print()
    
    # Step 1: Load data
    print("Step 1: Loading data from Excel...")
    df = pd.read_excel(data_xlsx)
    print(f"[OK] Loaded {len(df)} records with {len(df.columns)} columns")
    print(f"  Columns: {list(df.columns)}")
    print()
    
    # Step 2: Add label column
    print("Step 2: Adding label column (Gaming/Photographer/Daily)...")
    df = add_label_column(df)
    print()
    
    # Step 3: Save raw data
    print("Step 3: Saving raw data with labels...")
    raw_path = raw_dir / "hp_dataset_raw.csv"
    save_raw_data(df, raw_path)
    print()
    
    # Step 4: Preprocess and save clean data
    print("Step 4: Preprocessing data...")
    clean_path = processed_dir / "hp_dataset_clean.csv"
    df_clean = preprocess_and_save(df, clean_path)
    print()
    
    # Step 5: Split data for 70-30 scenario
    print("Step 5: Splitting data (70-30 scenario)...")
    split_and_save(df_clean, processed_dir, train_ratio=0.7)
    print()
    
    # Step 6: Split data for 80-20 scenario
    print("Step 6: Splitting data (80-20 scenario)...")
    split_and_save(df_clean, processed_dir, train_ratio=0.8)
    print()
    
    print("=" * 60)
    print("[SUCCESS] Data preparation completed successfully!")
    print("=" * 60)
    
    # Also update the original Excel file with label column
    print()
    print("Bonus: Updating original data.xlsx with Label column...")
    df.to_excel(data_xlsx, index=False)
    print(f"[OK] Updated: {data_xlsx}")


if __name__ == "__main__":
    main()
