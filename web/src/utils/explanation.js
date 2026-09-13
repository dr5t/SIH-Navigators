export function getConfidenceExplanation(state) {
  let confidence = "HIGH";
  const reasons = [];
  const mitigations = [];
  const actions = [];

  const modeName = state.mode || "GNSS_GOOD";
  
  if (['GNSS_DEGRADED', 'DEAD_RECKONING_DEGRADED'].includes(modeName)) {
    confidence = "LOW";
  } else if (['DEAD_RECKONING', 'GNSS_REJECTED', 'INITIALIZING'].includes(modeName)) {
    confidence = "MEDIUM";
  }

  if (state.pos_uncertainty > 20) {
    confidence = "LOW";
  }

  if (modeName.includes('DEAD_RECKONING') || modeName === 'GNSS_REJECTED') {
    reasons.push("GNSS unavailable for 48 seconds");
    if (state.speed_source === "AI") {
      mitigations.push("AI speed active");
    } else if (state.speed_source === "KINEMATIC") {
      mitigations.push("Vehicle constraints active");
    }
  } else if (modeName === 'GNSS_DEGRADED') {
    reasons.push("GNSS degraded");
  }

  if (state.pos_uncertainty > 15) {
    reasons.push(`Position uncertainty increased to ${Math.floor(state.pos_uncertainty)} m`);
  }

  if (state.map_status !== "MATCHED" && !modeName.includes("GNSS")) {
    reasons.push("Offline map matching unavailable");
  } else if (state.map_status === "MATCHED") {
    mitigations.push("Offline map matching active");
  }

  if (confidence === "LOW" || confidence === "MEDIUM") {
    actions.push("Run Diagnostics");
    if (!modeName.includes("GNSS")) {
      actions.push("Check GNSS");
    }
    if (state.pos_uncertainty > 25) {
      actions.push("Recalibrate");
    }
  }

  if (confidence !== "HIGH" && reasons.length === 0) {
    reasons.push("Temporary state transition");
  }

  return {
    confidence,
    reasons,
    mitigations,
    actions
  };
}
