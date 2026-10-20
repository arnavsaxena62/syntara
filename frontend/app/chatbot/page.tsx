import { Suspense } from "react"
import { auth } from "@clerk/nextjs/server"
import { ChatbotView } from "@/components/chatbot-view"

export default function ChatbotPage() {
  return (
    <Suspense fallback={<ChatbotFallback />}>
      <ProtectedChatbot />
    </Suspense>
  )
}

async function ProtectedChatbot() {
  await auth.protect()
  return <ChatbotView />
}

function ChatbotFallback() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-muted">
      <p className="text-sm text-muted-foreground">Loading your workspace...</p>
    </main>
  )
}
