import React, { useState, useEffect } from "react";

export default function SettingsPanel() {
  const [scoreThreshold, setScoreThreshold] = useState(0.8);
  const [k, setK] = useState(5);

  // Load settings on mount
  useEffect(() => {
    fetch("/api/rag-settings")
      .then((res) => res.json())
      .then((data) => {
        setScoreThreshold(data.score_threshold);
        setK(data.k);
      })
      .catch(console.error);
  }, []);

  const handleSave = () => {
    fetch("/api/rag-settings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ score_threshold: scoreThreshold, k }),
    })
      .then((res) => res.json())
      .then((msg) => {
        console.log(msg);
        alert(msg.message);
      })
      .catch(console.error);
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h3>RAG Settings</h3>
      <div>
        <label>Score Threshold: </label>
        <input
          type="number"
          step="0.01"
          value={scoreThreshold}
          onChange={(e) => setScoreThreshold(parseFloat(e.target.value))}
          style={{ width: "4rem", marginRight: "1rem" }}
        />
      </div>
      <div style={{ marginTop: "0.5rem" }}>
        <label>K (top results): </label>
        <input
          type="number"
          value={k}
          onChange={(e) => setK(parseInt(e.target.value, 10))}
          style={{ width: "4rem" }}
        />
      </div>
      <button style={{ marginTop: "1rem" }} onClick={handleSave}>
        Save
      </button>
    </div>
  );
}