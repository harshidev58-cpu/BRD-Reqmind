import { Mail, MessageSquare, FileText, Upload, RefreshCw } from 'lucide-react'
import './DataSources.css'

const DataSources = () => {
  const sources = [
    {
      name: 'Gmail',
      icon: Mail,
      status: 'Connected',
      lastSync: '2 hours ago',
      count: '345 messages',
      color: '#6366f1'
    },
    {
      name: 'Slack',
      icon: MessageSquare,
      status: 'Connected',
      lastSync: '5 minutes ago',
      count: '12 channels synced',
      color: '#8b5cf6'
    },
    {
      name: 'Meeting Transcripts',
      icon: FileText,
      status: 'Connected',
      lastSync: '1 hour ago',
      count: '23 transcripts',
      color: '#6366f1'
    }
  ]

  return (
    <div className="data-sources-page">
      <div className="page-header">
        <h1>Data Sources</h1>
      </div>

      <div className="total-messages-card">
        <div className="card-content">
          <div className="card-label">Total Messages Collected</div>
          <div className="card-value">1,245</div>
        </div>
        <div className="card-meta">
          <span className="meta-label">Last updated</span>
          <span className="meta-value">2 minutes ago</span>
        </div>
      </div>

      <div className="sources-grid">
        {sources.map((source) => {
          const Icon = source.icon
          return (
            <div key={source.name} className="source-card">
              <div className="source-header">
                <div className="source-title">
                  <h3>{source.name}</h3>
                </div>
                <div className="source-icon" style={{ background: source.color }}>
                  <Icon size={24} />
                </div>
              </div>

              <div className="source-details">
                <div className="detail-row">
                  <span className="detail-label">Status</span>
                  <span className="status-badge connected">
                    <span className="status-dot"></span>
                    {source.status}
                  </span>
                </div>

                <div className="detail-row">
                  <span className="detail-label">Last Sync</span>
                  <span className="detail-value">{source.lastSync}</span>
                </div>

                <div className="detail-row">
                  <span className="detail-label">Count</span>
                  <span className="detail-value">{source.count}</span>
                </div>
              </div>

              <button className="sync-button">
                <RefreshCw size={16} />
                Sync Now
              </button>
            </div>
          )
        })}

        <div className="source-card add-source">
          <div className="add-source-content">
            <div className="upload-icon">
              <Upload size={32} />
            </div>
            <h3>Add New Source</h3>
            <p>Connect additional data sources</p>
            <button className="add-button">Add Source</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DataSources
