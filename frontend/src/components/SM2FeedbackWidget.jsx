import { useState, useEffect, useCallback } from 'react';
import { getRevisionQueue, submitTopicReview, DEMO_USER_ID } from '../services/api';

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

const QUALITY_LABELS = {
  0: "Blackout",
  1: "Wrong / Familiar",
  2: "Wrong / Easy After",
  3: "Correct / Hard",
  4: "Correct / Hesitant",
  5: "Perfect Recall"
};

export default function SM2FeedbackWidget() {
  const [queue, setQueue] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState(null);

  const fetchQueue = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getRevisionQueue(DEMO_USER_ID, todayISO());
      setQueue(data);
    } catch (err) {
      console.warn("Failed to fetch revision queue", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchQueue();
  }, [fetchQueue]);

  const handleReview = async (topic, quality) => {
    setIsSubmitting(true);
    setFeedbackMsg(null);
    try {
      await submitTopicReview(DEMO_USER_ID, topic, quality, todayISO());
      setFeedbackMsg(`Review saved for ${topic}!`);
      setTimeout(() => {
        setFeedbackMsg(null);
        fetchQueue();
      }, 2000);
    } catch (err) {
      console.error("Failed to submit review", err);
      setFeedbackMsg("Failed to save. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="widget-card">
        <div className="widget-header">
          <h3 className="widget-title">Active Revision</h3>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Loading queue...</p>
      </div>
    );
  }

  const dueTopic = queue?.due_topics?.[0];

  return (
    <div className="widget-card">
      <div className="widget-header">
        <h3 className="widget-title">Active Revision (SM-2)</h3>
        {queue?.due_topics?.length > 1 && (
          <span style={{ fontSize: '0.75rem', background: 'var(--accent-red, #ef4444)', padding: '2px 6px', borderRadius: '4px', color: 'white', fontWeight: 'bold' }}>
            {queue.due_topics.length} Due
          </span>
        )}
      </div>

      {!dueTopic ? (
        <div style={{ padding: '1rem 0', textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🎉</div>
          <p style={{ color: 'var(--text-primary)', fontSize: '0.9rem', fontWeight: 600, margin: '0 0 0.25rem 0' }}>All Caught Up!</p>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', margin: 0 }}>No topics due for revision today.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--accent-indigo, #6366f1)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.05em' }}>Due Now</span>
            <h4 style={{ margin: '0.25rem 0 0 0', color: 'var(--text-primary)', fontSize: '1.1rem' }}>{dueTopic.topic}</h4>
            <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
              Interval: {dueTopic.interval_days} days • Ease: {dueTopic.easiness_factor.toFixed(2)}
            </p>
          </div>

          <div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0 0 0.75rem 0', textAlign: 'center' }}>Rate your recall quality:</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
              {[0, 1, 2, 3, 4, 5].map((quality) => (
                <button
                  key={quality}
                  onClick={() => handleReview(dueTopic.topic, quality)}
                  disabled={isSubmitting}
                  title={QUALITY_LABELS[quality]}
                  style={{
                    background: 'var(--bg-dark, rgba(15, 23, 42, 0.5))',
                    border: '1px solid var(--border-strong, rgba(148, 163, 184, 0.2))',
                    color: 'var(--text-primary)',
                    padding: '0.5rem',
                    borderRadius: '4px',
                    cursor: isSubmitting ? 'not-allowed' : 'pointer',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    transition: 'all 0.2s',
                  }}
                  onMouseOver={(e) => {
                    if (!isSubmitting) {
                      e.currentTarget.style.background = 'var(--accent-indigo, #6366f1)';
                      e.currentTarget.style.color = '#fff';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!isSubmitting) {
                      e.currentTarget.style.background = 'var(--bg-dark, rgba(15, 23, 42, 0.5))';
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }
                  }}
                >
                  {quality}
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', padding: '0 0.5rem' }}>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>0 = Blackout</span>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>5 = Perfect</span>
            </div>
          </div>

          {feedbackMsg && (
            <div style={{ fontSize: '0.8rem', color: feedbackMsg.includes('Failed') ? 'var(--accent-red, #ef4444)' : 'var(--accent-green, #4ade80)', textAlign: 'center', background: feedbackMsg.includes('Failed') ? 'rgba(239, 68, 68, 0.1)' : 'rgba(74, 222, 128, 0.1)', padding: '0.5rem', borderRadius: '4px' }}>
              {feedbackMsg}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
