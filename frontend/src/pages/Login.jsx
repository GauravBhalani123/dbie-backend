import { useState } from "react";
import api from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login({ setAuth }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);

            const res = await api.post("/auth/login", formData);
            localStorage.setItem("access_token", res.data.access_token);
            setAuth(true);
            navigate("/dashboard");
        } catch (err) {
            setError("Invalid username or password");
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>🚀 DBIE Login</h2>
                <p>Access your Deep Intelligence Engine</p>
                {error && <div className="error">{error}</div>}
                <form onSubmit={handleLogin}>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit" className="login-button">Connect Engine</button>
                </form>
            </div>
        </div>
    );
}
