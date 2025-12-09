import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Recommendation from './pages/Recommendation'
import Results from './pages/Results'
import Evaluation from './pages/Evaluation'
import Admin from './pages/Admin'
import PhoneList from './pages/PhoneList'
import PhoneDetail from './pages/PhoneDetail'

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/recommendation" element={<Recommendation />} />
                <Route path="/results" element={<Results />} />
                <Route path="/phones" element={<PhoneList />} />
                <Route path="/phones/:id" element={<PhoneDetail />} />
                <Route path="/evaluation" element={<Evaluation />} />
                <Route path="/admin" element={<Admin />} />
            </Routes>
        </Layout>
    )
}

export default App
