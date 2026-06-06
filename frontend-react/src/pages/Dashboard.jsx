import { useState, useEffect } from 'react'
import { TrendingUp, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { getMockDataSources, getMockAlignmentData } from '../lib/api'
import './Dashboard.css'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [sourcesData, alignmentData] = await Promise.all([
        getMockDataSources(),
        getMockAlignmentData()
      ])
      
      setStats({
        totalMessages: sourcesData.totalMessages,
        alignmentScore: alignmentData.alignmentScore,
        riskLevel: alignmentData.riskLevel,
        activeConflicts: alignmentData.conflicts.length
      })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level) => {
    const colors = {
      HIGH: '#ef4444',
      MEDIUM: '#f59e0b',
      LOW: '#10b981'
    }
    return colors[level] || colors.MEDIUM
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="page-header">
          <h1>Dashboard</h1>
        </div>
        <p style={{ color: '#64748b' }}>Loading...</p>
      </div>
    )
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p className="page-subtitle">Overview of your project alignment intelligence</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#6366f1' }}>
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Alignment Score</div>
            <div className="stat-value">{stats?.alignmentScore}%</div>
            <div className="stat-change positive">+5% from last week</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: getRiskColor(stats?.riskLevel) }}>
            <AlertCircle size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Risk Level</div>
            <div className="stat-value">{stats?.riskLevel}</div>
            <div className="stat-change neutral">Monitoring required</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#8b5cf6' }}>
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Messages Collected</div>
            <div className="stat-value">{stats?.totalMessages}</div>
            <div className="stat-change positive">+127 today</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#ef4444' }}>
            <Clock size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Active Conflicts</div>
            <div className="stat-value">{stats?.activeConflicts}</div>
            <div className="stat-change negative">Needs attention</div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Recent Activity</h3>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-dot" style={{ background: '#10b981' }} />
              <div className="activity-content">
                <div className="activity-title">BRD Generated</div>
                <div className="activity-time">2 hours ago</div>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-dot" style={{ background: '#6366f1' }} />
              <div className="activity-content">
                <div className="activity-title">Data Sources Synced</div>
                <div className="activity-time">5 hours ago</div>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-dot" style={{ background: '#f59e0b' }} />
              <div className="activity-content">
                <div className="activity-title">Conflict Detected</div>
                <div className="activity-time">1 day ago</div>
              </div>
            </div>
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Quick Actions</h3>
          <div className="quick-actions">
            <button className="action-card">
              <span>Generate New BRD</span>
            </button>
            <button className="action-card">
              <span>Sync Data Sources</span>
            </button>
            <button className="action-card">
              <span>View Conflicts</span>
            </button>
            <button className="action-card">
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
