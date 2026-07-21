import { useRef, useState } from "react"
import { ImagePlus, PawPrint } from "lucide-react"

import { Button } from "@/components/ui/button"
import { downscaleImage } from "@/lib/image"

interface PhotoUploadStepProps {
  onNext: (file: File, previewUrl: string) => void
}

export function PhotoUploadStep({ onNext }: PhotoUploadStepProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleFile(file: File | undefined) {
    if (!file) return
    if (!file.type.startsWith("image/")) {
      setError("Subí una imagen en formato JPG, PNG o WEBP.")
      return
    }
    setError(null)
    setIsProcessing(true)
    try {
      const processed = await downscaleImage(file)
      const previewUrl = URL.createObjectURL(processed)
      onNext(processed, previewUrl)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="flex flex-col items-center gap-6 text-center">
      <div className="flex items-center gap-2 text-primary">
        <PawPrint className="size-8" />
        <h1 className="text-3xl font-display font-semibold">¿Qué piensa tu mascota?</h1>
      </div>
      <p className="max-w-md text-muted-foreground">
        Subí una foto de tu mascota y contanos cómo es. La IA le va a dar voz con
        mucha ternura (y algo de humor).
      </p>

      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setIsDragging(false)
          void handleFile(e.dataTransfer.files[0])
        }}
        className={`flex w-full max-w-sm cursor-pointer flex-col items-center gap-3 rounded-xl border-2 border-dashed p-10 transition-colors ${
          isDragging ? "border-primary bg-primary/5" : "border-border bg-card"
        }`}
      >
        <ImagePlus className="size-10 text-primary" />
        <p className="font-medium">
          {isProcessing ? "Procesando foto..." : "Arrastrá una foto o tocá para elegir"}
        </p>
        <p className="text-xs text-muted-foreground">JPG, PNG o WEBP · hasta 8MB</p>
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => void handleFile(e.target.files?.[0])}
      />

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Button variant="ghost" onClick={() => inputRef.current?.click()} disabled={isProcessing}>
        Elegir archivo
      </Button>
    </div>
  )
}
