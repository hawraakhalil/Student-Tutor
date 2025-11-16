import React, { useEffect, useState } from 'react'
import api from '../api'
import TutorCard from './TutorCard'

export default function StudentDashboard(){
  const [students, setStudents] = useState([])
  const [selected, setSelected] = useState(null)
  const [recs, setRecs] = useState([])
  const [useAi, setUseAi] = useState(true)
  const [loading, setLoading] = useState(false)

  useEffect(()=>{ api.fetchStudents().then(s=>{ setStudents(s); if(s.length) setSelected(s[0].id) }).catch(()=>{}) }, [])

  useEffect(()=>{ if(selected) loadRecs() }, [selected, useAi])

  async function loadRecs(){
    if(!selected) return
    setLoading(true)
    try{
      const r = await api.getStudentRecommendations(selected, useAi)
      let arr = r
      if(!Array.isArray(r) && r.recommended_tutors) arr = r.recommended_tutors
      setRecs(Array.isArray(arr)?arr:[])
    }finally{ setLoading(false) }
  }

  return (
    <div>
      <div className="card mb-4">
        <div className="card-body d-flex gap-3 align-items-center">
          <div style={{minWidth:240}}>
            <label className="form-label small">Student</label>
            <select className="form-select" value={selected||''} onChange={e=>setSelected(Number(e.target.value))}>
              {students.map(s=> <option key={s.id} value={s.id}>{s.name} — {s.city||''}</option>)}
            </select>
          </div>
          <div className="form-check form-switch ms-3">
            <input className="form-check-input" type="checkbox" id="useAi" checked={useAi} onChange={e=>setUseAi(e.target.checked)} />
            <label className="form-check-label small" htmlFor="useAi">Use AI explanations</label>
          </div>
          <div className="ms-auto text-muted small">{loading ? 'Loading recommendations...' : 'Recommendations update automatically'}</div>
        </div>
      </div>

      <div>
        {recs.length === 0 && !loading ? <div className="text-muted">No recommendations yet.</div> : recs.map(t => <TutorCard key={t.id} t={t} />)}
      </div>
    </div>
  )
}
