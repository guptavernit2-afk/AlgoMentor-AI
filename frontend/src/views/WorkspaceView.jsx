import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import { getWorkspaceProblem, getWorkspaceProblemById, submitWorkspaceCode } from '../services/api';
import './WorkspaceView.css';

export default function WorkspaceView({ setActiveView, problemId }) {
  const [problem, setProblem] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  
  // Evaluation state
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState(null);

  useEffect(() => {
    async function loadProblem() {
      try {
        const data = problemId ? await getWorkspaceProblemById(problemId) : await getWorkspaceProblem();
        setProblem(data);
        setCode(data.starterCode[language]);
      } catch (err) {
        console.error("Failed to load problem", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadProblem();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [problemId]); // Run once on mount

  // Handle language change
  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    if (problem && problem.starterCode[newLang]) {
      setCode(problem.starterCode[newLang]);
    }
  };

  const handleEditorChange = (value) => {
    setCode(value);
  };

  const handleSubmit = async () => {
    if (!problem) return;
    
    setIsEvaluating(true);
    setEvalResult(null);
    try {
      const result = await submitWorkspaceCode(problem.id, code, language);
      setEvalResult(result);
    } catch (err) {
      console.error("Evaluation failed", err);
      setEvalResult({
        status: 'Error',
        feedback: 'Failed to connect to AI Mentor. Please try again.',
        is_optimal: false
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="workspace-root" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading Workspace...</p>
      </div>
    );
  }

  if (!problem) {
    return (
      <div className="workspace-root" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--accent-red)' }}>Failed to load problem data.</p>
        <button className="workspace-back-btn" onClick={() => setActiveView('dashboard')}>Return to Dashboard</button>
      </div>
    );
  }

  return (
    <div className="workspace-root">
      
      {/* ── TOP NAV BAR ── */}
      <header className="workspace-header">
        <div className="workspace-header-left">
          <button className="workspace-back-btn" onClick={() => setActiveView('dashboard')} title="Back to Dashboard">
            ←
          </button>
          <div className="workspace-logo">
            <span className="workspace-logo-icon">⬡</span>
            AlgoMentor <span style={{ fontWeight: 300, color: 'var(--accent-purple)' }}>Workspace</span>
          </div>
        </div>

        <div className="workspace-header-center">
          <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.2rem 1rem', borderRadius: '4px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            {problem.id}
          </div>
        </div>

        <div className="workspace-header-right">
          <button className="workspace-run-btn" onClick={handleSubmit} disabled={isEvaluating}>
            {isEvaluating ? 'Evaluating...' : (
              <>
                <span style={{ fontSize: '1rem' }}>☁️</span> Submit to AI Mentor
              </>
            )}
          </button>
        </div>
      </header>

      {/* ── SPLIT WORKSPACE BODY ── */}
      <div className="workspace-body">
        
        {/* Left Pane: Problem Description */}
        <div className="workspace-problem-pane">
          <div className="pane-header">
            <div className="pane-tab">Description</div>
            <div className="pane-tab" style={{ color: 'var(--text-muted)', border: 'none' }}>Solutions</div>
            <div className="pane-tab" style={{ color: 'var(--text-muted)', border: 'none' }}>Submissions</div>
          </div>
          
          <div className="problem-content">
            <h1 className="problem-title">{problem.title}</h1>
            
            <div className="problem-badges">
              <span className={`badge badge-${problem.difficulty.toLowerCase()}`}>
                {problem.difficulty}
              </span>
              {problem.topics.map(t => (
                <span key={t} className="badge" style={{ color: 'var(--text-secondary)' }}>{t}</span>
              ))}
            </div>

            <div className="markdown-body">
              <ReactMarkdown>{problem.description}</ReactMarkdown>
            </div>
          </div>
        </div>

        {/* Right Pane: Code Editor & Console */}
        <div className="workspace-editor-pane">
          
          <div className="editor-container">
            <div className="mac-header">
              <div className="mac-dots">
                <div className="mac-dot red"></div>
                <div className="mac-dot yellow"></div>
                <div className="mac-dot green"></div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>&lt;/&gt; Code</span>
                <select className="lang-selector" value={language} onChange={handleLanguageChange}>
                  <option value="python">Python</option>
                  <option value="cpp">C++</option>
                  <option value="javascript">JavaScript</option>
                </select>
              </div>
              <div style={{ width: '42px' }}>{/* Spacer for center alignment */}</div>
            </div>
            
            <div className="monaco-wrapper">
              <Editor
                height="100%"
                language={language}
                theme="vs-dark"
                value={code}
                onChange={handleEditorChange}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: "'Fira Code', 'Courier New', monospace",
                  scrollBeyondLastLine: false,
                  smoothScrolling: true,
                  padding: { top: 16 }
                }}
              />
            </div>
          </div>

          <div className="console-container">
            <div className="console-header">
              <span style={{ color: 'var(--accent-indigo)' }}>⚡</span> AI Mentor Feedback
            </div>
            <div className="console-body">
              {!evalResult && !isEvaluating && (
                <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center' }}>
                  Write your code and click Submit to get AI feedback.
                </div>
              )}
              
              {isEvaluating && (
                <div style={{ color: 'var(--accent-indigo)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span className="spinner">⏳</span> Analyzing complexity and logic...
                </div>
              )}

              {evalResult && (
                <div>
                  <div style={{ marginBottom: '0.5rem', fontSize: '1rem', fontWeight: 600 }} className={
                    evalResult.status === 'Accepted' ? 'status-accepted' : 
                    evalResult.status === 'Incomplete' ? 'status-incomplete' : 'status-error'
                  }>
                    [{evalResult.status}]
                  </div>
                  <div style={{ lineHeight: 1.6 }}>
                    {evalResult.feedback}
                  </div>
                  {evalResult.is_optimal && (
                    <div style={{ marginTop: '1rem', padding: '0.5rem', background: 'rgba(16, 185, 129, 0.1)', borderLeft: '3px solid var(--accent-green)', borderRadius: '0 4px 4px 0' }}>
                      🌟 Optimal Solution Detected
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
