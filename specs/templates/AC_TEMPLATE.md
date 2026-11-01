<!-- schema: action/1.0 -->

# Plantilla de acción derivada (AC-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar o actualizar una acción derivada en el campo `actions:` de la RFC correspondiente.
Los valores permitidos de `type` y `status` y sus transiciones se definen aquí; el actor de cada transición y su efecto sobre el cierre de la RFC están en [PROJECT_STATE.md](../PROJECT_STATE.md#transiciones-de-una-acción).
Los identificadores y relaciones siguen [RELATIONSHIPS.md](../RELATIONSHIPS.md).

## Identidad

| Campo | Formato | Ejemplo |
|---|---|---|
| ID | `AC-nnnnn` único en el proyecto | `AC-00042` |

Un identificador retirado no se reutiliza.

## Registro

El esquema de cada elemento de `actions:` se define en [RFC_TEMPLATE.md](RFC_TEMPLATE.md#acciones-derivadas); cada acción es un entregable individual bajo la RFC.

## Tipos

| Tipo | Propósito | Artefacto típico |
|---|---|---|
| `analysis` | Investigación o diagnóstico. | Documento en `analysis/`. |
| `plan` | Desglose previsto, aún sin ejecutar. | Documento en `plans/`; formato en [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md). |
| `decision` | Elección entre alternativas. | Registro en `decisions/` y ADR si aplica. |
| `implementation` | Producción de código o configuración. | Archivo en el módulo afectado. |
| `test` | Verificación automatizada o manual. | Documento `TEST-nnnnn.md` en `tests/`; formato en [TEST_TEMPLATE.md](TEST_TEMPLATE.md). |
| `evidence` | Prueba de un resultado. | Registro EVD junto al artefacto que la generó; formato en [EVIDENCE.md](../EVIDENCE.md). |
| `documentation` | Actualización de docs. | Documento afectado. |

Un `plan` representa intención; no afirma ejecución.

## Estados

| Estado | Significado |
|---|---|
| `pending` | Autorizada, sin inicio, dependencias satisfechas. |
| `blocked` | Requiere otra acción o decisión no resuelta. |
| `in-progress` | Ejecución en curso. |
| `completed` | Entregable producido y verificado localmente. |
| `cancelled` | Detenida antes de completar, con motivo registrado. |
| `superseded` | Reemplazada por otra acción identificada. |

```text
pending → in-progress → completed
pending ↔ blocked
in-progress → cancelled
completed → superseded
```

## Evidencia

Toda acción pasa a `completed` solo con al menos una evidencia referenciable: ruta de artefacto, hash de commit, salida de prueba o documento, vinculada a su RFC y a la revisión examinada.
El formato mínimo de la evidencia está en [EVIDENCE.md](../EVIDENCE.md).

## Diagrama de dependencias

```text
AC-00001 → AC-00002 → AC-00003
```

Incluir en la RFC cuando existan dependencias entre acciones de su alcance.
