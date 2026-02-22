import { useState } from "react";
import api from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Login({ setAuth }) {
    const [isRegister, setIsRegister] = useState(false);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        try {
            if (isRegister) {
                await api.post("/auth/register", { username, password });
                // auto-login after register
                const formData = new URLSearchParams();
                formData.append("username", username);
                formData.append("password", password);
                const res = await api.post("/auth/login", formData);
                localStorage.setItem("access_token", res.data.access_token);
                setAuth(true);
                navigate("/dashboard");
            } else {
                const formData = new URLSearchParams();
                formData.append("username", username);
                formData.append("password", password);
                const res = await api.post("/auth/login", formData);
                localStorage.setItem("access_token", res.data.access_token);
                setAuth(true);
                navigate("/dashboard");
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Authentication Failed. Try another username.");
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>🚀 DBIE Login</h2>
                <p>Access your Deep Intelligence Engine</p>
                {error && <div className="error">{error}</div>}
                <form onSubmit={handleSubmit}>
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
                    <button type="submit" className="login-button">
                        {isRegister ? "Create Account & Connect" : "Connect Engine"}
                    </button>
                    <p style={{ marginTop: "15px", cursor: "pointer", color: "#58a6ff" }} onClick={() => setIsRegister(!isRegister)}>
                        {isRegister ? "Already have an account? Login here" : "Need an account? Register here"}
                    </p>
                </form>
            </div>
        </div>
    );
}
