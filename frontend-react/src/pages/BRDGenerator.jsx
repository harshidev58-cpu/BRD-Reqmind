import { useState } from 'react'
import { FileText, Download, RefreshCw, ExternalLink } from 'lucide-react'
import { generateBRDWithAlignment } from '../lib/api'
import './BRDGenerator.css'

const BRDGenerator = () => {
  const [projectName, setProjectName] = useState('')
  const [emailText, setEmailText] = useState('')
  const [slackText, setSlackText] = useState('')
  const [meetingText, setMeetingText] = useState('')
  const [loading, setLoading] = useState(false)
  const [brdData, setBrdData] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    if (!projectName.trim()) {
      setError('Project name is required')
      return
    }

    if (!emailText.trim() && !slackText.trim() && !meetingText.trim()) {
      setError('At least one source (email, slack, or meeting) must be provided')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await generateBRDWithAlignment({
        projectName: projectName.trim(),
        emailText: emailText.trim() || undefined,
        slackText: slackText.trim() || undefined,
        meetingText: meetingText.trim() || undefined
      })

      setBrdData(response)
    } catch (err) {
      setError(err.message || 'Failed to generate BRD')
    } finally {
      setLoading(false)
    }
  }

  const handleExportPDF = () => {
    // TODO: Implement PDF export
    alert('PDF export coming soon!')
  }

  const handleRegenerate = () => {
    setBrdData(null)
    setError(null)
  }

  const getPriorityColor = (priority) => {
    const colors = {
      High: '#ef4444',
      Medium: '#f59e0b',
      Low: '#10b981'
    }
    return colors[priority] || colors.Medium
  }

  return (
    <div className="brd-generator-page">
      <div className="page-header">
        <h1>BRD Generator</h1>
        <p className="page-subtitle">Generate Business Requirements Documents from multi-channel communication</p>
      </div>

      {!brdData ? (
        <div className="input-section">
          <div className="input-card">
            <h3>Project Information</h3>
            <div className="form-group">
              <label>Project Name *</label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g., Q1 Platform Release"
                className="input-field"
              />
            </div>

            <h3 style={{ marginTop: '2rem' }}>Communication Sources</h3>
            <p className="helper-text">Provide at least one source</p>

            <div className="form-group">
              <label>Email Communications</label>
              <textarea
                value={emailText}
                onChange={(e) => setEmailText(e.target.value)}
                placeholder="Paste email content related to the project..."
                rows={4}
                className="input-field"
              />
            </div>

            <div className="form-group">
              <label>Slack Messages</label>
              <textarea
                value={slackText}
                onChange={(e) => setSlackText(e.target.value)}
                placeholder="Paste Slack messages related to the project..."
                rows={4}
                className="input-field"
              />
            </div>

            <div className="form-group">
              <label>Meeting Transcripts</label>
              <textarea
                value={meetingText}
                onChange={(e) => setMeetingText(e.target.value)}
                placeholder="Paste meeting transcript content..."
                rows={4}
                className="input-field"
              />
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="generate-button"
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="spinning" />
                  Generating BRD...
                </>
              ) : (
                <>
                  <FileText size={16} />
                  Generate BRD & Analysis
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        <div className="brd-output">
          <div className="brd-header-card">
            <div className="brd-meta">
              <h3>Generated from:</h3>
              <p>
                {[
                  emailText && 'Email',
                  slackText && 'Slack',
                  meetingText && 'Meeting'
                ].filter(Boolean).join(', ')}
              </p>
            </div>
            <div className="brd-actions">
              <button className="action-button secondary">
                <ExternalLink size={16} />
                View Sources
              </button>
              <button className="action-button primary" onClick={handleExportPDF}>
                <Download size={16} />
                Export PDF
              </button>
              <button className="action-button secondary" onClick={handleRegenerate}>
                <RefreshCw size={16} />
                Regenerate
              </button>
            </div>
          </div>

          <div className="brd-content">
            <div className="brd-section">
              <h2>Project Objective</h2>
              <p>{brdData.brd.executiveSummary}</p>
            </div>

            <div className="brd-section">
              <h2>Business Objectives</h2>
              <ul className="objectives-list">
                {brdData.brd.businessObjectives.map((obj, index) => (
                  <li key={index}>{obj}</li>
                ))}
              </ul>
            </div>

            <div className="brd-section">
              <h2>Stakeholders</h2>
              <div className="stakeholders-grid">
                {brdData.brd.stakeholders.map((stakeholder, index) => (
                  <div key={index} className="stakeholder-card">
                    <div className="stakeholder-name">{stakeholder.name}</div>
                    <div className="stakeholder-role">{stakeholder.role}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="brd-section">
              <h2>Functional Requirements</h2>
              <div className="requirements-list">
                {brdData.brd.requirements.map((req) => (
                  <div key={req.id} className="requirement-card">
                    <div className="requirement-header">
                      <span className="requirement-id">{req.id}</span>
                      <span 
                        className="priority-badge"
                        style={{ background: getPriorityColor(req.priority) }}
                      >
                        {req.priority}
                      </span>
                    </div>
                    <p className="requirement-description">{req.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BRDGenerator
