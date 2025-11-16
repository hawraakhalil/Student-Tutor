const API_BASE = 'https://studenttutorrecommendationsystem-cmafddgndrc9cnf8.germanywestcentral-01.azurewebsites.net/api';

async function fetchJson(url, options = {}){
  const res = await fetch(url, options)
  let text = null
  try{ text = await res.text() }catch(e){ /* ignore */ }
  const isJson = text && (text.trim().startsWith('{') || text.trim().startsWith('['))
  const body = isJson ? JSON.parse(text) : text
  if(!res.ok){
    let msg = `Request failed: ${res.status}`
    try{
      if(body){
        if(body.detail) msg += ` - ${JSON.stringify(body.detail)}`
        else msg += ` - ${JSON.stringify(body)}`
      }
    }catch(e){ /* ignore */ }
    const err = new Error(msg)
    err.status = res.status
    err.body = body
    throw err
  }
  return body
}

export const fetchSubjects = () => fetchJson(`${API_BASE}/subjects`)
export const fetchStudents = async () => {
  const body = await fetchJson(`${API_BASE}/students`)
  // normalize different backend shapes: array or { value: [...]} etc.
  if (Array.isArray(body)) return body
  if (body && Array.isArray(body.value)) return body.value
  if (body && Array.isArray(body.students)) return body.students
  if (body && Array.isArray(body.data)) return body.data
  // fallback: try to find first array in response
  for (const k of Object.keys(body||{})){
    if (Array.isArray(body[k])) return body[k]
  }
  return []
}
export const fetchCities = () => fetchJson(`${API_BASE}/cities`)
export const searchTutors = (params) => {
  const qs = new URLSearchParams(params)
  return fetchJson(`${API_BASE}/tutors/search?`+qs.toString())
}
export const getStudentRecommendations = (id, use_ai = true) => {
  const qs = new URLSearchParams({ use_ai: use_ai ? 'true' : 'false' })
  return fetchJson(`${API_BASE}/students/${id}/recommendations?`+qs.toString())
}
export const getTutor = (id) => fetchJson(`${API_BASE}/tutors/${id}`)
export const getSimilar = (id) => fetchJson(`${API_BASE}/tutors/${id}/similar`)
export const createTutor = (payload) => fetchJson(`${API_BASE}/tutors`, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' } })
export const updateTutor = (id, payload) => fetchJson(`${API_BASE}/tutors/${id}`, { method: 'PUT', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' } })
export const deleteTutor = (id) => fetchJson(`${API_BASE}/tutors/${id}`, { method: 'DELETE' })

export const createStudent = (payload) => fetchJson(`${API_BASE}/students`, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' } })
export const updateStudent = (id, payload) => fetchJson(`${API_BASE}/students/${id}`, { method: 'PUT', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' } })
export const deleteStudent = (id) => fetchJson(`${API_BASE}/students/${id}`, { method: 'DELETE' })

export default {
  fetchSubjects, fetchStudents, fetchCities, searchTutors, getStudentRecommendations, getTutor, getSimilar,
  createTutor, updateTutor, deleteTutor, createStudent, updateStudent, deleteStudent
}
