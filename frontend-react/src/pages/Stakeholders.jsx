import { useState, useEffect } from 'react'
import { Users, TrendingUp, MessageSquare } from 'lucide-react'
import { getMockStakeholders } from '../lib/api'
import './Stakeholders.css'

const Stakeholders = () => {
  const [stakeholdersData, setStakeholdersData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStakeholders()
  }, [])

  const loadStakeholders = async () => {
    try {
      const data = await getMockStakeholders()
      setStakeholdersData(data)
    } catch (error) {
      console.error('Error loading stakeholders:', error)
    } finally {
      setLoading(false)
    }
  }

  const getEngagementColor = (engagement) => {
    const colors = {
      high: '#10b981',
      medium: '#f59e0b',
      low: '#ef4444'
    }
    return colors[engagement] || colors.medium
  }

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: '#10b981',
      neutral: '#64748b',
      concerned: '#f59e0b',
      negative: '#ef4444'
    }
    return colors[sentiment] || colors.neutral
  }

  const getSentimentIcon = (sentiment) => {
    const icons = {
      positive: '😊',
      neutral: '😐',
      concerned: '😟',
      negative: '😠'
    }
    return icons[sentiment] || icons.neutral
  }

  if (loading) {
    return (
      <div className="stakeholders-page">
        <div className="page-header">
          <h1>Stakeholders</h1>
        </div>
        <p style={{ color: '#64748b' }}>Loading...</p>
      </div>
    )
  }

  return (
    <div className="stakeholders-page">
      <div className="page-header">
        <h1>Stakeholders</h1>
        <p className="page-subtitle">Team engagement and sentiment analysis</p>
      </div>

      <div className="stakeholders-grid">
        {stakeholdersData?.stakeholders.map((stakeholder) => (
          <div key={stakeholder.id} className="stakeholder-card">
            <div className="stakeholder-header">
              <div className="stakeholder-avatar">
                <Users size={24} />
              </div>
              <div className="stakeholder-info">
                <h3>{stakeholder.name}</h3>
                <p className="stakeholder-role">{stakeholder.role}</p>
              </div>
            </div>

            <div className="stakeholder-metrics">
              <div className="metric-row">
                <div className="metric-icon">
                  <TrendingUp size={16} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">Engagement</span>
                  <span 
                    className="metric-value"
                    style={{ color: getEngagementColor(stakeholder.engagement) }}
                  >
                    {stakeholder.engagement}
                  </span>
                </div>
              </div>

              <div className="metric-row">
                <div className="metric-icon">
                  <span style={{ fontSize: '1.25rem' }}>
                    {getSentimentIcon(stakeholder.sentiment)}
                  </span>
                </div>
                <div className="metric-content">
                  <span className="metric-label">Sentiment</span>
                  <span 
                    className="metric-value"
                    style={{ color: getSentimentColor(stakeholder.sentiment) }}
                  >
                    {stakeholder.sentiment}
                  </span>
                </div>
              </div>

              <div className="metric-row">
                <div className="metric-icon">
                  <MessageSquare size={16} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">Messages</span>
                  <span className="metric-value">
                    {stakeholder.messageCount}
                  </span>
                </div>
              </div>
            </div>

            <div className="engagement-bar">
              <div 
                className="engagement-fill"
                style={{ 
                  width: stakeholder.engagement === 'high' ? '100%' : 
                         stakeholder.engagement === 'medium' ? '60%' : '30%',
                  background: getEngagementColor(stakeholder.engagement)
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Stakeholders
