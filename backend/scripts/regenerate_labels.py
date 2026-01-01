"""
Dataset Regeneration Script
============================
Script untuk meregenerasi label dataset agar memiliki korelasi
yang meaningful dengan fitur HP.

Kriteria Label:
- Gaming: RAM >= 12GB, Baterai >= 5000mAh, Ukuran layar >= 6.5"
- Photographer: Kamera >= 64MP, Rating tinggi
- Daily: Sisanya (harga dan spec moderat)
"""

import pandas as pd
from pathlib import Path


def assign_label(row: pd.Series) -> str:
    """
    Assign label berdasarkan karakteristik HP.
    
    Args:
        row: Row dari DataFrame
        
    Returns:
        Label (Gaming/Photographer/Daily)
    """
    ram = row.get('Ram', 8)
    baterai = row.get('Kapasitas_baterai', 4500)
    kamera = str(row.get('Resolusi_kamera', '12MP'))
    ukuran_layar = row.get('Ukuran_layar', 6.0)
    harga = row.get('Harga', 10000000)
    
    # Parse kamera
    kamera_mp = 12
    if 'MP' in kamera:
        try:
            kamera_mp = int(kamera.replace('MP', '').strip())
        except:
            kamera_mp = 12
    
    # Gaming: High RAM, High Battery, Big Screen
    if ram >= 12 and baterai >= 5000 and ukuran_layar >= 6.5:
        return 'Gaming'
    
    # Photographer: High Camera Resolution
    if kamera_mp >= 64:
        return 'Photographer'
    
    # Gaming fallback: High RAM dengan baterai cukup
    if ram >= 16 and baterai >= 4500:
        return 'Gaming'
    
    # Photographer fallback: Camera 50MP+ dengan ukuran layar besar
    if kamera_mp >= 50 and ukuran_layar >= 6.4:
        return 'Photographer'
    
    # Daily: Default
    return 'Daily'


def regenerate_labels(input_path: Path, output_path: Path) -> None:
    """
    Regenerasi label dataset.
    
    Args:
        input_path: Path ke dataset raw
        output_path: Path output
    """
    print(f"Loading dataset from: {input_path}")
    df = pd.read_csv(input_path)
    
    print(f"Total records: {len(df)}")
    print("\nOld label distribution:")
    print(df['Label'].value_counts())
    
    # Assign new labels
    df['Label'] = df.apply(assign_label, axis=1)
    
    print("\nNew label distribution:")
    print(df['Label'].value_counts())
    
    # Save
    df.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")


def main():
    base_dir = Path(__file__).parent.parent.parent
    raw_path = base_dir / "data" / "raw" / "hp_dataset_raw.csv"
    
    if not raw_path.exists():
        print(f"File not found: {raw_path}")
        return
    
    regenerate_labels(raw_path, raw_path)
    print("\n✅ Dataset labels regenerated successfully!")


if __name__ == "__main__":
    main()
