import React, { useState, useEffect } from "react";
import TrajectoryList from "./components/TrajectoryList";
import TimelineView from "./components/TimelineView";
import SettingsPanel from "./components/SettingsPanel";

function App() {
  const [trajectories, setTrajectories] = useState([]);
  const [selectedTrajectories, setSelectedTrajectories] = useState([]);
  const [query, setQuery] = useState("");
  const [scoreRange, setScoreRange] = useState([0, 1]);

  // Fetch trajectories when query/scoreRange changes
  useEffect(() => {
    const [scoreMin, scoreMax] = scoreRange;
    const params = new URLSearchParams();
    if (query) {
      params.append("query", query);
    }
    params.append("score_min", scoreMin);
    params.append("score_max", scoreMax);

    fetch(`/api/trajectories?${params.toString()}`)
      .then((res) => res.json())
      .then((data) => setTrajectories(data))
      .catch(console.error);
  }, [query, scoreRange]);

  // Add or remove a trajectory in the timeline view
  const toggleTrajectorySelection = (tId) => {
    setSelectedTrajectories((prev) => {
      if (prev.includes(tId)) {
        return prev.filter((id) => id !== tId);
      } else {
        return [...prev, tId];
      }
    });
  };

  // Filter the full list to just the selected ones
  const displayedTrajectories = trajectories.filter((t) =>
    selectedTrajectories.includes(t.id)
  );

  return (
    <div style={{ display: "flex", flexDirection: "row", height: "100vh" }}>
      <div style={{ width: "300px", borderRight: "1px solid #ccc" }}>
        <TrajectoryList
          trajectories={trajectories}
          query={query}
          onQueryChange={setQuery}
          scoreRange={scoreRange}
          onScoreRangeChange={setScoreRange}
          selectedTrajectories={selectedTrajectories}
          onToggleTrajectory={toggleTrajectorySelection}
        />
      </div>
      <div style={{ flexGrow: 1, padding: "1rem", overflow: "auto" }}>
        <TimelineView trajectories={displayedTrajectories} />
      </div>
      <div style={{ width: "300px", borderLeft: "1px solid #ccc" }}>
        <SettingsPanel />
      </div>
    </div>
  );
}

export default App;