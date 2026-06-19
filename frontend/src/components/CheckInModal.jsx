import { useState } from 'react';
import { saveDailyOverride, DEMO_USER_ID } from '../services/api';
import './CheckInModal.css';

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export default function CheckInModal({ onClose, onComplete }) {
  const [situation, setSituation] = useState('Normal day');
  const [extraMinutes, setExtraMinutes] = useState(0);
  const [energyLevel, setEnergyLevel] = useState('Normal');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await saveDailyOverride(DEMO_USER_ID, todayISO(), {
        situation,
        extra_available_minutes: parseInt(extraMinutes, 10),
        energy_level: energyLevel
      });
      onComplete(); // Triggers a re-fetch of the daily plan
      onClose();
    } catch (err) {
      console.error("Failed to save check-in", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content checkin-modal">
        <div className="modal-header">
          <h2>Daily Check-in</h2>
          <p>Let's calibrate your study plan for today.</p>
        </div>
        
        <form onSubmit={handleSubmit} className="checkin-form">
          <div className="form-group">
            <label>Situation</label>
            <select value={situation} onChange={e => setSituation(e.target.value)}>
              <option value="Normal day">Normal day</option>
              <option value="Free day">Free day</option>
              <option value="Internal exam / Test">Internal exam / Test</option>
              <option value="Assignment">Assignment</option>
              <option value="Project work">Project work</option>
              <option value="Event / Hackathon">Event / Hackathon</option>
            </select>
          </div>

          <div className="form-group">
            <label>Energy Level</label>
            <div className="radio-group">
              {['Low', 'Normal', 'High'].map(level => (
                <label key={level} className={`radio-pill ${energyLevel === level ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="energyLevel"
                    value={level}
                    checked={energyLevel === level}
                    onChange={() => setEnergyLevel(level)}
                  />
                  {level}
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Extra Time Available (minutes)</label>
            <input 
              type="number" 
              value={extraMinutes} 
              onChange={e => setExtraMinutes(e.target.value)}
              min="-240" 
              max="480"
              step="15"
            />
            <small className="help-text">Can be negative if you have less time than usual.</small>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Skip</button>
            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Generating Plan...' : 'Generate Today\'s Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
