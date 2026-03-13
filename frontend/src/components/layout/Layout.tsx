import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>VQI Georgia</h2>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Dashboard
          </NavLink>
          <NavLink to="/patients" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Patients
          </NavLink>
          <NavLink to="/procedures" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Procedures
          </NavLink>
          <NavLink to="/audit" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Audit
          </NavLink>
        </nav>
      </aside>
      <div className="main-content">
        <header className="header">
          <div className="header-left">
            <h1>VQI Georgia Registry</h1>
          </div>
          <div className="header-right">
            {user && (
              <>
                <span className="user-name">{user.full_name}</span>
                <span className="user-role">{user.role}</span>
              </>
            )}
            <button className="btn-logout" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
