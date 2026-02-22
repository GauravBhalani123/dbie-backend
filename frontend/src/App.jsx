import { useEffect, useState } from 'react'

function App() {
  const [stats, setStats] = useState(null);
  const [businesses, setBusinesses] = useState([]);

  useEffect(() => {
    fetch('https://dbie-engine-api.onrender.com/api/dashboard/')
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(e => console.error(e));

    fetch('https://dbie-engine-api.onrender.com/api/businesses/')
      .then(r => r.json())
      .then(data => setBusinesses(data))
      .catch(e => console.error(e));
  }, []);

  return (
    <div className="app-container">
      <div className="header">
        <h1>🚀 Deep Business Intelligence Engine</h1>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card hot">
            <h3>🔥 Hot Leads</h3>
            <h2>{stats.leads_breakdown.hot}</h2>
          </div>
          <div className="stat-card warm">
            <h3>🌡️ Warm Leads</h3>
            <h2>{stats.leads_breakdown.warm}</h2>
          </div>
          <div className="stat-card cold">
            <h3>❄️ Cold Leads</h3>
            <h2>{stats.leads_breakdown.cold}</h2>
          </div>
        </div>
      )}

      <h2>Recent Intelligences</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Business Name</th>
            <th>Industry</th>
            <th>Location</th>
          </tr>
        </thead>
        <tbody>
          {businesses.map(b => (
            <tr key={b.id}>
              <td>{b.name}</td>
              <td>{b.industry}</td>
              <td>{b.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default App
