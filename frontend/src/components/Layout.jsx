import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Layout({ children }) {
  const { user, logout, isSuperuser } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="layout">
      <header className="layout-header">
        <div className="layout-header-content">
          <Link to="/" className="logo">
            Admin Panel
          </Link>
          <nav className="layout-nav">
            <Link to="/">Dashboard</Link>
            <Link to="/items">Items</Link>
            {isSuperuser && <Link to="/users">Users</Link>}
            <Link to="/profile">Profile</Link>
            <div className="user-menu">
              <span className="user-email">{user?.email}</span>
              <button onClick={handleLogout} className="btn-logout">
                Logout
              </button>
            </div>
          </nav>
        </div>
      </header>
      <main className="layout-main">{children}</main>
    </div>
  );
}

