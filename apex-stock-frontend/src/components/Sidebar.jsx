import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Package, 
  Users, 
  FileText, 
  UserCog,
  LogOut,
  TruckIcon
} from 'lucide-react';
import './Sidebar.css';

export default function Sidebar() {
  const { user, logout, isAdmin } = useAuth();

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', admin: false },
    { path: '/inventory', icon: Package, label: 'Inventory', admin: false },
    { path: '/suppliers', icon: TruckIcon, label: 'Suppliers', admin: false },
    { path: '/reports', icon: FileText, label: 'Reports', admin: true },
    { path: '/users', icon: UserCog, label: 'User Management', admin: true },
  ];

  return (
    <div className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">
          <Package size={24} />
        </div>
        <div className="sidebar-logo-text">
          <h1>Apex Stock</h1>
          <p>{user?.role}</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          if (item.admin && !isAdmin()) return null;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'active' : ''}`
              }
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">
            <Users size={20} />
          </div>
          <div className="user-details">
            <p className="user-name">{user?.username}</p>
            <p className="user-email">{user?.email}</p>
          </div>
        </div>
        <button onClick={logout} className="logout-button">
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
}