<!-- schema: plan/1.0 -->

# Plantilla de Plan

[actor: human | agent] redacta un plan cuando una RFC-A produce fases de implementación, una RFC-F requiere migración secuenciada, o un trabajo necesita pasos ordenados con puntos de decisión.
El plan es un artefacto revisable; su aprobación es una decisión secuencial conforme a [DECISIONS.md](../DECISIONS.md).
Su autoridad como artefacto está en [ARTIFACTS.md](../ARTIFACTS.md).

## Identidad

```yaml
id: PLAN-nnnnn
title: ""
origin: ""
status: draft
date: ""
proposed_by: ""
```

| Campo | Descripción |
|---|---|
| `id` | `PLAN-nnnnn` único en el proyecto; no se reutiliza al retirar. |
| `title` | Descripción concisa del objetivo del plan. |
| `origin` | RFC que produce el plan; típicamente una RFC-A o RFC-F. |
| `status` | `draft`, `proposed`, `approved`, `rejected`, `superseded`, `completed`. |
| `date` | `YYYY-MM-DD` de creación o última revisión. |
| `proposed_by` | Autoría del plan; no implica aprobación. |

## Cuerpo

```yaml
context: ""
objectives: []
steps: []
decision_gates: []
advancement_criteria: []
risks: []
derived_rfcs: []
references: []
```

### Secciones

**context:** situación que motiva el plan; qué RFC o hallazgo lo origina y qué restricciones aplica.

**objectives:** objetivos del plan; cada uno con identificador estable para trazabilidad.

**steps:** pasos ordenados; cada paso especifica:

- identificador,
- descripción,
- dependencias (otros pasos que deben completarse),
- artefacto esperado,
- criterio de avance,
- RFC derivada propuesta (si aplica).

**decision_gates:** puntos donde se requiere aprobación antes de avanzar; cada uno con:

- identificador,
- qué decide,
- actor requerido,
- criterio de aprobación,
- pasos que bloquea.

**advancement_criteria:** condiciones verificables para declarar un paso completado.

**risks:** riesgos conocidos; para cada uno: probabilidad, impacto y mitigación.

**derived_rfcs:** RFCs que el plan propone derivar; cada una con tipo, propósito y relación `derives` con la RFC de origen.

**references:** fuentes consultadas: RFC, hallazgos, ADR, documentos.

## Estados

| Estado | Significado |
|---|---|
| `draft` | En redacción; no revisado. |
| `proposed` | Completo, pendiente de aprobación. |
| `approved` | Aprobado; los pasos pueden ejecutarse. |
| `rejected` | Descartado, con motivo. |
| `superseded` | Sustituido por otro plan identificado. |
| `completed` | Todos los pasos completados y verificados. |

```text
draft → proposed → approved → completed
proposed → rejected
approved → superseded
```

## Relación con decisiones

Un plan aprobado es una decisión secuencial: compromete un orden de ejecución, recursos y criterios de avance.
Los decision gates dentro del plan son puntos donde [actor: human] aprueba o redirige antes de continuar.
Si el plan cambia después de aprobado, se registra la enmienda o se crea un plan sucesor; no se altera el plan aprobado en retroactivo.

## Relación con RFC

- Una RFC-A puede producir uno o más planes; cada plan conserva su `origin` y relación `derives`.
- Un plan puede proponer RFC-F derivadas; cada RFC-F conserva su identificador y ciclo de vida independiente.
- Las acciones derivadas (AC-nnnnn) de un plan siguen la jerarquía de PROJECT_STATE.md.

## Ubicación

Los documentos PLAN se ubican en `plans/` dentro del contexto de la RFC que los produce, o en `docs/plans/` si son transversales.
Su instancia de ejecución `plan_run` vive dentro del `rfc_run` correspondiente, puede contener rfc_runs de RFCs derivadas y referencia el documento sin copiar sus pasos, gates ni aprobación. La jerarquía recursiva, su ruta activa y creación se definen en [HACTORS_SYSTEM.md](../HACTORS_SYSTEM.md).

## Restricciones

- No ejecutar pasos de un plan en estado `draft` o `rejected`.
- No saltar decision gates sin aprobación de [actor: human].
- No alterar un plan `approved` sin registrar la modificación.
- Un plan no sustituye la RFC que lo produce; la complementa con secuencia de ejecución.
