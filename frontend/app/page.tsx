import { Suspense, type ReactNode } from "react"
import { redirect } from "next/navigation"
import { auth } from "@clerk/nextjs/server"

export default function Home() {
  return (
    <Suspense fallback={null}>
      <HomeRedirect />
    </Suspense>
  )
}

async function HomeRedirect(): Promise<ReactNode> {
  const { isAuthenticated } = await auth()
  redirect(isAuthenticated ? "/chatbot" : "/sign-in")
}
