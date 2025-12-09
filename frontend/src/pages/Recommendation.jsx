import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
    FiSearch, FiSliders, FiDollarSign, FiCpu,
    FiHardDrive, FiBattery, FiCamera, FiStar,
    FiMonitor, FiHeart, FiInfo
} from 'react-icons/fi';
import { recommendationAPI, adminAPI } from '../utils/api';
import { formatRupiah, validateWeights, storage } from '../utils/helpers';
import { Loading } from '../components/UI';

export default function Recommendation() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [brands, setBrands] = useState([]);
    const [priceRanges, setPriceRanges] = useState(null);
    const [weights, setWeights] = useState(null);
    const [showAdvanced, setShowAdvanced] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        min_harga: null,
        max_harga: 10000000,
        ram: 8,
        memori_internal: 128,
        min_baterai: 4500,
        resolusi_kamera: '48MP',
        ukuran_layar: 6.5,
        min_rating: 4.0,
        preferred_brands: [],
        preferred_os: null,
        custom_weights: null,
    });

    // Load initial data
    useEffect(() => {
        const loadData = async () => {
            try {
                const [brandsRes, priceRes, weightsRes] = await Promise.all([
                    recommendationAPI.getBrands(),
                    recommendationAPI.getPriceRanges(),
                    adminAPI.getWeights(),
                ]);

                setBrands(brandsRes.brands || []);
                setPriceRanges(priceRes);
                setWeights(weightsRes.weights);

                // Load saved preferences
                const saved = storage.get('recommendation_prefs');
                if (saved) {
                    setFormData(prev => ({ ...prev, ...saved }));
                }
            } catch (error) {
                console.error('Error loading data:', error);
            }
        };

        loadData();
    }, []);

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleBrandToggle = (brand) => {
        setFormData(prev => {
            const brands = prev.preferred_brands || [];
            const newBrands = brands.includes(brand)
                ? brands.filter(b => b !== brand)
                : [...brands, brand];
            return { ...prev, preferred_brands: newBrands };
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            // Save preferences
            storage.set('recommendation_prefs', formData);

            // Prepare request
            const specs = {
                min_harga: formData.min_harga,
                max_harga: formData.max_harga,
                ram: formData.ram,
                memori_internal: formData.memori_internal,
                min_baterai: formData.min_baterai,
                resolusi_kamera: formData.resolusi_kamera,
                ukuran_layar: formData.ukuran_layar,
                min_rating: formData.min_rating,
                preferred_brands: formData.preferred_brands.length > 0 ? formData.preferred_brands : null,
                preferred_os: formData.preferred_os,
                custom_weights: formData.custom_weights,
            };

            const result = await recommendationAPI.getRecommendations(specs, 10, 0.2);

            if (result.success && result.recommendations.length > 0) {
                // Store results and navigate
                storage.set('recommendation_results', result);
                navigate('/results');
                toast.success(`Ditemukan ${result.recommendations.length} rekomendasi!`);
            } else {
                toast.error('Tidak ditemukan HP yang sesuai. Coba ubah kriteria.');
            }
        } catch (error) {
            toast.error(error.message || 'Terjadi kesalahan');
        } finally {
            setLoading(false);
        }
    };

    const cameraOptions = ['8MP', '12MP', '16MP', '24MP', '32MP', '48MP', '50MP', '64MP', '108MP', '200MP'];
    const ramOptions = [2, 3, 4, 6, 8, 12, 16, 18, 24];
    const storageOptions = [32, 64, 128, 256, 512, 1024];

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h1 className="text-4xl font-bold text-white mb-4">
                        Cari HP <span className="gradient-text">Impian</span>
                    </h1>
                    <p className="text-gray-400 max-w-xl mx-auto">
                        Masukkan spesifikasi yang Anda inginkan, sistem akan mencari HP
                        dengan kemiripan tertinggi menggunakan algoritma CBR
                    </p>
                </motion.div>
            </div>

            <motion.form
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                onSubmit={handleSubmit}
                className="space-y-8"
            >
                {/* Budget Section */}
                <div className="glass-card">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                            <FiDollarSign className="text-green-400 text-xl" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-white">Budget</h2>
                            <p className="text-sm text-gray-500">Tentukan range harga yang sesuai</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="input-label">Budget Maksimum: {formatRupiah(formData.max_harga)}</label>
                            <input
                                type="range"
                                min={priceRanges?.min_price || 500000}
                                max={priceRanges?.max_price || 50000000}
                                step={500000}
                                value={formData.max_harga}
                                onChange={(e) => handleInputChange('max_harga', parseInt(e.target.value))}
                                className="range-slider"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>{formatRupiah(priceRanges?.min_price || 500000)}</span>
                                <span>{formatRupiah(priceRanges?.max_price || 50000000)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Specifications Section */}
                <div className="glass-card">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                            <FiCpu className="text-primary-400 text-xl" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-white">Spesifikasi</h2>
                            <p className="text-sm text-gray-500">Pilih spesifikasi yang diinginkan</p>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        {/* RAM */}
                        <div>
                            <label className="input-label flex items-center gap-2">
                                <FiCpu className="text-primary-400" />
                                RAM
                            </label>
                            <select
                                value={formData.ram}
                                onChange={(e) => handleInputChange('ram', parseInt(e.target.value))}
                                className="select"
                            >
                                {ramOptions.map(ram => (
                                    <option key={ram} value={ram}>{ram} GB</option>
                                ))}
                            </select>
                        </div>

                        {/* Storage */}
                        <div>
                            <label className="input-label flex items-center gap-2">
                                <FiHardDrive className="text-blue-400" />
                                Storage Internal
                            </label>
                            <select
                                value={formData.memori_internal}
                                onChange={(e) => handleInputChange('memori_internal', parseInt(e.target.value))}
                                className="select"
                            >
                                {storageOptions.map(storage => (
                                    <option key={storage} value={storage}>{storage >= 1024 ? `${storage / 1024} TB` : `${storage} GB`}</option>
                                ))}
                            </select>
                        </div>

                        {/* Battery */}
                        <div>
                            <label className="input-label flex items-center gap-2">
                                <FiBattery className="text-yellow-400" />
                                Baterai Minimum: {formData.min_baterai} mAh
                            </label>
                            <input
                                type="range"
                                min={3000}
                                max={7000}
                                step={500}
                                value={formData.min_baterai}
                                onChange={(e) => handleInputChange('min_baterai', parseInt(e.target.value))}
                                className="range-slider"
                            />
                        </div>

                        {/* Camera */}
                        <div>
                            <label className="input-label flex items-center gap-2">
                                <FiCamera className="text-pink-400" />
                                Resolusi Kamera
                            </label>
                            <select
                                value={formData.resolusi_kamera}
                                onChange={(e) => handleInputChange('resolusi_kamera', e.target.value)}
                                className="select"
                            >
                                {cameraOptions.map(cam => (
                                    <option key={cam} value={cam}>{cam}</option>
                                ))}
                            </select>
                        </div>

                        {/* Screen Size */}
                        <div>
                            <label className="input-label flex items-center gap-2">
                                <FiMonitor className="text-cyan-400" />
                                Ukuran Layar: {formData.ukuran_layar}"
                            </label>
                            <input
                                type="range"
                                min={5.0}
                                max={7.5}
                                step={0.1}
                                value={formData.ukuran_layar}
                                onChange={(e) => handleInputChange('ukuran_layar', parseFloat(e.target.value))}
                                className="range-slider"
                            />
                        </div>

                        {/* Rating */}
                        <div>
                            <label className="input-label flex items-center gap-2">
                                <FiStar className="text-yellow-400" />
                                Rating Minimum: {formData.min_rating}
                            </label>
                            <input
                                type="range"
                                min={1}
                                max={5}
                                step={0.1}
                                value={formData.min_rating}
                                onChange={(e) => handleInputChange('min_rating', parseFloat(e.target.value))}
                                className="range-slider"
                            />
                        </div>
                    </div>
                </div>

                {/* Preferences Section */}
                <div className="glass-card">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                            <FiHeart className="text-pink-400 text-xl" />
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-white">Preferensi (Opsional)</h2>
                            <p className="text-sm text-gray-500">Tambahkan preferensi untuk hasil lebih akurat</p>
                        </div>
                    </div>

                    {/* OS Preference */}
                    <div className="mb-6">
                        <label className="input-label">Sistem Operasi</label>
                        <div className="flex gap-4">
                            {['Android', 'iOS'].map(os => (
                                <button
                                    key={os}
                                    type="button"
                                    onClick={() => handleInputChange('preferred_os', formData.preferred_os === os ? null : os)}
                                    className={`px-6 py-3 rounded-xl border-2 transition-all ${formData.preferred_os === os
                                            ? 'border-primary-500 bg-primary-500/20 text-primary-400'
                                            : 'border-white/10 text-gray-400 hover:border-white/30'
                                        }`}
                                >
                                    {os === 'iOS' ? '🍎' : '🤖'} {os}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Brand Preference */}
                    <div>
                        <label className="input-label">Brand Favorit (pilih beberapa)</label>
                        <div className="flex flex-wrap gap-2">
                            {brands.map(brand => (
                                <button
                                    key={brand}
                                    type="button"
                                    onClick={() => handleBrandToggle(brand)}
                                    className={`px-4 py-2 rounded-lg border transition-all ${formData.preferred_brands?.includes(brand)
                                            ? 'border-secondary-500 bg-secondary-500/20 text-secondary-400'
                                            : 'border-white/10 text-gray-400 hover:border-white/30'
                                        }`}
                                >
                                    {brand}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Advanced Settings Toggle */}
                <button
                    type="button"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                >
                    <FiSliders />
                    <span>{showAdvanced ? 'Sembunyikan' : 'Tampilkan'} Pengaturan Lanjutan</span>
                </button>

                {/* Advanced Settings */}
                {showAdvanced && weights && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="glass-card"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                                <FiSliders className="text-purple-400 text-xl" />
                            </div>
                            <div>
                                <h2 className="text-xl font-semibold text-white">Bobot Atribut</h2>
                                <p className="text-sm text-gray-500">Sesuaikan bobot untuk setiap atribut (total 100%)</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg mb-6">
                            <FiInfo className="text-blue-400 flex-shrink-0" />
                            <p className="text-sm text-blue-300">
                                Bobot default sudah dioptimalkan. Ubah hanya jika diperlukan.
                            </p>
                        </div>

                        <div className="text-center text-gray-500 text-sm">
                            Fitur custom weights tersedia di halaman Admin
                        </div>
                    </motion.div>
                )}

                {/* Submit Button */}
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    disabled={loading}
                    className="w-full btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <>
                            <div className="spinner w-5 h-5 border-2" />
                            <span>Mencari...</span>
                        </>
                    ) : (
                        <>
                            <FiSearch className="text-xl" />
                            <span>Cari Rekomendasi</span>
                        </>
                    )}
                </motion.button>
            </motion.form>
        </div>
    );
}
