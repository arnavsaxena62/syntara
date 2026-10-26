"use client"

import { Show, UserButton } from "@clerk/nextjs"

import { Button } from "@/components/ui/button"
import type { PracticeSession } from "../usePracticeSession"

import { AnswerEditor } from "./AnswerEditor"
import { QuestionPane } from "./QuestionPane"
import { ResultsPane } from "./ResultPane"

type PracticeWorkspaceProps = {
  session: PracticeSession
}

export function PracticeWorkspace({
  session,
}: PracticeWorkspaceProps) {
  const {
    step,
    question,
    answer,
    setAnswer,
    language,
    result,
    loading,
    error,
    checkCurrentAnswer,
    resetToPrompt,
    tryAnother,
    prompt,
    setPrompt,
    difficulty,
    setDifficulty,
    setLanguage,
    model,
    setModel,
    files,
    addFiles,
    removeFile,
    generateQuestion
  } = session

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-background">
      <header className="flex h-16 shrink-0 items-center justify-between border-b bg-background px-4 md:px-6">
        <h1 className="text-xl font-bold">Syntara</h1>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={resetToPrompt}
          >
            New Question
          </Button>

          <Show when="signed-in">
            <UserButton />
          </Show>
        </div>
      </header>

      <main className="grid min-h-0 flex-1 overflow-auto lg:grid-cols-[minmax(280px,0.8fr)_minmax(450px,1.7fr)_minmax(280px,0.8fr)] lg:overflow-hidden">
        <QuestionPane question={question} />

        <div className="flex min-h-0 flex-col">
          <AnswerEditor
            language={language}
            answer={answer}
            onAnswerChange={setAnswer}
          />

          {error && (
            <p className="px-4 pb-4 text-sm text-destructive md:px-6" role="alert">
              {error}
            </p>
          )}
        </div>

        <ResultsPane
          step={step}
          result={result}
          loading={loading}
          onCheck={checkCurrentAnswer}
          onTryAnother={tryAnother}
        />
      </main>
    </div>
  )
}