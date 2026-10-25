import { Suspense } from "react"
import { auth } from "@clerk/nextjs/server"
import { ChatbotViewTest } from "@/components/chatbot/components/chatbotView"

export default function ChatbotPage() {
  return (
    <Suspense fallback={<ChatbotFallback />}>
      <ProtectedChatbot />
    </Suspense>
  )
}

async function ProtectedChatbot() {
  await auth.protect()
  return <ChatbotViewTest />
}

function ChatbotFallback() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-muted">
      <p className="text-sm text-muted-foreground">Loading your workspace...</p>
    </main>
  )
}
