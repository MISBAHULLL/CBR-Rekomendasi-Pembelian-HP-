import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiArrowLeft, FiCpu, FiHardDrive, FiBattery, FiCamera, FiStar, FiMonitor, FiCheck } from 'react-icons/fi';
import { recommendationAPI } from '../utils/api';
import { Loading, Empty } from '../components/UI';
import { formatRupiah, getSimilarityColor } from '../utils/helpers';
import PhoneCard from '../components/PhoneCard';

export default function PhoneDetail() {
    const { id } = useParams();
    const [loading, setLoading] = useState(true);
    const [phone, setPhone] = useState(null);
    const [similarPhones, setSimilarPhones] = useState([]);

    useEffect(() => {
        loadPhone();
    }, [id]);

    const loadPhone = async () => {
        try {
            setLoading(true);
            const res = await recommendationAPI.getPhoneDetail(id);
            setPhone(res.phone);
            setSimilarPhones(res.similar_phones || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Loading text="Memuat detail..." />;
    if (!phone) return <Empty icon="📱" title="HP Tidak Ditemukan" />;

    const specs = [
        { icon: FiCpu, label: 'RAM', value: `${phone.Ram} GB`, color: 'text-primary-400' },
        { icon: FiHardDrive, label: 'Storage', value: `${phone.Memori_internal} GB`, color: 'text-blue-400' },
        { icon: FiBattery, label: 'Baterai', value: `${phone.Kapasitas_baterai} mAh`, color: 'text-yellow-400' },
        { icon: FiCamera, label: 'Kamera', value: phone.Resolusi_kamera, color: 'text-pink-400' },
        { icon: FiMonitor, label: 'Layar', value: `${phone.Ukuran_layar}"`, color: 'text-cyan-400' },
        { icon: FiStar, label: 'Rating', value: phone.Rating_pengguna?.toFixed(1), color: 'text-yellow-400' },
    ];

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <Link to="/phones" className="inline-flex items-center gap-2 text-gray-400 hover:text-white">
                <FiArrowLeft /> Kembali
            </Link>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card">
                <div className="flex flex-col md:flex-row gap-8">
                    <div className="md:w-1/3 text-center">
                        <div className="text-8xl mb-4">📱</div>
                        <span className="badge badge-primary">{phone.Brand}</span>
                        <span className="badge badge-secondary ml-2">{phone.Os}</span>
                    </div>
                    <div className="md:w-2/3">
                        <h1 className="text-3xl font-bold text-white mb-2">{phone.Nama_hp}</h1>
                        <div className="text-4xl font-bold gradient-text mb-6">{formatRupiah(phone.Harga)}</div>

                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            {specs.map((spec, idx) => (
                                <div key={idx} className="p-4 bg-dark-200/50 rounded-xl">
                                    <spec.icon className={`text-2xl ${spec.color} mb-2`} />
                                    <div className="text-sm text-gray-500">{spec.label}</div>
                                    <div className="text-lg font-semibold text-white">{spec.value || '-'}</div>
                                </div>
                            ))}
                        </div>

                        <div className="flex items-center gap-2 mt-6">
                            {phone.Stok_tersedia ? (
                                <span className="badge badge-success"><FiCheck /> Stok Tersedia</span>
                            ) : (
                                <span className="badge bg-red-500/20 text-red-400">Stok Habis</span>
                            )}
                        </div>
                    </div>
                </div>
            </motion.div>

            {similarPhones.length > 0 && (
                <div>
                    <h2 className="text-2xl font-bold text-white mb-4">HP Serupa</h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {similarPhones.map((item, idx) => (
                            <motion.div key={idx} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.1 }}>
                                <Link to={`/phones/${item.phone.Id_hp}`} className="block">
                                    <div className="glass-card hover:border-primary-500/50">
                                        <div className="text-lg font-medium text-white truncate">{item.phone.Nama_hp}</div>
                                        <div className="text-primary-400">{formatRupiah(item.phone.Harga)}</div>
                                        <div className={`text-sm ${getSimilarityColor(item.similarity / 100)}`}>
                                            {item.similarity}% mirip
                                        </div>
                                    </div>
                                </Link>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
