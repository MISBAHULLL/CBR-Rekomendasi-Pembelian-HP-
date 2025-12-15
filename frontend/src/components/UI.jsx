// untuk styleing loading
import { motion } from 'framer-motion';

export function Loading({ size = 'md', text = 'Memuat...' }) {
    const sizes = {
        sm: 'w-6 h-6 border-2',
        md: 'w-10 h-10 border-3',
        lg: 'w-16 h-16 border-4',
    };

    return (
        <div className="flex flex-col items-center justify-center gap-4 py-12">
            <div className={`spinner ${sizes[size]}`} />
            {text && <p className="text-gray-400">{text}</p>}
        </div>
    );
}

export function LoadingOverlay({ text = 'Memproses...' }) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-dark-300/80 backdrop-blur-sm"
        >
            <div className="glass-card text-center p-8">
                <div className="spinner w-16 h-16 border-4 mx-auto mb-4" />
                <p className="text-white font-medium">{text}</p>
            </div>
        </motion.div>
    );
}

export function Skeleton({ className = '', lines = 1 }) {
    return (
        <div className={`space-y-2 ${className}`}>
            {Array.from({ length: lines }).map((_, i) => (
                <div
                    key={i}
                    className="h-4 bg-gray-700/50 rounded animate-pulse"
                    style={{ width: `${Math.random() * 40 + 60}%` }}
                />
            ))}
        </div>
    );
}

export function CardSkeleton() {
    return (
        <div className="card animate-pulse">
            <div className="h-6 bg-gray-700/50 rounded w-3/4 mb-4" />
            <div className="h-8 bg-gray-700/50 rounded w-1/2 mb-4" />
            <div className="grid grid-cols-2 gap-3">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="h-16 bg-gray-700/50 rounded" />
                ))}
            </div>
        </div>
    );
}

export function TableSkeleton({ rows = 5, cols = 4 }) {
    return (
        <div className="table-container">
            <table className="table">
                <thead>
                    <tr>
                        {Array.from({ length: cols }).map((_, i) => (
                            <th key={i}>
                                <div className="h-4 bg-gray-700/50 rounded w-20 animate-pulse" />
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {Array.from({ length: rows }).map((_, rowIdx) => (
                        <tr key={rowIdx}>
                            {Array.from({ length: cols }).map((_, colIdx) => (
                                <td key={colIdx}>
                                    <div className="h-4 bg-gray-700/50 rounded animate-pulse"
                                        style={{ width: `${Math.random() * 40 + 40}%` }} />
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export function Empty({
    title = 'Tidak ada data',
    description = 'Data tidak ditemukan',
    icon = '📭',
    action = null
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
        >
            <div className="text-6xl mb-4">{icon}</div>
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-400 mb-6">{description}</p>
            {action}
        </motion.div>
    );
}

export function Error({
    title = 'Terjadi Kesalahan',
    message = 'Silakan coba lagi',
    onRetry = null
}) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-16"
        >
            <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-4xl">⚠️</span>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-400 mb-6">{message}</p>
            {onRetry && (
                <button onClick={onRetry} className="btn-primary">
                    Coba Lagi
                </button>
            )}
        </motion.div>
    );
}

export function ProgressBar({ value, max = 100, showLabel = true, className = '' }) {
    const percentage = Math.min(100, (value / max) * 100);

    return (
        <div className={className}>
            <div className="progress-bar">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className="progress-bar-fill"
                />
            </div>
            {showLabel && (
                <div className="flex justify-between mt-1 text-xs text-gray-400">
                    <span>{value}</span>
                    <span>{percentage.toFixed(1)}%</span>
                </div>
            )}
        </div>
    );
}

export function Badge({ children, variant = 'primary', className = '' }) {
    const variants = {
        primary: 'badge-primary',
        secondary: 'badge-secondary',
        success: 'badge-success',
        warning: 'badge-warning',
    };

    return (
        <span className={`badge ${variants[variant]} ${className}`}>
            {children}
        </span>
    );
}

export function Tooltip({ children, content }) {
    return (
        <div className="tooltip">
            {children}
            <div className="tooltip-content">{content}</div>
        </div>
    );
}
