import React from 'react';

export default function StudyCalendarWidget() {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  
  // Generating a generic 30-day calendar layout for demonstration
  const calendarDates = [];
  let dayCounter = 1;
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 7; c++) {
      if (r === 0 && c < 2) {
        calendarDates.push({ date: 29 + c, currentMonth: false });
      } else if (dayCounter <= 31) {
        calendarDates.push({ date: dayCounter++, currentMonth: true });
      } else {
        calendarDates.push({ date: dayCounter - 31, currentMonth: false });
        dayCounter++;
      }
    }
  }

  return (
    <div className="study-calendar-widget" style={{ marginTop: '1rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '0.5rem', textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
        {days.map(d => <span key={d}>{d}</span>)}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '0.5rem', textAlign: 'center', fontSize: '0.8rem' }}>
        {calendarDates.map((item, i) => {
          // Highlight the 30th as active (from reference image)
          const isActive = item.date === 30 && item.currentMonth;
          const hasDot = item.currentMonth && (item.date % 3 === 0 || item.date % 5 === 0);
          
          return (
            <div 
              key={i} 
              style={{ 
                padding: '0.25rem', 
                color: item.currentMonth ? (isActive ? '#fff' : 'var(--text-primary)') : 'var(--text-muted)',
                backgroundColor: isActive ? 'var(--accent-indigo)' : 'transparent',
                borderRadius: '50%',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '24px',
                height: '24px',
                margin: '0 auto'
              }}
            >
              {item.date}
              {hasDot && !isActive && (
                <div style={{ position: 'absolute', bottom: '0px', width: '3px', height: '3px', borderRadius: '50%', backgroundColor: 'var(--accent-green)' }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
