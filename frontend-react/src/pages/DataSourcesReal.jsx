import { useState, useEffect } from 'react'
import { Mail, MessageSquare, FileText, Database, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react'
import { getDatasetStatus, generateBRDFromDataset } from '../lib/api'
import './DataSources.css'

const DataSourcesReal = () => {
  const [datasetStatus, setDatasetStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [brdResult, setBrdResult] = useState(null)
  const [error, setError] = useState(null)

  // Form state
  const [projectName, setProjectName] = useState('Autonomous Analysis')
  const [keywords, setKeywords] = useState('project, deadline, requirement, feature')
  const [sampleSize, setSampleSize] = useState(20)

  useEffect(() => {
    loadDatasetStatus()
  }, [])

  const loadDatasetStatus = async () => {
    try {
      const status = await getDatasetStatus()
      setDatasetStatus(status)
    } catch (error) {
      console.error('Error loading dataset status:', error)
      setError('Failed to load dataset status')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateBRD = async () => {
    setGenerating(true)
    setError(null)
    setBrdResult(null)

    try {
      const keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k)
      
      const result = await generateBRDFromDataset({
        projectName,
        keywords: keywordArray,
        sampleSize
      })

      setBrdResult(result)
    } catch (err) {
      setError(err.message || 'Failed to generate BRD from dataset')
    } finally {
      setGenerating(false)
    }
  }

  const handlePreset = (presetName, presetKeywords) => {
    setProjectName(presetName)
    setKeywords(presetKeywords)
  }

  if (loading) {
    return (
      <div className="data-sources-page">
        <div className="page-header">
          <h1>Autonomous Data Sources</h1>
        </div>
        <p style={{ color: '#64748b' }}>Loading dataset status...</p>
      </div>
    )
  }

  return (
    <div className="data-sources-page">
      <div className="page-header">
        <h1>🤖 Autonomous Data Sources</h1>
        <p className="page-subtitle">Real-world datasets: Enron Emails & AMI Meeting Transcripts</p>
      </div>

      {/* Dataset Status Cards */}
      <div className="dataset-status-grid">
        <div className="status-card">
          <div className="status-header">
            <Database size={24} className="status-icon" />
            <h3>Dataset Mode</h3>
          </div>
          <div className="status-value">
            {datasetStatus?.dataset_mode_enabled ? (
              <span className="status-badge enabled">
                <CheckCircle size={16} />
                Enabled
              </span>
            ) : (
              <span className="status-badge disabled">
                <AlertCircle size={16} />
                Disabled
              </span>
            )}
          </div>
        </div>

        <div className="status-card">
          <div className="status-header">
            <Mail size={24} className="status-icon" />
            <h3>Enron Email Dataset</h3>
          </div>
          <div className="status-details">
            <div className="detail-row">
              <span>Status:</span>
              <span className={datasetStatus?.email_dataset_configured ? 'text-success' : 'text-error'}>
                {datasetStatus?.email_dataset_configured ? 'Configured' : 'Not Configured'}
              </span>
            </div>
            <div className="detail-row">
              <span>Max Emails:</span>
              <span>{datasetStatus?.max_emails || 0}</span>
            </div>
          </div>
        </div>

        <div className="status-card">
          <div className="status-header">
            <FileText size={24} className="status-icon" />
            <h3>AMI Meeting Transcripts</h3>
          </div>
          <div className="status-details">
            <div className="detail-row">
              <span>Status:</span>
              <span className={datasetStatus?.meeting_dataset_configured ? 'text-success' : 'text-error'}>
                {datasetStatus?.meeting_dataset_configured ? 'Configured' : 'Not Configured'}
              </span>
            </div>
            <div className="detail-row">
              <span>Max Meetings:</span>
              <span>{datasetStatus?.max_meetings || 0}</span>
            </div>
          </div>
        </div>

        <div className="status-card">
          <div className="status-header">
            <MessageSquare size={24} className="status-icon" />
            <h3>Slack Simulation</h3>
          </div>
          <div className="status-details">
            <div className="detail-row">
              <span>Status:</span>
              <span className="text-success">Active</span>
            </div>
            <div className="detail-row">
              <span>Source:</span>
              <span>Email → Slack</span>
            </div>
          </div>
        </div>
      </div>

      {/* BRD Generation from Dataset */}
      {datasetStatus?.dataset_mode_enabled && (
        <div className="generation-section">
          <h2>Generate BRD from Datasets</h2>
          <p className="section-subtitle">
            Autonomously analyze Enron emails and AMI transcripts to generate BRDs
          </p>

          <div className="generation-form">
            <div className="form-row">
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="input-field"
                  placeholder="Enter project name"
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
              </div>
            </div>

            <div className="form-group">
              <label>Keywords (comma-separated)</label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                className="input-field"
                placeholder="e.g., project, deadline, requirement"
              />
            </div>

            {/* Preset Buttons */}
            <div className="preset-buttons">
              <button
                onClick={() => handlePreset('Timeline Conflict Analysis', 'deadline, timeline, delivery, schedule, date')}
                className="preset-btn"
              >
                📅 Timeline Conflicts
              </button>
              <button
                onClick={() => handlePreset('Requirement Volatility Analysis', 'requirement, feature, specification, scope, change')}
                className="preset-btn"
              >
                📋 Requirement Changes
              </button>
              <button
                onClick={() => handlePreset('Stakeholder Disagreement Analysis', 'disagree, concern, issue, problem, conflict')}
                className="preset-btn"
              >
                ⚔️ Stakeholder Conflicts
              </button>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button
              onClick={handleGenerateBRD}
              disabled={generating || !projectName}
              className="generate-button"
            >
              {generating ? (
                <>
                  <RefreshCw size={16} className="spinning" />
                  Analyzing Datasets...
                </>
              ) : (
                <>
                  <Database size={16} />
                  Generate BRD from Datasets
                </>
              )}
            </button>
          </div>

          {/* Results */}
          {brdResult && (
            <div className="brd-results">
              <h3>Generated BRD</h3>
              
              <div className="result-meta">
                <div className="meta-card">
                  <span className="meta-label">Emails Processed:</span>
                  <span className="meta-value">{brdResult.metadata?.email_count || 0}</span>
                </div>
                <div className="meta-card">
                  <span className="meta-label">Meetings Processed:</span>
                  <span className="meta-value">{brdResult.metadata?.meeting_count || 0}</span>
                </div>
                <div className="meta-card">
                  <span className="meta-label">Keywords Used:</span>
                  <span className="meta-value">{brdResult.metadata?.keywords_used?.length || 0}</span>
                </div>
              </div>

              {brdResult.conflicts && brdResult.conflicts.length > 0 && (
                <div className="conflicts-detected">
                  <h4>🚨 Auto-Detected Conflicts: {brdResult.conflicts.length}</h4>
                  {brdResult.conflicts.map((conflict, index) => (
                    <div key={index} className="conflict-item">
                      <div className="conflict-type">{conflict.type}</div>
                      <div className="conflict-patterns">
                        <span>Pattern 1: {conflict.pattern1}</span>
                        <span>Pattern 2: {conflict.pattern2}</span>
                      </div>
                      <div className="conflict-sources">
                        Sources: {conflict.sources_pattern1.join(', ')} vs {conflict.sources_pattern2.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="brd-content">
                <h4>Project: {brdResult.projectName}</h4>
                <p><strong>Executive Summary:</strong> {brdResult.executiveSummary}</p>
                
                <div className="brd-section">
                  <strong>Business Objectives:</strong>
                  <ul>
                    {brdResult.businessObjectives?.map((obj, i) => (
                      <li key={i}>{obj}</li>
                    ))}
                  </ul>
                </div>

                <div className="brd-section">
                  <strong>Requirements:</strong>
                  {brdResult.requirements?.map((req, i) => (
                    <div key={i} className="requirement-item">
                      <span className="req-id">{req.id}</span>
                      <span className="req-desc">{req.description}</span>
                      <span className={`req-priority priority-${req.priority.toLowerCase()}`}>
                        {req.priority}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {!datasetStatus?.dataset_mode_enabled && (
        <div className="dataset-disabled">
          <AlertCircle size={48} />
          <h3>Dataset Mode Disabled</h3>
          <p>Enable dataset mode in your backend configuration to use Enron emails and AMI transcripts.</p>
        </div>
      )}
    </div>
  )
}

export default DataSourcesReal
