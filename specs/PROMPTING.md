# Instrucciones para agentes

## Alcance

[actor: human | agent] usa esta estructura al preparar instrucciones de trabajo para un agente.
Una instrucción puede expresar una TASK directamente, pero no sustituye las decisiones que requieren aprobación de [actor: human].
Las obligaciones particulares del ejecutor están en [AI.md](AI.md); el contenido de una TASK, en [templates/TASK_TEMPLATE.md](templates/TASK_TEMPLATE.md).

## Estructura

| Sección | Información necesaria |
|---|---|
| Rol | Responsabilidad y especialidad requeridas, sin conceder autoridad adicional. |
| Contexto | TASK, RFC, contratos, archivos y entrada a [CONTEXT_LOADING.md](CONTEXT_LOADING.md). |
| Restricciones | Alcance autorizado, exclusiones y referencias a las normas aplicables. |
| Trabajo | Acciones, entregables y dependencias en el orden necesario. |
| Salida y verificación | Archivos o formato de entrega, criterios y evidencia requerida. |

Referenciar las reglas en lugar de copiarlas en cada instrucción: una norma copiada se desincroniza de su fuente.
Distinguir entradas obligatorias, contexto informativo y datos que todavía requieren una decisión.
Especificar el idioma y el formato del entregable conforme a su contrato, no a supuestos sobre el idioma del agente; el idioma de la documentación se declara en [DOCUMENTATION.md](DOCUMENTATION.md#idioma).
La política de selección y reutilización de contexto pertenece a [CONTEXT_LOADING.md](CONTEXT_LOADING.md#reutilización-del-contexto), no a la instrucción.

## Aplicación por tipo de trabajo

| Trabajo | Entradas específicas | Resultado esperado |
|---|---|---|
| Implementación | Contrato público aprobado y módulos afectados. | Código conforme al contrato y a los estándares que el proyecto active, conforme a [STANDARDS.md](STANDARDS.md). |
| Documentación | Contratos y código pertinentes, con evidencia de su estado. | Actualización de las capas definidas en [DOCUMENTATION.md](DOCUMENTATION.md#capas). |
| Pruebas | Criterios, interfaces y escenarios de error. | Pruebas y evidencia conforme a [TESTS.md](TESTS.md) y [EVIDENCE.md](EVIDENCE.md). |
| Análisis | Pregunta, alcance, fuentes y límites de la investigación. | Conclusiones trazables, distinguiendo hechos, inferencias y propuestas. |

Un análisis produce conclusiones, no cambios: si sus recomendaciones requieren implementarse, eso es un trabajo posterior con su propia autorización.
Los nombres de bibliotecas, versiones y reglas técnicas proceden de los perfiles que componga el proyecto, no de esta norma.
