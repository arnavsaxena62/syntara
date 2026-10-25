"use client"

import dynamic from "next/dynamic"

import { getMonacoLanguage } from "../monaco"

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

type AnswerEditorProps = {
  language: string
  answer: string
  onAnswerChange: (answer: string) => void
}

export function AnswerEditor({
  language,
  answer,
  onAnswerChange,
}: AnswerEditorProps) {
  const monacoLanguage = getMonacoLanguage(language)

  return (
    <section className="flex min-h-0 flex-1 flex-col p-4 md:p-6">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold">Your Solution</h2>

        <span className="rounded bg-primary/10 px-2 py-0.5 font-mono text-xs text-primary">
          {monacoLanguage}
        </span>
      </div>

      <div className="min-h-0 flex-1 overflow-hidden rounded-xl border bg-[#1e1e1e] shadow-sm">
        <MonacoEditor
          height="100%"
          language={monacoLanguage}
          value={answer}
          onChange={(value) => onAnswerChange(value ?? "")}
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
    </section>
  )
}