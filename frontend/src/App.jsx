import React, { useState } from 'react'
import Search from './components/Search'
import StudentDashboard from './components/StudentDashboard'
import Home from './components/Home'
import Admin from './components/Admin'

export default function App(){
  const [view, setView] = useState('home')

  return (
    <div className="app-root">
      <header className="app-header d-flex align-items-center px-4">
        <div className="brand" role="button" tabIndex={0} onClick={()=>setView('home')} onKeyDown={(e)=>{ if(e.key==='Enter' || e.key===' ') setView('home') }}>TutorFinder</div>
        <nav className="ms-auto">
          <button className={`btn btn-sm me-2 ${view==='search'?'btn-primary':'btn-outline-primary'}`} onClick={()=>setView('search')}>Search</button>
          <button className={`btn btn-sm ${view==='students'?'btn-primary':'btn-outline-primary'}`} onClick={()=>setView('students')}>Student Dashboard</button>
          <button className={`btn btn-sm ms-2 ${view==='admin'?'btn-danger':'btn-outline-danger'}`} onClick={()=>setView('admin')}>Admin</button>
        </nav>
      </header>

      <main className="container py-4">
        {view === 'home' ? <Home onGetStarted={(v)=>setView(v)} /> : null}
        {view === 'search' ? <Search /> : null}
        {view === 'students' ? <StudentDashboard /> : null}
        {view === 'admin' ? <Admin /> : null}
        <footer className="mt-5 text-muted small">Built with FastAPI + React. Use the student dashboard to enable AI explanations.</footer>
      </main>
    </div>
  )
}
