"use client"

import { useState } from "react"
import { useAuth } from "@clerk/nextjs"

import { checkAnswer, newQuestion } from "@/lib/api"
import type { CheckResult, Step } from "./practice"

export function usePracticeSession() {
  const { getToken } = useAuth()

  const [step, setStep] = useState<Step>("prompt")
  const [prompt, setPrompt] = useState("")
  const [difficulty, setDifficulty] = useState(1)
  const [language, setLanguage] = useState("python")
  const [model, setModel] = useState("recursive/flint-v1.0:free")

  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [result, setResult] = useState<CheckResult | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const generateQuestion = async () => {
    if (!prompt.trim()) {
      setError("Describe the type of problem you want to practice first.")
      return
    }

    setLoading(true)
    setError("")
    setResult(null)

    try {
      const token = await getToken()

      if (!token) {
        setError("Your session expired. Sign in again to continue.")
        return
      }

      const data = await newQuestion(
        token,
        prompt,
        difficulty,
        language,
        model
      )

      setQuestion(data.question)
      setAnswer("")
      setStep("question")
    } catch {
      setError("Could not generate a question. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const checkCurrentAnswer = async () => {
    if (!answer.trim()) {
      setError("Write an answer before submitting it for review.")
      return
    }

    setLoading(true)
    setError("")

    try {
      const token = await getToken()

      if (!token) {
        setError("Your session expired. Sign in again to continue.")
        return
      }

      const data = await checkAnswer(token, question, answer)

      setResult(data)
      setStep("result")
    } catch {
      setError("Could not check your answer. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const resetToPrompt = () => {
    setStep("prompt")
    setAnswer("")
    setQuestion("")
    setResult(null)
    setError("")
  }

  const tryAnother = () => {
    setStep("question")
    setAnswer("")
    setResult(null)
    setError("")
  }

  return {
    step,
    prompt,
    setPrompt,
    difficulty,
    setDifficulty,
    language,
    setLanguage,
    model,
    setModel,
    question,
    answer,
    setAnswer,
    result,
    loading,
    error,
    generateQuestion,
    checkCurrentAnswer,
    resetToPrompt,
    tryAnother,
  }
}

export type PracticeSession = ReturnType<typeof usePracticeSession>