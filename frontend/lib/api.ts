const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://100.66.224.73:8000"

export async function newQuestion(
  token: string,
  prompt: string,
  diff: number = 1,
  language: string = "python",
  model: string = "openrouter/free"
) {
  const res = await fetch(`${API_BASE}/newquestion`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ diff, UserPrompt: prompt, language, model }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed to generate question")
  return data
}

export async function checkAnswer(
  token: string,
  question: string,
  answer: string,
  model: string = "aion-labs/aion-rp-llama-3.1-8b"
) {
  const res = await fetch(`${API_BASE}/checkAnswer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ Question: question, Answer: answer, model }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed to check answer")
  return data
}
