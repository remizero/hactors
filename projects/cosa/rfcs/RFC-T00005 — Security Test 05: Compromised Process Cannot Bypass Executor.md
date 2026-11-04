```yaml
rfc: RFC-T00005
title: 'Security Test 05: Compromised Process Cannot Bypass Executor'
type: T
scope: >-
  La frontera entre un proceso COSA comprometido y el Executor; atraviesa kernel, libs/process,
  libs/core y libs/sal/linux, así que vive en rfcs/ de la raíz del proyecto.
status: tested
date: '2026-09-15'
proposed_by: agent
origin: null
supersedes: null
superseded_by: null
depends_on: []
affected_modules:
- kernel
- libs/process
- libs/core
- libs/sal/linux
- tests
relations:
- target: RFC-A00001
  relation: informs
```

# RFC-T00005 — Security Test 05: Compromised Process Cannot Bypass Executor

Estructura y campos: `specs/templates/RFC_TEMPLATE.md` y `specs/templates/RFC-T_TEMPLATE.md`.
Convenciones de identidad y relaciones: `specs/RFC.md`; estados y transiciones: `specs/LIFECYCLE.md`.

Registro en HACTORS del documento real `docs/analisis/tests/RFC-T005 — Security Test 05: Compromised
Process Cannot Bypass Executor.md` del repositorio COSA. La identidad pasa de tres a cinco cifras
conforme a `specs/RFC.md#identidad-y-tipos`; el número real se conserva para no romper la
correspondencia con el análisis que la consume. `relations` declara la arista `informs` hacia
`RFC-A00001` que esa RFC no puede declarar por sí misma, porque en la lista de un documento el
origen es implícito. `date` es la fecha observable del archivo fuente.

## Cuerpo común

```yaml
context: >-
  El modelo de seguridad de COSA declara que la ejecución efectiva de una operación pasa por el
  Executor. RFC-T005 encarga comprobar esa propiedad en el peor caso razonable: un proceso que
  forma parte del runtime ha sido comprometido y puede generar solicitudes arbitrarias.
problem_statement: >-
  No estaba demostrado que un proceso comprometido no pueda convertir su capacidad de emitir
  solicitudes arbitrarias en una ejecución efectiva que evite el Executor. Sin esa medición, la
  prohibición declarada en el mapa de fronteras de docs/security.md es documental, no estructural.
goals:
- G1 — Auditar los tests existentes de Executor, aislamiento de proceso, autorización y capabilities antes de escribir código, y reutilizar o extender en lugar de duplicar.
- G2 — Representar un proceso comprometido capaz de formular una solicitud arbitraria y de intentar rutas alternativas reales hacia la ejecución.
- 'G3 — Medir la frontera completa, no solo el rechazo de la solicitud: Executor alcanzado, ejecución realizada, recurso protegido y efectos laterales.'
- G4 — Incluir un control positivo que demuestre que un proceso autorizado sigue ejecutando por el flujo legítimo.
- G5 — Producir evidencia reproducible y aislada, sin red, sin servicios externos y sin LLM.
- G6 — Conservar un bypass observado como hallazgo de seguridad en lugar de modificar el test para obtener PASS.
non_goals:
- Demostrar que un proceso comprometido no puede existir, ni hacer una prueba de escalada de privilegios del sistema operativo.
- Implementar mecanismos de seguridad, sandbox, autenticación o autorización nuevos.
- Mitigaciones del sistema operativo, fuzzing general, explotación del kernel Linux, pruebas de red o pruebas con un LLM real.
- Cubrir otros threats de la matriz; esta RFC prueba una propiedad concreta.
- 'Corregir el defecto productivo que se encuentre: se informa y se deriva a su RFC de corrección.'
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional:
  - specs/RFC.md
  - specs/TESTS.md
  - specs/EVIDENCE.md
  - specs/FINDING.md
proposed_architecture: >-
  No aplicable a una RFC de tests: no se propone arquitectura ni se modifica la existente. La
  arquitectura que la propiedad atraviesa se describe en el modelo de amenaza y en el flujo
  Process → Identity → Policy → Capability → Executor → Sandbox → Host.
abi_api_contracts: >-
  No aplicable: esta RFC no crea ni modifica contratos. Consume las superficies productivas reales
  de COSA y prohíbe sustituir el sistema operativo o la autoridad por mocks en la evidencia final.
new_module: null
ownership_changes: >-
  Ninguno. El test observa superficies cuyo dueño no cambia; la corrección del defecto que se
  encuentre pertenece al componente que posee la frontera, no a esta RFC.
dependency_rules: >-
  No aplicable: no se alteran las reglas de dependencia entre módulos. El test depende de las
  abstracciones reales de COSA y no crea una infraestructura paralela de autorización ni de
  ejecución.
actions: []
migration_plan: >-
  No aplicable: no hay migración de datos ni de esquema.
benefits:
  architectural: >-
    Convierte la arista prohibida «proceso comprometido → recurso del anfitrión» en una arista
    medida, y localiza el componente que realmente la permite.
  engineering: >-
    Reutiliza la infraestructura de tests existente y se ejecuta de forma aislada con CTest, sin
    runner global nuevo.
  ai: >-
    La propiedad, los estímulos y el criterio de fallo quedan decidibles, así que un ejecutor
    automatizado puede reproducir la medición sin reinterpretar el objetivo.
risks:
- id: R1
  risk: Que el test se modifique para obtener PASS tras observar un bypass real.
  mitigation: El criterio de fallo es explícito y el comportamiento vulnerable se conserva como evidencia del hallazgo.
- id: R2
  risk: Que la instrumentación disponible no permita afirmar si el Executor fue alcanzado.
  mitigation: 'Inspeccionar la arquitectura antes de elegir entre «Executor reached: NO» y «Executor reached: YES con autorización denegada»; no asumir una variante.'
- id: R3
  risk: Que el escenario no represente un atacante capaz, y el test demuestre solo que nadie puede ejecutar nada.
  mitigation: Verificar que el proceso comprometido puede generar la solicitud arbitraria e incluir el control positivo.
alternatives_considered:
- id: A1
  alternative: Comprobar únicamente que la solicitud arbitraria es rechazada.
  rejection: 'Insuficiente: no distingue un rechazo de la ausencia de ruta alternativa, que es lo que la propiedad afirma.'
- id: A2
  alternative: Crear una infraestructura paralela de autorización para el test.
  rejection: 'Prohibida por la plantilla de tipo: no se probaría el sistema real y se duplicarían tests de seguridad existentes.'
- id: A3
  alternative: Asumir privilegios administrativos del sistema operativo en el atacante.
  rejection: Fuera del modelo de amenaza; convertiría la medición en una prueba de escalada de privilegios del kernel.
consequences: >-
  Un FAIL de esta RFC es un hallazgo de seguridad con deuda arquitectónica, no un defecto del test.
  Su resultado alimenta el análisis que clasifica la naturaleza del fallo y decide qué componente
  debe corregirlo.
documentation_impact: >-
  El resultado obliga a re-anclar la documentación de seguridad si la arista prohibida deja de
  existir, y a actualizar el addendum del test cuando la deuda se cierre.
testing: >-
  Esta RFC es el encargo de un test, no de una implementación. Su comprobación es la ejecución
  aislada y repetible del test que encarga, con la evidencia de ataque y resultado en su salida.
acceptance_criteria:
- id: C1
  condition: Se auditó el repositorio antes de crear código y se reutilizó o extendió un test existente cuando ya cubría parcial o totalmente el escenario.
  covers: [G1]
  verification: El registro de la auditoría previa y la ausencia de tests de seguridad duplicados.
- id: C2
  condition: El test representa un proceso comprometido que puede generar una solicitud arbitraria evaluada por los mecanismos reales de COSA.
  covers: [G2]
  verification: El fixture y los estímulos declarados en los campos específicos, sin comprobación especial dentro del test.
- id: C3
  condition: Se verifica específicamente la frontera del Executor y se demuestra que no existe ejecución arbitraria mediante bypass.
  covers: [G3]
  verification: El bloque de evidencia con «Executor reached», «Execution performed» y el estado del recurso protegido.
- id: C4
  condition: No se produce ningún efecto lateral no autorizado y el recurso controlado queda intacto.
  covers: [G3]
  verification: La comprobación de efectos sobre contenido, inventario y archivos creados.
- id: C5
  condition: Existe un control positivo, cuando la arquitectura lo permite, que ejecuta por el flujo legítimo.
  covers: [G4]
  verification: El caso autorizado con su efecto esperado y sus registros ordenados.
- id: C6
  condition: El test es determinista, repetible, autocontenido y ejecutable de forma aislada, sin red, sin servicios externos y sin LLM.
  covers: [G5]
  verification: El comando literal de ejecución aislada y las repeticiones con orden aleatorio y semilla fija.
- id: C7
  condition: La salida proporciona evidencia suficiente del ataque y de su resultado.
  covers: [G5]
  verification: El bloque estructurado de evidencia de seguridad con cada observación y su veredicto.
- id: C8
  condition: Si se encuentra un bypass, se registra como hallazgo de seguridad en lugar de ocultarlo modificando el test.
  covers: [G6]
  verification: El registro FND asociado a la ejecución, con su severidad y su estado.
references:
- path: 'docs/analisis/tests/RFC-T005 — Security Test 05: Compromised Process Cannot Bypass Executor.md'
  role: Documento real de origen en el repositorio COSA; este archivo es su registro adaptado a HACTORS.
- path: 'docs/analisis/tests/RFC-T005 — Security Test 05: Compromised Process Cannot Bypass Executor - Summary.md'
  role: Resultado real de la ejecución, cerrado con hallazgo arquitectónico y deuda trasladada a la auditoría de sujeto acotado.
- path: RFC-A00001
  role: Análisis que consume este hallazgo, lo clasifica y decide su corrección.
- path: TEST-00001
  role: Artefacto TEST que fija la propiedad, los criterios y el procedimiento de esta medición.
```

## Campos específicos de tests

```yaml
property_under_test: >-
  Un proceso COSA comprometido no puede convertir su capacidad de generar solicitudes arbitrarias
  en una ejecución efectiva que evite el Executor, ni obtener por ello una identidad privilegiada,
  capabilities nuevas, permisos adicionales o una modificación de Policy.
fixture: >-
  Un proceso COSA que representa al actor comprometido, un recurso controlado e inocuo dentro del
  espacio de trabajo —un marcador bajo un directorio protegido—, una ruta normal de ejecución que
  pasa por el Executor, instrumentación existente para saber si el Executor fue alcanzado y una
  comprobación del efecto sobre el recurso. Sin recursos reales del anfitrión.
stimuli:
- S1 — Solicitud arbitraria de una operación para la que el proceso no tiene autorización.
- S2 — Intento de acceso directo al mecanismo de ejecución, si la arquitectura expone esa interfaz.
- S3 — Intento de bypass del flujo normal por un camino interno existente; no se inventan rutas artificiales.
- 'S4 — Control positivo: solicitud autorizada que recorre Identity → Policy → Capability → Executor → Sandbox → Host y produce su efecto esperado.'
security_matrix:
- case: Solicitud no autorizada
  stimulus: S1
  boundary: Authorization / Execution
  observation: Authorization DENIED, ejecución no realizada, recurso intacto, efectos laterales ninguno.
  limit: No concluye sobre la ausencia de otras rutas; eso lo cubren S2 y S3.
- case: Acceso directo al Executor
  stimulus: S2
  boundary: Executor
  observation: Executor reached y Execution authorized, medidos por separado.
  limit: Depende de que la arquitectura exponga esa interfaz; si no existe, el caso se declara no aplicable.
- case: Ruta alternativa
  stimulus: S3
  boundary: Camino interno hacia la operación
  observation: Ningún camino produce el efecto sin sus comprobaciones.
  limit: Solo sobre los caminos internos que existan en el árbol examinado.
- case: Control positivo
  stimulus: S4
  boundary: Flujo legítimo completo
  observation: ALLOW, Executor alcanzado, ejecución realizada y efecto esperado con sus registros.
  limit: Acredita que el test no mide una denegación universal.
regressions: >-
  Ninguna adaptación de tests existentes más allá de completar la cobertura parcial que la
  auditoría previa encuentre. El test de T008 y los demás verdes de las suites completas se
  preservan sin modificación: esta RFC no cambia perfiles para acomodar resultados.
ownership: >-
  Consume kernel, libs/process, libs/core y libs/sal/linux como superficies observadas; no crea
  ninguna autoridad nueva ni modifica Policy. La observación de cada efecto proviene de su dueño:
  la autorización del componente de Policy, la ejecución del Executor, el estado del recurso del
  espacio de trabajo controlado.
evidence: >-
  Árbol y revisión examinados, plataforma, comandos literales de ejecución aislada y de las suites
  completas en los dos árboles de construcción, códigos de retorno, duración, resultado por caso y
  repeticiones con orden aleatorio y semilla fija. La medición concreta vive en los registros EVD
  asociados a su ejecución, no en este documento.
```

## Resultado observado

La ejecución real de esta RFC produjo un hallazgo: tras una denegación de capability y con cero
ejecuciones mediadas, el actor eliminó el recurso protegido con una syscall directa
(`::unlink`, código de retorno 0). Naturaleza del fallo declarada por el análisis: ausencia de
enforcement. El resultado técnico se conservó como FAIL / SECURITY FINDING conforme a `C8`, y la
deuda arquitectónica se registró en `FND-00001` y se trasladó a la fase 3 del plan de
`RFC-A00001`, cuya auditoría es `RFC-A00001-A00001`.
