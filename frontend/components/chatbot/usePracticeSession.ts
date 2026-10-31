"use client"

import { useState } from "react"
import { useAuth } from "@clerk/nextjs"

import { checkAnswer, newQuestion, newQuestionExample } from "@/lib/api"
import type { CheckResult, Step } from "./practice"

export type SelectedFile = {
  id: string
  file: File
  progress: number
  failed: boolean
}


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

  const [files, setFiles] = useState<SelectedFile[]>([])

  const generateQuestionExample = async () => {
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

      const data = await newQuestionExample(
        token,
        prompt,
        difficulty,
        language,
        model,
        files.map((selectedFile) => selectedFile.file)
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

  const addFiles = (newFiles: FileList) => {
    const incomingFiles = Array.from(newFiles).map((file) => ({
      id: crypto.randomUUID(),
      file,
      progress: 0,
      failed: false,
    }))
    setFiles((currentFiles) => [...currentFiles, ...incomingFiles])
  }
  const removeFile = (id: string) => {
    setFiles((currentFiles) =>
      currentFiles.filter((selectedFile) => selectedFile.id !== id)
    )
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

      const data = await checkAnswer(token, question, answer, model)

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
    setFiles([])
  }

  const tryAnother = () => {
    setQuestion("Generating")
    setStep("question")
    setAnswer("")
    setResult(null)
    setError("")
    generateQuestion()
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
    files,
    addFiles,
    removeFile,
    setFiles,
  }
}

export type PracticeSession = ReturnType<typeof usePracticeSession>