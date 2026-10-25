type QuestionPaneProps = {
  question: string
}

export function QuestionPane({ question }: QuestionPaneProps) {
  return (
    <aside className="border-b border-border bg-background lg:overflow-y-auto lg:border-b-0 lg:border-r">
      <div className="p-5 md:p-6">
        <h2 className="mb-3 text-sm font-semibold">Question</h2>

        <article className="whitespace-pre-wrap text-sm leading-7">
          {question}
        </article>
      </div>
    </aside>
  )
}