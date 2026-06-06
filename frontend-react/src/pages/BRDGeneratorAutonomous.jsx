import { useState } from 'react'
import { FileText, Download, RefreshCw, Sparkles, AlertCircle, Database, Zap } from 'lucide-react'
import { generateBRDFromDataset } from '../lib/api'
import './BRDGenerator.css'

const BRDGeneratorAutonomous = () => {
  const [projectName, setProjectName] = useState('')
  const [keywords, setKeywords] = useState('project, deadline, requirement, feature')
  const [sampleSize, setSampleSize] = useState(30)
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

  const scenarioPresets = [
    {
      name: '📅 Timeline Conflicts',
      projectName: 'Timeline Conflict Analysis',
      keywords: 'deadline, timeline, delivery, schedule, date',
      instructions: 'Focus on timeline discussions and deadline conflicts. Highlight any misalignments in delivery dates.'
    },
    {
      name: '📋 Requirements',
      projectName: 'Requirement Analysis',
      keywords: 'requirement, feature, specification, scope, change',
      instructions: 'Focus on functional requirements and feature specifications. Track requirement changes and scope evolution.'
    },
    {
      name: '⚔️ Conflicts',
      projectName: 'Stakeholder Conflict Analysis',
      keywords: 'disagree, concern, issue, problem, conflict',
      instructions: 'Identify stakeholder disagreements and conflicting priorities. Highlight areas needing alignment.'
    },
    {
      name: '🚀 MVP Planning',
      projectName: 'MVP Planning',
      keywords: 'mvp, minimum, viable, phase, priority',
      instructions: 'Focus only on MVP and Phase 1 features. Exclude future enhancements. Prioritize quick wins.'
    }
  ]

  const handleGenerate = async () => {
    if (!projectName.trim()) {
      setError('Project name is required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k)
      
      const payload = {
        projectName: projectName.trim(),
        keywords: keywordArray,
        sampleSize
      }

      // Add instructions if enabled
      if (useInstructions && instructions.trim()) {
        payload.instructions = instructions.trim()
      }

      const response = await generateBRDFromDataset(payload)
      setBrdData(response)
    } catch (err) {
      setError(err.message || 'Failed to generate BRD from datasets')
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

  const handleScenarioClick = (scenario) => {
    setProjectName(scenario.projectName)
    setKeywords(scenario.keywords)
    if (scenario.instructions) {
      setInstructions(scenario.instructions)
      setUseInstructions(true)
    }
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
        <h1>🤖 Autonomous BRD Generator</h1>
        <p className="page-subtitle">
          AI-powered BRD generation from Enron emails, Slack, and AMI meeting transcripts
        </p>
      </div>

      {!brdData ? (
        <div className="input-section">
          {/* Autonomous Data Info */}
          <div className="autonomous-info-card">
            <div className="info-icon">
              <Database size={32} />
            </div>
            <div className="info-content">
              <h3>Fully Autonomous Data Ingestion</h3>
              <p>
                This system automatically extracts and analyzes data from:
              </p>
              <div className="data-sources-list">
                <div className="data-source-item">
                  <span className="source-icon">📧</span>
                  <div>
                    <strong>Enron Email Dataset</strong>
                    <span>500,000+ real business emails</span>
                  </div>
                </div>
                <div className="data-source-item">
                  <span className="source-icon">💬</span>
                  <div>
                    <strong>Slack Simulation</strong>
                    <span>Auto-converted from emails</span>
                  </div>
                </div>
                <div className="data-source-item">
                  <span className="source-icon">🎤</span>
                  <div>
                    <strong>AMI Meeting Transcripts</strong>
                    <span>279 design meeting transcripts</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="input-card">
            <h3>Project Configuration</h3>
            
            {/* Scenario Presets */}
            <div className="scenario-presets">
              <label className="preset-label">Quick Scenarios:</label>
              <div className="scenario-buttons">
                {scenarioPresets.map((scenario, index) => (
                  <button
                    key={index}
                    onClick={() => handleScenarioClick(scenario)}
                    className="scenario-btn"
                  >
                    {scenario.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-row">
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

              <div className="form-group">
                <label>Sample Size</label>
                <input
                  type="number"
                  value={sampleSize}
                  onChange={(e) => setSampleSize(parseInt(e.target.value))}
                  className="input-field"
                  min="5"
                  max="100"
                />
                <span className="helper-text">
                  Number of items to analyze from datasets
                </span>
              </div>
            </div>

            <div className="form-group">
              <label>Keywords (comma-separated)</label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="e.g., project, deadline, requirement"
                className="input-field"
              />
              <span className="helper-text">
                Filter dataset content by these keywords
              </span>
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
                </>
              )}
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
                  <span className="loading-stages">
                    {loading && 'Analyzing datasets...'}
                  </span>
                </>
              ) : (
                <>
                  <Zap size={16} />
                  Generate BRD Autonomously
                </>
              )}
            </button>

            <div className="generation-info">
              <Sparkles size={14} />
              <span>
                This will automatically extract and analyze data from Enron emails, 
                Slack messages, and AMI transcripts based on your keywords
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="brd-output">
          <div className="brd-header-card">
            <div className="brd-meta">
              <h3>Generated from Autonomous Analysis:</h3>
              <div className="source-stats">
                <div className="stat-item">
                  <span className="stat-icon">📧</span>
                  <span>{brdData.metadata?.email_count || 0} emails</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">🎤</span>
                  <span>{brdData.metadata?.meeting_count || 0} meetings</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">🔍</span>
                  <span>{brdData.metadata?.keywords_used?.length || 0} keywords</span>
                </div>
              </div>
              {brdData.metadata?.applied_constraints && (
                <div className="constraints-applied-card">
                  <div className="constraints-header">
                    <Sparkles size={16} />
                    <strong>AI Instructions Applied</strong>
                  </div>
                  <div className="constraints-details">
                    {brdData.metadata.applied_constraints.scope && (
                      <div className="constraint-item">
                        <span className="constraint-label">Scope:</span>
                        <span className="constraint-value">{brdData.metadata.applied_constraints.scope}</span>
                      </div>
                    )}
                    {brdData.metadata.applied_constraints.exclude_topics?.length > 0 && (
                      <div className="constraint-item">
                        <span className="constraint-label">Excluded:</span>
                        <span className="constraint-value">{brdData.metadata.applied_constraints.exclude_topics.join(', ')}</span>
                      </div>
                    )}
                    {brdData.metadata.applied_constraints.priority_focus && (
                      <div className="constraint-item">
                        <span className="constraint-label">Priority:</span>
                        <span className="constraint-value">{brdData.metadata.applied_constraints.priority_focus}</span>
                      </div>
                    )}
                    {brdData.metadata.applied_constraints.deadline_override && (
                      <div className="constraint-item">
                        <span className="constraint-label">Deadline:</span>
                        <span className="constraint-value">{brdData.metadata.applied_constraints.deadline_override}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            <div className="brd-actions">
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

          {/* Auto-Detected Conflicts */}
          {brdData.conflicts && brdData.conflicts.length > 0 && (
            <div className="conflicts-detected">
              <h4>🚨 Auto-Detected Conflicts: {brdData.conflicts.length}</h4>
              {brdData.conflicts.map((conflict, index) => (
                <div key={index} className="conflict-item">
                  <div className="conflict-type">{conflict.type.replace('_', ' ')}</div>
                  <div className="conflict-patterns">
                    <span>Pattern 1: <strong>{conflict.pattern1}</strong></span>
                    <span>Pattern 2: <strong>{conflict.pattern2}</strong></span>
                  </div>
                  <div className="conflict-sources">
                    Sources: {conflict.sources_pattern1.join(', ')} vs {conflict.sources_pattern2.join(', ')}
                  </div>
                  <div className="conflict-severity">
                    Severity: <span className={`severity-${conflict.severity}`}>{conflict.severity}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="brd-content">
            <div className="brd-section">
              <h2>Project Objective</h2>
              <p>{brdData.executiveSummary}</p>
            </div>

            <div className="brd-section">
              <h2>Business Objectives</h2>
              <ul className="objectives-list">
                {brdData.businessObjectives?.map((obj, index) => (
                  <li key={index}>{obj}</li>
                ))}
              </ul>
            </div>

            <div className="brd-section">
              <h2>Stakeholders</h2>
              <div className="stakeholders-grid">
                {brdData.stakeholders?.map((stakeholder, index) => (
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
                {brdData.requirements?.map((req) => (
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

export default BRDGeneratorAutonomous
