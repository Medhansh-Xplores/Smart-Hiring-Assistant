const form = document.getElementById("matchForm");
const fileInput = document.getElementById("resumes");
const fileList = document.getElementById("fileList");
const dropzone = document.getElementById("dropzone");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("error");
const resultsSection = document.getElementById("resultsSection");
const resultsContainer = document.getElementById("results");
const submitButton = document.getElementById("submitButton");

function showFiles(files) {
  fileList.innerHTML = "";
  [...files].forEach(file => {
    const chip = document.createElement("span");
    chip.className = "file-chip";
    chip.textContent = `${file.name} · ${(file.size / 1024).toFixed(0)} KB`;
    fileList.appendChild(chip);
  });
}
fileInput.addEventListener("change", () => showFiles(fileInput.files));

["dragenter", "dragover"].forEach(eventName => dropzone.addEventListener(eventName, event => {
  event.preventDefault(); dropzone.classList.add("dragover");
}));
["dragleave", "drop"].forEach(eventName => dropzone.addEventListener(eventName, event => {
  event.preventDefault(); dropzone.classList.remove("dragover");
}));
dropzone.addEventListener("drop", event => {
  if (event.dataTransfer.files.length) {
    fileInput.files = event.dataTransfer.files;
    showFiles(fileInput.files);
  }
});

function metric(label, value) {
  return `<div><div class="metric-label"><span>${label}</span><b>${Number(value).toFixed(1)}%</b></div><div class="bar"><span style="width:${Math.max(0, Math.min(100, value))}%"></span></div></div>`;
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[char]));
}
function renderResults(candidates) {
  resultsContainer.innerHTML = candidates.map((candidate, index) => {
    const matched = candidate.matched_skills.length
      ? candidate.matched_skills.map(skill => `<span class="skill">${escapeHtml(skill)}</span>`).join("")
      : '<span class="preview">No overlapping skills identified from the configured skill list.</span>';
    const missing = candidate.missing_skills.length
      ? candidate.missing_skills.map(skill => `<span class="skill missing">${escapeHtml(skill)}</span>`).join("")
      : '<span class="preview">No missing listed skills.</span>';
    return `<article class="candidate">
      <div class="candidate-top">
        <div><span class="rank">#${index + 1}</span><span class="candidate-name">${escapeHtml(candidate.name)}</span></div>
        <div class="score">${candidate.overall_score.toFixed(1)}<small>OVERALL MATCH</small></div>
      </div>
      <div class="score-bars">
        ${metric("Semantic relevance · 60%", candidate.semantic_score)}
        ${metric("Technical skills · 30%", candidate.skill_score)}
        ${metric("Education · 10%", candidate.education_score)}
      </div>
      <div class="skill-heading">MATCHED SKILLS</div><div class="skill-row">${matched}</div>
      <div class="skill-heading">SKILLS TO REVIEW</div><div class="skill-row">${missing}</div>
      <p class="preview">${escapeHtml(candidate.resume_preview || "")}${candidate.resume_preview && candidate.resume_preview.length >= 260 ? "…" : ""}</p>
    </article>`;
  }).join("");
  document.getElementById("candidateCount").textContent = `${candidates.length} candidate${candidates.length === 1 ? "" : "s"}`;
  resultsSection.classList.remove("hidden");
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  errorBox.classList.add("hidden");
  resultsSection.classList.add("hidden");
  loading.classList.remove("hidden");
  submitButton.disabled = true;

  try {
    const response = await fetch("/api/match", { method: "POST", body: new FormData(form) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Unable to process resumes.");
    renderResults(data.results || []);
    if (data.errors && data.errors.length) {
      errorBox.textContent = `Some files were skipped: ${data.errors.join("; ")}`;
      errorBox.classList.remove("hidden");
    }
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    errorBox.textContent = error.message || "Something went wrong. Please try again.";
    errorBox.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
    submitButton.disabled = false;
  }
});
