/**
 * Utility Functions
 * =================
 */

/**
 * Format number to Indonesian Rupiah
 */
export const formatRupiah = (number) => {
    if (!number) return 'Rp 0';
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(number);
};

/**
 * Format number with thousand separator
 */
export const formatNumber = (number) => {
    if (!number) return '0';
    return new Intl.NumberFormat('id-ID').format(number);
};

/**
 * Format percentage
 */
export const formatPercentage = (value, decimals = 1) => {
    if (value === null || value === undefined) return '0%';
    return `${Number(value).toFixed(decimals)}%`;
};

/**
 * Get similarity color class based on score
 */
export const getSimilarityColor = (score) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-emerald-400';
    if (score >= 0.4) return 'text-yellow-400';
    if (score >= 0.2) return 'text-orange-400';
    return 'text-red-400';
};

/**
 * Get similarity badge variant
 */
export const getSimilarityBadge = (score) => {
    if (score >= 0.8) return { text: 'Sangat Cocok', class: 'badge-success' };
    if (score >= 0.6) return { text: 'Cocok', class: 'badge-primary' };
    if (score >= 0.4) return { text: 'Cukup Cocok', class: 'badge-warning' };
    return { text: 'Kurang Cocok', class: 'badge-secondary' };
};

/**
 * Get gradient color for progress bar
 */
export const getProgressGradient = (value) => {
    if (value >= 80) return 'from-green-500 to-emerald-400';
    if (value >= 60) return 'from-blue-500 to-cyan-400';
    if (value >= 40) return 'from-yellow-500 to-orange-400';
    return 'from-red-500 to-pink-400';
};

/**
 * Debounce function
 */
export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

/**
 * Truncate text
 */
export const truncate = (text, length = 50) => {
    if (!text) return '';
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
};

/**
 * Generate random ID
 */
export const generateId = () => {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
};

/**
 * Parse camera resolution to number
 */
export const parseCameraResolution = (resolution) => {
    if (!resolution) return 0;
    const match = resolution.toString().match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
};

/**
 * Validate weights (total should be 100%)
 */
export const validateWeights = (weights) => {
    const total = Object.values(weights).reduce((sum, val) => sum + val, 0);
    const isValid = total >= 99 && total <= 101;
    const hasZero = Object.values(weights).some(val => val === 0);

    return {
        isValid: isValid && !hasZero,
        total,
        hasZero,
        message: !isValid
            ? `Total bobot harus 100% (saat ini: ${total.toFixed(1)}%)`
            : hasZero
                ? 'Tidak boleh ada bobot bernilai 0'
                : 'Valid',
    };
};

/**
 * Storage helper
 */
export const storage = {
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch {
            return defaultValue;
        }
    },
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Storage error:', e);
        }
    },
    remove: (key) => {
        localStorage.removeItem(key);
    },
};

/**
 * Brand icons/colors mapping
 */
export const brandConfig = {
    Apple: { color: '#A3A3A3', icon: '🍎' },
    Samsung: { color: '#1428A0', icon: '📱' },
    Xiaomi: { color: '#FF6700', icon: '📱' },
    Oppo: { color: '#1BA784', icon: '📱' },
    Vivo: { color: '#415FFF', icon: '📱' },
    Realme: { color: '#F7C800', icon: '📱' },
    Huawei: { color: '#CF0A2C', icon: '📱' },
    Asus: { color: '#000000', icon: '📱' },
    Sony: { color: '#000000', icon: '📱' },
    OnePlus: { color: '#EB0029', icon: '📱' },
    default: { color: '#6366F1', icon: '📱' },
};

/**
 * Get brand config
 */
export const getBrandConfig = (brand) => {
    return brandConfig[brand] || brandConfig.default;
};

/**
 * Chart.js common options
 */
export const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#94a3b8',
                font: {
                    family: 'Inter',
                },
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
        },
    },
};
