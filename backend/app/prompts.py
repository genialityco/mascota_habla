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

AGE_STAGE_LABELS = {
    "cachorro": "cachorro/a",
    "adulto": "adulto/a",
    "senior": "mayor/senior",
}

PRESENCE_LABELS = {
    "siempre": "siempre está atento/a y presente para su dueño/a",
    "a_veces": "está presente a veces, pero también tiene su espacio propio",
    "independiente": "es bastante independiente",
}

HUNGER_BEHAVIOR_LABELS = {
    "ladra_pide": "pide la comida ladrando o insistiendo sin parar",
    "espera_paciente": "espera la comida con paciencia, calladito/a",
    "sigue_por_todos_lados": "sigue a su dueño/a por todos lados hasta que le da de comer",
}

CONTRIBUTION_LABELS = {
    "paz": "paz",
    "alegria": "alegría",
    "consuelo": "consuelo",
    "compania": "compañía",
}


def _traits_text(traits: list[str]) -> str:
    labels = [TRAIT_LABELS.get(t, t) for t in traits]
    return ", ".join(labels) if labels else "sin rasgos particulares indicados"


def build_monologue_prompt(meta: PetMetadata) -> str:
    name = meta.pet_name.strip() or "esta mascota"
    owner_name = meta.owner_name.strip()
    anecdote = meta.anecdote.strip()
    anecdote_line = f'El dueño cuenta esta anécdota: "{anecdote}".' if anecdote else ""
    owner_line = (
        f'- Nombre del dueño/a: {owner_name} (dirigite a él/ella por su nombre en vez de decir '
        f'"mi humano/a" genérico)'
        if owner_name
        else ""
    )

    return f"""Mirá la foto adjunta de una mascota y escribí, en español, el monólogo
interno de la mascota sobre su humano/a.

Datos:
- Nombre: {name}
- Especie: {meta.species}
- Sexo: {meta.sexo}
- Edad: {AGE_STAGE_LABELS.get(meta.age_stage, meta.age_stage)}
- Personalidad: {_traits_text(meta.traits)}
- Vínculo con su dueño/a: {PRESENCE_LABELS.get(meta.presence, meta.presence)}
- Cuando tiene hambre: {HUNGER_BEHAVIOR_LABELS.get(meta.hunger_behavior, meta.hunger_behavior)}
- Lo que más le aporta a su dueño/a: {CONTRIBUTION_LABELS.get(meta.contribution, meta.contribution)}
{owner_line}
{anecdote_line}

Reglas:
- Primera persona, como si la mascota hablara/pensara.
- Tono tierno y humorístico a la vez, nunca cruel ni sarcástico de forma pesada.
- Basate en rasgos visibles reales de la foto (color, tamaño, expresión, entorno), en la
  personalidad y en el vínculo indicado para que se sienta específico, no genérico.
- Debe sonar breve, claro y muy expresivo, idealmente entre 20 y 40 palabras para que el audio
  dure menos de 20 segundos.
- Devolvé también un título corto y pegadizo (máximo 6 palabras) para la tarjeta.

Respondé exclusivamente en el formato JSON solicitado."""


def build_illustration_prompt(meta: PetMetadata, scene_hint: str = "", monologue: str = "") -> str:
    focus = f"\nEnfocá la escena en esta idea del monólogo: {monologue[:220]}" if monologue else ""
    scene = f"\nEscena sugerida: {scene_hint}" if scene_hint else ""

    return f"""Generá una ilustración tierna, estilo caricatura/acuarela suave, de la mascota
de la foto adjunta. Mantené sus rasgos distintivos reales (color de pelaje o pelo,
manchas, forma de orejas, tamaño). La expresión debe transmitir personalidad
{_traits_text(meta.traits)}. Fondo simple y cálido, sin texto, sin marcas de agua,
formato cuadrado, apto para compartir en redes sociales.

IMPORTANTE: NO generes una sola escena grande ni una imagen continua. Debe ser un collage
visual en cuadrícula 2x2 con cuatro paneles iguales, organizados en 2 filas y 2 columnas,
con espacio claro entre ellos. Cada panel debe representar una parte distinta del monólogo y
debe corresponder a una idea concreta del texto.
- Panel 1: inicio o introducción.
- Panel 2: emoción o giro del monólogo.
- Panel 3: momento concreto o divertido.
- Panel 4: cierre o resolución.

Usá el texto del monólogo como guía para decidir qué pasa en cada panel. No mezcles todo en
una sola escena. La composición debe verse como cuatro momentos separados, no como una única
ilustración grande. Es obligatorio que la imagen NO tenga texto, NO tenga letras, NO tenga
títulos, NO tenga bocadillos ni marcas de agua.{scene}{focus}"""
