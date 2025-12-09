import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiSearch, FiFilter, FiGrid, FiList, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import { recommendationAPI } from '../utils/api';
import PhoneCard from '../components/PhoneCard';
import { Loading, Empty, CardSkeleton } from '../components/UI';

export default function PhoneList() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [phones, setPhones] = useState([]);
    const [pagination, setPagination] = useState({ page: 1, total: 0, totalPages: 0 });
    const [viewMode, setViewMode] = useState('grid');
    const [brands, setBrands] = useState([]);
    const [filters, setFilters] = useState({
        brand: '', min_price: null, max_price: null, sort_by: 'Harga', sort_order: 'asc'
    });

    useEffect(() => { loadBrands(); }, []);
    useEffect(() => { loadPhones(); }, [filters, pagination.page]);

    const loadBrands = async () => {
        try { const res = await recommendationAPI.getBrands(); setBrands(res.brands || []); }
        catch (err) { console.error(err); }
    };

    const loadPhones = async () => {
        try {
            setLoading(true);
            const res = await recommendationAPI.getPhones({ page: pagination.page, limit: 12, ...filters });
            setPhones(res.phones || []);
            setPagination({ page: res.page, total: res.total, totalPages: res.total_pages });
        } catch (err) { console.error(err); } finally { setLoading(false); }
    };

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
        setPagination(prev => ({ ...prev, page: 1 }));
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white">Daftar <span className="gradient-text">HP</span></h1>
                    <p className="text-gray-400 mt-1">Total: {pagination.total} HP</p>
                </div>
                <Link to="/recommendation" className="btn-primary"><FiSearch />Cari Rekomendasi</Link>
            </div>

            <div className="glass-card">
                <div className="grid md:grid-cols-4 gap-4">
                    <select value={filters.brand} onChange={e => handleFilterChange('brand', e.target.value)} className="select">
                        <option value="">Semua Brand</option>
                        {brands.map(b => <option key={b} value={b}>{b}</option>)}
                    </select>
                    <select value={filters.max_price || ''} onChange={e => handleFilterChange('max_price', e.target.value ? parseInt(e.target.value) : null)} className="select">
                        <option value="">Max Harga</option>
                        <option value="5000000">5 Juta</option><option value="10000000">10 Juta</option><option value="20000000">20 Juta</option>
                    </select>
                    <select value={filters.sort_by} onChange={e => handleFilterChange('sort_by', e.target.value)} className="select">
                        <option value="Harga">Harga</option><option value="Ram">RAM</option><option value="Rating_pengguna">Rating</option>
                    </select>
                    <select value={filters.sort_order} onChange={e => handleFilterChange('sort_order', e.target.value)} className="select">
                        <option value="asc">Rendah-Tinggi</option><option value="desc">Tinggi-Rendah</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">{Array(8).fill(0).map((_, i) => <CardSkeleton key={i} />)}</div>
            ) : phones.length === 0 ? (
                <Empty icon="📱" title="Tidak Ada HP" description="Coba ubah filter" />
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {phones.map((phone, idx) => (
                        <motion.div key={phone.Id_hp} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.03 }}>
                            <PhoneCard phone={phone} onClick={() => navigate(`/phones/${phone.Id_hp}`)} />
                        </motion.div>
                    ))}
                </div>
            )}

            {pagination.totalPages > 1 && (
                <div className="flex justify-center gap-2">
                    <button onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))} disabled={pagination.page === 1} className="btn-ghost p-2 disabled:opacity-50"><FiChevronLeft /></button>
                    <span className="px-4 py-2 text-white">{pagination.page} / {pagination.totalPages}</span>
                    <button onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))} disabled={pagination.page === pagination.totalPages} className="btn-ghost p-2 disabled:opacity-50"><FiChevronRight /></button>
                </div>
            )}
        </div>
    );
}
