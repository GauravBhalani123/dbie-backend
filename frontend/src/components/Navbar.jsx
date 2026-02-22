import { Link } from 'react-router-dom';

export default function Navbar() {
    const handleLogout = () => {
        localStorage.removeItem("access_token");
        window.location.href = '/login';
    };

    const isAuthenticated = !!localStorage.getItem("access_token");

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <div className="navbar-left">
                    <Link to="/dashboard" className="navbar-logo">
                        <span className="logo-icon">☁️</span> DBIE AI Engine
                    </Link>
                    {isAuthenticated && (
                        <ul className="nav-menu">
                            <li className="nav-item">
                                <Link to="/dashboard" className="nav-link">Dashboard</Link>
                            </li>
                            <li className="nav-item">
                                <Link to="/leads" className="nav-link">Leads CRM</Link>
                            </li>
                            <li className="nav-item">
                                <Link to="/products" className="nav-link">Products</Link>
                            </li>
                            <li className="nav-item dropdown">
                                <span className="nav-link">Analytics ▾</span>
                            </li>
                            <li className="nav-item dropdown">
                                <span className="nav-link">Integrations ▾</span>
                            </li>
                        </ul>
                    )}
                </div>
                <div className="navbar-right">
                    <div className="search-bar">
                        <span className="search-icon">🔍</span>
                        <input type="text" placeholder="Search leads, signals..." />
                    </div>
                    <div className="contact-info">
                        <span className="contact-text">Support</span>
                        <span className="contact-number">1800-420-7332</span>
                    </div>
                    {isAuthenticated ? (
                        <button className="btn-logout" onClick={handleLogout}>Log Out</button>
                    ) : (
                        <Link to="/login" className="btn-login">Login</Link>
                    )}
                </div>
            </div>
        </nav>
    );
}
