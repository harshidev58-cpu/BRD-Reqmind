import { useState } from 'react'
import { FileText, Download, RefreshCw, ExternalLink, Sparkles, AlertCircle } from 'lucide-react'
import { generateBRDWithContext } from '../lib/api'
import './BRDGenerator.css'

const BRDGeneratorAdvanced = () => {
  const [projectName, setProjectName] = useState('')
  const [emailText, setEmailText] = useState('')
  const [slackText, setSlackText] = useState('')
  const [meetingText, setMeetingText] = useState('')
  const [instructions, setInstructions] = useState('')
  const [useInstructions, setUseInstructions] = useState(false)
  const [loading, setLoading] = useState(false)
  const [brdData, setBrdData] = useState(null)
  const [error, setError] = useState(null)

  const instructionPresets = [
    {
      name: 'MVP Focus',
      value: 'Focus only on MVP features and Phase 1. Ignore future enhancements and nice-to-have features.'
    },
    {
      name: 'Exclude Marketing',
      value: 'Ignore all marketing and sales discussions. Focus only on technical requirements and product features.'
    },
    {
      name: 'Mobile Priority',
      value: 'Prioritize mobile features and mobile-first design. Desktop features are secondary.'
    },
    {
      name: 'Security Focus',
      value: 'Prioritize security and compliance requirements. Highlight all security-related discussions.'
    },
    {
      name: 'Quick Timeline',
      value: 'Client deadline is end of Q1. Prioritize features that can be delivered quickly. Exclude complex features.'
    }
  ]

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
      const payload = {
        projectName: projectName.trim(),
        emailText: emailText.trim() || undefined,
        slackText: slackText.trim() || undefined,
        meetingText: meetingText.trim() || undefined
      }

      // Add instructions if enabled
      if (useInstructions && instructions.trim()) {
        payload.instructions = instructions.trim()
      }

      const response = await generateBRDWithContext(payload)
      setBrdData(response)
    } catch (err) {
      setError(err.message || 'Failed to generate BRD')
    } finally {
      setLoading(false)
    }
  }

  const handleExportPDF = () => {
    alert('PDF export coming soon!')
  }

  const handleRegenerate = () => {
    setBrdData(null)
    setError(null)
  }

  const handlePresetClick = (preset) => {
    setInstructions(preset.value)
    setUseInstructions(true)
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
        <h1>🤖 Advanced BRD Generator</h1>
        <p className="page-subtitle">
          Generate BRDs with AI-powered project instructions and constraints
        </p>
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

            {/* AI Instructions Section */}
            <div className="instructions-section">
              <div className="instructions-header">
                <div className="instructions-toggle">
                  <input
                    type="checkbox"
                    id="use-instructions"
                    checked={useInstructions}
                    onChange={(e) => setUseInstructions(e.target.checked)}
                    className="toggle-checkbox"
                  />
                  <label htmlFor="use-instructions" className="toggle-label">
                    <Sparkles size={16} />
                    Enable AI Instructions (Gemini-powered)
                  </label>
                </div>
                <span className="beta-badge">BETA</span>
              </div>

              {useInstructions && (
                <>
                  <div className="instructions-info">
                    <AlertCircle size={16} />
                    <span>
                      Provide natural language instructions to guide BRD generation. 
                      Gemini AI will convert them into structured constraints.
                    </span>
                  </div>

                  <div className="form-group">
                    <label>Project Instructions</label>
                    <textarea
                      value={instructions}
                      onChange={(e) => setInstructions(e.target.value)}
                      placeholder="e.g., Focus only on Phase 1, ignore marketing discussions, prioritize mobile features..."
                      rows={4}
                      className="input-field"
                    />
                  </div>

                  <div className="preset-section">
                    <label className="preset-label">Quick Presets:</label>
                    <div className="preset-buttons">
                      {instructionPresets.map((preset, index) => (
                        <button
                          key={index}
                          onClick={() => handlePresetClick(preset)}
                          className="preset-btn"
                        >
                          {preset.name}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="instructions-example">
                    <strong>Examples:</strong>
                    <ul>
                      <li>"Focus only on MVP and ignore internal discussions"</li>
                      <li>"Client deadline is June 15. Prioritize quick wins"</li>
                      <li>"Exclude all marketing content. Technical requirements only"</li>
                      <li>"Mobile-first approach. Desktop is secondary"</li>
                    </ul>
                  </div>
                </>
              )}
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
                placeholder="Paste meeting transcript content (supports large transcripts with auto-chunking)..."
                rows={4}
                className="input-field"
              />
              <span className="helper-text">
                ✨ Large transcripts (3000+ words) are automatically chunked and processed
              </span>
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
                  {useInstructions ? 'Processing with AI Instructions...' : 'Generating BRD...'}
                </>
              ) : (
                <>
                  {useInstructions ? <Sparkles size={16} /> : <FileText size={16} />}
                  {useInstructions ? 'Generate with AI Instructions' : 'Generate BRD & Analysis'}
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
              {brdData.constraints && (
                <div className="constraints-applied">
                  <Sparkles size={14} />
                  <span>AI Instructions Applied</span>
                </div>
              )}
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

          {/* Show Applied Constraints */}
          {brdData.constraints && (
            <div className="constraints-card">
              <h3>
                <Sparkles size={20} />
                Applied AI Constraints
              </h3>
              <div className="constraints-grid">
                {brdData.constraints.scope && (
                  <div className="constraint-item">
                    <span className="constraint-label">Scope:</span>
                    <span className="constraint-value">{brdData.constraints.scope}</span>
                  </div>
                )}
                {brdData.constraints.exclude_topics && brdData.constraints.exclude_topics.length > 0 && (
                  <div className="constraint-item">
                    <span className="constraint-label">Excluded Topics:</span>
                    <span className="constraint-value">
                      {brdData.constraints.exclude_topics.join(', ')}
                    </span>
                  </div>
                )}
                {brdData.constraints.priority_focus && (
                  <div className="constraint-item">
                    <span className="constraint-label">Priority Focus:</span>
                    <span className="constraint-value">{brdData.constraints.priority_focus}</span>
                  </div>
                )}
                {brdData.constraints.deadline_override && (
                  <div className="constraint-item">
                    <span className="constraint-label">Deadline:</span>
                    <span className="constraint-value">{brdData.constraints.deadline_override}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Show Chunking Info */}
          {brdData.chunking_applied && (
            <div className="chunking-info">
              <AlertCircle size={16} />
              <span>
                Large content detected: Processed in {brdData.chunk_count || 'multiple'} chunks for optimal results
              </span>
            </div>
          )}

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

export default BRDGeneratorAdvanced
