const BASE_URL = "https://study-smart-4ezm.onrender.com";

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

  if (!res.ok) {
    throw new Error(`Login failed with status ${res.status}`);
  }

  const data = await res.json();
  return data.access_token;
}

export async function getUserInfo(token) {
  const res = await fetch(`${BASE_URL}/auth/userinfo`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    throw new Error("Failed to fetch user info");
  }

  return await res.json();
}

export async function getSchedule(token, text, minutes) {
  const res = await fetch(`${BASE_URL}/personalized-schedule`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ raw_tasks_text: text, available_time_minutes: minutes })
  });
  return await res.json();
}

export async function logTaskAction(token, userId, task, action, extended_by) {
  const res = await fetch(`${BASE_URL}/log-task`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ user_id: userId, task, action, extended_by })
  });
  return await res.json();
}
