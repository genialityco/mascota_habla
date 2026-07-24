import type { GenerateResult, PetDetails } from "@/lib/types"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

export class ApiError extends Error {}

export async function generatePetVoice(photo: File, details: PetDetails): Promise<GenerateResult> {
  const form = new FormData()
  form.append("photo", photo)
  form.append("pet_name", details.petName)
  form.append("owner_name", details.ownerName)
  form.append("species", details.species)
  form.append("sexo", details.sexo)
  form.append("age_stage", details.ageStage)
  form.append("traits", details.traits.join(","))
  form.append("presence", details.presence)
  form.append("hunger_behavior", details.hungerBehavior)
  form.append("contribution", details.contribution)
  form.append("anecdote", details.anecdote)

  const response = await fetch(`${API_BASE_URL}/api/generate`, {
    method: "POST",
    body: form,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(body?.detail ?? "Algo salió mal generando la voz de tu mascota.")
  }

  const data = await response.json()
  return {
    id: data.id,
    title: data.title,
    monologue: data.monologue,
    illustrationUrl: `${API_BASE_URL}${data.illustration_url}`,
    cardUrl: `${API_BASE_URL}${data.card_url}`,
    audioUrl: `${API_BASE_URL}${data.audio_url}`,
    videoUrl: `${API_BASE_URL}${data.video_url}`,
  }
}
