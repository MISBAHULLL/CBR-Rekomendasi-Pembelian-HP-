import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    FiSearch, FiBarChart2, FiSettings, FiArrowRight,
    FiCheck, FiZap, FiTarget, FiCpu
} from 'react-icons/fi';

const features = [
    {
        icon: FiSearch,
        title: 'Rekomendasi Cerdas',
        description: 'Temukan HP terbaik berdasarkan preferensi Anda menggunakan algoritma CBR yang canggih',
    },
    {
        icon: FiTarget,
        title: 'Weighted Euclidean',
        description: 'Perhitungan similarity menggunakan bobot yang dapat disesuaikan sesuai prioritas',
    },
    {
        icon: FiBarChart2,
        title: 'Evaluasi Model',
        description: 'Visualisasi performa model dengan berbagai metrik evaluasi',
    },
    {
        icon: FiSettings,
        title: 'Kustomisasi Bobot',
        description: 'Atur bobot setiap atribut sesuai kebutuhan analisis Anda',
    },
];

const steps = [
    { number: '01', title: 'Input Preferensi', desc: 'Masukkan spesifikasi HP yang Anda inginkan' },
    { number: '02', title: 'Proses CBR', desc: 'Sistem mencari HP dengan kemiripan tertinggi' },
    { number: '03', title: 'Hasil Rekomendasi', desc: 'Dapatkan HP terbaik dengan skor similarity' },
];

export default function Home() {
    return (
        <div className="space-y-24">
            {/* Hero Section */}
            <section className="relative py-16 overflow-hidden">
                {/* Background Effects */}
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl" />
                    <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-secondary-500/20 rounded-full blur-3xl" />
                </div>

                <div className="relative text-center max-w-4xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        {/* Badge */}
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-6">
                            <FiZap className="text-primary-400" />
                            <span className="text-sm text-primary-300">Case-Based Reasoning System</span>
                        </div>

                        {/* Title */}
                        <h1 className="text-5xl md:text-7xl font-bold mb-6">
                            <span className="text-white">Temukan HP</span>
                            <br />
                            <span className="gradient-text">Impian Anda</span>
                        </h1>

                        {/* Subtitle */}
                        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
                            Sistem rekomendasi handphone cerdas menggunakan
                            <span className="text-primary-400"> Case-Based Reasoning </span>
                            dengan metode
                            <span className="text-secondary-400"> Weighted Euclidean Distance</span>
                        </p>

                        {/* CTA Buttons */}
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link to="/recommendation" className="btn-primary text-lg px-8 py-4">
                                <FiSearch className="text-xl" />
                                Mulai Rekomendasi
                                <FiArrowRight className="ml-2" />
                            </Link>
                            <Link to="/evaluation" className="btn-outline text-lg px-8 py-4">
                                <FiBarChart2 className="text-xl" />
                                Lihat Evaluasi
                            </Link>
                        </div>
                    </motion.div>

                    {/* Stats */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16"
                    >
                        {[
                            { value: '1000+', label: 'Database HP' },
                            { value: '7', label: 'Atribut Terbobot' },
                            { value: '4', label: 'Fase CBR' },
                            { value: '~90%', label: 'Akurasi' },
                        ].map((stat, idx) => (
                            <div key={idx} className="glass-card text-center py-6">
                                <div className="text-3xl font-bold gradient-text">{stat.value}</div>
                                <div className="text-gray-400 mt-1">{stat.label}</div>
                            </div>
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* Features Section */}
            <section>
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Fitur Unggulan
                    </h2>
                    <p className="text-gray-400 max-w-xl mx-auto">
                        Sistem rekomendasi berbasis CBR dengan berbagai fitur canggih
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {features.map((feature, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: idx * 0.1 }}
                            className="glass-card group"
                        >
                            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                <feature.icon className="text-2xl text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-white mb-2">
                                {feature.title}
                            </h3>
                            <p className="text-gray-400">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* How It Works Section */}
            <section>
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Cara Kerja Sistem
                    </h2>
                    <p className="text-gray-400 max-w-xl mx-auto">
                        3 langkah mudah mendapatkan rekomendasi HP terbaik
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {steps.map((step, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -30 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.5, delay: idx * 0.2 }}
                            className="relative"
                        >
                            {/* Connector Line */}
                            {idx < steps.length - 1 && (
                                <div className="hidden md:block absolute top-12 left-full w-full h-0.5 bg-gradient-to-r from-primary-500 to-transparent" />
                            )}

                            <div className="glass-card text-center">
                                <div className="text-6xl font-bold text-primary-500/20 mb-4">
                                    {step.number}
                                </div>
                                <h3 className="text-xl font-semibold text-white mb-2">
                                    {step.title}
                                </h3>
                                <p className="text-gray-400">{step.desc}</p>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* CBR Explanation Section */}
            <section className="glass-card">
                <div className="grid md:grid-cols-2 gap-12 items-center">
                    <div>
                        <h2 className="text-3xl font-bold text-white mb-6">
                            Tentang Case-Based Reasoning
                        </h2>
                        <p className="text-gray-400 mb-6">
                            CBR adalah metode penalaran berbasis kasus yang menyelesaikan masalah baru
                            dengan menggunakan pengalaman dari kasus-kasus sebelumnya.
                        </p>

                        <div className="space-y-4">
                            {[
                                { phase: 'RETRIEVE', desc: 'Mencari kasus serupa dari database' },
                                { phase: 'REUSE', desc: 'Menggunakan solusi kasus yang ditemukan' },
                                { phase: 'REVISE', desc: 'Menyesuaikan solusi jika diperlukan' },
                                { phase: 'RETAIN', desc: 'Menyimpan kasus baru untuk pembelajaran' },
                            ].map((item, idx) => (
                                <div key={idx} className="flex items-start gap-3">
                                    <div className="w-6 h-6 rounded-full bg-primary-500/20 flex items-center justify-center flex-shrink-0 mt-1">
                                        <FiCheck className="text-primary-400 text-sm" />
                                    </div>
                                    <div>
                                        <span className="font-semibold text-primary-400">{item.phase}</span>
                                        <span className="text-gray-400"> - {item.desc}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-dark-200/50 rounded-xl p-6 font-mono text-sm">
                        <div className="text-gray-500 mb-2"># Weighted Euclidean Distance</div>
                        <div className="text-green-400">
                            d(x, y) = √(Σ wᵢ × (xᵢ - yᵢ)²)
                        </div>
                        <div className="text-gray-500 mt-4 mb-2"># Similarity</div>
                        <div className="text-blue-400">
                            similarity = 1 / (1 + distance)
                        </div>
                        <div className="text-gray-500 mt-4 mb-2"># Bobot (Total = 100%)</div>
                        <div className="text-yellow-400">
                            {'{'}<br />
                            &nbsp;&nbsp;"Harga": 25%,<br />
                            &nbsp;&nbsp;"RAM": 15%,<br />
                            &nbsp;&nbsp;"Storage": 10%,<br />
                            &nbsp;&nbsp;"Baterai": 15%,<br />
                            &nbsp;&nbsp;"Kamera": 15%,<br />
                            &nbsp;&nbsp;"Layar": 5%,<br />
                            &nbsp;&nbsp;"Rating": 15%<br />
                            {'}'}
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="text-center py-12">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass-card max-w-2xl mx-auto animate-pulse-glow"
                >
                    <FiCpu className="text-5xl text-primary-400 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-white mb-4">
                        Siap Menemukan HP Impian?
                    </h2>
                    <p className="text-gray-400 mb-6">
                        Mulai sekarang dan biarkan AI membantu mencari HP terbaik untuk Anda
                    </p>
                    <Link to="/recommendation" className="btn-secondary text-lg px-8 py-4">
                        Coba Sekarang
                        <FiArrowRight className="ml-2" />
                    </Link>
                </motion.div>
            </section>
        </div>
    );
}
