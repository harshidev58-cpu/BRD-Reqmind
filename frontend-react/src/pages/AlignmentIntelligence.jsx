import { useState, useEffect } from 'react'
import { AlertTriangle } from 'lucide-react'
import { getMockAlignmentData } from '../lib/api'
import './AlignmentIntelligence.css'

const AlignmentIntelligence = () => {
  const [alignmentData, setAlignmentData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAlignmentData()
  }, [])

  const loadAlignmentData = async () => {
    try {
      const data = await getMockAlignmentData()
      setAlignmentData(data)
    } catch (error) {
      console.error('Error loading alignment data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      healthy: '#10b981',
      moderate: '#f59e0b',
      critical: '#ef4444'
    }
    return colors[status] || colors.moderate
  }

  const getStatusLabel = (status) => {
    const labels = {
      healthy: 'Healthy',
      moderate: 'Moderate',
      critical: 'Critical'
    }
    return labels[status] || 'Moderate'
  }

  if (loading) {
    return (
      <div className="alignment-page">
        <div className="page-header">
          <h1>Alignment Intelligence</h1>
        </div>
        <p style={{ color: '#64748b' }}>Loading...</p>
      </div>
    )
  }

  return (
    <div className="alignment-page">
      <div className="page-header">
        <h1>Alignment Intelligence</h1>
        <p className="page-subtitle">Cross-team alignment analysis and conflict detection</p>
      </div>

      <div className="metrics-grid">
        {alignmentData?.metrics.map((metric) => (
          <div key={metric.name} className="metric-card">
            <div className="metric-header">
              <h3>{metric.name}</h3>
              <div className="metric-score" style={{ color: getStatusColor(metric.status) }}>
                {metric.score}%
              </div>
            </div>
            <p className="metric-description">{metric.description}</p>
            <div className="metric-progress">
              <div 
                className="metric-progress-bar"
                style={{ 
                  width: `${metric.score}%`,
                  background: getStatusColor(metric.status)
                }}
              />
            </div>
            <div className="metric-status">
              <span 
                className="status-dot"
                style={{ background: getStatusColor(metric.status) }}
              />
              <span className="status-label">{getStatusLabel(metric.status)}</span>
            </div>
          </div>
        ))}
      </div>

      {alignmentData?.conflicts && alignmentData.conflicts.length > 0 && (
        <div className="conflicts-section">
          <h2 className="section-title">Detected Conflicts</h2>
          {alignmentData.conflicts.map((conflict) => (
            <div key={conflict.id} className={`conflict-card severity-${conflict.severity}`}>
              <div className="conflict-header">
                <div className="conflict-icon">
                  <AlertTriangle size={24} />
                </div>
                <div className="conflict-title">
                  <h3>{conflict.type}</h3>
                  <span className={`severity-badge ${conflict.severity}`}>
                    {conflict.severity}
                  </span>
                </div>
              </div>
              <p className="conflict-description">{conflict.description}</p>
              <div className="conflict-meta">
                <div className="meta-item">
                  <span className="meta-label">Sources:</span>
                  <span className="meta-value">{conflict.sources.join(', ')}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Recommendation:</span>
                  <span className="meta-value">{conflict.recommendation}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AlignmentIntelligence
