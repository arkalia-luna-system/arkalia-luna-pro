import React from 'react'
import { Route, Routes } from 'react-router-dom'
import ArkaliaLunaHomepage from '../components/ArkaliaLunaHomepage'

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<ArkaliaLunaHomepage />} />
        {/* Routes futures pour les différentes sections */}
        <Route path="/modules" element={<div className="min-h-screen bg-arkalia-black text-slate-200 p-8"><h1 className="text-4xl font-orbitron">Modules</h1></div>} />
        <Route path="/api" element={<div className="min-h-screen bg-arkalia-black text-slate-200 p-8"><h1 className="text-4xl font-orbitron">API</h1></div>} />
        <Route path="/usage" element={<div className="min-h-screen bg-arkalia-black text-slate-200 p-8"><h1 className="text-4xl font-orbitron">Usage</h1></div>} />
        <Route path="/architecture" element={<div className="min-h-screen bg-arkalia-black text-slate-200 p-8"><h1 className="text-4xl font-orbitron">Architecture</h1></div>} />
        <Route path="/logs" element={<div className="min-h-screen bg-arkalia-black text-slate-200 p-8"><h1 className="text-4xl font-orbitron">Logs</h1></div>} />
        <Route path="/mind" element={<div className="min-h-screen bg-arkalia-black text-slate-200 p-8"><h1 className="text-4xl font-orbitron">Mind</h1></div>} />
      </Routes>
    </div>
  )
}

export default App
