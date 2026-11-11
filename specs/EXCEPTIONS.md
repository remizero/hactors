# Mecanismo formal de excepciones

## Alcance

Define el procedimiento para apartarse de una regla, una restricción o un requisito de estas especificaciones de manera controlada, justificada y temporal.

Una excepción no modifica la regla: suspende su aplicación sobre un alcance concreto durante un plazo o hasta que se cumpla una condición.

Los actores y artefactos están en [DEFINITIONS.md](DEFINITIONS.md); los estados base, en [LIFECYCLE.md](LIFECYCLE.md); la autoridad documental, en [ARTIFACTS.md](ARTIFACTS.md).

## Principios

1. **Temporalidad**: toda excepción tiene un límite temporal o una condición de retirada. No hay excepciones permanentes.
2. **Justificación**: toda excepción declara la razón técnica o de proyecto que la motiva.
3. **Alcance acotado**: toda excepción se aplica a un artefacto, una regla o una situación concreta, no a una categoría general.
4. **Autoridad humana**: solo [actor: human] puede aprobar una excepción; un agente la propone.
5. **Trazabilidad**: toda excepción queda registrada como una decisión identificable del proyecto.
6. **No propagación**: una excepción sobre un artefacto no se propaga a sus descendientes ni a sus relacionados.

## Registro

HACTORS no tiene identificador `EXC-nnnnn`, ni contador de excepciones, ni registro agregado: **una excepción es una decisión** y se registra como tal, en `decisions/ADR-nnnnn — nombre-descriptivo.md`, con el contador `adr` y `hactors create-adr`, conforme a [DECISIONS.md](DECISIONS.md). Ese documento ya exige registrar una decisión que establezca «un estándar, restricción o excepción técnica»; esta sección fija el contenido adicional que una excepción requiere.

| Contenido adicional | Qué declara |
|---|---|
| Regla excepcionada | La norma, su sección y la restricción concreta cuya aplicación se suspende. |
| Alcance | El artefacto, la situación o el conjunto de archivos al que se aplica. |
| Límite | Una fecha `YYYY-MM-DD` o una condición de retirada verificable. |
| Justificación | La razón técnica o de proyecto. |
| Consecuencias | Qué deja de comprobarse mientras esté en vigor y qué riesgo se asume. |

El contenido mínimo general del ADR sigue siendo el de [DECISIONS.md](DECISIONS.md#contenido-mínimo-de-un-adr); estos cinco puntos lo completan, no lo sustituyen.

## Estados

Una excepción usa los estados de una decisión y no introduce otros:

| Hecho de la excepción | Estado del ADR |
|---|---|
| Solicitada, pendiente de aprobación. | `proposed` |
| Aprobada y en vigor. | `accepted` |
| Solicitud descartada antes de aprobarse. | `rejected` |
| Retirada antes de su límite, o límite alcanzado. | `superseded`, por el ADR sucesor que la retira. |

El retiro y la expiración no son estados propios: los produce un ADR sucesor que declara la retirada o acredita el cumplimiento del límite, con la sustitución declarada en ambos sentidos conforme a [RELATIONSHIPS.md](RELATIONSHIPS.md#restricciones).

Una excepción que alcanza su límite sin ADR sucesor registrado sigue constando como `accepted`. Su límite sigue vigente aunque el registro vaya detrás: aplicar la regla suspendida más allá de él, o seguir amparándose en la suspensión, es un hallazgo conforme a [FINDING.md](FINDING.md), no una expiración automática.

## Transiciones

| Transición | Actor |
|---|---|
| Redactar el ADR de la excepción en `proposed`. | `[actor: human \| agent]` |
| `proposed` → `accepted`, aprobando la excepción. | `[actor: human]` |
| `proposed` → `rejected`. | `[actor: human]` |
| Registrar el ADR sucesor que retira una excepción `accepted`. | `[actor: human \| agent]` lo redacta; `[actor: human]` lo decide. |

## Lo que no puede excepcionarse

- Los principios de esta sección.
- La autoridad de cierre y la regla de consistencia entre niveles de [PROJECT_STATE.md](PROJECT_STATE.md#regla-de-consistencia-entre-niveles).
- Las etiquetas de actor de [DEFINITIONS.md](DEFINITIONS.md#actores): una excepción no convierte a `[actor: agent]` en aprobador.
- El orden de escritura y la reconciliación de [TRANSACTIONS.md](TRANSACTIONS.md).
- La reconstrucción del estado desde los artefactos persistidos: ninguna excepción autoriza a acreditarlo desde Git, desde una vista o desde un resumen.
- La exigencia de evidencia para cerrar un nivel: una excepción puede suspender una comprobación concreta, no sustituir la evidencia por una declaración de cumplimiento.

Una excepción a una regla del perfil técnico de un proyecto sigue este mismo mecanismo y se registra en el `decisions/` de ese proyecto, conforme a [STANDARDS.md](STANDARDS.md).

## Consultas mínimas

- ¿Qué excepciones están en vigor sobre un artefacto o una regla?
- ¿Qué excepciones alcanzan su límite en una fecha dada?
- ¿Quién aprobó una excepción concreta y con qué justificación?
- ¿Qué reglas acumulan excepciones y podrían necesitar su propia revisión?

No hay un registro de excepciones que consultar aparte: las dos primeras se responden recorriendo `decisions/` y leyendo el límite declarado en cada ADR, y las dos últimas exigen leer su contenido, que las vistas derivadas no proyectan, conforme a [VIEWS.md](VIEWS.md#artefactos). Una excepción recurrente sobre la misma regla es un hallazgo sobre la regla, no una razón para prorrogarla en silencio.
