import { useState } from "react"
import { Toaster } from "sonner"

import { GenerationLoading } from "@/components/GenerationLoading"
import { PetDetailsStep } from "@/components/PetDetailsStep"
import { PhotoUploadStep } from "@/components/PhotoUploadStep"
import { ResultView } from "@/components/ResultView"
import { Button } from "@/components/ui/button"
import { ApiError, generatePetVoice } from "@/lib/api"
import type { GenerateResult, PetDetails, Step } from "@/lib/types"

function App() {
  const [step, setStep] = useState<Step>("upload")
  const [photo, setPhoto] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>("")
  const [result, setResult] = useState<GenerateResult | null>(null)
  const [errorMessage, setErrorMessage] = useState("")

  function handlePhotoSelected(file: File, preview: string) {
    setPhoto(file)
    setPreviewUrl(preview)
    setStep("details")
  }

  async function handleDetailsSubmit(details: PetDetails) {
    if (!photo) return
    setStep("loading")
    try {
      const generated = await generatePetVoice(photo, details)
      setResult(generated)
      setStep("result")
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "No pudimos conectar con el servidor."
      setErrorMessage(message)
      setStep("error")
    }
  }

  function handleRestart() {
    setPhoto(null)
    setPreviewUrl("")
    setResult(null)
    setStep("upload")
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-8 bg-background px-4 py-12">
      <Toaster richColors position="top-center" />

      {step === "upload" && <PhotoUploadStep onNext={handlePhotoSelected} />}

      {step === "details" && (
        <PetDetailsStep
          previewUrl={previewUrl}
          onBack={() => setStep("upload")}
          onSubmit={handleDetailsSubmit}
        />
      )}

      {step === "loading" && <GenerationLoading />}

      {step === "result" && result && (
        <ResultView result={result} onRestart={handleRestart} />
      )}

      {step === "error" && (
        <div className="flex flex-col items-center gap-4 text-center">
          <h2 className="font-display text-xl font-semibold">Se nos escapó un gato 🙀</h2>
          <p className="max-w-sm text-muted-foreground">{errorMessage}</p>
          <Button onClick={() => setStep("details")}>Reintentar</Button>
          <Button variant="ghost" onClick={handleRestart}>
            Empezar de nuevo
          </Button>
        </div>
      )}
    </div>
  )
}

export default App
