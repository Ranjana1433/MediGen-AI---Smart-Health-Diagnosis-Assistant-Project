(function () {
  var token = localStorage.getItem("pulse_token"), role = localStorage.getItem("pulse_role");
  var H = { Authorization: "Bearer " + token };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  document.getElementById("bmiBtn").addEventListener("click", function () {
    var w = parseFloat(document.getElementById("bmiW").value), h = parseFloat(document.getElementById("bmiH").value) / 100;
    var out = document.getElementById("bmiOut");
    if (!(w > 0) || !(h > 0)) { out.textContent = "Enter valid weight and height."; return; }
    var b = w / (h * h), c = b < 18.5 ? "Underweight" : b < 25 ? "Normal ✅" : b < 30 ? "Overweight" : "Obese";
    out.textContent = "BMI " + b.toFixed(1) + " — " + c;
  });
  if (role !== "admin" || !token) return;
  document.getElementById("adminPanel").style.display = "block";
  async function load() {
    try {
      var s = await (await fetch("/api/admin/stats", { headers: H })).json();
      document.getElementById("adminStats").innerHTML = [["Users", s.users], ["Admins", s.admins], ["Diagnoses", s.diagnoses], ["Appointments", s.appointments]]
        .map(function (x) { return '<div class="stat"><b>' + x[1] + "</b>" + x[0] + "</div>"; }).join("");
      if (window.Chart && s.top_diseases.length) {
        if (window._ac) window._ac.destroy();
        window._ac = new Chart(document.getElementById("adminChart"), { type: "bar", data: { labels: s.top_diseases.map(function (d) { return d.disease; }), datasets: [{ label: "Cases", data: s.top_diseases.map(function (d) { return d.count; }), backgroundColor: "#6366f1", borderRadius: 8 }] }, options: { plugins: { legend: { display: false } } } });
      }
      var u = await (await fetch("/api/admin/users", { headers: H })).json();
      document.getElementById("usersTable").innerHTML = "<tr><th>Email</th><th>Role</th><th>Joined</th><th>Action</th></tr>" +
        u.users.map(function (x) { return "<tr><td>" + esc(x.email) + "</td><td>" + x.role + "</td><td>" + esc((x.created_at || "").slice(0, 10)) + "</td><td>" +
          (x.email === "admin@medigen.com" ? "—" : '<button class="del-btn" data-e="' + esc(x.email) + '">Delete</button>') + "</td></tr>"; }).join("");
    } catch (e) { console.error(e); }
  }
  document.getElementById("usersTable").addEventListener("click", async function (e) {
    var em = e.target.getAttribute && e.target.getAttribute("data-e");
    if (em && confirm("Delete " + em + "?")) { await fetch("/api/admin/users?email=" + encodeURIComponent(em), { method: "DELETE", headers: H }); load(); }
  });
  load();
})();
