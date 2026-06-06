import { useState } from 'react'
import { Search, Filter, Mail, MessageSquare, FileText } from 'lucide-react'
import './SourceExplorer.css'

const SourceExplorer = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSource, setSelectedSource] = useState('all')

  const mockMessages = [
    {
      id: 1,
      type: 'email',
      from: 'Product Team',
      subject: 'Q1 Release Timeline',
      preview: 'We need to finalize the Q1 release timeline by end of this week...',
      timestamp: '2 hours ago',
      tags: ['timeline', 'release']
    },
    {
      id: 2,
      type: 'slack',
      from: 'Engineering Team',
      subject: 'Backend API Discussion',
      preview: 'The new API endpoints are ready for review. Can we schedule a sync?',
      timestamp: '5 hours ago',
      tags: ['api', 'review']
    },
    {
      id: 3,
      type: 'meeting',
      from: 'Design Team',
      subject: 'UI/UX Review Meeting',
      preview: 'Discussed the new dashboard design and user flow improvements...',
      timestamp: '1 day ago',
      tags: ['design', 'ui']
    }
  ]

  const getSourceIcon = (type) => {
    const icons = {
      email: Mail,
      slack: MessageSquare,
      meeting: FileText
    }
    return icons[type] || Mail
  }

  const getSourceColor = (type) => {
    const colors = {
      email: '#6366f1',
      slack: '#8b5cf6',
      meeting: '#ec4899'
    }
    return colors[type] || '#6366f1'
  }

  const filteredMessages = mockMessages.filter(msg => {
    const matchesSearch = searchQuery === '' || 
      msg.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      msg.preview.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesSource = selectedSource === 'all' || msg.type === selectedSource
    
    return matchesSearch && matchesSource
  })

  return (
    <div className="source-explorer-page">
      <div className="page-header">
        <h1>Source Explorer</h1>
        <p className="page-subtitle">Search and explore all communication sources</p>
      </div>

      <div className="explorer-controls">
        <div className="search-bar">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search messages, emails, transcripts..."
            className="search-input"
          />
        </div>

        <div className="filter-buttons">
          <button 
            className={`filter-btn ${selectedSource === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedSource('all')}
          >
            <Filter size={16} />
            All Sources
          </button>
          <button 
            className={`filter-btn ${selectedSource === 'email' ? 'active' : ''}`}
            onClick={() => setSelectedSource('email')}
          >
            <Mail size={16} />
            Email
          </button>
          <button 
            className={`filter-btn ${selectedSource === 'slack' ? 'active' : ''}`}
            onClick={() => setSelectedSource('slack')}
          >
            <MessageSquare size={16} />
            Slack
          </button>
          <button 
            className={`filter-btn ${selectedSource === 'meeting' ? 'active' : ''}`}
            onClick={() => setSelectedSource('meeting')}
          >
            <FileText size={16} />
            Meetings
          </button>
        </div>
      </div>

      <div className="messages-list">
        {filteredMessages.map((message) => {
          const Icon = getSourceIcon(message.type)
          return (
            <div key={message.id} className="message-card">
              <div 
                className="message-icon"
                style={{ background: getSourceColor(message.type) }}
              >
                <Icon size={20} />
              </div>
              <div className="message-content">
                <div className="message-header">
                  <div className="message-meta">
                    <span className="message-from">{message.from}</span>
                    <span className="message-timestamp">{message.timestamp}</span>
                  </div>
                  <span className="source-badge" style={{ color: getSourceColor(message.type) }}>
                    {message.type}
                  </span>
                </div>
                <h3 className="message-subject">{message.subject}</h3>
                <p className="message-preview">{message.preview}</p>
                <div className="message-tags">
                  {message.tags.map((tag, index) => (
                    <span key={index} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {filteredMessages.length === 0 && (
        <div className="empty-state">
          <Search size={48} className="empty-icon" />
          <h3>No messages found</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  )
}

export default SourceExplorer
