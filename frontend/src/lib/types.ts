export type Species = "perro" | "gato" | "otro"
export type Sex = "macho" | "hembra"
export type AgeStage = "cachorro" | "adulto" | "senior"
export type Presence = "siempre" | "a_veces" | "independiente"
export type HungerBehavior = "ladra_pide" | "espera_paciente" | "sigue_por_todos_lados"
export type Contribution = "paz" | "alegria" | "consuelo" | "compania"

export interface Trait {
  key: string
  label: string
}

export const TRAITS: Trait[] = [
  { key: "dormilon", label: "Dormilón" },
  { key: "gloton", label: "Glotón" },
  { key: "dramatico", label: "Dramático" },
  { key: "carinoso", label: "Cariñoso" },
  { key: "travieso", label: "Travieso" },
  { key: "grunon", label: "Gruñón" },
  { key: "payaso", label: "Payaso" },
  { key: "consentido", label: "Consentido" },
]

export interface PetDetails {
  petName: string
  ownerName: string
  species: Species
  sexo: Sex
  ageStage: AgeStage
  traits: string[]
  presence: Presence
  hungerBehavior: HungerBehavior
  contribution: Contribution
  anecdote: string
}

export interface GenerateResult {
  id: string
  title: string
  monologue: string
  illustrationUrl: string
  cardUrl: string
  audioUrl: string
  videoUrl: string
}

export type Step = "upload" | "details" | "loading" | "result" | "error"
