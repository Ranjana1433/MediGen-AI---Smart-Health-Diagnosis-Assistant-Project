const API_BASE = "";

const tabs = document.querySelectorAll(".auth-tab");
const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    if (tab.dataset.tab === "login") {
      loginForm.style.display = "flex";
      signupForm.style.display = "none";
    } else {
      loginForm.style.display = "none";
      signupForm.style.display = "flex";
    }
  });
});

// If already logged in, skip straight to the app
if (localStorage.getItem("pulse_token")) {
  window.location.href = "/";
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  const errorBox = document.getElementById("loginError");
  errorBox.textContent = "";

  try {
    const res = await fetch(`${API_BASE}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed.");

    localStorage.setItem("pulse_token", data.token);
    localStorage.setItem("pulse_email", data.email);
    localStorage.setItem("pulse_role", data.role);
    window.location.href = "/";
  } catch (err) {
    errorBox.textContent = err.message;
  }
});

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("signupEmail").value.trim();
  const password = document.getElementById("signupPassword").value;
  const role = document.querySelector('input[name="signupRole"]:checked').value;
  const errorBox = document.getElementById("signupError");
  const successBox = document.getElementById("signupSuccess");
  errorBox.textContent = "";
  successBox.textContent = "";

  try {
    const res = await fetch(`${API_BASE}/api/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, role }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed.");

    successBox.textContent = "Account created! You can sign in now.";
    document.querySelector('.auth-tab[data-tab="login"]').click();
    document.getElementById("loginEmail").value = email;
  } catch (err) {
    errorBox.textContent = err.message;
  }
});
