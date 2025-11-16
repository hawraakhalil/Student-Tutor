import React, { useEffect, useState } from 'react'
import api from '../api'

const emptyStudent = { name: '', email: '', city: '', address: '', preferred_subjects: '', max_hourly_rate: '' }

export default function StudentForm({student, onCancel, onSaved}){
  const [form, setForm] = useState(emptyStudent)
  const [saving, setSaving] = useState(false)

  useEffect(()=>{
    if(student && student.id){
      let prefs = student.preferred_subjects
      if(Array.isArray(prefs)) prefs = prefs.join(', ')
      if(!prefs) prefs = ''
      setForm({ ...emptyStudent, ...student, preferred_subjects: prefs })
    } else setForm({...emptyStudent})
  }, [student])

  async function submit(e){
    e.preventDefault(); setSaving(true)
    const payload = { ...form }
    // backend expects preferred_subjects as a string (or null)
    payload.preferred_subjects = form.preferred_subjects ? form.preferred_subjects : null
    payload.max_hourly_rate = form.max_hourly_rate ? parseFloat(form.max_hourly_rate) : null
    try{
      if(student && student.id) await api.updateStudent(student.id, payload)
      else await api.createStudent(payload)
      if(onSaved) await onSaved()
    }catch(e){ alert('Save failed: '+e.message) }
    finally{ setSaving(false) }
  }

  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5>{student && student.id ? 'Edit Student' : 'Add Student'}</h5>
        <form onSubmit={submit}>
          <div className="row">
            <div className="col-md-6 mb-3"><label className="form-label">Name</label><input className="form-control" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required /></div>
            <div className="col-md-6 mb-3"><label className="form-label">Email</label><input className="form-control" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required /></div>
          </div>
          <div className="row">
            <div className="col-md-6 mb-3"><label className="form-label">City</label><input className="form-control" value={form.city} onChange={e=>setForm({...form,city:e.target.value})} /></div>
            <div className="col-md-6 mb-3"><label className="form-label">Max Hourly Rate</label><input type="number" step="0.01" className="form-control" value={form.max_hourly_rate} onChange={e=>setForm({...form,max_hourly_rate:e.target.value})} /></div>
          </div>
          <div className="mb-3"><label className="form-label">Preferred Subjects (comma separated)</label><input className="form-control" value={form.preferred_subjects} onChange={e=>setForm({...form,preferred_subjects:e.target.value})} /></div>

          <div className="d-flex gap-2">
            <button className="btn btn-primary" disabled={saving} type="submit">{saving? 'Saving...' : 'Save'}</button>
            <button type="button" className="btn btn-outline-secondary" onClick={onCancel}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}
