import { Bell, ChevronDown } from 'lucide-react'
import './Header.css'

const Header = ({ currentProject }) => {
  return (
    <header className="header">
      <div className="header-left">
        <div className="sync-status">
          Synced 2 minutes ago
        </div>
      </div>
      
      <div className="header-right">
        <button className="notification-btn">
          <Bell size={20} />
          <span className="notification-badge">1</span>
        </button>
        
        <button className="project-selector">
          <span>{currentProject}</span>
          <ChevronDown size={16} />
        </button>
        
        <div className="user-avatar-small">JD</div>
      </div>
    </header>
  )
}

export default Header
