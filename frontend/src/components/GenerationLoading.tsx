import { useEffect, useState } from "react"
import { PawPrint } from "lucide-react"

import { Progress } from "@/components/ui/progress"

const MESSAGES = [
  "Traduciendo ladridos y maullidos...",
  "Puliendo el drama...",
  "Buscando la voz perfecta...",
  "Agregando una pizca de ternura...",
  "Practicando el monólogo frente al espejo...",
  "Casi listo, últimos retoques...",
]

export function GenerationLoading() {
  const [messageIndex, setMessageIndex] = useState(0)
  const [progress, setProgress] = useState(8)

  useEffect(() => {
    const messageInterval = setInterval(() => {
      setMessageIndex((i) => (i + 1) % MESSAGES.length)
    }, 2200)
    const progressInterval = setInterval(() => {
      setProgress((p) => (p < 90 ? p + Math.random() * 8 : p))
    }, 700)
    return () => {
      clearInterval(messageInterval)
      clearInterval(progressInterval)
    }
  }, [])

  return (
    <div className="flex flex-col items-center gap-6 text-center">
      <PawPrint className="size-12 animate-bounce text-primary" />
      <h2 className="font-display text-2xl font-semibold">Dándole voz a tu mascota...</h2>
      <p className="min-h-6 text-muted-foreground">{MESSAGES[messageIndex]}</p>
      <Progress value={progress} className="w-full max-w-xs" />
    </div>
  )
}
