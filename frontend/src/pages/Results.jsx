import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    FiArrowLeft, FiRefreshCw, FiFilter, FiGrid, FiList,
    FiDownload, FiShare2
} from 'react-icons/fi';
import PhoneCard from '../components/PhoneCard';
import { Empty, Loading } from '../components/UI';
import { storage, formatRupiah } from '../utils/helpers';

export default function Results() {
    const navigate = useNavigate();
    const [results, setResults] = useState(null);
    const [viewMode, setViewMode] = useState('grid');
    const [sortBy, setSortBy] = useState('similarity');

    useEffect(() => {
        const savedResults = storage.get('recommendation_results');
        if (savedResults) {
            setResults(savedResults);
        }
    }, []);

    if (!results) {
        return (
            <Empty
                icon="🔍"
                title="Belum Ada Hasil"
                description="Silakan lakukan pencarian rekomendasi terlebih dahulu"
                action={
                    <Link to="/recommendation" className="btn-primary">
                        Mulai Rekomendasi
                    </Link>
                }
            />
        );
    }

    const { recommendations, query_summary, weights_used, total_results } = results;

    // Sort recommendations
    const sortedRecommendations = [...recommendations].sort((a, b) => {
        switch (sortBy) {
            case 'price_asc':
                return (a.phone.Harga || a.phone.harga) - (b.phone.Harga || b.phone.harga);
            case 'price_desc':
                return (b.phone.Harga || b.phone.harga) - (a.phone.Harga || a.phone.harga);
            case 'rating':
                return (b.phone.Rating_pengguna || b.phone.rating_pengguna || 0) -
                    (a.phone.Rating_pengguna || a.phone.rating_pengguna || 0);
            case 'similarity':
            default:
                return b.similarity_score - a.similarity_score;
        }
    });

    const handlePhoneClick = (phone) => {
        const phoneId = phone.Id_hp || phone.id_hp;
        if (phoneId) {
            navigate(`/phones/${phoneId}`);
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <Link
                        to="/recommendation"
                        className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-2 transition-colors"
                    >
                        <FiArrowLeft />
                        Ubah Kriteria
                    </Link>
                    <h1 className="text-3xl font-bold text-white">
                        Hasil Rekomendasi
                    </h1>
                    <p className="text-gray-400 mt-1">
                        Ditemukan <span className="text-primary-400 font-semibold">{total_results}</span> HP yang cocok
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    {/* Sort Dropdown */}
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="select py-2"
                    >
                        <option value="similarity">Urutkan: Kemiripan</option>
                        <option value="price_asc">Harga Terendah</option>
                        <option value="price_desc">Harga Tertinggi</option>
                        <option value="rating">Rating Tertinggi</option>
                    </select>

                    {/* View Mode Toggle */}
                    <div className="flex bg-dark-100 rounded-lg p-1">
                        <button
                            onClick={() => setViewMode('grid')}
                            className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-primary-500 text-white' : 'text-gray-400'
                                }`}
                        >
                            <FiGrid />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-primary-500 text-white' : 'text-gray-400'
                                }`}
                        >
                            <FiList />
                        </button>
                    </div>

                    {/* Refresh */}
                    <button
                        onClick={() => navigate('/recommendation')}
                        className="btn-ghost p-2"
                        title="Cari Ulang"
                    >
                        <FiRefreshCw />
                    </button>
                </div>
            </div>

            {/* Query Summary */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card"
            >
                <h3 className="text-lg font-semibold text-white mb-4">Kriteria Pencarian</h3>
                <div className="flex flex-wrap gap-3">
                    {query_summary.budget && (
                        <span className="badge badge-primary">💰 {query_summary.budget}</span>
                    )}
                    {query_summary.ram && (
                        <span className="badge badge-secondary">🧠 RAM {query_summary.ram}</span>
                    )}
                    {query_summary.storage && (
                        <span className="badge badge-secondary">💾 {query_summary.storage}</span>
                    )}
                    {query_summary.battery && (
                        <span className="badge badge-secondary">🔋 {query_summary.battery}</span>
                    )}
                    {query_summary.os && (
                        <span className="badge badge-primary">📱 {query_summary.os}</span>
                    )}
                    {query_summary.brands && query_summary.brands.length > 0 && (
                        <span className="badge badge-success">❤️ {query_summary.brands.join(', ')}</span>
                    )}
                </div>
            </motion.div>

            {/* Weights Used */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="glass-card"
            >
                <h3 className="text-lg font-semibold text-white mb-4">Bobot yang Digunakan</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                    {Object.entries(weights_used || {}).map(([key, value]) => (
                        <div key={key} className="text-center p-3 bg-dark-200/50 rounded-lg">
                            <div className="text-xl font-bold text-primary-400">{value}%</div>
                            <div className="text-xs text-gray-500 truncate">{key.replace(/_/g, ' ')}</div>
                        </div>
                    ))}
                </div>
            </motion.div>

            {/* Results Grid/List */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className={viewMode === 'grid'
                    ? 'grid md:grid-cols-2 lg:grid-cols-3 gap-6'
                    : 'space-y-4'
                }
            >
                {sortedRecommendations.map((rec, idx) => (
                    <motion.div
                        key={rec.phone.Id_hp || rec.phone.id_hp || idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                    >
                        <PhoneCard
                            phone={rec.phone}
                            similarity={rec.similarity_score}
                            rank={sortBy === 'similarity' ? rec.rank : null}
                            highlights={rec.match_highlights}
                            onClick={() => handlePhoneClick(rec.phone)}
                            className={viewMode === 'list' ? 'flex-row' : ''}
                        />
                    </motion.div>
                ))}
            </motion.div>

            {/* Top 3 Comparison */}
            {sortedRecommendations.length >= 3 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-card"
                >
                    <h3 className="text-xl font-semibold text-white mb-6">
                        🏆 Perbandingan Top 3
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-white/10">
                                    <th className="text-left py-3 text-gray-400 font-medium">Fitur</th>
                                    {sortedRecommendations.slice(0, 3).map((rec, idx) => (
                                        <th key={idx} className="text-center py-3 text-white font-medium">
                                            #{idx + 1} {rec.phone.Nama_hp || rec.phone.nama_hp}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    { label: 'Similarity', key: 'similarity_percentage', format: v => `${v}%` },
                                    { label: 'Harga', key: 'Harga', format: formatRupiah },
                                    { label: 'RAM', key: 'Ram', format: v => `${v} GB` },
                                    { label: 'Storage', key: 'Memori_internal', format: v => `${v} GB` },
                                    { label: 'Baterai', key: 'Kapasitas_baterai', format: v => `${v} mAh` },
                                    { label: 'Kamera', key: 'Resolusi_kamera', format: v => v },
                                    { label: 'Rating', key: 'Rating_pengguna', format: v => `⭐ ${v?.toFixed(1)}` },
                                ].map((row, idx) => (
                                    <tr key={idx} className="border-b border-white/5">
                                        <td className="py-3 text-gray-400">{row.label}</td>
                                        {sortedRecommendations.slice(0, 3).map((rec, recIdx) => {
                                            const value = row.key === 'similarity_percentage'
                                                ? rec.similarity_percentage
                                                : (rec.phone[row.key] || rec.phone[row.key.toLowerCase()]);
                                            return (
                                                <td key={recIdx} className="text-center py-3 text-white">
                                                    {row.format(value)}
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </motion.div>
            )}

            {/* Actions */}
            <div className="flex flex-wrap gap-4 justify-center">
                <Link to="/recommendation" className="btn-outline">
                    <FiRefreshCw />
                    Cari Lagi
                </Link>
                <Link to="/evaluation" className="btn-outline">
                    <FiFilter />
                    Lihat Evaluasi Model
                </Link>
            </div>
        </div>
    );
}
