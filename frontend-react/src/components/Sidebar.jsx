import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Database, 
  Zap, 
  Target, 
  FileText, 
  Users, 
  Search,
  Settings,
  LogOut
} from 'lucide-react'
import './Sidebar.css'

const Sidebar = () => {
  const location = useLocation()

  const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/data-sources', icon: Database, label: 'Data Sources' },
    { path: '/processing', icon: Zap, label: 'Processing' },
    { path: '/alignment', icon: Target, label: 'Alignment Intelligence' },
    { path: '/brd-generator', icon: FileText, label: 'BRD Generator' },
    { path: '/stakeholders', icon: Users, label: 'Stakeholders' },
    { path: '/source-explorer', icon: Search, label: 'Source Explorer' },
  ]

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <div className="logo-icon">R</div>
          <div className="logo-text">
            <div className="logo-title">ReqMind</div>
            <div className="logo-subtitle">Alignment</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <button className="footer-item">
          <Settings size={20} />
          <span>Settings</span>
        </button>
        <button className="footer-item">
          <LogOut size={20} />
          <span>Sign Out</span>
        </button>
        
        <div className="user-profile">
          <div className="user-avatar">JD</div>
          <div className="user-info">
            <div className="user-name">John Doe</div>
            <div className="user-email">john@reqmind.com</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
