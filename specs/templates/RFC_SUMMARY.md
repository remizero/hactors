<!-- schema: rfc-summary/1.0 -->

# Plantilla de resumen RFC

[actor: human | agent] redacta este resumen al cerrar una RFC-A, RFC-F, RFC-I o RFC-T.
El resumen enlaza a la RFC y sintetiza propósito, alcance, estado, decisiones y relaciones, sin redefinir requisitos.
Los campos vacíos son información por resolver, no secciones omitidas.

## Cabecera

```yaml
rfc: ""
title: ""
type: ""
status: ""
date: ""
tree: ""
sources: []
```

`rfc` identifica la RFC resumida. `date` usa `YYYY-MM-DD`.
`tree` indica la rama y revisión del árbol analizado o implementado.
`sources` lista las fuentes consultadas: RFC de origen, tests, documentos, código.

## Resumen ejecutivo

Síntesis en prosa del propósito, resultado principal y estado final.
Si la RFC produjo hallazgos, decisiones o fases, enunciarlos en una tabla o lista numerada.
No repetir el contenido de la RFC; el resumen apunta a ella.

## Propósito y alcance

Qué problema aborda la RFC y qué límites se fijó.
Incluir exclusiones deliberadas y lo que queda fuera de este cierre.

## Hallazgos o decisiones clave

Para cada hallazgo o decisión relevante:

- Identificador estable (objetivo, criterio, causa raíz, componente).
- Qué se observó o decidió.
- Naturaleza o clasificación.
- Componente o frontera afectada.

Si la RFC es de tipo análisis, agrupar por causas raíz y correlaciones.
Si la RFC es de tipo feature, agrupar por arquitectura, contratos y migración.
Si la RFC es de tipo integración, agrupar por composición, adopción y pruebas.
Si la RFC es de tipo tests, agrupar por propiedad, fixture, matriz y evidencia.

## Plan de implementación o verificación

Fases o pasos resultantes; cada uno con:

- objetivo,
- causa raíz o propiedad que aborda,
- componentes afectados,
- cambios previstos,
- contratos y compatibilidad,
- tests,
- dependencias,
- criterio de cierre.

Omitir si la RFC no produce un plan secuenciable.

## Matriz de trazabilidad

Relación entre objetivos, criterios de aceptación, evidencias y estado.
Cada fila enlaza un criterio con la evidencia que lo verifica o la razón de su ausencia.

## Riesgos

Riesgos conocidos de implementación, operación o interpretación.
Para cada riesgo: probabilidad, impacto y mitigación propuesta.

## Criterios de cierre

Condiciones verificables que permiten declarar la RFC `done`, no solo terminal.
Distinguir entre criterios satisfechos y criterios pendientes.

## Información insuficiente

Secciones donde la evidencia o el alcance no bastaron para resolver una cuestión.
Indicar qué falta y qué RFC o trabajo puede cerrarla.
Omitir si no hay cuestiones abiertas.

## Conclusión

Síntesis final: qué se logró, qué queda pendiente y qué paso sigue.
No introducir requisitos ni decisiones nuevas.

## Restricciones del resumen

- No redefinir requisitos aprobados ni alterar el contenido de la RFC.
- No declarar cerrado lo que los tests no demostraron.
- No añadir análisis, arquitectura o contratos que la RFC no contenía.
- Enlazar a la RFC y a sus derivadas cuando existan.
- Conservar los identificadores estables de objetivos y criterios para trazabilidad.
