import React from 'react'

function Stars({n}){
  const rounded = Math.round((n || 0) * 2) / 2
  const full = Math.floor(rounded)
  const half = rounded - full >= 0.5
  return (
    <span className="stars" aria-hidden>
      {Array.from({length: full}).map((_,i)=><span key={i}>★</span>)}{half? <span>☆</span>: null}
    </span>
  )
}

export default function TutorCard({t, onView}){
  const subjects = (t.subjects || []).map(s => typeof s === 'string' ? s : (s.name || '')).join(', ')
  const avatarUrl = t.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(t.name)}&background=2F6FDE&color=fff&size=128`
  return (
    <div className="tutor-card card mb-3 shadow-sm">
      <div className="card-body d-flex gap-3 align-items-start">
        <img src={avatarUrl} alt="avatar" className="avatar" />
        <div className="flex-grow-1">
          <div className="d-flex align-items-start justify-content-between">
            <div>
              <h5 className="mb-1">{t.name}</h5>
              <div className="text-muted small">{subjects}</div>
            </div>
            <div className="text-end">
              <div className="price">${t.hourly_rate}</div>
              <div className="text-muted small">{t.city}</div>
            </div>
          </div>

          <div className="mt-3 d-flex align-items-center justify-content-between">
            <div>
              <Stars n={t.overall_rating} />
              <span className="ms-2 text-muted small">{t.overall_rating || 'N/A'} • {t.number_of_reviews || 0} reviews</span>
            </div>
            <div>
              <button className="btn btn-sm btn-outline-primary me-2" onClick={()=>onView && onView(t.id)}>View</button>
            </div>
          </div>
          {t.explanation ? <p className="mt-2 mb-0 text-muted">{t.explanation}</p> : null}
        </div>
      </div>
    </div>
  )
}
