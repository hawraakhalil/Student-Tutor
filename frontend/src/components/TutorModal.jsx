import React, { useEffect, useState } from 'react'
import api from '../api'

export default function TutorModal({tutorId, onClose}){
  const [tutor, setTutor] = useState(null)

  useEffect(()=>{
    let mounted = true
    api.getTutor(tutorId).then(d=>{ if(mounted) setTutor(d) }).catch(()=>{})
    return ()=>{ mounted=false }
  }, [tutorId])

  if(!tutor) return (
    <div className="modal-backdrop">
      <div className="modal-card">Loading...</div>
    </div>
  )

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={e=>e.stopPropagation()}>
        <div className="d-flex justify-content-between align-items-start mb-3">
          <h5>{tutor.name}</h5>
          <button className="btn-close" onClick={onClose}></button>
        </div>
        <div className="mb-2"><strong>Subjects:</strong> { (tutor.subjects||[]).map(s=>typeof s==='string'?s:s.name).join(', ') }</div>
        <div className="mb-2"><strong>Rate:</strong> ${tutor.hourly_rate} / hr</div>
        <div className="mb-2"><strong>Rating:</strong> {tutor.overall_rating} ({tutor.number_of_reviews} reviews)</div>
        <p>{tutor.bio}</p>
        <hr />
        <h6>Reviews</h6>
        <div style={{maxHeight:240, overflow:'auto'}}>
          {(tutor.reviews||[]).map((r,i)=>(
            <div key={i} className="mb-2">
              <div className="small text-muted">{new Date(r.created_at).toLocaleDateString()}</div>
              <div>Rating: {r.rating}</div>
              <div>{r.comment}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
