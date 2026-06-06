import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import DataSources from './pages/DataSources'
import Processing from './pages/Processing'
import AlignmentIntelligence from './pages/AlignmentIntelligence'
import BRDGenerator from './pages/BRDGenerator'
import Stakeholders from './pages/Stakeholders'
import SourceExplorer from './pages/SourceExplorer'
import './App.css'

function App() {
  const [currentProject, setCurrentProject] = useState('Project Alpha')

  return (
    <Router>
      <div className="app">
        <Sidebar />
        <div className="main-content">
          <Header currentProject={currentProject} />
          <div className="page-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/data-sources" element={<DataSources />} />
              <Route path="/processing" element={<Processing />} />
              <Route path="/alignment" element={<AlignmentIntelligence />} />
              <Route path="/brd-generator" element={<BRDGenerator />} />
              <Route path="/stakeholders" element={<Stakeholders />} />
              <Route path="/source-explorer" element={<SourceExplorer />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  )
}

export default App
