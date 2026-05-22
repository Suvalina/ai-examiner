import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiCheckCircle, FiZap, FiBarChart2 } from 'react-icons/fi';
import './Home.css';

const Home = () => {
  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            AI-Powered Answer
            <span className="gradient-text"> Evaluation</span>
          </h1>
          <p className="hero-subtitle">
            Automatically evaluate student answers using advanced AI technology. 
            Save time, improve consistency, and get detailed feedback.
          </p>
          <div className="hero-buttons">
            <Link to="/evaluate" className="btn btn-primary btn-lg">
              Start Evaluating <FiArrowRight />
            </Link>
            <Link to="/dashboard" className="btn btn-secondary btn-lg">
              View Dashboard
            </Link>
          </div>
        </div>
        <div className="hero-animation">
          <div className="floating-card card-1">📊</div>
          <div className="floating-card card-2">✨</div>
          <div className="floating-card card-3">🎯</div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2 className="section-title">Why AI Examiner?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <FiZap size={32} />
            </div>
            <h3>Lightning Fast</h3>
            <p>Evaluate hundreds of answer sheets in seconds, not hours</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FiCheckCircle size={32} />
            </div>
            <h3>Consistent Grading</h3>
            <p>Ensure fair and consistent evaluation criteria for all students</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <FiBarChart2 size={32} />
            </div>
            <h3>Detailed Analytics</h3>
            <p>Get comprehensive insights and performance analysis</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              🤖
            </div>
            <h3>AI-Powered</h3>
            <p>Leverages state-of-the-art machine learning technology</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              📝
            </div>
            <h3>Handwriting Recognition</h3>
            <p>Advanced OCR technology to extract handwritten text accurately</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              🔐
            </div>
            <h3>Secure & Private</h3>
            <p>Your data is safely stored and protected with encryption</p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <h2 className="section-title">How It Works</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Upload Model Answer</h3>
            <p>Upload the correct answer PDF or text</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">2</div>
            <h3>Submit Student Answer</h3>
            <p>Upload the student's handwritten or typed answer</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">3</div>
            <h3>AI Evaluation</h3>
            <p>Our AI analyzes and scores the answer</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">4</div>
            <h3>Get Results</h3>
            <p>Receive detailed feedback and grades</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="cta-content">
          <h2>Ready to Transform Your Grading Process?</h2>
          <p>Join educators worldwide who are saving time and improving student outcomes</p>
          <Link to="/evaluate" className="btn btn-primary btn-lg btn-cta">
            Get Started Now
          </Link>
          <p className="cta-note">Copyright &copy; 2026 AI Examiner. All rights reserved.</p>
        </div>
      </section>
    </div>
  );
};

export default Home;
