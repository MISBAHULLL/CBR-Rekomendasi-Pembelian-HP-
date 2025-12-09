import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FiHome, FiSearch, FiBarChart2, FiSettings,
    FiMenu, FiX, FiSmartphone, FiList
} from 'react-icons/fi';

const navItems = [
    { path: '/', label: 'Beranda', icon: FiHome },
    { path: '/recommendation', label: 'Rekomendasi', icon: FiSearch },
    { path: '/phones', label: 'Daftar HP', icon: FiList },
    { path: '/evaluation', label: 'Evaluasi', icon: FiBarChart2 },
    { path: '/admin', label: 'Admin', icon: FiSettings },
];

export default function Layout({ children }) {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const location = useLocation();

    return (
        <div className="min-h-screen bg-dark-300 bg-grid">
            {/* Navbar */}
            <nav className="navbar">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-3 group">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <FiSmartphone className="text-white text-xl" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">PhoneMatch</h1>
                            <p className="text-xs text-gray-400">AI Recommendation</p>
                        </div>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path;

                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300 ${isActive
                                            ? 'bg-primary-500/20 text-primary-400'
                                            : 'text-gray-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    <Icon className="text-lg" />
                                    <span className="font-medium">{item.label}</span>
                                </Link>
                            );
                        })}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
                    >
                        {isMobileMenuOpen ? (
                            <FiX className="text-2xl text-white" />
                        ) : (
                            <FiMenu className="text-2xl text-white" />
                        )}
                    </button>
                </div>

                {/* Mobile Navigation */}
                <AnimatePresence>
                    {isMobileMenuOpen && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="md:hidden mt-4 pb-4 border-t border-white/10"
                        >
                            <div className="flex flex-col gap-2 pt-4">
                                {navItems.map((item) => {
                                    const Icon = item.icon;
                                    const isActive = location.pathname === item.path;

                                    return (
                                        <Link
                                            key={item.path}
                                            to={item.path}
                                            onClick={() => setIsMobileMenuOpen(false)}
                                            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${isActive
                                                    ? 'bg-primary-500/20 text-primary-400'
                                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                                }`}
                                        >
                                            <Icon className="text-xl" />
                                            <span className="font-medium">{item.label}</span>
                                        </Link>
                                    );
                                })}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </nav>

            {/* Main Content */}
            <main className="pt-24 pb-12 px-4 md:px-6">
                <div className="max-w-7xl mx-auto">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={location.pathname}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.3 }}
                        >
                            {children}
                        </motion.div>
                    </AnimatePresence>
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t border-white/10 py-8 px-6">
                <div className="max-w-7xl mx-auto text-center">
                    <p className="text-gray-500 text-sm">
                        © 2024 PhoneMatch AI - Sistem Rekomendasi HP dengan Case-Based Reasoning
                    </p>
                    <p className="text-gray-600 text-xs mt-2">
                        Menggunakan Weighted Euclidean Distance untuk perhitungan similarity
                    </p>
                </div>
            </footer>
        </div>
    );
}
