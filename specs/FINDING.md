# Hallazgo.

Un hallazgo es un hecho observado que requiere tratamiento: un defecto, una brecha, una inconsistencia, un riesgo o una ausencia verificada.

Un hallazgo afirma lo observado; no interpreta, no aprueba cambios y no sustituye una decisión ni una RFC. Puede derivar en una RFC o quedar como antecedente documentado.

## Mínimos de un hallazgo.

1. Ser identificable: `FND-nnnnn` único en el proyecto, que no se reutiliza al retirar el hallazgo.
2. Identificar su procedencia —la actividad, ejecución o fuente donde se detectó— sin confundirla con los artefactos afectados ni atribuirle por sí sola la causa del defecto.
3. Declarar mediante relaciones qué artefactos están afectados, referenciándolos sin redefinirlos; identificar nuevos afectados no cambia el origen ni crea copias del hallazgo.
4. Registrar su tipo, su severidad y su estado, y conservar la entrada con un estado terminal cuando se retira.
5. Resolverlo solo con al menos una evidencia verificada que lo respalde, conforme a [EVIDENCE.md](EVIDENCE.md).

## Ubicación.

El hallazgo se registra en un único `findings.yaml` en la raíz del proyecto, como entrada de una lista. No hay un archivo por hallazgo ni registros repartidos entre directorios: los hallazgos que impactan varios artefactos se mantienen centralizados y los afectados solo los referencian por `id`.

Ese archivo es una representación consultable derivada de las observaciones; su autoridad proviene de la fuente documentada. La procedencia conserva la ruta completa del origen: cuando es una ejecución, `source.execution` guarda todos sus ancestros; cuando es otro artefacto del proyecto, `source.artifact` registra literalmente la ruta declarada. La numeración es única en el proyecto.

`hactors create-finding` añade la entrada con el ID y la procedencia: `--origin <ruta>` declara el origen y, si se omite, el origen es la instancia activa. El archivo se escribe siempre en la raíz del proyecto activo, cualquiera que sea el origen. Las reglas del origen admitido y de los valores que no rellena se describen en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#14-registro-de-hallazgos-desde-cualquier-origen).

## Esquema.

El formato, los campos, los tipos, las severidades, los estados y las transiciones se definen en [templates/FND_TEMPLATE.md](templates/FND_TEMPLATE.md).

## Relación con RFC y TASK.

El contexto de origen se obtiene de `source`, no de la lista de afectados. La TASK de origen se recupera siguiendo `source.execution` hasta el workflow_run y su `identity.task_ref`; cuando exista una TASK de origen que no pueda recuperarse allí, se declara en `source.task`. Las relaciones de afectación no sustituyen esa TASK ni cambian la regla de bloqueo: un hallazgo `critical` o `high` en estado `open` bloquea el cierre de la TASK donde se originó.

Si la resolución cambia un contrato vigente, se crea la RFC correspondiente; el hallazgo queda como antecedente referenciado por `supersedes` o `informs`.

Las evidencias que sustentan un hallazgo lo referencian mediante `supports`, conforme a [templates/EVD_TEMPLATE.md](templates/EVD_TEMPLATE.md); ese respaldo no se confunde con la procedencia ni con la afectación.

## Operación.

| Acción | Actor |
|---|---|
| Registrar un hallazgo detectado. | `[actor: human \| agent]` |
| Clasificar la severidad inicial. | `[actor: human \| agent]` |
| Cambiar `open` a `tracked`. | `[actor: human \| agent]` |
| Marcar `resolved`. | `[actor: human \| agent]` con evidencia. |
| Decidir `wont-fix`. | `[actor: human]`. |
| Modificar la severidad tras análisis. | `[actor: human]` si afecta el alcance aprobado. |

## Consultas mínimas.

[actor: human | agent] debe poder responder desde el registro:

- ¿Qué hallazgos abiertos afectan a mi TASK o a mi RFC?
- ¿Qué acciones tratan cada hallazgo y en qué estado están?
- ¿Qué hallazgos bloquean el cierre de una TASK o de una RFC?
- ¿Qué decisiones `wont-fix` existen y con qué justificación?
