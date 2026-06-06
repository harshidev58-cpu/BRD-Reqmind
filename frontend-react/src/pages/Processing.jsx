import { useState, useEffect } from 'react'
import { CheckCircle, Clock, Circle } from 'lucide-react'
import { getProcessingStatus } from '../lib/api'
import './Processing.css'

const Processing = () => {
  const [processingData, setProcessingData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProcessingStatus()
    
    // Poll every 2 seconds for updates
    const interval = setInterval(() => {
      loadProcessingStatus()
    }, 2000)
    
    return () => clearInterval(interval)
  }, [])

  const loadProcessingStatus = async () => {
    try {
      const data = await getProcessingStatus()
      setProcessingData(data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to load processing status:', error)
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={24} className="status-icon completed" />
      case 'processing':
        return <Clock size={24} className="status-icon processing" />
      default:
        return <Circle size={24} className="status-icon pending" />
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      completed: { text: 'Completed', class: 'completed' },
      processing: { text: 'Processing...', class: 'processing' },
      pending: { text: 'Pending', class: 'pending' }
    }
    return badges[status] || badges.pending
  }

  if (loading) {
    return (
      <div className="processing-page">
        <div className="page-header">
          <h1>Processing Pipeline</h1>
        </div>
        <p style={{ color: '#64748b' }}>Loading...</p>
      </div>
    )
  }

  // Show idle state if no processing session
  if (!processingData || !processingData.steps || processingData.steps.length === 0) {
    return (
      <div className="processing-page">
        <div className="page-header">
          <h1>Processing Pipeline</h1>
          <p className="page-subtitle">Real-time status of autonomous data processing and BRD generation</p>
        </div>
        <div className="idle-state">
          <Circle size={48} style={{ color: '#475569' }} />
          <h3>No Active Processing</h3>
          <p>Start a BRD generation to see the pipeline in action</p>
        </div>
      </div>
    )
  }

  return (
    <div className="processing-page">
      <div className="page-header">
        <h1>Processing Pipeline</h1>
        <p className="page-subtitle">Real-time status of autonomous data processing and BRD generation</p>
      </div>

      <div className="pipeline-info">
        <div className="info-card">
          <span className="info-label">Current Stage:</span>
          <span className="info-value">
            {processingData?.steps.find(s => s.status === 'processing')?.name || 'Idle'}
          </span>
        </div>
        <div className="info-card">
          <span className="info-label">Overall Progress:</span>
          <span className="info-value">
            {processingData?.overall_progress || 0}%
          </span>
        </div>
        <div className="info-card">
          <span className="info-label">Estimated Time:</span>
          <span className="info-value">{processingData?.estimated_time || 'N/A'}</span>
        </div>
      </div>

      <div className="pipeline-container">
        {processingData?.steps.map((step, index) => (
          <div key={step.id} className={`pipeline-step ${step.status}`}>
            <div className="step-indicator">
              {getStatusIcon(step.status)}
              {index < processingData.steps.length - 1 && (
                <div className={`step-connector ${step.status === 'completed' ? 'completed' : ''}`} />
              )}
            </div>

            <div className="step-content">
              <div className="step-header">
                <div className="step-title">
                  <span className="step-number">{step.id}.</span>
                  <h3>{step.name}</h3>
                </div>
                <span className={`status-badge ${getStatusBadge(step.status).class}`}>
                  {getStatusBadge(step.status).text}
                </span>
              </div>

              <p className="step-description">{step.description}</p>

              <div className="step-details">
                <div className="progress-info">
                  <span className="progress-text">
                    {step.processed}/{step.total} {step.status === 'completed' ? 'processed' : step.status === 'processing' ? 'extracted' : 'items'}
                  </span>
                  <span className="progress-percentage">{step.progress}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className={`progress-fill ${step.status}`}
                    style={{ width: `${step.progress}%` }}
                  />
                </div>
              </div>

              {step.status === 'processing' && (
                <div className="processing-details">
                  <div className="processing-animation">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                  <span>Processing in real-time...</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="pipeline-footer">
        <div className="footer-info">
          <span className="footer-icon">ℹ️</span>
          <div>
            <strong>Autonomous Processing</strong>
            <p>This pipeline automatically processes data from Enron emails, Slack messages, and AMI transcripts. 
            Large content is automatically chunked for optimal processing.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Processing
