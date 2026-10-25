export type Step = "prompt" | "question" | "result"

export type CheckResult = {
  score: number
  correct: boolean
  remarks: string
}