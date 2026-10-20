import { Suspense } from "react";
import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted p-6">
      <Suspense fallback={<p className="text-sm text-muted-foreground">Loading sign in...</p>}>
        <SignIn />
      </Suspense>
    </div>
  );
}
