// untuk styleing phone card
import { motion } from 'framer-motion';
import { formatRupiah, getSimilarityColor, getBrandConfig } from '../utils/helpers';
import { FiCpu, FiHardDrive, FiBattery, FiCamera, FiStar, FiMonitor } from 'react-icons/fi';

export default function PhoneCard({
    phone,
    similarity = null,
    rank = null,
    highlights = [],
    onClick,
    className = ''
}) {
    const brandConfig = getBrandConfig(phone.brand || phone.Brand);
    const similarityScore = similarity || phone.similarity_score;
    const phoneData = {
        name: phone.nama_hp || phone.Nama_hp || phone.name,
        brand: phone.brand || phone.Brand,
        price: phone.harga || phone.Harga || phone.price,
        ram: phone.ram || phone.Ram,
        storage: phone.memori_internal || phone.Memori_internal || phone.storage,
        battery: phone.kapasitas_baterai || phone.Kapasitas_baterai || phone.battery,
        camera: phone.resolusi_kamera || phone.Resolusi_kamera || phone.camera,
        rating: phone.rating_pengguna || phone.Rating_pengguna || phone.rating,
        screen: phone.ukuran_layar || phone.Ukuran_layar || phone.screen,
        os: phone.os || phone.Os,
        inStock: phone.stok_tersedia ?? phone.Stok_tersedia ?? true,
    };

    return (
        <motion.div
            whileHover={{ y: -5, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`phone-card cursor-pointer ${className}`}
            onClick={onClick}
        >
            {/* Rank Badge */}
            {rank && (
                <div className="absolute -top-3 -left-3 w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-lg">
                    <span className="text-white font-bold">#{rank}</span>
                </div>
            )}

            {/* Header */}
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl">{brandConfig.icon}</span>
                        <span className="badge badge-primary">{phoneData.brand}</span>
                        {!phoneData.inStock && (
                            <span className="badge bg-red-500/20 text-red-400">Stok Habis</span>
                        )}
                    </div>
                    <h3 className="text-lg font-semibold text-white truncate">
                        {phoneData.name}
                    </h3>
                </div>

                {/* Similarity Score */}
                {similarityScore && (
                    <div className="text-right">
                        <div className={`text-2xl font-bold ${getSimilarityColor(similarityScore)}`}>
                            {(similarityScore * 100).toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500">Kemiripan</div>
                    </div>
                )}
            </div>

            {/* Price */}
            <div className="mb-4">
                <span className="text-2xl font-bold gradient-text">
                    {formatRupiah(phoneData.price)}
                </span>
            </div>

            {/* Specs Grid */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <SpecItem icon={FiCpu} label="RAM" value={`${phoneData.ram} GB`} />
                <SpecItem icon={FiHardDrive} label="Storage" value={`${phoneData.storage} GB`} />
                <SpecItem icon={FiBattery} label="Baterai" value={`${phoneData.battery} mAh`} />
                <SpecItem icon={FiCamera} label="Kamera" value={phoneData.camera} />
                <SpecItem icon={FiMonitor} label="Layar" value={`${phoneData.screen}"`} />
                <SpecItem icon={FiStar} label="Rating" value={phoneData.rating?.toFixed(1)} highlight />
            </div>

            {/* OS Badge */}
            <div className="flex items-center gap-2 mb-4">
                <span className={`badge ${phoneData.os === 'iOS' ? 'badge-secondary' : 'badge-primary'}`}>
                    {phoneData.os}
                </span>
            </div>

            {/* Highlights */}
            {highlights && highlights.length > 0 && (
                <div className="border-t border-white/10 pt-4">
                    <div className="flex flex-wrap gap-2">
                        {highlights.slice(0, 3).map((highlight, idx) => (
                            <span key={idx} className="text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded-lg">
                                {highlight}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </motion.div>
    );
}

function SpecItem({ icon: Icon, label, value, highlight = false }) {
    return (
        <div className="flex items-center gap-2 p-2 bg-dark-200/50 rounded-lg">
            <Icon className={`text-lg ${highlight ? 'text-yellow-400' : 'text-gray-500'}`} />
            <div>
                <div className="text-xs text-gray-500">{label}</div>
                <div className={`text-sm font-medium ${highlight ? 'text-yellow-400' : 'text-white'}`}>
                    {value || '-'}
                </div>
            </div>
        </div>
    );
}
