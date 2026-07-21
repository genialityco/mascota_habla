from app.schemas import PetMetadata

TRAIT_LABELS = {
    "dormilon": "dormilón/a",
    "gloton": "glotón/a",
    "dramatico": "dramático/a",
    "carinoso": "cariñoso/a",
    "travieso": "travieso/a",
    "grunon": "gruñón/a",
    "payaso": "payaso/a",
    "consentido": "consentido/a",
}


def _traits_text(traits: list[str]) -> str:
    labels = [TRAIT_LABELS.get(t, t) for t in traits]
    return ", ".join(labels) if labels else "sin rasgos particulares indicados"


def build_monologue_prompt(meta: PetMetadata) -> str:
    name = meta.pet_name.strip() or "esta mascota"
    anecdote = meta.anecdote.strip()
    anecdote_line = f'El dueño cuenta esta anécdota: "{anecdote}".' if anecdote else ""

    return f"""Mirá la foto adjunta de una mascota y escribí, en español, el monólogo
interno de la mascota sobre su humano/a.

Datos:
- Nombre: {name}
- Especie: {meta.species}
- Personalidad: {_traits_text(meta.traits)}
{anecdote_line}

Reglas:
- Primera persona, como si la mascota hablara/pensara.
- Tono tierno y humorístico a la vez, nunca cruel ni sarcástico de forma pesada.
- Basate en rasgos visibles reales de la foto (color, tamaño, expresión, entorno) y en la
  personalidad indicada para que se sienta específico, no genérico.
- Entre 60 y 100 palabras.
- Devolvé también un título corto y pegadizo (máximo 6 palabras) para la tarjeta.

Respondé exclusivamente en el formato JSON solicitado."""


def build_illustration_prompt(meta: PetMetadata) -> str:
    return f"""Generá una ilustración tierna, estilo caricatura/acuarela suave, de la mascota
de la foto adjunta. Mantené sus rasgos distintivos reales (color de pelaje o pelo,
manchas, forma de orejas, tamaño). La expresión debe transmitir personalidad
{_traits_text(meta.traits)}. Fondo simple y cálido, sin texto, sin marcas de agua,
formato cuadrado, apto para compartir en redes sociales."""
