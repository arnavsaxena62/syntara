"use client"

import { Show, UserButton } from "@clerk/nextjs"

import { Button } from "@/components/ui/button"
import type { PracticeSession } from "../usePracticeSession"
import * as FileUpload from "@/components/application/file-upload/file-upload-base"

type PromptPanelProps = {
  session: PracticeSession
}


export function PromptPanel({ session }: PromptPanelProps) {
  const {
    prompt,
    setPrompt,
    difficulty,
    setDifficulty,
    language,
    setLanguage,
    model,
    setModel,
    error,
    loading,
    generateQuestion,
    files,
    addFiles,
    removeFile,
    setFiles
  } = session

  const difficultyLabel =
    difficulty === 1 ? "Easy" : difficulty === 2 ? "Medium" : "Hard"

  const difficultyDescription =
    difficulty === 1
      ? "beginner"
      : difficulty === 2
        ? "medium"
        : "challenging"


  return (
    <main className="flex min-h-screen items-center justify-center bg-muted p-6">
      <div className="w-full max-w-2xl space-y-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">Ask a Question</h1>
            <p className="mt-2 text-muted-foreground">
              Describe a problem you want to practice and get a coding
              challenge.
            </p>
          </div>

          <Show when="signed-in">
            <UserButton />
          </Show>
        </div>

        <div className="space-y-2">
          <label htmlFor="language" className="text-sm font-medium">
            Language
          </label>

          <select
            id="language"
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            className="h-10 w-full rounded-md border bg-background px-3 text-sm"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="java">Java</option>
            <option value="csharp">C#</option>
            <option value="cpp">C++</option>
            <option value="sql">SQL</option>
            <option value="mysql">MySQL</option>
          </select>
        </div>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">Difficulty</label>

            <div className="flex items-center gap-3">
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() =>
                  setDifficulty((current) => Math.max(1, current - 1))
                }
                disabled={difficulty === 1}
                aria-label="Decrease difficulty"
              >
                −
              </Button>

              <div className="min-w-32 text-center">
                <p className="font-semibold">{difficultyLabel}</p>
                <p className="text-xs text-muted-foreground">
                  Difficulty {difficulty} of 3
                </p>
              </div>

              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() =>
                  setDifficulty((current) => Math.min(3, current + 1))
                }
                disabled={difficulty === 3}
                aria-label="Increase difficulty"
              >
                +
              </Button>
            </div>
          </div>

          <div className="w-full space-y-2 sm:w-56">
            <label htmlFor="model" className="text-sm font-medium">
              Model
            </label>

            <input
              id="model"
              value={model}
              onChange={(event) => setModel(event.target.value)}
              placeholder="recursive/flint-v1.0:free"
              className="h-10 w-full rounded-md border bg-background px-3 text-sm"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="prompt" className="text-sm font-medium">
            What would you like to practice?
          </label>

          <textarea
            id="prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            className="h-40 min-h-40 w-full resize-none rounded-lg border bg-background p-4"
            placeholder={`Example: Give me a ${difficultyDescription} ${language} problem about dictionaries and arrays...`}
          />
        </div>

        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}

        <Button
          onClick={generateQuestion}
          disabled={loading}
          className="w-full py-2"
        >
          {loading ? "Generating..." : `Generate ${difficultyLabel} Question`}
        </Button>
      </div>
    </main>
  )
}