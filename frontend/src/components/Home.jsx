import React from 'react'
import Educator from '../../../educator.svg'

export default function Home({onGetStarted}){
  return (
    <div className="home-hero">
      <section className="hero py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-md-7">
              <h1 className="display-5 fw-bold">Find the perfect tutor, faster.</h1>
              <p className="lead text-muted">Browse verified tutors, get personalized recommendations, and book lessons that fit your budget and schedule.</p>

              <div className="d-flex gap-3 mt-4">
                <button className="btn btn-lg btn-primary" onClick={()=>onGetStarted('search')}>Search Tutors</button>
                <button className="btn btn-lg btn-outline-secondary" onClick={()=>onGetStarted('students')}>Student Dashboard</button>
              </div>
            </div>
            <div className="col-md-5 text-center text-md-end mt-4 mt-md-0">
              <img src={Educator} alt="Educator" className="hero-illustration img-fluid" />
            </div>
          </div>
        </div>
      </section>

      <section className="features py-5">
        <div className="container">
          <div className="row g-4">
            <div className="col-md-4">
              <div className="card p-4 h-100">
                <h5>Smart Recommendations</h5>
                <p className="text-muted small mb-0">Get AI-enhanced suggestions tailored to your subjects, budget, and location.</p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card p-4 h-100">
                <h5>Verified Tutors</h5>
                <p className="text-muted small mb-0">Profiles with ratings and reviews help you pick the best match.</p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card p-4 h-100">
                <h5>Easy Scheduling</h5>
                <p className="text-muted small mb-0">Contact tutors and request lessons directly from the platform.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="cta py-5 bg-light">
        <div className="container text-center">
          <h4>Ready to get started?</h4>
          <p className="text-muted">Create a student profile, explore tutors, and compare recommendations.</p>
          <button className="btn btn-primary btn-lg" onClick={()=>onGetStarted('students')}>Go to Student Dashboard</button>
        </div>
      </section>
    </div>
  )
}
