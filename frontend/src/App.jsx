import { useMemo, useState, useEffect } from "react";
import { checkBackendHealth } from "./services/api";
import "./App.css";

const topics = [
  {
    name: "Arrays",
    status: "Revision Due",
    mastery: 74,
    daysAgo: 8,
    risk: 64,
    position: "node-pos-1",
  },
  {
    name: "Hashing",
    status: "Active",
    mastery: 61,
    daysAgo: 1,
    risk: 10,
    position: "node-pos-2",
  },
  {
    name: "Sliding Window",
    status: "Upcoming",
    mastery: 20,
    daysAgo: 0,
    risk: 0,
    position: "node-pos-3",
  },
  {
    name: "Binary Search",
    status: "Fading",
    mastery: 48,
    daysAgo: 5,
    risk: 35,
    position: "node-pos-4",
  },
];

const recommendedProblems = [
  {
    id: 1,
    title: "Two Sum",
    difficulty: "Easy",
    tags: ["Array", "Hashing"],
    reason:
      "Best mixed revision problem because it refreshes Array traversal while strengthening Hash Map lookup.",
    link: "https://leetcode.com/problems/two-sum/",
    statement:
      "Given an array of integers and a target value, return the indices of two numbers such that they add up to the target.",
    sample: "nums = [2, 7, 11, 15], target = 9 → [0, 1]",
    code: `function twoSum(nums, target) {
  const seen = new Map();

  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];

    if (seen.has(need)) {
      return [seen.get(need), i];
    }

    seen.set(nums[i], i);
  }
}`,
    review: {
      clarity: "Good",
      pattern: "Hash Map Lookup",
      time: "O(n)",
      space: "O(n)",
      edge: "Duplicate values",
      note:
        "Your logic is optimized. Next, solve one variation where the array contains repeated numbers to check whether your hashing concept is stable.",
    },
  },
  {
    id: 2,
    title: "Contains Duplicate",
    difficulty: "Easy",
    tags: ["Array", "Set"],
    reason:
      "Good quick recall problem for Arrays and introduces HashSet based duplicate detection.",
    link: "https://leetcode.com/problems/contains-duplicate/",
    statement:
      "Given an integer array, return true if any value appears at least twice, and return false if every element is distinct.",
    sample: "nums = [1, 2, 3, 1] → true",
    code: `function containsDuplicate(nums) {
  const seen = new Set();

  for (const num of nums) {
    if (seen.has(num)) {
      return true;
    }

    seen.add(num);
  }

  return false;
}`,
    review: {
      clarity: "Strong",
      pattern: "HashSet Tracking",
      time: "O(n)",
      space: "O(n)",
      edge: "Empty array",
      note:
        "This is a strong recall problem. It checks whether you remember array traversal and can apply set-based duplicate detection cleanly.",
    },
  },
  {
    id: 3,
    title: "Subarray Sum Equals K",
    difficulty: "Medium",
    tags: ["Prefix Sum", "Hashing"],
    reason:
      "Recommended because Prefix Sum is marked weak and this problem connects it with Hashing.",
    link: "https://leetcode.com/problems/subarray-sum-equals-k/",
    statement:
      "Given an array of integers and an integer k, return the total number of continuous subarrays whose sum equals k.",
    sample: "nums = [1, 1, 1], k = 2 → 2",
    code: `function subarraySum(nums, k) {
  const prefixCount = new Map();
  prefixCount.set(0, 1);

  let sum = 0;
  let count = 0;

  for (const num of nums) {
    sum += num;

    if (prefixCount.has(sum - k)) {
      count += prefixCount.get(sum - k);
    }

    prefixCount.set(sum, (prefixCount.get(sum) || 0) + 1);
  }

  return count;
}`,
    review: {
      clarity: "Needs Revision",
      pattern: "Prefix Sum + Hash Map",
      time: "O(n)",
      space: "O(n)",
      edge: "Negative numbers",
      note:
        "This problem is important because normal sliding window may fail with negative numbers. Prefix sum with hash map is the correct pattern to revise.",
    },
  },
];

function getStatusClass(status) {
  if (status === "Active") return "node-active";
  if (status === "Revision Due") return "node-danger";
  if (status === "Fading") return "node-warning";
  return "node-muted";
}

function buildDailyPlan(workload, situation) {
  if (situation === "Internal exam / Test") {
    return [
      "10 min quick Arrays recall only.",
      "Skip heavy problem solving today.",
      "Do one AI-reviewed code reading session after exam prep.",
    ];
  }

  if (situation === "Free day" || workload === "Low") {
    return [
      "20 min Arrays revision problem.",
      "40 min Hashing practice with frequency-map problems.",
      "30 min mixed Array + Hashing challenge.",
      "10 min AI code review and revision scheduling.",
    ];
  }

  if (workload === "High" || situation === "Assignment") {
    return [
      "15 min Arrays recall problem only.",
      "10 min Hashing concept flash revision.",
      "Save medium-level practice for tomorrow.",
    ];
  }

  return [
    "20 min Arrays revision problem.",
    "30 min Hashing practice problem.",
    "10 min AI code review and next revision scheduling.",
  ];
}

function calculateMatchScore(problem, workload, situation, weakConcept, goal) {
  let score = 62;

  if (problem.tags.includes("Hashing")) score += 12;
  if (problem.tags.includes("Array")) score += 10;
  if (problem.tags.includes(weakConcept)) score += 16;

  if (goal === "Placement Prep") {
    if (problem.tags.includes("Hashing")) score += 6;
    if (problem.difficulty === "Medium") score += 4;
  }

  if (goal === "Beginner DSA") {
    if (problem.difficulty === "Easy") score += 12;
    if (problem.difficulty === "Medium") score -= 10;
  }

  if (goal === "Competitive Programming") {
    if (problem.difficulty === "Medium") score += 12;
    if (problem.tags.includes("Prefix Sum")) score += 8;
  }

  if (goal === "Internship Prep") {
    if (problem.difficulty === "Easy") score += 5;
    if (problem.difficulty === "Medium") score += 5;
  }

  if (workload === "High" || situation === "Internal exam / Test") {
    if (problem.difficulty === "Easy") score += 8;
    if (problem.difficulty === "Medium") score -= 18;
  }

  if (workload === "Low" || situation === "Free day") {
    if (problem.difficulty === "Medium") score += 10;
  }

  if (situation === "Assignment" || situation === "Project work") {
    if (problem.difficulty === "Easy") score += 6;
    if (problem.difficulty === "Medium") score -= 8;
  }

  return Math.max(45, Math.min(score, 98));
}

// SVG neural connections between topic node positions (percentage-based)
const NODE_CENTERS = {
  "node-pos-1": { cx: "18%", cy: "27%" },
  "node-pos-2": { cx: "54%", cy: "16%" },
  "node-pos-3": { cx: "78%", cy: "42%" },
  "node-pos-4": { cx: "36%", cy: "72%" },
};

const CONNECTIONS = [
  ["node-pos-1", "node-pos-2"],
  ["node-pos-2", "node-pos-3"],
  ["node-pos-1", "node-pos-4"],
  ["node-pos-4", "node-pos-2"],
];

function App() {
  const [selectedProblem, setSelectedProblem] = useState(recommendedProblems[0]);
  const [userCode, setUserCode] = useState(recommendedProblems[0].code);
  const [reviewGenerated, setReviewGenerated] = useState(false);
  const [backendStatus, setBackendStatus] = useState("PROTOTYPE · CHECKING API");

  useEffect(() => {
    checkBackendHealth().then((isHealthy) => {
      setBackendStatus(isHealthy ? "PROTOTYPE · API CONNECTED" : "PROTOTYPE · API OFFLINE");
    });
  }, []);

  const [collegeSchedule, setCollegeSchedule] = useState("9 AM - 4 PM");
  const [availableTime, setAvailableTime] = useState("1 hour");
  const [workload, setWorkload] = useState("Medium");
  const [situation, setSituation] = useState("Normal day");
  const [weakConcept, setWeakConcept] = useState("Prefix Sum");
  const [goal, setGoal] = useState("Placement Prep");

  // Reminder System state
  const [reminderStatus, setReminderStatus] = useState("Not enabled");

  const todayPlan = useMemo(
    () => buildDailyPlan(workload, situation),
    [workload, situation]
  );

  const scoredProblems = useMemo(() => {
    return recommendedProblems
      .map((problem) => ({
        ...problem,
        matchScore: calculateMatchScore(
          problem,
          workload,
          situation,
          weakConcept,
          goal
        ),
      }))
      .sort((a, b) => b.matchScore - a.matchScore);
  }, [workload, situation, weakConcept, goal]);

  function handlePracticeHere(problem) {
    setSelectedProblem(problem);
    setUserCode(problem.code);
    setReviewGenerated(false);
  }

  function handleReviewCode() {
    setReviewGenerated(true);
  }

  function handleEnableReminders() {
    if (!('Notification' in window)) {
      setReminderStatus("Not supported");
      return;
    }
    if (Notification.permission === "granted") {
      new Notification("Arrays revision due", {
        body: "Your memory decay crossed 64%. Solve one Array + Hashing problem today.",
        icon: "/favicon.svg",
      });
      setReminderStatus("Enabled");
      return;
    }
    if (Notification.permission === "denied") {
      setReminderStatus("Blocked");
      return;
    }
    // default — request permission
    Notification.requestPermission().then((permission) => {
      if (permission === "granted") {
        new Notification("Arrays revision due", {
          body: "Your memory decay crossed 64%. Solve one Array + Hashing problem today.",
          icon: "/favicon.svg",
        });
        setReminderStatus("Enabled");
      } else {
        setReminderStatus("Blocked");
      }
    });
  }

  return (
    <div className="app-root">
      {/* ── Top Navigation ── */}
      <nav className="top-nav">
        <div className="nav-logo">
          <span className="nav-logo-icon">⬡</span>
          <span className="nav-logo-text">AlgoMentor<span className="nav-logo-accent"> AI</span></span>
          <span className="prototype-badge">{backendStatus}</span>
        </div>
        <div className="nav-links">
          <a href="#dashboard" className="nav-link nav-link-active">Dashboard</a>
          <a href="#problems" className="nav-link">Problems</a>
          <a href="#workspace" className="nav-link">Workspace</a>
        </div>
        <div className="nav-status">
          <span className="nav-status-dot dot-danger" />
          <span className="nav-status-label">Memory Risk Detected</span>
        </div>
      </nav>

      <main className="app-shell" id="dashboard">
        {/* ── Hero Panel ── */}
        <section className="hero-panel">
          <div className="hero-content">
            <p className="eyebrow">AI + Spaced Revision for DSA</p>
            <h1>AlgoMentor<span className="hero-accent"> AI</span></h1>
            <p className="tagline">
              Remembers what you forget — so you don't have to.
            </p>
            <p className="subtitle">
              A neural recall cockpit that tracks your DSA memory decay, adapts
              your daily schedule, and recommends exactly what to revise before
              concepts fade away.
            </p>
          </div>

          <div className="hero-right">
            <div className="hero-status-cluster">
              <div className="status-chip chip-danger">
                <span className="chip-dot" />
                Memory Risk Detected
              </div>
              <div className="status-chip chip-success">
                <span className="chip-dot chip-dot-green" />
                AI Plan Ready
              </div>
            </div>
            <div className="hero-badge">
              <span>Today's Priority</span>
              <strong>Arrays revision is due</strong>
              <p className="hero-badge-sub">Last practiced 8 days ago · 64% decay risk</p>
            </div>
          </div>
        </section>

        {/* ── Smart Schedule Setup ── */}
        <section className="schedule-panel" id="schedule">
          <div className="section-head">
            <div>
              <p className="eyebrow">Smart Schedule Setup</p>
              <h2>Personalize today's DSA load</h2>
              <p className="section-helper">
                One-time schedule setup + daily check-in · Recommendations update live
              </p>
            </div>
            <span className="live-pill">
              <span className="live-dot" />
              Daily Check-in
            </span>
          </div>

          <div className="schedule-grid">
            <div className="setup-card">
              <label>
                <span className="setup-icon">🕐</span>
                College Schedule
              </label>
              <p className="setup-helper">Your daily class hours</p>
              <input
                value={collegeSchedule}
                onChange={(event) => setCollegeSchedule(event.target.value)}
                placeholder="e.g. 9 AM – 4 PM"
              />
            </div>

            <div className="setup-card">
              <label>
                <span className="setup-icon">⏱</span>
                Available DSA Time
              </label>
              <p className="setup-helper">Free time for practice today</p>
              <select
                value={availableTime}
                onChange={(event) => setAvailableTime(event.target.value)}
              >
                <option>30 minutes</option>
                <option>1 hour</option>
                <option>1.5 hours</option>
                <option>2+ hours</option>
              </select>
            </div>

            <div className="setup-card">
              <label>
                <span className="setup-icon">📊</span>
                Today's Workload
              </label>
              <p className="setup-helper">Academic load affects difficulty</p>
              <select
                value={workload}
                onChange={(event) => setWorkload(event.target.value)}
              >
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
              </select>
            </div>

            <div className="setup-card">
              <label>
                <span className="setup-icon">📌</span>
                Special Situation
              </label>
              <p className="setup-helper">Adjusts plan for today's context</p>
              <select
                value={situation}
                onChange={(event) => setSituation(event.target.value)}
              >
                <option>Normal day</option>
                <option>Assignment</option>
                <option>Internal exam / Test</option>
                <option>Project work</option>
                <option>Event / Hackathon</option>
                <option>Free day</option>
              </select>
            </div>

            <div className="setup-card">
              <label>
                <span className="setup-icon">🎯</span>
                Weak Concept
              </label>
              <p className="setup-helper">Boosts match score for this topic</p>
              <select
                value={weakConcept}
                onChange={(event) => setWeakConcept(event.target.value)}
              >
                <option>Prefix Sum</option>
                <option>Recursion</option>
                <option>Binary Search</option>
                <option>Sliding Window</option>
                <option>Dynamic Programming</option>
                <option>Graphs</option>
              </select>
            </div>

            <div className="setup-card">
              <label>
                <span className="setup-icon">🏆</span>
                Learning Goal
              </label>
              <p className="setup-helper">Calibrates difficulty preference</p>
              <select value={goal} onChange={(event) => setGoal(event.target.value)}>
                <option>Beginner DSA</option>
                <option>College Practice</option>
                <option>Internship Prep</option>
                <option>Placement Prep</option>
                <option>Competitive Programming</option>
              </select>
            </div>
          </div>

          <div className="profile-summary">
            <div>
              <span>Current Topic</span>
              <strong>Hashing</strong>
            </div>
            <div>
              <span>Completed Topic</span>
              <strong>Arrays</strong>
            </div>
            <div>
              <span>Weak Concept</span>
              <strong>{weakConcept}</strong>
            </div>
            <div>
              <span>Goal</span>
              <strong>{goal}</strong>
            </div>
          </div>
        </section>

        {/* ── Stats Grid ── */}
        <section className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Current Topic</span>
            <strong>Hashing</strong>
            <p>Learning for 5 days</p>
          </div>

          <div className="stat-card danger">
            <span className="stat-label">Highest Forgetting Risk</span>
            <strong>Arrays · 64%</strong>
            <p>Last practiced 8 days ago</p>
          </div>

          <div className="stat-card">
            <span className="stat-label">Consistency Score</span>
            <strong>72%</strong>
            <p>4 active days this week</p>
          </div>

          <div className="stat-card">
            <span className="stat-label">Revision Queue</span>
            <strong>3 Topics</strong>
            <p>Arrays, Binary Search, Prefix Sum</p>
          </div>
        </section>

        {/* ── Memory Map + Mentor ── */}
        <section className="main-grid">
          <div className="memory-card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Memory Map</p>
                <h2>DSA Topic Recall Network</h2>
              </div>
              <span className="live-pill">
                <span className="live-dot" />
                Live Risk Scan
              </span>
            </div>

            <div className="memory-map">
              {/* SVG neural connection lines */}
              <svg className="memory-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="connGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="rgba(103,232,249,0)" />
                    <stop offset="50%" stopColor="rgba(103,232,249,0.55)" />
                    <stop offset="100%" stopColor="rgba(168,85,247,0)" />
                  </linearGradient>
                  <linearGradient id="connGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="rgba(103,232,249,0)" />
                    <stop offset="50%" stopColor="rgba(103,232,249,0.4)" />
                    <stop offset="100%" stopColor="rgba(168,85,247,0)" />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="0.8" result="coloredBlur" />
                    <feMerge>
                      <feMergeNode in="coloredBlur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                {/* Arrays → Hashing */}
                <line x1="18" y1="27" x2="54" y2="16" stroke="url(#connGrad1)" strokeWidth="0.4" filter="url(#glow)" />
                {/* Hashing → Sliding Window */}
                <line x1="54" y1="16" x2="78" y2="42" stroke="url(#connGrad1)" strokeWidth="0.4" filter="url(#glow)" />
                {/* Arrays → Binary Search */}
                <line x1="18" y1="27" x2="36" y2="72" stroke="url(#connGrad2)" strokeWidth="0.35" filter="url(#glow)" />
                {/* Binary Search → Hashing */}
                <line x1="36" y1="72" x2="54" y2="16" stroke="url(#connGrad2)" strokeWidth="0.35" filter="url(#glow)" />
                {/* Sliding Window → Binary Search */}
                <line x1="78" y1="42" x2="36" y2="72" stroke="url(#connGrad1)" strokeWidth="0.3" filter="url(#glow)" strokeDasharray="1.5 1.5" />
              </svg>

              {topics.map((topic) => (
                <div
                  key={topic.name}
                  className={`topic-node ${topic.position} ${getStatusClass(topic.status)}`}
                >
                  <div className="node-header">
                    <span className="node-name">{topic.name}</span>
                    <span className={`node-badge badge-${getStatusClass(topic.status)}`}>
                      {topic.status}
                    </span>
                  </div>
                  <div className="node-meta">
                    {topic.daysAgo > 0 && (
                      <span className="node-days">{topic.daysAgo}d ago</span>
                    )}
                    <span className="node-mastery">{topic.mastery}%</span>
                  </div>
                  <div className="mini-bar">
                    <div style={{ width: `${topic.mastery}%` }} />
                  </div>
                  {topic.risk > 0 && (
                    <div className="node-risk">
                      <span className="risk-label">Risk</span>
                      <span className="risk-val">{topic.risk}%</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <aside className="mentor-panel">
            <p className="eyebrow">AI Mentor</p>
            <h2>Why revise Arrays today?</h2>

            <p>
              Your college schedule is {collegeSchedule}, and today is marked as a{" "}
              {workload.toLowerCase()} workload day. Since Arrays was last
              practiced 8 days ago, the plan is adjusted to revise it without
              overloading you.
            </p>

            <div className="decay-meter">
              <div className="decay-top">
                <span>Memory Decay</span>
                <strong>64%</strong>
              </div>

              <div className="decay-track">
                <div className="decay-fill" />
              </div>

              <p>
                Arrays has entered the revision zone. A quick recall task today
                can prevent concept fading.
              </p>
              <p className="sm2-note">
                Powered by SM-2 style spaced repetition logic.
              </p>
            </div>

            <div className="mentor-insight">
              <span>Recommendation</span>
              <strong>
                {workload === "High"
                  ? "Do light revision only today"
                  : "Solve 1 Array recall + 1 Array-Hashing mixed problem"}
              </strong>
            </div>

            <div className="mentor-actions">
              <button>Analyze Pattern</button>
              <button onClick={handleReviewCode}>Review Code</button>
              <button>Schedule Revision</button>
              <button>Next Problem</button>
            </div>

            <button className="primary-btn">Generate Today's Practice</button>
          </aside>
        </section>

        {/* ── Plan + Queue ── */}
        <section className="bottom-grid">
          <div className="plan-card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Smart Plan</p>
                <h2>Today's DSA Tasks</h2>
              </div>
            </div>

            <div className="task-list">
              {todayPlan.map((task, index) => (
                <div className="task-item" key={task}>
                  <span className="task-num">0{index + 1}</span>
                  <p>{task}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="queue-card">
            <p className="eyebrow">Revision Queue</p>
            <h2>Concepts close to fading</h2>

            <div className="queue-item">
              <span>Arrays</span>
              <strong className="risk-high">64% Risk</strong>
            </div>

            <div className="queue-item">
              <span>Binary Search</span>
              <strong className="risk-mid">35% Risk</strong>
            </div>

            <div className="queue-item">
              <span>Prefix Sum</span>
              <strong className="risk-low">28% Risk</strong>
            </div>
          </div>
        </section>

        {/* ── Revision Reminder System ── */}
        <section className="reminder-panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Revision Reminder System</p>
              <h2>Bring students back before concepts fade.</h2>
              <p className="section-helper">
                Prototype uses browser notification permission. Production version can connect Firebase Cloud Messaging for scheduled reminders.
              </p>
            </div>
            <span className={`reminder-status-badge status-${reminderStatus.toLowerCase().replace(/\s/g, '-')}`}>
              {reminderStatus === "Enabled" ? "🔔" : reminderStatus === "Blocked" ? "🚫" : reminderStatus === "Not supported" ? "⚠️" : "🔕"}
              &nbsp;{reminderStatus}
            </span>
          </div>

          <div className="reminder-grid">
            {/* Browser Push */}
            <div className="reminder-card reminder-card-primary">
              <div className="reminder-card-top">
                <div className="reminder-icon-wrap reminder-icon-cyan">
                  <span>🔔</span>
                </div>
                <div>
                  <p className="reminder-channel">Browser Push</p>
                  <span className={`reminder-tag tag-${reminderStatus === "Enabled" ? "enabled" : reminderStatus === "Blocked" ? "blocked" : reminderStatus === "Not supported" ? "unsupported" : "ready"}`}>
                    {reminderStatus === "Enabled" ? "Enabled" : reminderStatus === "Blocked" ? "Blocked" : reminderStatus === "Not supported" ? "Not Supported" : "Ready"}
                  </span>
                </div>
              </div>
              <p className="reminder-desc">
                Sends revision reminders when memory decay crosses the threshold. Works directly in the browser without any app install. Browser reminders can later be scheduled through Firebase Cloud Messaging.
              </p>
              <button
                className={`reminder-btn ${reminderStatus === "Enabled" ? "reminder-btn-success" : reminderStatus === "Blocked" ? "reminder-btn-blocked" : ""}`}
                onClick={handleEnableReminders}
                disabled={reminderStatus === "Blocked" || reminderStatus === "Not supported"}
              >
                {reminderStatus === "Enabled"
                  ? "✓ Reminders Active"
                  : reminderStatus === "Blocked"
                  ? "Permission Blocked"
                  : reminderStatus === "Not supported"
                  ? "Not Supported"
                  : "Enable Browser Reminders"}
              </button>
            </div>

            {/* WhatsApp Reminder */}
            <div className="reminder-card">
              <div className="reminder-card-top">
                <div className="reminder-icon-wrap reminder-icon-green">
                  <span>💬</span>
                </div>
                <div>
                  <p className="reminder-channel">WhatsApp Reminder</p>
                  <span className="reminder-tag tag-future">Future Scope</span>
                </div>
              </div>
              <p className="reminder-desc">
                Can be integrated using WhatsApp Cloud API or Twilio after backend setup. Ideal for mobile-first students who miss browser notifications.
              </p>
              <button className="reminder-btn reminder-btn-muted" disabled>
                Requires Backend Setup
              </button>
            </div>

            {/* Email Reminder */}
            <div className="reminder-card">
              <div className="reminder-card-top">
                <div className="reminder-icon-wrap reminder-icon-purple">
                  <span>✉️</span>
                </div>
                <div>
                  <p className="reminder-channel">Email Reminder</p>
                  <span className="reminder-tag tag-optional">Optional</span>
                </div>
              </div>
              <p className="reminder-desc">
                Backup reminder channel for weekly revision summaries. Connects to SendGrid or Nodemailer in the production version.
              </p>
              <button className="reminder-btn reminder-btn-muted" disabled>
                Optional Integration
              </button>
            </div>
          </div>

          {/* Reminder Preview Card */}
          <div className="reminder-preview">
            <div className="reminder-preview-label">
              <span className="rp-dot" />
              Scheduled Reminder Preview
            </div>
            <div className="reminder-preview-body">
              <div className="rp-time">Tomorrow at 8:00 PM</div>
              <div className="rp-message">
                Arrays revision due — solve <strong>Two Sum</strong> or <strong>Contains Duplicate</strong> before the concept fades.
              </div>
              <div className="rp-meta">
                <span>Memory decay: 64%</span>
                <span>·</span>
                <span>Topic: Arrays + Hashing</span>
              </div>
            </div>
          </div>
        </section>

        {/* ── Recommended Problem Bank ── */}
        <section className="recommend-panel" id="problems">
          <div className="section-head">
            <div>
              <p className="eyebrow">Recommended Problem Bank</p>
              <h2>What should you solve next?</h2>
            </div>
            <span className="live-pill">
              <span className="live-dot" />
              Dynamic Recall Score
            </span>
          </div>

          <div className="problem-grid">
            {scoredProblems.map((problem) => (
              <article
                className={`recommend-card ${
                  selectedProblem.id === problem.id ? "selected-problem" : ""
                }`}
                key={problem.title}
              >
                {selectedProblem.id === problem.id && (
                  <div className="selected-banner">
                    <span>● Practicing Now</span>
                  </div>
                )}

                <div className="recommend-top">
                  <div className="recommend-title-group">
                    <span
                      className={`difficulty-pill diff-${problem.difficulty.toLowerCase()}`}
                    >
                      {problem.difficulty}
                    </span>
                    <h3>{problem.title}</h3>
                  </div>
                  <div className="match-score-block">
                    <span className="match-number">{problem.matchScore}</span>
                    <span className="match-label">% match</span>
                  </div>
                </div>

                <div className="tag-row">
                  {problem.tags.map((tag) => (
                    <span key={tag}>{tag}</span>
                  ))}
                </div>

                <p className="recommend-reason">{problem.reason}</p>

                <div className="score-reason">
                  <span>Why this score?</span>
                  <p>
                    Based on workload, goal, weak topic, difficulty, and topic
                    match.
                  </p>
                </div>

                <div className="recommend-actions">
                  <a href={problem.link} target="_blank" rel="noreferrer">
                    LeetCode ↗
                  </a>
                  <button onClick={() => handlePracticeHere(problem)}>
                    Practice Here
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* ── Practice Workspace ── */}
        <section className="workspace-panel" id="workspace">
          <div className="section-head">
            <div>
              <p className="eyebrow">Practice Workspace</p>
              <h2>{selectedProblem.title} · AI Solving Companion</h2>
            </div>
            <span className="live-pill">
              <span className="live-dot live-dot-green" />
              Editable Code Review
            </span>
          </div>

          <div className="workspace-grid">
            {/* Problem Description */}
            <div className="problem-card">
              <div className="problem-top">
                <div>
                  <span className={`difficulty-pill diff-${selectedProblem.difficulty.toLowerCase()}`}>
                    {selectedProblem.difficulty}
                  </span>
                  <h3>{selectedProblem.title}</h3>
                </div>
                <span className="topic-tag">
                  {selectedProblem.tags.join(" + ")}
                </span>
              </div>

              <p>{selectedProblem.statement}</p>

              <div className="problem-detail">
                <span>Why this problem?</span>
                <p>{selectedProblem.reason}</p>
              </div>

              <div className="test-box">
                <span>Sample I/O</span>
                <code>{selectedProblem.sample}</code>
              </div>
            </div>

            {/* Code Editor */}
            <div className="code-card editable-code-card">
              <div className="code-head">
                <div className="editor-dots">
                  <span className="dot dot-r" />
                  <span className="dot dot-y" />
                  <span className="dot dot-g" />
                </div>
                <span className="editor-title">Paste / Edit Your Code</span>
                <strong className="editor-lang">JavaScript</strong>
              </div>

              <textarea
                className="code-editor"
                value={userCode}
                onChange={(event) => {
                  setUserCode(event.target.value);
                  setReviewGenerated(false);
                }}
                spellCheck="false"
              />

              <div className="code-actions">
                <button className="btn-review" onClick={handleReviewCode}>
                  ▶ Review Code
                </button>
                <button
                  className="btn-reset"
                  onClick={() => {
                    setUserCode(selectedProblem.code);
                    setReviewGenerated(false);
                  }}
                >
                  ↺ Reset Sample
                </button>
              </div>
            </div>

            {/* AI Review Panel */}
            <div className={`review-card ${reviewGenerated ? "review-ready" : ""}`}>
              <p className="eyebrow">AI Review Preview</p>

              {!reviewGenerated ? (
                <>
                  <h3 className="review-waiting-title">Awaiting Code Review</h3>
                  <div className="empty-review">
                    <div className="waiting-icon">⬡</div>
                    <span>Ready to analyze</span>
                    <p>
                      Click <strong>Review Code</strong> to simulate how the AI
                      mentor will analyze pattern, complexity, edge cases, and
                      revision needs.
                    </p>
                    <div className="waiting-indicators">
                      <span className="wi-dot" />
                      <span className="wi-dot" />
                      <span className="wi-dot" />
                    </div>
                  </div>
                  <p className="review-proto-note">
                    Prototype uses mock diagnostics. Production version connects Gemini through FastAPI.
                  </p>
                </>
              ) : (
                <>
                  <div className="review-header-row">
                    <h3>Diagnostic Complete</h3>
                    <span className={`clarity-badge clarity-${selectedProblem.review.clarity.toLowerCase().replace(/\s/g, '-')}`}>
                      {selectedProblem.review.clarity}
                    </span>
                  </div>

                  <div className="review-list">
                    <div className="review-row">
                      <span>Pattern detected</span>
                      <strong>{selectedProblem.review.pattern}</strong>
                    </div>

                    <div className="review-row">
                      <span>Time complexity</span>
                      <strong className="complexity-badge">{selectedProblem.review.time}</strong>
                    </div>

                    <div className="review-row">
                      <span>Space complexity</span>
                      <strong className="complexity-badge">{selectedProblem.review.space}</strong>
                    </div>

                    <div className="review-row">
                      <span>Edge case to revise</span>
                      <strong>{selectedProblem.review.edge}</strong>
                    </div>
                  </div>

                  <div className="ai-note">
                    <span>AI Mentor Note</span>
                    <p>{selectedProblem.review.note}</p>
                  </div>

                  <button className="secondary-btn">
                    Add Similar Problem to Revision
                  </button>
                </>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;