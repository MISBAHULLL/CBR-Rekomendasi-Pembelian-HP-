import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import {
    FiSave, FiRefreshCw, FiSliders, FiDatabase,
    FiTrendingUp, FiPlusCircle, FiTrash2, FiInfo
} from 'react-icons/fi';
import { adminAPI, recommendationAPI } from '../utils/api';
import { Loading, Error as ErrorComponent } from '../components/UI';
import { validateWeights, formatRupiah, formatNumber } from '../utils/helpers';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function Admin() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [weights, setWeights] = useState({});
    const [originalWeights, setOriginalWeights] = useState({});
    const [presets, setPresets] = useState({});
    const [dashboard, setDashboard] = useState(null);
    const [activeTab, setActiveTab] = useState('weights');

    // Form for adding new phone
    const [newPhone, setNewPhone] = useState({
        nama_hp: '',
        brand: '',
        harga: 0,
        ram: 8,
        memori_internal: 128,
        ukuran_layar: 6.5,
        resolusi_kamera: '48MP',
        kapasitas_baterai: 5000,
        os: 'Android',
        rating_pengguna: 4.0,
        stok_tersedia: true,
    });

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [weightsRes, presetsRes, dashboardRes] = await Promise.all([
                adminAPI.getWeights(),
                adminAPI.getWeightPresets(),
                adminAPI.getDashboard(),
            ]);

            setWeights(weightsRes.weights);
            setOriginalWeights(weightsRes.weights);
            setPresets(presetsRes.presets);
            setDashboard(dashboardRes);
        } catch (error) {
            toast.error('Gagal memuat data');
        } finally {
            setLoading(false);
        }
    };

    const handleWeightChange = (key, value) => {
        setWeights(prev => ({
            ...prev,
            [key]: parseFloat(value) || 0,
        }));
    };

    const applyPreset = (presetKey) => {
        const preset = presets[presetKey];
        if (preset) {
            setWeights(preset.weights);
            toast.success(`Preset "${preset.name}" diterapkan`);
        }
    };

    const saveWeights = async () => {
        const validation = validateWeights(weights);
        if (!validation.isValid) {
            toast.error(validation.message);
            return;
        }

        try {
            setSaving(true);
            await adminAPI.updateWeights(weights);
            setOriginalWeights(weights);
            toast.success('Bobot berhasil disimpan');
        } catch (error) {
            toast.error('Gagal menyimpan bobot');
        } finally {
            setSaving(false);
        }
    };

    const resetWeights = async () => {
        try {
            const result = await adminAPI.resetWeights();
            setWeights(result.new_weights);
            setOriginalWeights(result.new_weights);
            toast.success('Bobot direset ke default');
        } catch (error) {
            toast.error('Gagal mereset bobot');
        }
    };

    const handleAddPhone = async (e) => {
        e.preventDefault();
        try {
            await adminAPI.addPhone(newPhone);
            toast.success('HP berhasil ditambahkan');
            setNewPhone({
                nama_hp: '',
                brand: '',
                harga: 0,
                ram: 8,
                memori_internal: 128,
                ukuran_layar: 6.5,
                resolusi_kamera: '48MP',
                kapasitas_baterai: 5000,
                os: 'Android',
                rating_pengguna: 4.0,
                stok_tersedia: true,
            });
            loadData();
        } catch (error) {
            toast.error('Gagal menambahkan HP');
        }
    };

    if (loading) {
        return <Loading text="Memuat dashboard admin..." />;
    }

    const totalWeight = Object.values(weights).reduce((sum, val) => sum + val, 0);
    const isChanged = JSON.stringify(weights) !== JSON.stringify(originalWeights);

    // Prepare chart data
    const weightChartData = {
        labels: Object.keys(weights).map(k => k.replace(/_/g, ' ')),
        datasets: [{
            data: Object.values(weights),
            backgroundColor: [
                'rgba(99, 102, 241, 0.8)',
                'rgba(20, 184, 166, 0.8)',
                'rgba(245, 158, 11, 0.8)',
                'rgba(236, 72, 153, 0.8)',
                'rgba(139, 92, 246, 0.8)',
                'rgba(6, 182, 212, 0.8)',
                'rgba(34, 197, 94, 0.8)',
            ],
            borderWidth: 0,
        }],
    };

    const brandChartData = dashboard?.distributions?.by_brand ? {
        labels: Object.keys(dashboard.distributions.by_brand).slice(0, 6),
        datasets: [{
            data: Object.values(dashboard.distributions.by_brand).slice(0, 6),
            backgroundColor: [
                'rgba(99, 102, 241, 0.8)',
                'rgba(20, 184, 166, 0.8)',
                'rgba(245, 158, 11, 0.8)',
                'rgba(236, 72, 153, 0.8)',
                'rgba(139, 92, 246, 0.8)',
                'rgba(6, 182, 212, 0.8)',
            ],
            borderWidth: 0,
        }],
    } : null;

    const tabs = [
        { id: 'weights', label: 'Pengaturan Bobot', icon: FiSliders },
        { id: 'database', label: 'Database HP', icon: FiDatabase },
        { id: 'add', label: 'Tambah HP', icon: FiPlusCircle },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white">
                    Admin <span className="gradient-text">Dashboard</span>
                </h1>
                <p className="text-gray-400 mt-1">
                    Kelola bobot atribut dan database HP
                </p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total HP', value: dashboard?.overview?.total_phones || 0, icon: '📱' },
                    { label: 'Total Brand', value: dashboard?.overview?.total_brands || 0, icon: '🏷️' },
                    { label: 'Harga Min', value: formatRupiah(dashboard?.overview?.price_range?.min), icon: '💰' },
                    { label: 'Harga Max', value: formatRupiah(dashboard?.overview?.price_range?.max), icon: '💎' },
                ].map((stat, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="glass-card text-center"
                    >
                        <div className="text-3xl mb-2">{stat.icon}</div>
                        <div className="text-2xl font-bold text-white">{stat.value}</div>
                        <div className="text-sm text-gray-500">{stat.label}</div>
                    </motion.div>
                ))}
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-white/10 pb-2">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeTab === tab.id
                                ? 'bg-primary-500/20 text-primary-400'
                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <tab.icon />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'weights' && (
                <div className="grid lg:grid-cols-3 gap-6">
                    {/* Weight Sliders */}
                    <div className="lg:col-span-2 space-y-6">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="glass-card"
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-semibold text-white">Pengaturan Bobot</h2>
                                <div className={`px-3 py-1 rounded-full text-sm font-medium ${Math.abs(totalWeight - 100) < 1
                                        ? 'bg-green-500/20 text-green-400'
                                        : 'bg-red-500/20 text-red-400'
                                    }`}>
                                    Total: {totalWeight.toFixed(1)}%
                                </div>
                            </div>

                            <div className="flex items-center gap-2 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg mb-6">
                                <FiInfo className="text-blue-400 flex-shrink-0" />
                                <p className="text-sm text-blue-300">
                                    Total bobot harus 100%. Tidak boleh ada bobot bernilai 0.
                                </p>
                            </div>

                            <div className="space-y-4">
                                {Object.entries(weights).map(([key, value]) => (
                                    <div key={key}>
                                        <div className="flex items-center justify-between mb-2">
                                            <label className="text-gray-300 font-medium">
                                                {key.replace(/_/g, ' ')}
                                            </label>
                                            <div className="flex items-center gap-2">
                                                <input
                                                    type="number"
                                                    min="1"
                                                    max="100"
                                                    value={value}
                                                    onChange={(e) => handleWeightChange(key, e.target.value)}
                                                    className="w-20 px-2 py-1 bg-dark-200 border border-white/10 rounded text-center text-white"
                                                />
                                                <span className="text-gray-500">%</span>
                                            </div>
                                        </div>
                                        <input
                                            type="range"
                                            min="1"
                                            max="50"
                                            step="1"
                                            value={value}
                                            onChange={(e) => handleWeightChange(key, e.target.value)}
                                            className="range-slider"
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="flex gap-3 mt-6 pt-6 border-t border-white/10">
                                <button
                                    onClick={saveWeights}
                                    disabled={saving || !isChanged}
                                    className="btn-primary flex-1 disabled:opacity-50"
                                >
                                    {saving ? (
                                        <>
                                            <div className="spinner w-5 h-5 border-2" />
                                            Menyimpan...
                                        </>
                                    ) : (
                                        <>
                                            <FiSave />
                                            Simpan Perubahan
                                        </>
                                    )}
                                </button>
                                <button onClick={resetWeights} className="btn-outline">
                                    <FiRefreshCw />
                                    Reset
                                </button>
                            </div>
                        </motion.div>

                        {/* Presets */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.1 }}
                            className="glass-card"
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">Preset Bobot</h3>
                            <div className="grid md:grid-cols-2 gap-3">
                                {Object.entries(presets).map(([key, preset]) => (
                                    <button
                                        key={key}
                                        onClick={() => applyPreset(key)}
                                        className="p-4 bg-dark-200/50 rounded-lg text-left hover:bg-white/10 transition-colors group"
                                    >
                                        <div className="font-medium text-white group-hover:text-primary-400 transition-colors">
                                            {preset.name}
                                        </div>
                                        <div className="text-sm text-gray-500">{preset.description}</div>
                                    </button>
                                ))}
                            </div>
                        </motion.div>
                    </div>

                    {/* Charts */}
                    <div className="space-y-6">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="glass-card"
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">Distribusi Bobot</h3>
                            <div className="h-64">
                                <Doughnut
                                    data={weightChartData}
                                    options={{
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        plugins: {
                                            legend: {
                                                position: 'bottom',
                                                labels: { color: '#94a3b8', font: { size: 10 } },
                                            },
                                        },
                                    }}
                                />
                            </div>
                        </motion.div>

                        {brandChartData && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.1 }}
                                className="glass-card"
                            >
                                <h3 className="text-lg font-semibold text-white mb-4">Distribusi Brand</h3>
                                <div className="h-64">
                                    <Doughnut
                                        data={brandChartData}
                                        options={{
                                            responsive: true,
                                            maintainAspectRatio: false,
                                            plugins: {
                                                legend: {
                                                    position: 'bottom',
                                                    labels: { color: '#94a3b8', font: { size: 10 } },
                                                },
                                            },
                                        }}
                                    />
                                </div>
                            </motion.div>
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'database' && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="glass-card"
                >
                    <h2 className="text-xl font-semibold text-white mb-6">Statistik Database</h2>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* By OS */}
                        <div className="p-4 bg-dark-200/50 rounded-lg">
                            <h4 className="font-medium text-white mb-3">Berdasarkan OS</h4>
                            {dashboard?.distributions?.by_os && Object.entries(dashboard.distributions.by_os).map(([os, count]) => (
                                <div key={os} className="flex justify-between py-2 border-b border-white/5">
                                    <span className="text-gray-400">{os}</span>
                                    <span className="text-white font-medium">{count}</span>
                                </div>
                            ))}
                        </div>

                        {/* By RAM */}
                        <div className="p-4 bg-dark-200/50 rounded-lg">
                            <h4 className="font-medium text-white mb-3">Berdasarkan RAM</h4>
                            {dashboard?.distributions?.by_ram && Object.entries(dashboard.distributions.by_ram).slice(0, 6).map(([ram, count]) => (
                                <div key={ram} className="flex justify-between py-2 border-b border-white/5">
                                    <span className="text-gray-400">{ram} GB</span>
                                    <span className="text-white font-medium">{count}</span>
                                </div>
                            ))}
                        </div>

                        {/* By Price Segment */}
                        <div className="p-4 bg-dark-200/50 rounded-lg">
                            <h4 className="font-medium text-white mb-3">Berdasarkan Harga</h4>
                            {dashboard?.distributions?.by_price_segment && Object.entries(dashboard.distributions.by_price_segment).map(([segment, count]) => (
                                <div key={segment} className="flex justify-between py-2 border-b border-white/5">
                                    <span className="text-gray-400">{segment}</span>
                                    <span className="text-white font-medium">{count}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}

            {activeTab === 'add' && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="glass-card max-w-2xl"
                >
                    <h2 className="text-xl font-semibold text-white mb-6">Tambah HP Baru</h2>

                    <form onSubmit={handleAddPhone} className="space-y-4">
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <label className="input-label">Nama HP</label>
                                <input
                                    type="text"
                                    value={newPhone.nama_hp}
                                    onChange={(e) => setNewPhone(p => ({ ...p, nama_hp: e.target.value }))}
                                    className="input"
                                    required
                                    placeholder="Samsung Galaxy S24"
                                />
                            </div>
                            <div>
                                <label className="input-label">Brand</label>
                                <input
                                    type="text"
                                    value={newPhone.brand}
                                    onChange={(e) => setNewPhone(p => ({ ...p, brand: e.target.value }))}
                                    className="input"
                                    required
                                    placeholder="Samsung"
                                />
                            </div>
                            <div>
                                <label className="input-label">Harga (Rp)</label>
                                <input
                                    type="number"
                                    value={newPhone.harga}
                                    onChange={(e) => setNewPhone(p => ({ ...p, harga: parseInt(e.target.value) }))}
                                    className="input"
                                    required
                                    min="0"
                                />
                            </div>
                            <div>
                                <label className="input-label">RAM (GB)</label>
                                <input
                                    type="number"
                                    value={newPhone.ram}
                                    onChange={(e) => setNewPhone(p => ({ ...p, ram: parseInt(e.target.value) }))}
                                    className="input"
                                    required
                                    min="1"
                                />
                            </div>
                            <div>
                                <label className="input-label">Storage (GB)</label>
                                <input
                                    type="number"
                                    value={newPhone.memori_internal}
                                    onChange={(e) => setNewPhone(p => ({ ...p, memori_internal: parseInt(e.target.value) }))}
                                    className="input"
                                    required
                                />
                            </div>
                            <div>
                                <label className="input-label">Baterai (mAh)</label>
                                <input
                                    type="number"
                                    value={newPhone.kapasitas_baterai}
                                    onChange={(e) => setNewPhone(p => ({ ...p, kapasitas_baterai: parseInt(e.target.value) }))}
                                    className="input"
                                    required
                                />
                            </div>
                            <div>
                                <label className="input-label">Resolusi Kamera</label>
                                <input
                                    type="text"
                                    value={newPhone.resolusi_kamera}
                                    onChange={(e) => setNewPhone(p => ({ ...p, resolusi_kamera: e.target.value }))}
                                    className="input"
                                    placeholder="48MP"
                                />
                            </div>
                            <div>
                                <label className="input-label">OS</label>
                                <select
                                    value={newPhone.os}
                                    onChange={(e) => setNewPhone(p => ({ ...p, os: e.target.value }))}
                                    className="select"
                                >
                                    <option value="Android">Android</option>
                                    <option value="iOS">iOS</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" className="btn-primary w-full">
                            <FiPlusCircle />
                            Tambah HP
                        </button>
                    </form>
                </motion.div>
            )}
        </div>
    );
}
