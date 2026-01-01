"""
Loader untuk dataset HP dari file Excel
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Loader untuk dataset HP dari Excel dengan validasi."""
    
    # Kolom yang diharapkan dalam dataset
    REQUIRED_COLUMNS = [
        'Id_hp', 'Nama_hp', 'Brand', 'Harga', 'Ram', 
        'Memori_internal', 'Ukuran_layar', 'Resolusi_kamera',
        'Kapasitas_baterai', 'Os', 'Rating_pengguna'
    ]
    
    # Kolom opsional
    OPTIONAL_COLUMNS = ['Tahun_rilis', 'Stok_tersedia']
    
    def __init__(self, file_path: str):
        """
        Inisialisasi DataLoader.
        
        Args:
            file_path: Path ke file Excel dataset
        """
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.is_loaded = False
        self._validation_errors: List[str] = []
        
    def load(self, validate: bool = True) -> pd.DataFrame:
        """
        Memuat dataset dari file Excel.
        
        Args:
            validate: Apakah perlu validasi setelah load
            
        Returns:
            DataFrame berisi data handphone
            
        Raises:
            FileNotFoundError: Jika file tidak ditemukan
            ValueError: Jika struktur data tidak valid
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Dataset tidak ditemukan: {self.file_path}")
        
        logger.info(f"Loading dataset dari {self.file_path}")
        
        try:
            # Load Excel file
            self.df = pd.read_excel(self.file_path, engine='openpyxl')
            logger.info(f"Berhasil memuat {len(self.df)} baris data")
            
            if validate:
                self._validate_dataset()
                
            self.is_loaded = True
            return self.df
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def _validate_dataset(self) -> bool:
        """
        Validasi struktur dan isi dataset.
        
        Returns:
            True jika valid, False jika ada error
        """
        self._validation_errors = []
        
        # Check required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
        if missing_cols:
            self._validation_errors.append(
                f"Kolom yang diperlukan tidak ada: {missing_cols}"
            )
        
        # Check data types
        if 'Harga' in self.df.columns:
            if not pd.api.types.is_numeric_dtype(self.df['Harga']):
                self._validation_errors.append("Kolom 'Harga' harus berupa angka")
        
        if 'Ram' in self.df.columns:
            if not pd.api.types.is_numeric_dtype(self.df['Ram']):
                self._validation_errors.append("Kolom 'Ram' harus berupa angka")
        
        # Check for null values in critical columns
        critical_cols = ['Id_hp', 'Nama_hp', 'Harga']
        for col in critical_cols:
            if col in self.df.columns and self.df[col].isnull().any():
                null_count = self.df[col].isnull().sum()
                self._validation_errors.append(
                    f"Kolom '{col}' memiliki {null_count} nilai kosong"
                )
        
        if self._validation_errors:
            for error in self._validation_errors:
                logger.warning(f"Validation Warning: {error}")
            return False
        
        logger.info("Dataset validation passed!")
        return True
    
    def get_validation_errors(self) -> List[str]:
        """Mendapatkan list error validasi."""
        return self._validation_errors
    
    def get_statistics(self) -> Dict:
        """
        Mendapatkan statistik dataset.
        
        Returns:
            Dictionary berisi statistik dataset
        """
        if not self.is_loaded:
            raise ValueError("Dataset belum dimuat. Panggil load() terlebih dahulu.")
        
        stats = {
            "total_phones": len(self.df),
            "total_columns": len(self.df.columns),
            "columns": list(self.df.columns),
            "brands": self.df['Brand'].nunique() if 'Brand' in self.df.columns else 0,
            "brand_list": self.df['Brand'].unique().tolist() if 'Brand' in self.df.columns else [],
            "price_range": {
                "min": int(self.df['Harga'].min()) if 'Harga' in self.df.columns else 0,
                "max": int(self.df['Harga'].max()) if 'Harga' in self.df.columns else 0,
                "mean": int(self.df['Harga'].mean()) if 'Harga' in self.df.columns else 0
            },
            "ram_options": sorted(self.df['Ram'].unique().tolist()) if 'Ram' in self.df.columns else [],
            "storage_options": sorted(self.df['Memori_internal'].unique().tolist()) if 'Memori_internal' in self.df.columns else [],
            "missing_values": self.df.isnull().sum().to_dict()
        }
        
        return stats
    
    def get_unique_values(self, column: str) -> List:
        """
        Mendapatkan nilai unik dari suatu kolom.
        
        Args:
            column: Nama kolom
            
        Returns:
            List nilai unik
        """
        if not self.is_loaded:
            self.load()
        
        if column not in self.df.columns:
            raise ValueError(f"Kolom '{column}' tidak ditemukan dalam dataset")
        
        return self.df[column].dropna().unique().tolist()
    
    def filter_by_criteria(self, criteria: Dict) -> pd.DataFrame:
        """
        Filter dataset berdasarkan kriteria tertentu.
        
        Args:
            criteria: Dictionary berisi kondisi filter
                     contoh: {"Brand": "Samsung", "Ram": 8}
        
        Returns:
            DataFrame hasil filter
        """
        if not self.is_loaded:
            self.load()
        
        filtered_df = self.df.copy()
        
        for column, value in criteria.items():
            if column not in filtered_df.columns:
                continue
                
            if isinstance(value, dict):
                # Handle range filter
                if 'min' in value:
                    filtered_df = filtered_df[filtered_df[column] >= value['min']]
                if 'max' in value:
                    filtered_df = filtered_df[filtered_df[column] <= value['max']]
            elif isinstance(value, list):
                # Handle multiple values
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:
                # Exact match
                filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def add_new_case(self, phone_data: Dict) -> bool:
        """
        Menambahkan kasus baru ke dataset (RETAIN phase).
        
        Args:
            phone_data: Dictionary berisi data HP baru
            
        Returns:
            True jika berhasil
        """
        if not self.is_loaded:
            self.load()
        
        # Generate new ID
        new_id = self.df['Id_hp'].max() + 1
        phone_data['Id_hp'] = new_id
        
        # Add to DataFrame
        new_row = pd.DataFrame([phone_data])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        
        # Save to Excel
        self.df.to_excel(self.file_path, index=False, engine='openpyxl')
        
        logger.info(f"Case baru ditambahkan dengan ID: {new_id}")
        return True
    
    def to_dict_list(self) -> List[Dict]:
        """
        Convert DataFrame ke list of dictionaries.
        
        Returns:
            List of dictionaries, masing-masing merepresentasikan satu HP
        """
        if not self.is_loaded:
            self.load()
        
        return self.df.to_dict('records')
    
    def split_train_test(
        self, 
        train_ratio: float = 0.7, 
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Membagi dataset menjadi training dan testing.
        
        Args:
            train_ratio: Proporsi data training (default 0.7 = 70%)
            random_state: Seed untuk reproducibility
            
        Returns:
            Tuple (train_df, test_df)
        """
        if not self.is_loaded:
            self.load()
        
        # Shuffle data
        shuffled_df = self.df.sample(frac=1, random_state=random_state).reset_index(drop=True)
        
        # Calculate split point
        split_idx = int(len(shuffled_df) * train_ratio)
        
        train_df = shuffled_df[:split_idx]
        test_df = shuffled_df[split_idx:]
        
        logger.info(f"Data split: Training={len(train_df)}, Testing={len(test_df)}")
        
        return train_df, test_df


# Singleton instance untuk reuse
_data_loader_instance: Optional[DataLoader] = None

def get_data_loader(file_path: str = None) -> DataLoader:
    """
    Factory function untuk mendapatkan DataLoader instance.
    
    Args:
        file_path: Path ke file dataset
        
    Returns:
        DataLoader instance
    """
    global _data_loader_instance
    
    if _data_loader_instance is None:
        if file_path is None:
            from ..config import settings
            file_path = settings.DATASET_PATH
        _data_loader_instance = DataLoader(file_path)
    
    return _data_loader_instance
