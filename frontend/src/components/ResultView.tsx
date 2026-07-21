import { useState } from "react"
import { Download, RotateCcw, Share2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { fetchAsFile } from "@/lib/image"
import type { GenerateResult } from "@/lib/types"

interface ResultViewProps {
  result: GenerateResult
  onRestart: () => void
}

export function ResultView({ result, onRestart }: ResultViewProps) {
  const [sharing, setSharing] = useState(false)

  async function handleShare(url: string, filename: string) {
    setSharing(true)
    try {
      const file = await fetchAsFile(url, filename)
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: result.title,
          text: result.monologue,
        })
        return
      }
      downloadUrl(url, filename)
    } catch (err) {
      if ((err as Error)?.name !== "AbortError") {
        toast.error("No se pudo compartir. Se descargó el archivo en su lugar.")
        downloadUrl(url, filename)
      }
    } finally {
      setSharing(false)
    }
  }

  function downloadUrl(url: string, filename: string) {
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
  }

  return (
    <div className="flex w-full max-w-md flex-col items-center gap-5 text-center">
      <h2 className="font-display text-2xl font-semibold">{result.title}</h2>

      <Tabs defaultValue="card" className="w-full">
        <TabsList className="w-full">
          <TabsTrigger value="card">Tarjeta</TabsTrigger>
          <TabsTrigger value="video">Video</TabsTrigger>
        </TabsList>

        <TabsContent value="card" className="flex flex-col items-center gap-4">
          <img
            src={result.cardUrl}
            alt={result.title}
            className="w-full rounded-xl border border-border shadow-sm"
          />
          <audio controls src={result.audioUrl} className="w-full" />
          <div className="flex w-full gap-2">
            <Button
              className="flex-1"
              variant="outline"
              onClick={() => downloadUrl(result.cardUrl, "tarjeta-mascota.png")}
            >
              <Download className="size-4" /> Descargar
            </Button>
            <Button
              className="flex-1"
              disabled={sharing}
              onClick={() => handleShare(result.cardUrl, "tarjeta-mascota.png")}
            >
              <Share2 className="size-4" /> Compartir
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="video" className="flex flex-col items-center gap-4">
          <video
            controls
            src={result.videoUrl}
            className="w-full rounded-xl border border-border shadow-sm"
          />
          <div className="flex w-full gap-2">
            <Button
              className="flex-1"
              variant="outline"
              onClick={() => downloadUrl(result.videoUrl, "video-mascota.mp4")}
            >
              <Download className="size-4" /> Descargar
            </Button>
            <Button
              className="flex-1"
              disabled={sharing}
              onClick={() => handleShare(result.videoUrl, "video-mascota.mp4")}
            >
              <Share2 className="size-4" /> Compartir
            </Button>
          </div>
        </TabsContent>
      </Tabs>

      <p className="text-sm text-muted-foreground italic">"{result.monologue}"</p>

      <Button variant="ghost" onClick={onRestart}>
        <RotateCcw className="size-4" /> Crear otra
      </Button>
    </div>
  )
}
