const BASE_URL = "https://study-smart-4ezm.onrender.com";

// ✅ Helper to attach token automatically
function getAuthHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function signup(username, password) {
  await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
}

export async function login(username, password) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  return data.access_token;
}

export async function getUserInfo() {
  const res = await fetch(`${BASE_URL}/auth/userinfo`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error("Unauthorized");
  return await res.json();
}

export async function getSchedule(text, minutes) {
  const res = await fetch(`${BASE_URL}/personalized-schedule`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      raw_tasks_text: text,
      available_time_minutes: minutes,
      must_do_tasks: []   // ✅ always send this field (fix)
    })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Schedule failed");
  return data;
}

export async function logTaskAction(userId, task, action, extended_by) {
  const res = await fetch(`${BASE_URL}/log-task`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ user_id: userId, task, action, extended_by })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Log task failed");
  return data;
}
