import { useState } from "react"
import { ArrowLeft } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import {
  TRAITS,
  type AgeStage,
  type Contribution,
  type HungerBehavior,
  type PetDetails,
  type Presence,
  type Sex,
  type Species,
} from "@/lib/types"

const SPECIES_OPTIONS: { value: Species; label: string; emoji: string }[] = [
  { value: "perro", label: "Perro", emoji: "🐶" },
  { value: "gato", label: "Gato", emoji: "🐱" },
  { value: "otro", label: "Otro", emoji: "🐾" },
]

const SEXO_OPTIONS: { value: Sex; label: string; emoji: string }[] = [
  { value: "macho", label: "Macho", emoji: "♂️" },
  { value: "hembra", label: "Hembra", emoji: "♀️" },
]

const AGE_OPTIONS: { value: AgeStage; label: string; emoji: string }[] = [
  { value: "cachorro", label: "Cachorro/a", emoji: "🐣" },
  { value: "adulto", label: "Adulto/a", emoji: "🐾" },
  { value: "senior", label: "Senior", emoji: "🦴" },
]

const PRESENCE_OPTIONS: { value: Presence; label: string }[] = [
  { value: "siempre", label: "Siempre está para mí" },
  { value: "a_veces", label: "A veces, tiene su espacio" },
  { value: "independiente", label: "Es bastante independiente" },
]

const HUNGER_OPTIONS: { value: HungerBehavior; label: string }[] = [
  { value: "ladra_pide", label: "Ladra o insiste sin parar" },
  { value: "espera_paciente", label: "Espera con paciencia" },
  { value: "sigue_por_todos_lados", label: "Me sigue a todos lados" },
]

const CONTRIBUTION_OPTIONS: { value: Contribution; label: string; emoji: string }[] = [
  { value: "paz", label: "Paz", emoji: "🕊️" },
  { value: "alegria", label: "Alegría", emoji: "🎉" },
  { value: "consuelo", label: "Consuelo", emoji: "🤗" },
  { value: "compania", label: "Compañía", emoji: "🐾" },
]

const MAX_TRAITS = 3

interface PetDetailsStepProps {
  previewUrl: string
  onBack: () => void
  onSubmit: (details: PetDetails) => void
}

export function PetDetailsStep({ previewUrl, onBack, onSubmit }: PetDetailsStepProps) {
  const [species, setSpecies] = useState<Species | "">("")
  const [sexo, setSexo] = useState<Sex | "">("")
  const [ageStage, setAgeStage] = useState<AgeStage | "">("")
  const [traits, setTraits] = useState<string[]>([])
  const [presence, setPresence] = useState<Presence | "">("")
  const [hungerBehavior, setHungerBehavior] = useState<HungerBehavior | "">("")
  const [contribution, setContribution] = useState<Contribution | "">("")
  const [petName, setPetName] = useState("")
  const [ownerName, setOwnerName] = useState("")
  const [anecdote, setAnecdote] = useState("")

  const canSubmit =
    species !== "" &&
    sexo !== "" &&
    ageStage !== "" &&
    traits.length > 0 &&
    presence !== "" &&
    hungerBehavior !== "" &&
    contribution !== ""

  function toggleTrait(key: string) {
    setTraits((prev) => {
      if (prev.includes(key)) return prev.filter((t) => t !== key)
      if (prev.length >= MAX_TRAITS) return prev
      return [...prev, key]
    })
  }

  function handleSubmit() {
    if (!canSubmit) return
    onSubmit({
      petName,
      ownerName,
      species,
      sexo,
      ageStage,
      traits,
      presence,
      hungerBehavior,
      contribution,
      anecdote,
    })
  }

  return (
    <div className="flex w-full max-w-md flex-col gap-6">
      <Button variant="ghost" size="sm" className="w-fit -ml-2" onClick={onBack}>
        <ArrowLeft className="size-4" /> Cambiar foto
      </Button>

      <div className="flex items-center gap-4">
        <img
          src={previewUrl}
          alt="Tu mascota"
          className="size-20 rounded-xl object-cover border border-border"
        />
        <div>
          <h2 className="font-display text-xl font-semibold">Contanos de ella/él</h2>
          <p className="text-sm text-muted-foreground">Son todos toques rápidos ✌️</p>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="pet-name">Nombre de la mascota (opcional)</Label>
        <Input
          id="pet-name"
          placeholder="Ej: Firulais"
          value={petName}
          onChange={(e) => setPetName(e.target.value)}
          maxLength={40}
        />
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="owner-name">Tu nombre (opcional)</Label>
        <Input
          id="owner-name"
          placeholder="Ej: Juan"
          value={ownerName}
          onChange={(e) => setOwnerName(e.target.value)}
          maxLength={40}
        />
      </div>

      <div className="flex flex-col gap-2">
        <Label>1. ¿Qué es?</Label>
        <ToggleGroup
          type="single"
          value={species}
          onValueChange={(value) => setSpecies((value as Species) || "")}
          className="justify-start gap-2"
        >
          {SPECIES_OPTIONS.map((opt) => (
            <ToggleGroupItem
              key={opt.value}
              value={opt.value}
              variant="outline"
              className="rounded-full px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
            >
              {opt.emoji} {opt.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      <div className="flex flex-col gap-2">
        <Label>2. ¿Macho o hembra?</Label>
        <ToggleGroup
          type="single"
          value={sexo}
          onValueChange={(value) => setSexo((value as Sex) || "")}
          className="justify-start gap-2"
        >
          {SEXO_OPTIONS.map((opt) => (
            <ToggleGroupItem
              key={opt.value}
              value={opt.value}
              variant="outline"
              className="rounded-full px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
            >
              {opt.emoji} {opt.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      <div className="flex flex-col gap-2">
        <Label>3. ¿Qué edad tiene?</Label>
        <ToggleGroup
          type="single"
          value={ageStage}
          onValueChange={(value) => setAgeStage((value as AgeStage) || "")}
          className="justify-start gap-2"
        >
          {AGE_OPTIONS.map((opt) => (
            <ToggleGroupItem
              key={opt.value}
              value={opt.value}
              variant="outline"
              className="rounded-full px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
            >
              {opt.emoji} {opt.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      <div className="flex flex-col gap-2">
        <Label>4. ¿Cómo es su personalidad? (hasta 3)</Label>
        <div className="flex flex-wrap gap-2">
          {TRAITS.map((trait) => {
            const selected = traits.includes(trait.key)
            return (
              <Badge
                key={trait.key}
                variant={selected ? "default" : "outline"}
                className="cursor-pointer select-none rounded-full px-3 py-1.5 text-sm"
                onClick={() => toggleTrait(trait.key)}
              >
                {trait.label}
              </Badge>
            )
          })}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <Label>5. ¿Ves que tu mascota siempre está para vos?</Label>
        <ToggleGroup
          type="single"
          value={presence}
          onValueChange={(value) => setPresence((value as Presence) || "")}
          className="flex-wrap justify-start gap-2"
        >
          {PRESENCE_OPTIONS.map((opt) => (
            <ToggleGroupItem
              key={opt.value}
              value={opt.value}
              variant="outline"
              className="rounded-full px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
            >
              {opt.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      <div className="flex flex-col gap-2">
        <Label>6. Cuando tiene hambre...</Label>
        <ToggleGroup
          type="single"
          value={hungerBehavior}
          onValueChange={(value) => setHungerBehavior((value as HungerBehavior) || "")}
          className="flex-wrap justify-start gap-2"
        >
          {HUNGER_OPTIONS.map((opt) => (
            <ToggleGroupItem
              key={opt.value}
              value={opt.value}
              variant="outline"
              className="rounded-full px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
            >
              {opt.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      <div className="flex flex-col gap-2">
        <Label>7. ¿Qué te aporta?</Label>
        <ToggleGroup
          type="single"
          value={contribution}
          onValueChange={(value) => setContribution((value as Contribution) || "")}
          className="justify-start gap-2"
        >
          {CONTRIBUTION_OPTIONS.map((opt) => (
            <ToggleGroupItem
              key={opt.value}
              value={opt.value}
              variant="outline"
              className="rounded-full px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
            >
              {opt.emoji} {opt.label}
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="anecdote">Una anécdota corta (opcional)</Label>
        <Textarea
          id="anecdote"
          placeholder="Ej: cada vez que salgo se pone triste y me espera en la ventana..."
          value={anecdote}
          onChange={(e) => setAnecdote(e.target.value.slice(0, 200))}
          rows={3}
        />
        <p className="text-right text-xs text-muted-foreground">{anecdote.length}/200</p>
      </div>

      <Button size="lg" disabled={!canSubmit} onClick={handleSubmit}>
        Dale voz a mi mascota 🐾
      </Button>
    </div>
  )
}
