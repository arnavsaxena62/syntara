import { Suspense } from "react";
import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted p-6">
      <Suspense fallback={<p className="text-sm text-muted-foreground">Loading sign up...</p>}>
        <SignUp />
      </Suspense>
    </div>
  );
}
