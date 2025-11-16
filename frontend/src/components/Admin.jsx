import React, { useState } from 'react'
import TutorManager from './TutorManager'
import StudentManager from './StudentManager'

export default function Admin(){
  const [section, setSection] = useState('tutors')
  return (
    <div>
      <div className="d-flex gap-2 mb-3">
        <button className={`btn ${section==='tutors'?'btn-primary':'btn-outline-primary'}`} onClick={()=>setSection('tutors')}>Manage Tutors</button>
        <button className={`btn ${section==='students'?'btn-primary':'btn-outline-primary'}`} onClick={()=>setSection('students')}>Manage Students</button>
      </div>
      <div>
        {section === 'tutors' ? <TutorManager /> : <StudentManager />}
      </div>
    </div>
  )
}
