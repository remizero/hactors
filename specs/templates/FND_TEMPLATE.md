<!-- schema: finding/1.0 -->

# Plantilla de hallazgo (FND-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar un hallazgo en `findings.yaml` dentro del proyecto.
El formato, tipos, severidades y transiciones se definen aquí; las reglas de operación están en [FINDINGS.md](../FINDINGS.md).
Los identificadores y relaciones siguen [RELATIONSHIPS.md](../RELATIONSHIPS.md).

## Qué es un hallazgo

Un hallazgo afirma un hecho observado: defecto, brecha, inconsistencia, riesgo o ausencia verificada.
No aprueba cambios ni reemplaza una RFC; puede derivar en una o quedar como antecedente documentado.

## Esquema YAML

Copiar como entrada en `findings.yaml` del proyecto.

```yaml
- id: FND-00001
  title: ""
  kind: ""
  severity: ""
  state: open
  source:
    workflow: ""
    task: ""
    rfc: ""
  actions: []
  affects: []
  opened: ""
  updated: ""
  resolved: null
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | `FND-nnnnn` | Identificador único; no se reutiliza al retirar. |
| `title` | texto | Descripción concisa del hecho observado. |
| `kind` | enum | Tipo de hallazgo; ver tabla de tipos. |
| `severity` | enum | Impacto; ver tabla de severidad. |
| `state` | enum | Estado actual; ver tabla de estados. |
| `source` | objeto | Contexto de origen: workflow, task y RFC. |
| `actions` | lista de `AC-nnnnn` | Acciones que tratan este hallazgo. |
| `affects` | lista de RFC-ID | RFCs impactadas sin ser fuente. |
| `opened` | `YYYY-MM-DD` | Fecha de registro. |
| `updated` | `YYYY-MM-DD` | Última modificación. |
| `resolved` | `YYYY-MM-DD` o null | Fecha de cierre terminal; null si no resuelto. |

## Tipos

| `kind` | Uso |
|---|---|
| `defect` | Comportamiento incorrecto observado. |
| `gap` | Requisito sin cubierta, contrato sin implementación. |
| `inconsistency` | Fuentes o comportamientos que discrepan. |
| `risk` | Amenaza probable sin ocurrencia actual. |
| `blocker` | Impide avanzar hasta una resolución externa. |
| `observation` | Nota relevante sin acción inmediata. |

## Severidad

| Valor | Criterio |
|---|---|
| `critical` | Detiene el WORKFLOW o expone un requisito de seguridad no cubierto. |
| `high` | Bloquea una TASK o invalida un criterio aprobado. |
| `medium` | Degrada la calidad sin impedir el avance de la TASK. |
| `low` | Detalle utilizable pero mejorable. |
| `info` | Contexto sin consecuencia práctica. |

## Estados y transiciones

| Estado | Significado |
|---|---|
| `open` | Registrado, sin acción asociada. |
| `tracked` | Una o más acciones lo tratan. |
| `resolved` | Acción completada y evidencia verificada. |
| `wont-fix` | Se decide no actuar, con motivo y autoridad humana. |
| `superseded` | Sustituido por otro hallazgo. |

```text
open → tracked → resolved
open → wont-fix
open → superseded
tracked → open   (si se retira la acción)
```

Un `critical` o `high` en estado `open` bloquea el cierre de la TASK donde se originó.

## Operación

| Acción | Actor |
|---|---|
| Registrar un hallazgo detectado. | `[actor: human \| agent]` |
| Clasificar severidad inicial. | `[actor: human \| agent]` |
| Cambiar `open` a `tracked`. | `[actor: human \| agent]` |
| Marcar `resolved`. | `[actor: human \| agent]` con evidencia. |
| Decidir `wont-fix`. | `[actor: human]`. |
| Modificar severidad tras análisis. | `[actor: human]` si afecta alcance aprobado. |

## Relación con RFC y TASK

Un hallazgo se origina dentro de un contexto identificable: workflow, task y RFC.
Si la resolución cambia un contrato vigente, se crea la RFC correspondiente; el hallazgo queda como antecedente referenciado por `supersedes` o `informs`.
Hallazgos que impactan varias RFCs se mantienen centralizados en el `findings.yaml` del proyecto; las RFCs afectadas solo los referencian por `id`.
