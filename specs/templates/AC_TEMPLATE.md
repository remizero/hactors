<!-- schema: action/1.0 -->

# Plantilla de acción derivada (AC-nnnnn)

[actor: human | agent] utiliza esta plantilla al registrar o actualizar una acción derivada dentro del `CONTEXT.md` de una RFC.
El formato y los valores permitidos se definen aquí; las reglas de transición y propiedad están en [PROJECT_STATE.md](../PROJECT_STATE.md).
Los identificadores y relaciones siguen [RELATIONSHIPS.md](../RELATIONSHIPS.md).

## Identidad

| Campo | Formato | Ejemplo |
|---|---|---|
| ID | `AC-nnnnn` único en el proyecto | `AC-00042` |

Un identificador retirado no se reutiliza.

## Tabla de acciones

Copiar dentro de la sección «Acciones derivadas» del `CONTEXT.md` de la RFC.

| ID | Tipo | Estado | Depende de | Artefacto | Evidencia |
|---|---|---|---|---|---|
| AC-00000 | _ver tipos abajo_ | pending | — | | |

Cada fila es un entregable individual bajo la RFC.

## Tipos

| Tipo | Propósito | Artefacto típico |
|---|---|---|
| `analysis` | Investigación o diagnóstico. | Documento en `analysis/`. |
| `plan` | Desglose previsto, aún sin ejecutar. | Documento en `plans/`; formato en [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md). |
| `decision` | Elección entre alternativas. | Registro en `decisions/` y ADR si aplica. |
| `implementation` | Producción de código o configuración. | Archivo en el módulo afectado. |
| `test` | Verificación automatizada o manual. | Resultado en `tests/`. |
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

Incluir en el `CONTEXT.md` cuando existan dependencias entre acciones de la misma RFC.
