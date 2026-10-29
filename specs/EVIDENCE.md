# Evidencia.

Una evidencia es un registro verificable que respalda una afirmación observada: el resultado de una prueba, un artefacto producido, un documento o una observación directa.

Una evidencia afirma un hecho observado; no interpreta, no aprueba cambios y no sustituye una decisión.

## Mínimos de una evidencia.

1. Ser referenciable: ruta de artefacto, hash de commit, salida de prueba o documento.
2. Identificar su procedencia y la revisión examinada, sin confundir el contexto de origen con su aplicabilidad.
3. Declarar mediante relaciones qué criterios, objetivos o afirmaciones de otros artefactos respalda, referenciándolos sin redefinirlos; puede respaldar varios destinos sin cambiar su origen.
4. Cuando proviene de un harness, quedar vinculada a la versión concreta del harness (HRN) y a su ejecución, conforme a la regla de aislamiento de [HARNESS.md](HARNESS.md).
5. Bastarse a sí misma: la evidencia conserva el contexto completo de la observación (plataforma, comandos, retornos) y no depende de la existencia posterior del harness que la produjo.

La inexistencia del harness construido no contradice los resultados, evidencias o hallazgos derivados de él: la receta del harness y el registro de la evidencia conservan todo el contexto de la ejecución.

## Ubicación.

La evidencia se registra directamente en el directorio del artefacto que la generó. No existe un directorio central de evidencias.

## Esquema.

El formato, los campos y los tipos de evidencia se definen en [templates/EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md).

## Relación con otros artefactos.

- Una TASK referencia evidencias en `execution.evidence`.
- Una acción derivada solo pasa a `completed` con al menos una evidencia referenciable, conforme a [templates/AC_TEMPLATE.md](templates/AC_TEMPLATE.md).
- Un hallazgo solo pasa a `resolved` con evidencia verificada, conforme a [templates/FND_TEMPLATE.md](templates/FND_TEMPLATE.md).
- Un workflow_run registra referencias de verificación en `integration.verification_refs`, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md).
