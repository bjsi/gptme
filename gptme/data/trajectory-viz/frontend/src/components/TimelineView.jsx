import React from "react";

export default function TimelineView({ trajectories }) {
  return (
    <div>
      <h2>Timeline View</h2>
      {trajectories.map((t) => (
        <div key={t.id} style={{ marginBottom: "2rem" }}>
          <h3>Trajectory: {t.id}</h3>
          <div style={{ borderLeft: "2px solid #666", marginLeft: "1rem", paddingLeft: "1rem" }}>
            {t.steps.map((step, idx) => (
              <div key={idx} style={{ marginBottom: "1rem" }}>
                <div><strong>Timestamp:</strong> {step.timestamp}</div>
                <div><strong>Plan:</strong> {step.plan}</div>
                <div><strong>Action:</strong> {step.action}</div>
                <div><strong>Outcome:</strong> {step.outcome}</div>
                <div><strong>Score:</strong> {step.score}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}