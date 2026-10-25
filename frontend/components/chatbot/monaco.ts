export function getMonacoLanguage(language: string): string {
  const languageMap: Record<string, string> = {
    python: "python",
    javascript: "javascript",
    typescript: "typescript",
    java: "java",
    csharp: "csharp",
    cpp: "cpp",
    sql: "sql",
    mysql: "sql",
  }

  return languageMap[language.toLowerCase()] ?? "plaintext"
}