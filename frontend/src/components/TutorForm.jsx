import React, { useEffect, useState } from 'react'
import api from '../api'

const emptyTutor = {
  name: '', email: '', phone: '', city: '', address: '', latitude: '', longitude: '', hourly_rate: '', teaching_mode: '', bio: '', subjects: ''
}

export default function TutorForm({tutor, onCancel, onSaved}){
  const [form, setForm] = useState(emptyTutor)
  const [saving, setSaving] = useState(false)

  useEffect(()=>{
    if(tutor && tutor.id){
      // editing: ensure subjects is a comma-separated string
      let subs = tutor.subjects
      if(Array.isArray(subs)) subs = subs.join(', ')
      if(!subs) subs = ''
      setForm({ ...emptyTutor, ...tutor, subjects: subs })
    } else {
      setForm({ ...emptyTutor })
    }
  }, [tutor])

  async function submit(e){
    e.preventDefault(); setSaving(true)
    const payload = { ...form, subjects: form.subjects ? form.subjects.split(',').map(s=>s.trim()).filter(Boolean) : [] }
    try{
      if(tutor && tutor.id){
        await api.updateTutor(tutor.id, payload)
      } else {
        await api.createTutor(payload)
      }
      if(onSaved) await onSaved()
    }catch(err){ alert('Save failed: '+err.message) }
    finally{ setSaving(false) }
  }

  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5>{tutor && tutor.id ? 'Edit Tutor' : 'Add Tutor'}</h5>
        <form onSubmit={submit}>
          <div className="row">
            <div className="col-md-6 mb-3"><label className="form-label">Name</label><input className="form-control" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required /></div>
            <div className="col-md-6 mb-3"><label className="form-label">Email</label><input className="form-control" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required /></div>
          </div>
          <div className="row">
            <div className="col-md-4 mb-3"><label className="form-label">Phone</label><input className="form-control" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})} /></div>
            <div className="col-md-4 mb-3"><label className="form-label">City</label><input className="form-control" value={form.city} onChange={e=>setForm({...form,city:e.target.value})} /></div>
            <div className="col-md-4 mb-3"><label className="form-label">Hourly Rate</label><input type="number" step="0.01" className="form-control" value={form.hourly_rate} onChange={e=>setForm({...form,hourly_rate:parseFloat(e.target.value||0)})} /></div>
          </div>
          <div className="mb-3"><label className="form-label">Subjects (comma separated)</label><input className="form-control" value={form.subjects} onChange={e=>setForm({...form,subjects:e.target.value})} /></div>
          <div className="mb-3"><label className="form-label">Teaching Mode</label><select className="form-select" value={form.teaching_mode||''} onChange={e=>setForm({...form,teaching_mode:e.target.value})}><option value="">Any</option><option value="online">Online</option><option value="in_person">In-person</option><option value="hybrid">Hybrid</option></select></div>
          <div className="mb-3"><label className="form-label">Bio</label><textarea className="form-control" rows={4} value={form.bio} onChange={e=>setForm({...form,bio:e.target.value})}></textarea></div>

          <div className="d-flex gap-2">
            <button className="btn btn-primary" disabled={saving} type="submit">{saving? 'Saving...' : 'Save'}</button>
            <button type="button" className="btn btn-outline-secondary" onClick={onCancel}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}
