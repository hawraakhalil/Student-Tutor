import React, { useEffect, useState } from 'react'
import api from '../api'
import TutorForm from './TutorForm'

export default function TutorManager(){
  const [tutors, setTutors] = useState([])
  const [loading, setLoading] = useState(false)
  const [editing, setEditing] = useState(null) // tutor object or null

  async function load(){
    setLoading(true)
    try{
      const res = await api.searchTutors({})
      setTutors(res)
    }finally{ setLoading(false) }
  }

  useEffect(()=>{ load() }, [])

  async function onDelete(id){
    if(!confirm('Delete this tutor? This action cannot be undone.')) return
    try{
      await api.deleteTutor(id)
      await load()
    }catch(e){ alert('Delete failed: '+e.message) }
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="m-0">Tutors</h4>
        <div>
          <button className="btn btn-success" onClick={()=>setEditing({})}>Add Tutor</button>
        </div>
      </div>

      {editing ? <TutorForm tutor={editing} onCancel={()=>{setEditing(null)}} onSaved={async ()=>{ setEditing(null); await load() }} /> : (
        <div>
          {loading ? <div className="text-muted">Loading...</div> : (
            <div className="list-group">
              {tutors.map(t => (
                <div key={t.id} className="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{t.name}</strong>
                    <div className="small text-muted">{(t.subjects||[]).join(', ')} — ${t.hourly_rate}</div>
                  </div>
                  <div>
                    <button className="btn btn-sm btn-outline-primary me-2" onClick={async ()=>{
                      try{
                        const full = await api.getTutor(t.id)
                        setEditing(full)
                      }catch(e){
                        alert('Failed to load tutor details: '+(e.message||e))
                      }
                    }}>Edit</button>
                    <button className="btn btn-sm btn-outline-danger" onClick={()=>onDelete(t.id)}>Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
