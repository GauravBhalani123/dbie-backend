import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Navbar from "./components/Navbar";
import { useState } from "react";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("access_token"));

  return (
    <Router>
      <Navbar />
      <div className="app-container">
        <Routes>
          <Route path="/login" element={<Login setAuth={setIsAuthenticated} />} />
          <Route
            path="/dashboard"
            element={isAuthenticated ? <Dashboard setAuth={setIsAuthenticated} /> : <Navigate to="/login" />}
          />
          <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
