import { Button } from "@/components/ui/button"
import type { CheckResult, Step } from "../practice"

type ResultsPaneProps = {
  step: Step
  result: CheckResult | null
  loading: boolean
  onCheck: () => void
  onTryAnother: () => void
}

export function ResultsPane({
  step,
  result,
  loading,
  onCheck,
  onTryAnother
}: ResultsPaneProps) {
  return (
    <aside className="border-t border-border bg-background lg:overflow-y-auto lg:border-l lg:border-t-0">
      <div className="p-5 md:p-6">
        <h2 className="mb-3 text-sm font-semibold">Results</h2>

        {step === "question" && (
          <div className="rounded-xl border border-dashed p-8 text-center">
            <p className="text-sm font-medium">Ready when you are</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Submit your solution for review.
            </p>

            <Button
              onClick={onCheck}
              disabled={loading}
              className="mt-4 w-full py-2"
            >
              {loading ? "Reviewing..." : "Check Answer"}
            </Button>
          </div>
        )}

        {step === "result" && result && (
          <div className="space-y-4">
            <div
              className={`rounded-xl border p-4 ${
                result.correct
                  ? "border-emerald-500/30 bg-emerald-500/10"
                  : "border-destructive/30 bg-destructive/10"
              }`}
            >
              <p className="font-bold">
                {result.correct ? "Correct" : "Needs improvement"}
              </p>

              <p className="text-xs text-muted-foreground">
                Score: {result.score}/100
              </p>

              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {result.remarks}
              </p>
            </div>

            <Button onClick={onCheck} disabled={loading} className="w-full">
              {loading ? "Reviewing..." : "Recheck Answer"}
            </Button>

            <Button onClick={onTryAnother} className="w-full">
              Try Another
            </Button>
          </div>
        )}
      </div>
    </aside>
  )
}