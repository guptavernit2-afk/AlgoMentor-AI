import { useState } from 'react';
import SmartDailyPlanPanel from '../components/SmartDailyPlanPanel';
import { submitTopicReview, DEMO_USER_ID } from '../services/api';

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

const topics = [
  { name: "Arrays", status: "Revision Due", mastery: 74, daysAgo: 8, risk: 64, position: "node-pos-1" },
  { name: "Hashing", status: "Active", mastery: 61, daysAgo: 1, risk: 10, position: "node-pos-2" },
  { name: "Sliding Window", status: "Upcoming", mastery: 20, daysAgo: 0, risk: 0, position: "node-pos-3" },
  { name: "Binary Search", status: "Fading", mastery: 48, daysAgo: 5, risk: 35, position: "node-pos-4" },
];

export default function RevisionView() {
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [userCode, setUserCode] = useState("");
  const [reviewGenerated, setReviewGenerated] = useState(false);
  const [activeTab, setActiveTab] = useState("workspace");
  const [ratingSubmitted, setRatingSubmitted] = useState(false);

  function handleProblemSelect(problem) {
    setSelectedProblem(problem);
    setUserCode(problem.code || "// Write your solution here...");
    setReviewGenerated(false);
    setRatingSubmitted(false);
    setActiveTab("workspace");
  }

  const handleRating = async (quality) => {
    if (!selectedProblem) return;
    try {
      await submitTopicReview(DEMO_USER_ID, selectedProblem.topic, quality, todayISO());
      setRatingSubmitted(true);
    } catch (err) {
      console.error("Failed to submit rating", err);
    }
  };

  return (
    <div className="layout-view layout-view-padded">
      
      {/* ── TOP & MIDDLE: Smart Daily Plan (Summary, Focus, Tasks, Recommended) ── */}
      <section style={{ marginBottom: '2rem' }}>
        <SmartDailyPlanPanel onProblemSelect={handleProblemSelect} />
      </section>

      {/* ── BOTTOM: Practice Workspace OR Memory Graph (Tabs to save vertical space) ── */}
      <section style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-light)', background: 'var(--bg-dark)' }}>
          <button 
            onClick={() => setActiveTab("workspace")}
            style={{ flex: 1, padding: '1rem', background: activeTab === 'workspace' ? 'transparent' : 'rgba(0,0,0,0.2)', border: 'none', borderBottom: activeTab === 'workspace' ? '2px solid var(--accent-indigo)' : '2px solid transparent', color: activeTab === 'workspace' ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer', fontSize: '0.9rem' }}
          >
            Practice Workspace
          </button>
          <button 
            onClick={() => setActiveTab("memory")}
            style={{ flex: 1, padding: '1rem', background: activeTab === 'memory' ? 'transparent' : 'rgba(0,0,0,0.2)', border: 'none', borderBottom: activeTab === 'memory' ? '2px solid var(--accent-indigo)' : '2px solid transparent', color: activeTab === 'memory' ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer', fontSize: '0.9rem' }}
          >
            Topic Memory Graph
          </button>
        </div>

        <div style={{ padding: '1.5rem' }}>
          {activeTab === 'workspace' ? (
            selectedProblem ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1rem' }}>{selectedProblem.title}</h3>
                    <span style={{ fontSize: '0.75rem', background: 'var(--bg-dark)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>JavaScript</span>
                  </div>
                  <textarea
                    value={userCode}
                    onChange={(e) => { setUserCode(e.target.value); setReviewGenerated(false); }}
                    spellCheck="false"
                    style={{ flex: 1, minHeight: '220px', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', color: '#a5b4fc', fontFamily: 'monospace', padding: '1rem', fontSize: '0.85rem', resize: 'vertical' }}
                  />
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                    <button onClick={() => setReviewGenerated(true)} style={{ background: 'var(--accent-indigo)', color: 'white', border: 'none', padding: '0.6rem 1rem', borderRadius: 'var(--radius-sm)', fontWeight: 600, cursor: 'pointer' }}>▶ Run AI Review</button>
                    <button onClick={() => { setUserCode(selectedProblem.code || ""); setReviewGenerated(false); }} style={{ background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border-strong)', padding: '0.6rem 1rem', borderRadius: 'var(--radius-sm)', cursor: 'pointer' }}>Reset</button>
                  </div>
                </div>

                <div>
                  {!reviewGenerated ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-sm)', border: '1px dashed var(--border-strong)' }}>
                      <span style={{ fontSize: '2rem', marginBottom: '1rem' }}>⬡</span>
                      <p>Awaiting Code Review</p>
                    </div>
                  ) : (
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3 style={{ margin: 0, fontSize: '1.1rem', color: 'var(--accent-green)' }}>Diagnostic Complete</h3>
                        <span style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-green)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>Strong</span>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Pattern detected</span>
                          <strong style={{ fontSize: '0.85rem' }}>Hash Map Lookup</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Time complexity</span>
                          <strong style={{ fontSize: '0.85rem', color: 'var(--accent-blue)' }}>O(n)</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Space complexity</span>
                          <strong style={{ fontSize: '0.85rem', color: 'var(--accent-purple)' }}>O(n)</strong>
                        </div>
                      </div>
                      <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '1rem', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-indigo)' }}>
                        <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-indigo)', marginBottom: '0.25rem', textTransform: 'uppercase' }}>AI Note</span>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Your logic is optimized. Next, try a variation where the array contains repeated numbers.</p>
                      </div>

                      {/* SM-2 Feedback Section */}
                      <div style={{ marginTop: '1.5rem', background: 'var(--bg-base)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-md)', padding: '1.25rem', textAlign: 'center' }}>
                        {!ratingSubmitted ? (
                          <>
                            <h4 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', color: 'var(--text-primary)' }}>How well did you recall this topic?</h4>
                            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                              {[0, 1, 2, 3, 4, 5].map(q => (
                                <button
                                  key={q}
                                  onClick={() => handleRating(q)}
                                  title={`Quality: ${q}`}
                                  style={{
                                    width: '32px', height: '32px', borderRadius: '50%',
                                    background: 'var(--bg-dark)', border: '1px solid var(--border-strong)',
                                    color: 'var(--text-primary)', cursor: 'pointer', fontWeight: 600,
                                    transition: 'all 0.2s'
                                  }}
                                  onMouseOver={e => { e.currentTarget.style.borderColor = 'var(--accent-indigo)'; e.currentTarget.style.color = 'var(--accent-indigo)'; }}
                                  onMouseOut={e => { e.currentTarget.style.borderColor = 'var(--border-strong)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                                >
                                  {q}
                                </button>
                              ))}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              <span>0 = Blackout</span>
                              <span>5 = Perfect Recall</span>
                            </div>
                          </>
                        ) : (
                          <div style={{ color: 'var(--accent-green)', fontWeight: 500, fontSize: '0.95rem' }}>
                            <span style={{ marginRight: '0.5rem' }}>✔</span>
                            Memory graph updated!
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                <span style={{ fontSize: '2rem', display: 'block', marginBottom: '1rem' }}>🎯</span>
                Select a problem from the Recommended Queue to begin practice.
              </div>
            )
          ) : (
            <div className="memory-map" style={{ position: 'relative', height: '300px', background: 'var(--bg-dark)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-strong)', overflow: 'hidden' }}>
              <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
                <line x1="18%" y1="27%" x2="54%" y2="16%" stroke="var(--border-strong)" strokeWidth="2" />
                <line x1="54%" y1="16%" x2="78%" y2="42%" stroke="var(--border-strong)" strokeWidth="2" />
                <line x1="18%" y1="27%" x2="36%" y2="72%" stroke="var(--accent-red)" strokeWidth="2" />
              </svg>
              {topics.map(topic => {
                const pos = { cx: "50%", cy: "50%" };
                if(topic.position === "node-pos-1") { pos.cx = "18%"; pos.cy = "27%"; }
                if(topic.position === "node-pos-2") { pos.cx = "54%"; pos.cy = "16%"; }
                if(topic.position === "node-pos-3") { pos.cx = "78%"; pos.cy = "42%"; }
                if(topic.position === "node-pos-4") { pos.cx = "36%"; pos.cy = "72%"; }
                return (
                  <div key={topic.name} style={{ position: 'absolute', left: pos.cx, top: pos.cy, transform: 'translate(-50%, -50%)', background: 'var(--bg-card)', border: `2px solid ${topic.risk > 50 ? 'var(--accent-red)' : 'var(--border-strong)'}`, padding: '0.5rem', borderRadius: '8px', textAlign: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>{topic.name}</div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>{topic.mastery}%</div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

    </div>
  );
}
