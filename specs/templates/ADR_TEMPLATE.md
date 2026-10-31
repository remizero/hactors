<!-- schema: adr/1.0 -->

# Plantilla de decisión (ADR-nnnnn)

[actor: human | agent] registra aquí una decisión que cumple los criterios de [DECISIONS.md](../DECISIONS.md#cuándo-registrar).
El contenido mínimo, los estados, la relación con una RFC y la identidad están en [DECISIONS.md](../DECISIONS.md); esta plantilla fija la forma del archivo.
Los campos vacíos son información por resolver, no secciones omitidas.

## Cabecera

```yaml
adr: ""
title: ""
status: proposed
date: ""
```

| Campo | Contenido |
|---|---|
| `adr` | `ADR-nnnnn`, único en el proyecto; lo asigna el contador `adr` del manifest del proyecto. |
| `title` | Descripción breve de la decisión. |
| `status` | Uno de los estados de [DECISIONS.md](../DECISIONS.md#estados-de-adr); una decisión nueva comienza en `proposed`. |
| `date` | `YYYY-MM-DD` del registro. |

## Cuerpo

Las secciones del cuerpo son las del contenido mínimo de [DECISIONS.md](../DECISIONS.md#contenido-mínimo-de-un-adr) que la cabecera no lleva: Contexto, Alternativas, Decisión, Consecuencias y Trazabilidad.
La trazabilidad enlaza las RFC relacionadas y la decisión sustituta, en ambos sentidos, sin copiar su contenido.

## Creación con la CLI

`hactors create-adr` escribe la cabecera como frontmatter YAML, seguido de una remisión a esta plantilla; no copia las secciones ni redacta su contenido. Asigna el identificador con el contador `adr` del manifest del proyecto, deriva el nombre del archivo de `--title` como `decisions/ADR-nnnnn — nombre-descriptivo.md`, conforme a [DECISIONS.md](../DECISIONS.md#identidad-y-ubicación), y acepta `--status` y `--date`. Los valores declarados se registran literalmente, los campos omitidos conservan los de [adr_template.yaml](adr_template.yaml) y un valor vacío explícito sustituye al de la plantilla.

El comando no redacta el contexto, las alternativas, la decisión ni sus consecuencias, y no registra la sustitución de una decisión anterior: quien la declara enlaza ambas conforme a [DECISIONS.md](../DECISIONS.md#rfc-y-adr). Tampoco la representa en `relations` del manifest del proyecto, porque la correspondencia de [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md#relaciones-del-proyecto) no traduce aún ningún campo de un ADR. Aceptar o rechazar una decisión corresponde a [actor: human] según [DECISIONS.md](../DECISIONS.md#estados-de-adr).
