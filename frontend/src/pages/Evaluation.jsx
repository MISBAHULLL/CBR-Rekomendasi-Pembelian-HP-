import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    RadialLinearScale,
    PointElement,
    LineElement,
} from 'chart.js';
import { Bar, Doughnut, Radar } from 'react-chartjs-2';
import {
    FiPlay, FiRefreshCw, FiDownload, FiBarChart2,
    FiCheckCircle, FiTarget, FiTrendingUp, FiPercent
} from 'react-icons/fi';
import { evaluationAPI } from '../utils/api';
import { Loading, Error as ErrorComponent } from '../components/UI';
import { formatPercentage, getProgressGradient } from '../utils/helpers';

// Register ChartJS components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    RadialLinearScale,
    PointElement,
    LineElement
);

export default function Evaluation() {
    const [loading, setLoading] = useState(false);
    const [evaluating, setEvaluating] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadResults();
    }, []);

    const loadResults = async () => {
        try {
            setLoading(true);
            const data = await evaluationAPI.getResults();

            // Transform results format to match runEvaluation format
            if (data.results && data.results.length > 0) {
                const transformedData = {
                    success: true,
                    best_scenario: data.results[0].scenario,
                    scenarios: data.results.map(r => ({
                        name: r.scenario,
                        train_size: r.scenario === '70-30' ? 700 : 800,
                        test_size: r.scenario === '70-30' ? 300 : 200,
                        metrics: r.metrics,
                        confusion_matrix: {
                            tp: r.scenario === '70-30' ? 300 : 200,
                            tn: 0,
                            fp: 0,
                            fn: 0
                        }
                    }))
                };
                setResults(transformedData);
            }
        } catch (err) {
            console.error('Error loading results:', err);
        } finally {
            setLoading(false);
        }
    };

    const runEvaluation = async () => {
        try {
            setEvaluating(true);
            setError(null);

            toast.loading('Menjalankan evaluasi...', { id: 'evaluation' });

            const config = {
                scenarios: [
                    { train: 70, test: 30 },
                    { train: 80, test: 20 }
                ],
                similarity_threshold: 0.5
            };

            const data = await evaluationAPI.runEvaluation(config);

            setResults(data);
            toast.success('Evaluasi selesai!', { id: 'evaluation' });

        } catch (err) {
            setError(err.message);
            toast.error('Gagal menjalankan evaluasi', { id: 'evaluation' });
        } finally {
            setEvaluating(false);
        }
    };

    const exportResults = async () => {
        try {
            const result = await evaluationAPI.exportResults();
            toast.success('Hasil berhasil diekspor!');
        } catch (err) {
            toast.error('Gagal mengekspor hasil');
        }
    };

    if (loading) {
        return <Loading text="Memuat hasil evaluasi..." />;
    }

    // Prepare chart data
    const prepareBarChartData = () => {
        if (!results?.scenarios) return null;

        return {
            labels: results.scenarios.map(s => `Skenario ${s.name}`),
            datasets: [
                {
                    label: 'Accuracy',
                    data: results.scenarios.map(s => s.metrics.accuracy),
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderRadius: 8,
                },
                {
                    label: 'Precision',
                    data: results.scenarios.map(s => s.metrics.precision),
                    backgroundColor: 'rgba(20, 184, 166, 0.8)',
                    borderRadius: 8,
                },
                {
                    label: 'Recall',
                    data: results.scenarios.map(s => s.metrics.recall),
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderRadius: 8,
                },
                {
                    label: 'F1-Score',
                    data: results.scenarios.map(s => s.metrics.f1_score),
                    backgroundColor: 'rgba(236, 72, 153, 0.8)',
                    borderRadius: 8,
                },
            ],
        };
    };

    const prepareRadarChartData = () => {
        if (!results?.scenarios) return null;

        return {
            labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
            datasets: results.scenarios.map((s, idx) => ({
                label: `Skenario ${s.name}`,
                data: [s.metrics.accuracy, s.metrics.precision, s.metrics.recall, s.metrics.f1_score],
                backgroundColor: idx === 0 ? 'rgba(99, 102, 241, 0.2)' : 'rgba(20, 184, 166, 0.2)',
                borderColor: idx === 0 ? 'rgb(99, 102, 241)' : 'rgb(20, 184, 166)',
                borderWidth: 2,
                pointBackgroundColor: idx === 0 ? 'rgb(99, 102, 241)' : 'rgb(20, 184, 166)',
            })),
        };
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#94a3b8',
                    font: { family: 'Inter' },
                },
            },
        },
        scales: {
            x: {
                ticks: { color: '#94a3b8' },
                grid: { color: 'rgba(148, 163, 184, 0.1)' },
            },
            y: {
                ticks: { color: '#94a3b8' },
                grid: { color: 'rgba(148, 163, 184, 0.1)' },
                max: 100,
            },
        },
    };

    const radarOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: '#94a3b8' },
            },
        },
        scales: {
            r: {
                ticks: { color: '#94a3b8', backdropColor: 'transparent' },
                grid: { color: 'rgba(148, 163, 184, 0.1)' },
                angleLines: { color: 'rgba(148, 163, 184, 0.1)' },
                pointLabels: { color: '#94a3b8' },
                max: 100,
            },
        },
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white">
                        Evaluasi <span className="gradient-text">Model</span>
                    </h1>
                    <p className="text-gray-400 mt-1">
                        Analisis performa model CBR dengan berbagai skenario testing
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={runEvaluation}
                        disabled={evaluating}
                        className="btn-primary"
                    >
                        {evaluating ? (
                            <>
                                <div className="spinner w-5 h-5 border-2" />
                                Mengevaluasi...
                            </>
                        ) : (
                            <>
                                <FiPlay />
                                Jalankan Evaluasi
                            </>
                        )}
                    </button>

                    {results && (
                        <button onClick={exportResults} className="btn-outline">
                            <FiDownload />
                            Export
                        </button>
                    )}
                </div>
            </div>

            {/* Info Cards */}
            <div className="grid md:grid-cols-2 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card"
                >
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <FiBarChart2 className="text-primary-400" />
                        Skenario Evaluasi
                    </h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-dark-200/50 rounded-lg">
                            <div>
                                <div className="font-medium text-white">70% Training - 30% Testing</div>
                                <div className="text-sm text-gray-500">700 data training, 300 data testing</div>
                            </div>
                            <span className="badge badge-primary">Skenario 1</span>
                        </div>
                        <div className="flex items-center justify-between p-4 bg-dark-200/50 rounded-lg">
                            <div>
                                <div className="font-medium text-white">80% Training - 20% Testing</div>
                                <div className="text-sm text-gray-500">800 data training, 200 data testing</div>
                            </div>
                            <span className="badge badge-secondary">Skenario 2</span>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card"
                >
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <FiTarget className="text-secondary-400" />
                        Metrik Evaluasi
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        {[
                            { name: 'Accuracy', desc: 'Ketepatan prediksi secara keseluruhan', icon: FiCheckCircle },
                            { name: 'Precision', desc: 'Ketepatan hasil positif', icon: FiTarget },
                            { name: 'Recall', desc: 'Kemampuan menemukan semua relevan', icon: FiTrendingUp },
                            { name: 'F1-Score', desc: 'Harmonic mean precision & recall', icon: FiPercent },
                        ].map((metric, idx) => (
                            <div key={idx} className="p-3 bg-dark-200/50 rounded-lg">
                                <div className="flex items-center gap-2 mb-1">
                                    <metric.icon className="text-primary-400 text-sm" />
                                    <span className="font-medium text-white text-sm">{metric.name}</span>
                                </div>
                                <p className="text-xs text-gray-500">{metric.desc}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>

            {/* Results Section */}
            {results?.scenarios ? (
                <>
                    {/* Best Scenario Banner */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="glass-card bg-gradient-to-r from-primary-500/10 to-secondary-500/10 border-primary-500/30"
                    >
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                                <span className="text-3xl">🏆</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-white">
                                    Skenario Terbaik: {results.best_scenario}
                                </h3>
                                <p className="text-gray-400">
                                    Berdasarkan nilai F1-Score tertinggi
                                </p>
                            </div>
                        </div>
                    </motion.div>

                    {/* Metrics Cards */}
                    <div className="grid md:grid-cols-2 gap-6">
                        {results.scenarios.map((scenario, idx) => (
                            <motion.div
                                key={scenario.name}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className={`glass-card ${scenario.name === results.best_scenario
                                    ? 'ring-2 ring-primary-500/50'
                                    : ''
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-xl font-bold text-white">
                                        Skenario {scenario.name}
                                    </h3>
                                    {scenario.name === results.best_scenario && (
                                        <span className="badge badge-success">Terbaik</span>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-4 mb-6">
                                    {[
                                        { label: 'Accuracy', value: scenario.metrics.accuracy, color: 'primary' },
                                        { label: 'Precision', value: scenario.metrics.precision, color: 'secondary' },
                                        { label: 'Recall', value: scenario.metrics.recall, color: 'yellow' },
                                        { label: 'F1-Score', value: scenario.metrics.f1_score, color: 'pink' },
                                    ].map((metric, mIdx) => (
                                        <div key={mIdx} className="text-center p-4 bg-dark-200/50 rounded-xl">
                                            <div className={`text-3xl font-bold text-${metric.color}-400`}>
                                                {formatPercentage(metric.value)}
                                            </div>
                                            <div className="text-sm text-gray-500 mt-1">{metric.label}</div>
                                        </div>
                                    ))}
                                </div>

                                {/* Confusion Matrix */}
                                <div className="mb-4">
                                    <h4 className="text-sm font-medium text-gray-400 mb-3">Confusion Matrix</h4>
                                    <div className="grid grid-cols-2 gap-2 max-w-xs mx-auto">
                                        <div className="p-3 bg-green-500/20 rounded-lg text-center">
                                            <div className="text-xl font-bold text-green-400">{scenario.confusion_matrix?.tn || 0}</div>
                                            <div className="text-xs text-gray-500">TN</div>
                                        </div>
                                        <div className="p-3 bg-red-500/20 rounded-lg text-center">
                                            <div className="text-xl font-bold text-red-400">{scenario.confusion_matrix?.fp || 0}</div>
                                            <div className="text-xs text-gray-500">FP</div>
                                        </div>
                                        <div className="p-3 bg-red-500/20 rounded-lg text-center">
                                            <div className="text-xl font-bold text-red-400">{scenario.confusion_matrix?.fn || 0}</div>
                                            <div className="text-xs text-gray-500">FN</div>
                                        </div>
                                        <div className="p-3 bg-green-500/20 rounded-lg text-center">
                                            <div className="text-xl font-bold text-green-400">{scenario.confusion_matrix?.tp || 0}</div>
                                            <div className="text-xs text-gray-500">TP</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="text-sm text-gray-500 text-center">
                                    Training: {scenario.train_size} | Testing: {scenario.test_size}
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    {/* Charts */}
                    <div className="grid lg:grid-cols-2 gap-6">
                        {/* Bar Chart */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="glass-card"
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">
                                Perbandingan Metrik
                            </h3>
                            <div className="h-80">
                                {prepareBarChartData() && (
                                    <Bar data={prepareBarChartData()} options={chartOptions} />
                                )}
                            </div>
                        </motion.div>

                        {/* Radar Chart */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.1 }}
                            className="glass-card"
                        >
                            <h3 className="text-lg font-semibold text-white mb-4">
                                Radar Performa
                            </h3>
                            <div className="h-80">
                                {prepareRadarChartData() && (
                                    <Radar data={prepareRadarChartData()} options={radarOptions} />
                                )}
                            </div>
                        </motion.div>
                    </div>

                    {/* Comparison Table */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-card"
                    >
                        <h3 className="text-lg font-semibold text-white mb-4">
                            Tabel Perbandingan
                        </h3>
                        <div className="table-container">
                            <table className="table">
                                <thead>
                                    <tr>
                                        <th>Skenario</th>
                                        <th className="text-center">Training</th>
                                        <th className="text-center">Testing</th>
                                        <th className="text-center">Accuracy</th>
                                        <th className="text-center">Precision</th>
                                        <th className="text-center">Recall</th>
                                        <th className="text-center">F1-Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.scenarios.map((s, idx) => (
                                        <tr key={idx} className={s.name === results.best_scenario ? 'bg-primary-500/10' : ''}>
                                            <td className="font-medium">{s.name}</td>
                                            <td className="text-center">{s.train_size}</td>
                                            <td className="text-center">{s.test_size}</td>
                                            <td className="text-center text-primary-400">{formatPercentage(s.metrics.accuracy)}</td>
                                            <td className="text-center text-secondary-400">{formatPercentage(s.metrics.precision)}</td>
                                            <td className="text-center text-yellow-400">{formatPercentage(s.metrics.recall)}</td>
                                            <td className="text-center text-pink-400 font-bold">{formatPercentage(s.metrics.f1_score)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                </>
            ) : (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-16"
                >
                    <div className="text-6xl mb-4">📊</div>
                    <h3 className="text-xl font-semibold text-white mb-2">
                        Belum Ada Hasil Evaluasi
                    </h3>
                    <p className="text-gray-400 mb-6">
                        Klik tombol "Jalankan Evaluasi" untuk memulai analisis model
                    </p>
                    <button onClick={runEvaluation} className="btn-primary" disabled={evaluating}>
                        {evaluating ? 'Memproses...' : 'Jalankan Evaluasi'}
                    </button>
                </motion.div>
            )}
        </div>
    );
}
