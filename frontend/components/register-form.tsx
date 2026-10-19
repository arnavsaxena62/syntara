"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { FieldLabel } from "@/components/ui/field"

export function RegisterForm() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: ""
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("http://100.66.224.73:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      })
      const data = await res.json()
      if (res.ok && data.access_token) {
        localStorage.setItem("token", data.access_token)
        window.location.href = "/chatbot"
      } else if (data.detail) {
        setError(Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail)
      } else {
        setError("Registration failed")
      }
    } catch (err) {
      setError("Failed to connect to server")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="overflow-hidden p-0">
      <CardContent className="grid p-0 md:grid-cols-2">
        <form className="p-6 md:p-8" onSubmit={handleSubmit}>
          <div className="flex flex-col gap-4">
            {error && (
              <div>
                <span className="text-sm text-destructive">{error}</span>
              </div>
            )}
            <div>
              <FieldLabel htmlFor="username">Username</FieldLabel>
              <Input id="username" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} required />
            </div>
            <div>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input id="email" type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required />
            </div>
            <div>
              <FieldLabel htmlFor="password">Password</FieldLabel>
              <Input id="password" type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} required />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? "Registering..." : "Register"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}