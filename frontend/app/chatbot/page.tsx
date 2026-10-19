"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { Button } from "@/components/ui/button"
import { newQuestion, checkAnswer } from "@/lib/api"

const MonacoEditor = dynamic(
  () => import("@monaco-editor/react").then((mod) => mod.Editor),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center bg-[#1e1e1e] text-sm text-zinc-400">
        Loading editor...
      </div>
    ),
  }
)

type CheckResult = {
  Score: number
  correct: boolean
  remarks: string
}

export default function ChatbotPage() {
  const [step, setStep] = useState<"prompt" | "question" | "result">("prompt")
  const [prompt, setPrompt] = useState("")
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [result, setResult] = useState<CheckResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const userId = 1

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("Describe the type of problem you want to practice first.")
      return
    }
    setLoading(true)
    setError("")
    try {
      const data = await newQuestion(userId, prompt)
      setQuestion(data.Question)
      setStep("question")
    } catch {
      setError("Could not generate a question. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleCheck = async () => {
    if (!answer.trim()) {
      setError("Write an answer before submitting it for review.")
      return
    }
    setLoading(true)
    setError("")
    try {
      const data = await checkAnswer(userId, question, answer)
      setResult(data)
      setStep("result")
    } catch {
      setError("Could not check your answer. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  if (step === "prompt") {
    return (
      <main className="min-h-screen flex items-center justify-center p-6 bg-muted">
        <div className="w-full max-w-2xl space-y-4">
          <h1 className="text-3xl font-bold">Ask a Question</h1>
          <p className="text-muted-foreground">
            Describe a problem you want to practice and get a coding challenge.
          </p>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="h-40 w-full min-h-40 p-4 border rounded-lg resize-none bg-background"
            placeholder="Example: Give me a medium Python problem about dictionaries and arrays..."
          />
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button onClick={handleGenerate} disabled={loading} className="w-full py-2">
            {loading ? "Generating..." : "Generate Question"}
          </Button>
        </div>
      </main>
    )
  }

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-muted/30">
      <header className="flex h-16 shrink-0 items-center justify-between border-b bg-background px-4 md:px-6">
        <h1 className="text-xl font-bold">Syntara</h1>
        <Button variant="outline" size="sm" onClick={() => setStep("prompt")}>
          New Question
        </Button>
      </header>

      <main className="grid min-h-0 flex-1 overflow-auto lg:grid-cols-[minmax(280px,0.8fr)_minmax(450px,1.7fr)_minmax(280px,0.8fr)] lg:overflow-hidden">
        {/* Questions Pane */}
        <aside className="border-b border-border bg-background lg:overflow-y-auto lg:border-b-0 lg:border-r">
          <div className="p-5 md:p-6">
            <h2 className="mb-3 text-sm font-semibold">Questions</h2>
            <article className="whitespace-pre-wrap text-sm leading-7">
              {question}
            </article>
          </div>
        </aside>

        {/* Answer Pane - Monaco Editor */}
        <section className="flex min-h-0 flex-1 flex-col p-4 md:p-6">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold">Your Solution</h2>
            <span className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary font-mono">Python</span>
          </div>
          <div className="min-h-0 flex-1 overflow-hidden rounded-xl border bg-[#1e1e1e] shadow-sm">
            <MonacoEditor
              height="100%"
              language="python"
              value={answer}
              onChange={(val) => val && setAnswer(val)}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineHeight: 22,
                padding: { top: 16, bottom: 16 },
                scrollBeyondLastLine: false,
                automaticLayout: true,
                wordWrap: "on",
              }}
            />
          </div>
          {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
        </section>

        {/* Results Pane */}
        <aside className="border-t border-border bg-background lg:overflow-y-auto lg:border-l lg:border-t-0">
          <div className="p-5 md:p-6">
            <h2 className="mb-3 text-sm font-semibold">Results</h2>
            {step === "question" ? (
              <div className="rounded-xl border border-dashed p-8 text-center">
                <p className="text-sm font-medium">Ready when you are</p>
                <p className="mt-1 text-xs text-muted-foreground">Submit your solution for review.</p>
                <Button onClick={handleCheck} disabled={loading} className="mt-4 w-full py-2">
                  {loading ? "Reviewing..." : "Check Answer"}
                </Button>
              </div>
            ) : result ? (
              <div className="space-y-4">
                <div
                  className={`rounded-xl border p-4 ${
                    result.correct
                      ? "border-emerald-500/30 bg-emerald-500/10"
                      : "border-destructive/30 bg-destructive/10"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">
                        {result.correct ? "Correct" : "Needs improvement"}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        Score: {result.Score}/100
                      </span>
                    </div>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {result.remarks}
                  </p>
                </div>
                <Button onClick={() => setStep("question")} className="w-full">
                  Try Another
                </Button>
              </div>
            ) : null}
          </div>
        </aside>
      </main>
    </div>
  )
}
