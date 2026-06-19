import './ActivityGraph.css';

export default function ActivityGraph({ activityData, totalSolved }) {
  const today = new Date();
  const cells = [];
  
  // Create 52 cols x 7 rows (approx 364 days)
  for (let col = 0; col < 52; col++) {
    const colCells = [];
    for (let row = 0; row < 7; row++) {
      // Calculate date for this cell (going backwards from today)
      // col=51, row=6 is today
      const daysAgo = (51 - col) * 7 + (6 - row);
      const cellDate = new Date(today);
      cellDate.setDate(today.getDate() - daysAgo);
      
      const yyyy = cellDate.getFullYear();
      const mm = String(cellDate.getMonth() + 1).padStart(2, '0');
      const dd = String(cellDate.getDate()).padStart(2, '0');
      const dateStr = `${yyyy}-${mm}-${dd}`;
      
      // Determine intensity based on activityData map
      let count = 0;
      if (activityData && activityData[dateStr] !== undefined) {
        count = activityData[dateStr];
      }
      
      let intensity = 0;
      if (count > 0) intensity = 1;
      if (count >= 2) intensity = 2;
      if (count >= 4) intensity = 3;
      if (count >= 6) intensity = 4;

      colCells.push(
        <div 
          key={`${col}-${row}`} 
          className={`activity-cell intensity-${intensity}`} 
          title={`${count} contributions on ${dateStr}`}
        ></div>
      );
    }
    cells.push(
      <div key={`col-${col}`} className="activity-col">
        {colCells}
      </div>
    );
  }

  return (
    <div className="activity-graph-container">
      <div className="activity-graph-header">
        <h3 className="activity-graph-title">Activity Graph</h3>
        <span className="activity-graph-total">{totalSolved !== undefined ? totalSolved : '...'} problems solved in the last year</span>
      </div>
      
      <div className="activity-graph-scroll">
        <div className="activity-graph-grid">
          {cells}
        </div>
      </div>
      
      <div className="activity-graph-legend">
        <span>Less</span>
        <div className="activity-cell intensity-0"></div>
        <div className="activity-cell intensity-1"></div>
        <div className="activity-cell intensity-2"></div>
        <div className="activity-cell intensity-3"></div>
        <div className="activity-cell intensity-4"></div>
        <span>More</span>
      </div>
    </div>
  );
}
