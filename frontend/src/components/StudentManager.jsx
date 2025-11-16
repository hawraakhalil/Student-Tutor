import React, { useEffect, useState } from 'react'
import api from '../api'
import StudentForm from './StudentForm'

export default function StudentManager(){
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [editing, setEditing] = useState(null)

  useEffect(()=>{ load() }, [])

  async function load(){ setLoading(true); try{ const res = await api.fetchStudents(); setStudents(Array.isArray(res)?res:[]) }catch(e){ alert('Load failed:'+e.message) } finally{ setLoading(false) } }

  async function remove(id){ if(!confirm('Delete this student?')) return; try{ await api.deleteStudent(id); await load() }catch(e){ alert('Delete failed:'+e.message) } }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="m-0">Students</h4>
        <div>
          <button className="btn btn-success" onClick={()=>setEditing({})}>Add Student</button>
        </div>
      </div>

      {editing ? (
        <StudentForm student={editing} onCancel={()=>setEditing(null)} onSaved={async ()=>{ setEditing(null); await load() }} />
      ) : (
        <>
          {loading ? <div className="text-muted">Loading...</div> : (
            <div className="list-group">
              {students.map(s=> {
                const prefs = s.preferred_subjects
                let prefsText = ''
                if(Array.isArray(prefs)){
                  // array of objects or strings
                  prefsText = prefs.map(p => (p && typeof p === 'object') ? (p.name || '') : String(p)).filter(Boolean).join(', ')
                } else if(typeof prefs === 'string') prefsText = prefs
                return (
                  <div key={s.id} className="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{s.name}</strong>
                      <div className="small text-muted">{prefsText} — {s.city}</div>
                    </div>
                    <div>
                      <button className="btn btn-sm btn-outline-primary me-2" onClick={()=>setEditing(s)}>Edit</button>
                      <button className="btn btn-sm btn-outline-danger" onClick={()=>remove(s.id)}>Delete</button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}
    </div>
  )
}
