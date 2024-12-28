import React from "react";

export default function TrajectoryList({
  trajectories,
  query,
  onQueryChange,
  scoreRange,
  onScoreRangeChange,
  selectedTrajectories,
  onToggleTrajectory,
}) {
  const [minScore, maxScore] = scoreRange;

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Trajectories</h2>
      <div style={{ marginBottom: "1rem" }}>
        <label>Search: </label>
        <input
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Search plan/action/outcome"
        />
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <label>Score Min: {minScore.toFixed(2)}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={minScore}
          onChange={(e) => {
            onScoreRangeChange([parseFloat(e.target.value), maxScore]);
          }}
        />
        <label>Score Max: {maxScore.toFixed(2)}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={maxScore}
          onChange={(e) => {
            onScoreRangeChange([minScore, parseFloat(e.target.value)]);
          }}
        />
      </div>
      <ul style={{ listStyle: "none", paddingLeft: 0, height: "60vh", overflowY: "auto" }}>
        {trajectories.map((t) => (
          <li key={t.id} style={{ marginBottom: "0.5rem" }}>
            <label>
              <input
                type="checkbox"
                checked={selectedTrajectories.includes(t.id)}
                onChange={() => onToggleTrajectory(t.id)}
              />
              {t.id}
            </label>
            <span style={{ marginLeft: "0.5rem", color: "#777" }}>
              ({t.steps.length} steps)
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}