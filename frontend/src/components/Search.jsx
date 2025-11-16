import React, { useEffect, useState } from 'react'
import api from '../api'
import TutorCard from './TutorCard'
import TutorModal from './TutorModal'

export default function Search(){
  const [subjects, setSubjects] = useState([])
  const [cities, setCities] = useState([])
  const [filters, setFilters] = useState({subject:'', city:'', max_hourly_rate:'', min_rating:'', teaching_mode:'', sort_by:''})
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedTutor, setSelectedTutor] = useState(null)

  useEffect(()=>{
    api.fetchSubjects().then(setSubjects).catch(()=>{});
    api.fetchCities().then(setCities).catch(()=>{})
  }, [])

  const onSearch = async (e) =>{
    if(e) e.preventDefault()
    setLoading(true)
    try{
      const params = {}
      Object.keys(filters).forEach(k => { if(filters[k]) params[k]=filters[k] })
      const res = await api.searchTutors(params)
      setResults(res)
    }finally{ setLoading(false) }
  }

  useEffect(()=>{ onSearch() }, [])

  return (
    <div className="row">
      <div className="col-lg-3 mb-4">
        <div className="card sticky-card">
          <div className="card-body">
            <h6>Filters</h6>
            <form onSubmit={onSearch}>
              <div className="mb-2">
                <label className="form-label small">Subject</label>
                <select className="form-select" value={filters.subject} onChange={e=>setFilters({...filters, subject:e.target.value})}>
                  <option value="">Any</option>
                  {subjects.map(s=> <option key={s.id} value={s.name}>{s.name}</option>)}
                </select>
              </div>
              <div className="mb-2">
                <label className="form-label small">City</label>
                <select className="form-select" value={filters.city} onChange={e=>setFilters({...filters, city:e.target.value})}>
                  <option value="">Any</option>
                  {cities.map(c=> <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="mb-2">
                <label className="form-label small">Max $/hr</label>
                <input type="number" className="form-control" value={filters.max_hourly_rate} onChange={e=>setFilters({...filters, max_hourly_rate:e.target.value})} />
              </div>
              <div className="mb-2">
                <label className="form-label small">Min Rating</label>
                <input type="number" className="form-control" step="0.1" min="0" max="5" value={filters.min_rating} onChange={e=>setFilters({...filters, min_rating:e.target.value})} />
              </div>
              <div className="d-grid mt-3">
                <button className="btn btn-primary" type="submit">Apply</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div className="col-lg-9">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5 className="m-0">{loading? 'Searching...' : `${results.length} tutors`}</h5>
        </div>

        <div>
          {results.length === 0 && !loading ? <div className="text-muted">No tutors found. Try adjusting filters.</div> : results.map(t => <TutorCard key={t.id} t={t} onView={(id)=>setSelectedTutor(id)} />)}
        </div>
      </div>

      {selectedTutor ? <TutorModal tutorId={selectedTutor} onClose={()=>setSelectedTutor(null)} /> : null}
    </div>
  )
}
