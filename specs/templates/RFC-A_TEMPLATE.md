<!-- schema: rfc/1.0 -->

# Plantilla RFC-A — Análisis

[actor: human | agent] completa esta plantilla siguiendo [RFC.md](../RFC.md).
Los campos vacíos son información por resolver, no criterios satisfechos.
Los estados y autorizaciones proceden de [LIFECYCLE.md](../LIFECYCLE.md).

## Metadatos y cuerpo común

Completar los metadatos y el cuerpo común conforme a [RFC_TEMPLATE.md](RFC_TEMPLATE.md).
`type` debe ser `"A"` (Análisis).
Esta plantilla añade únicamente las secciones específicas del tipo.

## Campos específicos

```yaml
analysis_scope: ""
data_sources: []
methodology: ""
root_causes: []
implementation_plan:
  phases: []
```

### Secciones específicas de análisis

**analysis_scope:** límites del análisis; qué componentes, contratos o comportamientos se examinan.

**data_sources:** fuentes de información: tests, documentos, código, métricas, hallazgos previos.

**methodology:** enfoque de análisis: reconstrucción de hechos, trazabilidad, correlación, alternativas.

**root_causes:** causas raíz identificadas; cada una con evidencia y componente afectado.

**implementation_plan.phases:** plan de implementación dividido en fases; si el plan requiere secuencia con puntos de decisión, formalizarlo como PLAN conforme a [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md). Cada fase especifica:
- objetivo,
- causa raíz que aborda,
- componentes afectados,
- cambio arquitectónico,
- cambio de implementación,
- enforcement,
- contratos,
- compatibilidad,
- tests,
- dependencias,
- criterio de cierre.

## Restricciones

- NO modificar código de producción.
- NO modificar tests.
- NO crear commits de implementación.
- NO ejecutar una implementación parcial de las soluciones.
- Mantener separación entre diagnóstico, diseño de solución e implementación.
- Si existe información insuficiente para determinar una causa raíz, indicarlo explícitamente en lugar de inferirla.

## Resumen y continuidad

Al completar el análisis, [actor: human | agent] redacta un resumen conforme a [SUMMARY_TEMPLATE.md](SUMMARY_TEMPLATE.md).
El resumen sintetiza causas raíz, plan de implementación y fases propuestas.
Las fases del plan pueden derivar en RFC-F (implementación) independientes; cada una conserva su identificador y relación `derives` con esta RFC-A.
