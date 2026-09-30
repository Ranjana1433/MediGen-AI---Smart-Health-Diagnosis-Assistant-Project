const API_BASE = "";

// ---------- Auth guard ----------
const token = localStorage.getItem("pulse_token");
const userEmail = localStorage.getItem("pulse_email");
const userRole = localStorage.getItem("pulse_role") || "user";

if (!token) {
  window.location.href = "/login";
}

const roleLabel = userRole === "admin" ? " (Admin)" : "";
document.getElementById("topbarUsername").textContent = userEmail ? `Hi, ${userEmail}${roleLabel}` : "";
document.getElementById("logoutBtn").addEventListener("click", async () => {
  try {
    await fetch(`${API_BASE}/api/logout?token=${encodeURIComponent(token)}`, { method: "POST" });
  } catch (e) { /* ignore network errors on logout */ }
  localStorage.removeItem("pulse_token");
  localStorage.removeItem("pulse_email");
  localStorage.removeItem("pulse_role");
  window.location.href = "/login";
});

// ---------- Elements ----------
const symptomGrid = document.getElementById("symptomGrid");
const symptomSearch = document.getElementById("symptomSearch");
const diagnoseBtn = document.getElementById("diagnoseBtn");
const selectedBar = document.getElementById("selectedBar");
const selectedCount = document.getElementById("selectedCount");
const resultEmpty = document.getElementById("resultEmpty");
const resultContent = document.getElementById("resultContent");
const historyContent = document.getElementById("historyContent");
const loadHistoryBtn = document.getElementById("loadHistoryBtn");
const userNameInput = document.getElementById("userName");
const micBtn = document.getElementById("micBtn");
const voiceHint = document.getElementById("voiceHint");

let allSymptoms = [];
let selectedSymptoms = new Set();

function formatLabel(symptom) {
  return symptom.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// ---------- Load symptoms ----------
async function loadSymptoms() {
  try {
    const res = await fetch(`${API_BASE}/api/symptoms`);
    const data = await res.json();
    allSymptoms = data.symptoms;
    renderSymptoms(allSymptoms);
  } catch (err) {
    symptomGrid.innerHTML = "Could not load symptoms. Is the backend running?";
  }
}

function renderSymptoms(list) {
  symptomGrid.innerHTML = "";
  list.forEach((symptom) => {
    const chip = document.createElement("div");
    chip.className = "symptom-chip" + (selectedSymptoms.has(symptom) ? " selected" : "");
    chip.textContent = formatLabel(symptom);
    chip.dataset.symptom = symptom;
    chip.addEventListener("click", () => toggleSymptom(symptom));
    symptomGrid.appendChild(chip);
  });
}

function toggleSymptom(symptom) {
  if (selectedSymptoms.has(symptom)) {
    selectedSymptoms.delete(symptom);
  } else {
    selectedSymptoms.add(symptom);
  }
  renderSymptoms(
    symptomSearch.value.trim()
      ? allSymptoms.filter((s) => s.includes(symptomSearch.value.trim().toLowerCase().replace(/ /g, "_")))
      : allSymptoms
  );
  updateSelectedBar();
}

function updateSelectedBar() {
  if (selectedSymptoms.size > 0) {
    selectedBar.style.display = "flex";
    selectedCount.textContent = `${selectedSymptoms.size} selected`;
  } else {
    selectedBar.style.display = "none";
  }
}

symptomSearch.addEventListener("input", () => {
  const q = symptomSearch.value.trim().toLowerCase().replace(/ /g, "_");
  renderSymptoms(q ? allSymptoms.filter((s) => s.includes(q)) : allSymptoms);
});

// ---------- Voice input (Web Speech API) ----------
const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;

if (SpeechRecognitionAPI) {
  recognition = new SpeechRecognitionAPI();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    micBtn.classList.add("listening");
    voiceHint.textContent = "Listening… speak your symptoms now.";
  };

  recognition.onerror = (event) => {
    voiceHint.textContent = `Voice input error: ${event.error}. Try again or type instead.`;
    micBtn.classList.remove("listening");
  };

  recognition.onend = () => {
    micBtn.classList.remove("listening");
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript.toLowerCase();
    voiceHint.textContent = `Heard: "${transcript}"`;
    matchSymptomsFromSpeech(transcript);
  };

  micBtn.addEventListener("click", () => {
    if (micBtn.classList.contains("listening")) {
      recognition.stop();
    } else {
      recognition.start();
    }
  });
} else {
  micBtn.style.display = "none";
}

function matchSymptomsFromSpeech(transcript) {
  const cleaned = transcript.replace(/[^a-z\s]/g, " ");
  let matchedAny = false;
  allSymptoms.forEach((symptom) => {
    const words = symptom.split("_");
    // match if every word of the symptom key appears in the spoken text
    const isMatch = words.every((w) => cleaned.includes(w));
    // also try the human-readable phrase directly
    const phrase = words.join(" ");
    if (isMatch || cleaned.includes(phrase)) {
      selectedSymptoms.add(symptom);
      matchedAny = true;
    }
  });
  renderSymptoms(allSymptoms);
  updateSelectedBar();
  if (!matchedAny) {
    voiceHint.textContent += " — no matching symptoms recognized, try different wording or select manually.";
  }
}

// ---------- Voice output (speech synthesis) ----------
function speakText(text, buttonEl) {
  if (!("speechSynthesis" in window)) return;
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    if (buttonEl) buttonEl.classList.remove("speaking");
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  if (buttonEl) {
    buttonEl.classList.add("speaking");
    utterance.onend = () => buttonEl.classList.remove("speaking");
  }
  window.speechSynthesis.speak(utterance);
}

// ---------- Diagnosis ----------
function severityClass(severity) {
  const s = severity.toLowerCase();
  if (s.includes("severe")) return "severe";
  if (s.includes("moderate")) return "moderate";
  return "mild";
}

async function diagnose() {
  if (selectedSymptoms.size === 0) {
    alert("Please select at least one symptom.");
    return;
  }
  diagnoseBtn.disabled = true;
  diagnoseBtn.textContent = "Analyzing…";

  try {
    const res = await fetch(`${API_BASE}/api/diagnose`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: userNameInput.value || userEmail || "Guest",
        symptoms: Array.from(selectedSymptoms),
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Something went wrong");
    }

    const data = await res.json();
    renderResult(data);
    loadHistory();
  } catch (err) {
    alert(err.message);
  } finally {
    diagnoseBtn.disabled = false;
    diagnoseBtn.textContent = "Analyze symptoms";
  }
}

function renderResult(data) {
  resultEmpty.style.display = "none";
  resultContent.style.display = "block";

  const precautionsHtml = data.precautions.map((p) => `<li>${p}</li>`).join("");
  const medicinesHtml = data.medicines.map((m) => `<li>${m}</li>`).join("");

  resultContent.innerHTML = `
    <div class="confidence-row">
      <span class="badge ${severityClass(data.severity)}">${data.severity}</span>
    </div>
    <div class="disease-name">${data.predicted_disease}</div>
    <div class="confidence-bar-track">
      <div class="confidence-bar-fill" style="width:${data.confidence}%"></div>
    </div>
    <div style="font-size:0.82rem;color:var(--muted);margin-bottom:4px;">${data.confidence}% model confidence</div>

    <div class="explanation" id="explanationText">${data.explanation}</div>
    <button class="speak-btn" id="speakBtn" type="button">🔊 Listen to explanation</button>

    <h3>Suggested precautions</h3>
    <ul class="info-list">${precautionsHtml}</ul>

    <h3>Common medicine categories</h3>
    <ul class="info-list">${medicinesHtml}</ul>
    <div class="medicine-note">${data.medical_disclaimer}</div>

    <h3>Recommended specialist</h3>
    <div class="specialist-cta">
      <span>${data.specialist}</span>
      <button class="cta cta-solid" id="bookApptCta" type="button">Book appointment</button>
    </div>

    <h3>Other possibilities considered</h3>
    <div class="chart-wrap"><canvas id="predictionChart" height="140"></canvas></div>
  `;

  document.getElementById("speakBtn").addEventListener("click", (e) => {
    speakText(data.explanation, e.currentTarget);
  });

  document.getElementById("bookApptCta").addEventListener("click", () => {
    preselectSpecialty(data.specialist);
    document.getElementById("appointment").scrollIntoView({ behavior: "smooth" });
  });

  renderPredictionChart(data.top_predictions);

  resultContent.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ---------- Chart (Chart.js) ----------
let predictionChartInstance = null;

function renderPredictionChart(topPredictions) {
  const ctx = document.getElementById("predictionChart");
  if (!ctx || typeof Chart === "undefined") return;

  if (predictionChartInstance) {
    predictionChartInstance.destroy();
  }

  const styles = getComputedStyle(document.documentElement);
  const teal = styles.getPropertyValue("--teal").trim() || "#2F9C8F";
  const navy = styles.getPropertyValue("--navy").trim() || "#0B2E33";
  const line = styles.getPropertyValue("--line").trim() || "#E2DCCC";

  predictionChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: topPredictions.map((p) => p.disease),
      datasets: [
        {
          label: "Model confidence (%)",
          data: topPredictions.map((p) => p.confidence),
          backgroundColor: topPredictions.map((_, i) => (i === 0 ? teal : navy + "55")),
          borderRadius: 8,
          maxBarThickness: 46,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: (ctx) => `${ctx.raw}% confidence` },
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          max: 100,
          grid: { color: line },
          ticks: { callback: (v) => v + "%" },
        },
        y: {
          grid: { display: false },
        },
      },
    },
  });
}

// ---------- History ----------
async function loadHistory() {
  try {
    const res = await fetch(`${API_BASE}/api/history`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Session expired");
    const data = await res.json();
    if (data.history.length === 0) {
      historyContent.innerHTML = "<p class='empty-note'>No checks yet — run your first symptom check above.</p>";
      return;
    }
    historyContent.innerHTML = data.history
      .map(
        (h) => `
        <div class="history-item">
          <div class="history-time">${new Date(h.created_at).toLocaleString()}</div>
          <div>
            <div class="history-disease">${h.predicted_disease} <span style="color:var(--muted);font-weight:400;">(${h.confidence}%)</span></div>
            <div class="history-symptoms">${h.name} — ${h.symptoms.replace(/,/g, ", ")}</div>
          </div>
        </div>`
      )
      .join("");

    renderSeverityChart(data.history);
  } catch (err) {
    historyContent.innerHTML = "<p class='empty-note'>Could not load history.</p>";
  }
}

// ---------- History severity chart (Chart.js) ----------
let severityChartInstance = null;

function severityBucket(severity) {
  const s = (severity || "").toLowerCase();
  if (s.includes("severe")) return "Severe";
  if (s.includes("moderate")) return "Moderate";
  return "Mild";
}

function renderSeverityChart(historyRows) {
  const canvas = document.getElementById("severityChart");
  if (!canvas || typeof Chart === "undefined") return;

  const counts = { Mild: 0, Moderate: 0, Severe: 0 };
  historyRows.forEach((h) => {
    counts[severityBucket(h.severity)]++;
  });

  const styles = getComputedStyle(document.documentElement);
  const mild = styles.getPropertyValue("--mild").trim() || "#5B8C6E";
  const moderate = styles.getPropertyValue("--moderate").trim() || "#C08A3E";
  const severe = styles.getPropertyValue("--severe").trim() || "#C1503F";

  if (severityChartInstance) severityChartInstance.destroy();

  severityChartInstance = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["Mild", "Moderate", "Severe"],
      datasets: [
        {
          data: [counts.Mild, counts.Moderate, counts.Severe],
          backgroundColor: [mild, moderate, severe],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      cutout: "62%",
      plugins: {
        legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } },
      },
    },
  });
}

diagnoseBtn.addEventListener("click", diagnose);
loadHistoryBtn.addEventListener("click", loadHistory);

loadSymptoms();
loadHistory();

// ==================== Appointment booking ====================
const apptForm = document.getElementById("appointmentForm");
const apptPatientName = document.getElementById("apptPatientName");
const apptDoctorSelect = document.getElementById("apptDoctor");
const apptDoctorMeta = document.getElementById("apptDoctorMeta");
const apptDate = document.getElementById("apptDate");
const apptTimeSelect = document.getElementById("apptTime");
const apptReason = document.getElementById("apptReason");
const apptError = document.getElementById("apptError");
const apptSuccess = document.getElementById("apptSuccess");
const appointmentsContent = document.getElementById("appointmentsContent");

let allDoctors = [];

// Prevent picking a date in the past
apptDate.min = new Date().toISOString().split("T")[0];

async function loadDoctors() {
  try {
    const res = await fetch(`${API_BASE}/api/doctors`);
    const data = await res.json();
    allDoctors = data.doctors;
    apptDoctorSelect.innerHTML =
      `<option value="">Select a doctor / specialty</option>` +
      allDoctors
        .map((d) => `<option value="${d.id}">${d.name} — ${d.specialty}</option>`)
        .join("");
  } catch (err) {
    apptDoctorSelect.innerHTML = `<option value="">Could not load doctors</option>`;
  }
}

function updateDoctorMeta() {
  const doctor = allDoctors.find((d) => d.id === apptDoctorSelect.value);
  if (!doctor) {
    apptDoctorMeta.textContent = "";
    apptTimeSelect.innerHTML = `<option value="">Select doctor first</option>`;
    return;
  }
  apptDoctorMeta.textContent = `Available: ${doctor.available_days}`;
  apptTimeSelect.innerHTML =
    `<option value="">Select a time</option>` +
    doctor.available_slots.map((s) => `<option value="${s}">${s}</option>`).join("");
}

function preselectSpecialty(specialty) {
  const match = allDoctors.find((d) => d.specialty === specialty);
  if (match) {
    apptDoctorSelect.value = match.id;
    updateDoctorMeta();
  }
}

apptDoctorSelect.addEventListener("change", updateDoctorMeta);

apptForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  apptError.textContent = "";
  apptSuccess.textContent = "";

  try {
    const res = await fetch(`${API_BASE}/api/appointments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        patient_name: apptPatientName.value.trim(),
        doctor_id: apptDoctorSelect.value,
        appointment_date: apptDate.value,
        appointment_time: apptTimeSelect.value,
        reason: apptReason.value.trim(),
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Could not book appointment.");

    apptSuccess.textContent = data.message;
    apptForm.reset();
    apptTimeSelect.innerHTML = `<option value="">Select doctor first</option>`;
    apptDoctorMeta.textContent = "";
    loadAppointments();
  } catch (err) {
    apptError.textContent = err.message;
  }
});

async function loadAppointments() {
  try {
    const res = await fetch(`${API_BASE}/api/appointments`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Session expired");
    const data = await res.json();

    if (data.appointments.length === 0) {
      appointmentsContent.innerHTML = "<p class='empty-note'>No appointments booked yet.</p>";
      return;
    }

    appointmentsContent.innerHTML = data.appointments
      .map((a) => {
        const cancelled = a.status === "Cancelled";
        return `
        <div class="appointment-item ${cancelled ? "cancelled" : ""}">
          <div>
            <div class="appt-doctor">${a.doctor_name} <span class="appt-specialty">(${a.specialty})</span></div>
            <div class="appt-meta">${a.patient_name} — ${a.appointment_date} at ${a.appointment_time}</div>
            ${a.reason ? `<div class="appt-reason">"${a.reason}"</div>` : ""}
          </div>
          <div class="appt-actions">
            <span class="badge ${cancelled ? "severe" : "mild"}">${a.status}</span>
            ${!cancelled ? `<button class="ghost-btn small" data-id="${a.id}">Cancel</button>` : ""}
          </div>
        </div>`;
      })
      .join("");

    appointmentsContent.querySelectorAll("button[data-id]").forEach((btn) => {
      btn.addEventListener("click", () => cancelAppointment(btn.dataset.id));
    });
  } catch (err) {
    appointmentsContent.innerHTML = "<p class='empty-note'>Could not load appointments.</p>";
  }
}

async function cancelAppointment(id) {
  try {
    const res = await fetch(`${API_BASE}/api/appointments/${id}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Could not cancel appointment.");
    }
    loadAppointments();
  } catch (err) {
    alert(err.message);
  }
}

loadDoctors().then(loadAppointments);
