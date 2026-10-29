<!-- schema: task/1.0 -->

# Plantilla de TASK

[actor: human | agent] delimita una unidad de ejecución sin redefinir el diseño de sus RFC.
La semántica de actores está en [GLOSSARY.md](specs/GLOSSARY.md) y los estados en [LIFECYCLE.md](specs/LIFECYCLE.md).
El ejemplo parte de redacción humana en `draft`; una propuesta nueva de agente comienza en `proposed`.
Crear una TASK directamente en `approved` solo es válido cuando su alcance ya está autorizado conforme al ciclo de vida.

```yaml
task: ""
rfcs: []
required_knowledge:
  index: specs/INDEX_SPECS.md
  from_affected_modules: []
  additional: []
actor: ""
deliverables: []
acceptance_criteria:
  scope: full
  criteria: []
execution:
  status: draft
  target_status: done
  evidence: []
  blockers: []
```

## Cumplimentación

- `task`: descripción breve en imperativo.
- `rfcs`: identidades de las RFC cuyo alcance se ejecuta; una tarea de propuesta inicial puede no tenerlas aún.
- `required_knowledge`: índice y fuentes pertinentes; derivar módulos de las RFC, sin duplicar la lista de normas obligatorias.
- `actor`: ejecutor autorizado; la combinación de actores permitidos se expresa conforme al glosario.
- `deliverables`: resultados concretos de esta unidad de trabajo.
- `scope: full`: referenciar los criterios de la RFC, sin copiarlos.
- `scope: partial`: referenciar únicamente los identificadores de criterios cubiertos por esta TASK.
- `execution.status`: hecho observado, no resultado deseado; `target_status` expresa el objetivo.
- `evidence`: referencias a registros con los mínimos de [EVIDENCE.md](../EVIDENCE.md).
- `blockers`: condiciones que impiden avanzar, sin convertirlas en aprobaciones implícitas.

Una tarea parcial no puede reducir ni reinterpretar los criterios originales.
Si un criterio necesita dividirse, acordar esa división en su fuente antes de declarar cobertura parcial.
Una TASK no puede ser cerrada hasta que sus RFCs no hayan cerrado. La integración no puede garantizarse automáticamente, dado que quedan decisiones pendientes del humano.
Actualizar el índice de conocimiento al instalar SPECS fuera de esta copia.
