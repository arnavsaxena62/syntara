const API_BASE = "http://100.66.224.73:8000"

export function getToken(): string | null {
  return typeof window !== "undefined" ? localStorage.getItem("token") : null
}

export async function login(username: string, password: string) {
  const formData = new URLSearchParams({ grant_type: "password", username, password })
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  })
  const data = await res.json()
  if (res.ok && data.access_token) localStorage.setItem("token", data.access_token)
  return { ...data, ok: res.ok }
}

export async function newQuestion(userId: number, prompt: string, diff: number = 1, language: string = "python", model: string = "openrouter/free") {
  const token = getToken()
  const res = await fetch(`${API_BASE}/newquestion`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ Userid: userId, diff, UserPrompt: prompt, language, model }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed to generate question")
  return data
}

export async function checkAnswer(userId: number, question: string, answer: string, model: string = "aion-labs/aion-rp-llama-3.1-8b") {
  const token = getToken()
  const res = await fetch(`${API_BASE}/checkAnswer`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ Userid: userId, Question: question, Answer: answer, model }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed to check answer")
  return data
}