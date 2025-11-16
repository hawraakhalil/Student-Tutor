const API_BASE = location.hostname === '127.0.0.1' || location.hostname === 'localhost' ? 'http://127.0.0.1:8000/api' : 'https://studenttutorrecommendationsystem-cmafddgndrc9cnf8.germanywestcentral-01.azurewebsites.net/api'; // Azure backend

async function fetchSubjects(){
  const res = await fetch(`${API_BASE}/subjects`);
  return await res.json();
}

async function fetchStudents(){
  const res = await fetch(`${API_BASE}/students`);
  return await res.json();
}

async function fetchCities(){
  const res = await fetch(`${API_BASE}/cities`);
  return await res.json();
}

async function searchTutors(params){
  const qs = new URLSearchParams(params);
  const res = await fetch(`${API_BASE}/tutors/search?`+qs.toString());
  return await res.json();
}

async function getTutor(id){
  const res = await fetch(`${API_BASE}/tutors/${id}`);
  return await res.json();
}

async function getSimilar(id){
  const res = await fetch(`${API_BASE}/tutors/${id}/similar`);
  return await res.json();
}

async function getStudentRecommendations(id, use_ai = true){
  const qs = new URLSearchParams({ use_ai: use_ai ? 'true' : 'false' });
  const res = await fetch(`${API_BASE}/students/${id}/recommendations?`+qs.toString());
  return await res.json();
}

function createTutorCard(t){
  const subjects = (() => {
    if (!t.subjects) return '';
    if (!Array.isArray(t.subjects)) return t.subjects;
    return t.subjects.map(s => typeof s === 'string' ? s : (s.name || JSON.stringify(s))).join(', ');
  })();
  const rating = t.overall_rating !== undefined ? t.overall_rating : (t.rating || 'N/A');
  const reviews = t.number_of_reviews !== undefined ? t.number_of_reviews : (t.reviews_count || 0);
  const distance = t.distance_km ? `<div class="text-muted small">${t.distance_km} km away</div>` : '';

  const explanationHtml = t.explanation ? `<p class="mt-2 mb-0 text-muted">${t.explanation}</p>` : '';

  const html = `
    <div class="card tutor-card mb-3 shadow-sm">
      <div class="card-body d-flex align-items-start">
        <div class="flex-grow-1">
          <h5 class="card-title mb-1"><a href="tutor.html?id=${t.id}">${t.name}</a></h5>
          <div class="text-muted small">${subjects}</div>
          <div class="mt-2">
            <span class="rating-badge">${rating}</span>
            <span class="ms-3">${reviews} reviews</span>
          </div>
          ${explanationHtml}
        </div>
        <div class="text-end ms-3">
          <div class="price">$${t.hourly_rate}</div>
          <div class="text-muted small">${t.city || ''}</div>
          ${distance}
        </div>
      </div>
    </div>`;
  const div = document.createElement('div');
  div.innerHTML = html;
  return div.firstElementChild;
}

function renderTutors(container, tutors){
  container.innerHTML = '';
  if(!tutors || tutors.length === 0){
    container.innerHTML = '<div class="alert alert-info">No tutors found.</div>';
    return;
  }
  tutors.forEach(t => {
    const card = createTutorCard(t);
    container.appendChild(card);
  });
}

function renderTutorDetails(container, t){
  container.innerHTML = '';
  const subjects = (() => {
    if (!t.subjects) return '';
    if (!Array.isArray(t.subjects)) return t.subjects;
    return t.subjects.map(s => typeof s === 'string' ? s : (s.name || JSON.stringify(s))).join(', ');
  })();
  const html = `
    <div class="card mb-3">
      <div class="card-body">
        <h2 class="card-title">${t.name} <span class="badge bg-secondary">${t.teaching_mode || ''}</span></h2>
        <div class="mb-2"><strong>Subjects:</strong> ${subjects}</div>
        <div class="mb-2"><strong>Rate:</strong> $${t.hourly_rate} / hr</div>
        <div class="mb-2"><strong>Rating:</strong> ${t.overall_rating} (${t.number_of_reviews} reviews)</div>
        <p>${t.bio || ''}</p>
      </div>
    </div>
    <div class="card mb-3"><div class="card-body"><h5>Reviews</h5><div id="reviewsList"></div></div></div>
  `;
  container.innerHTML = html;
  const rl = document.getElementById('reviewsList');
  if(t.reviews && t.reviews.length){
    t.reviews.forEach(r => {
      const div = document.createElement('div');
      div.className = 'border rounded p-2 mb-2';
      div.innerHTML = `<div class="small text-muted">${new Date(r.created_at).toLocaleString()}</div><div>Rating: ${r.rating}</div><div>${r.comment || ''}</div>`;
      rl.appendChild(div);
    });
  } else {
    rl.innerHTML = '<div class="text-muted">No reviews yet.</div>';
  }
}