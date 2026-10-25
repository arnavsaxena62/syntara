"use client"

import { PromptPanel } from "./promptPanel"
import { PracticeWorkspace } from "./practiceWorkspace"
import { usePracticeSession } from "../usePracticeSession"

export function ChatbotViewTest() {
  const session = usePracticeSession()

  if (session.step === "prompt") {
    return <PromptPanel session={session} />
  }

  return <PracticeWorkspace session={session} />
}