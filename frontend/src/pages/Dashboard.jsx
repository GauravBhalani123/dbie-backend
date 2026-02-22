import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard({ setAuth }) {
    const [stats, setStats] = useState(null);
    const [businesses, setBusinesses] = useState([]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [statsRes, busRes] = await Promise.all([
                api.get("/dashboard/"),
                api.get("/businesses/")
            ]);
            setStats(statsRes.data);
            setBusinesses(busRes.data);
        } catch (e) {
            if (e.response?.status === 401) {
                setAuth(false);
            }
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        setAuth(false);
    };

    return (
        <div>
            <div className="header">
                <h1>🚀 Deep Business Intelligence Engine</h1>
                <button onClick={handleLogout} className="logout-button">Logout</button>
            </div>

            {stats && (
                <div className="stats-grid">
                    <div className="stat-card hot">
                        <h3>🔥 Hot Leads</h3>
                        <h2>{stats.leads_breakdown?.hot || 0}</h2>
                    </div>
                    <div className="stat-card warm">
                        <h3>🌡️ Warm Leads</h3>
                        <h2>{stats.leads_breakdown?.warm || 0}</h2>
                    </div>
                    <div className="stat-card cold">
                        <h3>❄️ Cold Leads</h3>
                        <h2>{stats.leads_breakdown?.cold || 0}</h2>
                    </div>
                </div>
            )}

            <div className="section-title">
                <h2>Recent Intelligences</h2>
            </div>

            <table className="table">
                <thead>
                    <tr>
                        <th>Business Name</th>
                        <th>Industry</th>
                        <th>Location</th>
                        <th>Digital Level</th>
                        <th>Lead Type</th>
                    </tr>
                </thead>
                <tbody>
                    {businesses.map(b => (
                        <tr key={b.id}>
                            <td>{b.name}</td>
                            <td>{b.industry}</td>
                            <td>{b.location}</td>
                            <td>{b.scores?.digital_score < 50 ? 'Low' : 'High'}</td>
                            <td>
                                <span className={`badge ${b.scores?.category?.toLowerCase() || 'cold'}`}>
                                    {b.scores?.category || 'Cold'}
                                </span>
                            </td>
                        </tr>
                    ))}
                    {businesses.length === 0 && (
                        <tr><td colSpan="5" style={{ textAlign: "center", color: "#888" }}>No intelligences found yet.</td></tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}
