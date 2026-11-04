```yaml
rfc: RFC-T00006
title: 'Security Test 06: Invalid IPC Message Is Rejected by Contract Validation'
type: T
scope: >-
  La frontera entre el codec wire y la admisión de una solicitud COSA; atraviesa libs/common,
  libs/server y kernel, así que vive en rfcs/ de la raíz del proyecto.
status: tested
date: '2026-09-17'
proposed_by: agent
origin: null
supersedes: null
superseded_by: null
depends_on: []
affected_modules:
- libs/common
- libs/server
- kernel
- tests
relations:
- target: RFC-A00001
  relation: informs
```

# RFC-T00006 — Security Test 06: Invalid IPC Message Is Rejected by Contract Validation

Estructura y campos: `specs/templates/RFC_TEMPLATE.md` y `specs/templates/RFC-T_TEMPLATE.md`.
Convenciones de identidad y relaciones: `specs/RFC.md`; estados y transiciones: `specs/LIFECYCLE.md`.

Registro en HACTORS del documento real `docs/analisis/tests/RFC-T006 — Security Test 06: Invalid IPC
Message Is Rejected by Contract Validation.md` del repositorio COSA, incluida su sección de
resultado de 2026-09-17. La identidad pasa de tres a cinco cifras conforme a
`specs/RFC.md#identidad-y-tipos`, conservando el número real. `relations` declara la arista
`informs` hacia `RFC-A00001`, que el documento informado no puede declarar por sí mismo. `date` es
la fecha observable del archivo fuente.

## Cuerpo común

```yaml
context: >-
  El IPC de COSA declara que un payload que no cumple el contrato se rechaza en la validación
  contractual. RFC-T006 encarga medir esa propiedad atravesando el flujo real de IPC, no una
  llamada aislada al decoder.
problem_statement: >-
  No estaba demostrado que un atacante no pueda usar un mensaje estructuralmente inválido para
  provocar procesamiento incorrecto, saltarse validaciones posteriores, alcanzar una operación con
  datos no válidos o producir efectos laterales. Un rechazo observado en el decoder no acredita el
  rechazo del recorrido, porque solo producción decide si los bytes llegan al dispatcher.
goals:
- G1 — Auditar la cobertura IPC, codec y contrato existente, y reutilizarla sin duplicar el montaje de Policy, Capability, Executor ni SAL.
- G2 — Componer el recorrido real completo, del constructor de mensajes al handler, con socketpair y ambos codecs exteriores.
- G3 — Probar los casos de payload malformado que el contrato real permite expresar, sin inventar restricciones que no existen.
- 'G4 — Distinguir malformed de unauthorized: el rechazo contractual no se prueba con una autorización denegada.'
- G5 — Verificar que la lógica de negocio, la admisión, el Executor y el handler no se alcanzan, y que el recurso controlado queda íntegro.
- G6 — Incluir un control positivo con un mensaje válido que recorra admisión, Executor, Policy y el handler real.
- G7 — Conservar cualquier bypass o comportamiento inesperado como hallazgo de seguridad, sin adaptar las expectativas a la vulnerabilidad.
non_goals:
- Convertir el test en fuzzing ni introducir infraestructura innecesaria.
- Modificar otras capas de seguridad ni código de producción para corregir u ocultar los hallazgos.
- Ejecutar `InboundPipeline`, registro de peers ni autenticación `SO_PEERCRED`, que el fixture no monta.
- Introducir LLM, red IP, servicios externos, sanitizers ni dependencias externas.
- Cubrir la suplantación de identidad ni el bypass de proceso comprometido, que pertenecen a RFC-T00007 y RFC-T00005.
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional:
  - specs/RFC.md
  - specs/TESTS.md
  - specs/EVIDENCE.md
  - specs/FINDING.md
proposed_architecture: >-
  No aplicable a una RFC de tests. La composición del recorrido se describe en el fixture y respeta
  la arquitectura existente; el test no crea un segundo protocolo ni un validador propio.
abi_api_contracts: >-
  No aplicable: esta RFC no crea ni modifica contratos. El contrato examinado es el binario de
  disposición fija `WireAgentRequest` de 64 bytes, y sus restricciones reales son presencia de
  operación, caracteres, versión, reservados, estructura y capacidad.
new_module: null
ownership_changes: >-
  Ninguno en producción. La extracción del fixture compartido mueve código de test, no una frontera
  pública: los cuerpos de los tests preexistentes permanecen idénticos, comprobado por comparación
  textual.
dependency_rules: >-
  No aplicable: no se alteran las reglas de dependencia entre módulos. El test consume el codec, el
  dispatcher, el endpoint y el handler de producción, y reutiliza el fixture de seguridad existente.
actions: []
migration_plan: >-
  No aplicable: no hay migración de datos ni de esquema.
benefits:
  architectural: >-
    Convierte «payload inválido ≠ solicitud COSA válida» en una medición del recorrido completo y
    localiza en qué componente se rompe cuando se rompe.
  engineering: >-
    Reutiliza el fixture, el pipeline, los sinks y las comprobaciones de integridad ya existentes, y
    se ejecuta de forma aislada con CTest en los dos árboles de construcción.
  ai: >-
    Los casos, sus oráculos y sus límites quedan explícitos, así que un ejecutor automatizado no
    puede presentar un error de transporte ni una autorización denegada como rechazo contractual.
risks:
- id: R1
  risk: Que un error de transporte o de frame se cuente como rechazo del contrato.
  mitigation: Para los cuerpos malformados se reconstruyen longitudes y checksum exteriores correctos, y se comprueba la identidad de los bytes enviados y recibidos.
- id: R2
  risk: Que un crash o un error de validación se considere automáticamente PASS.
  mitigation: Un error de lectura, un EOF inesperado o un fallo de codec hace fallar el test.
- id: R3
  risk: Que el test se adapte a la vulnerabilidad observada para obtener verde.
  rejection: 'Prohibido: los tres casos fallidos se conservan como fallos reales, sin `WILL_FAIL`, sin skips y sin expectativas adaptadas.'
- id: R4
  risk: Que la composición en un único proceso sobreesté la conclusión.
  mitigation: 'Los límites se declaran por escrito: sin kernel ni servidores OS, sin `InboundPipeline`, sin autenticación de peer; la igualdad de caller en el endpoint no demuestra autenticación.'
alternatives_considered:
- id: A1
  alternative: Probar el contrato con una llamada directa al decoder.
  rejection: Da evidencia adicional pero no impide entregar los bytes al dispatcher; no mide el recorrido.
- id: A2
  alternative: Copiar el kernel de prueba de `InboundPipelineSecurityTest`.
  rejection: Duplicaría infraestructura y exigiría declarar un recorrido que T006 no ejecuta.
- id: A3
  alternative: Reproducir literalmente todos los ejemplos de payload malformado del encargo.
  rejection: 'El contrato real es binario de disposición fija, no JSON: no hay tipo dinámico, `null`, campos con nombre desconocidos ni enum de payload. Se prueban las restricciones que sí existen y se declara la diferencia.'
- id: A4
  alternative: Crear un segundo protocolo o un fixture de negocio propio.
  rejection: Prohibido por la plantilla de tipo; se reutiliza el dispatcher y el handler de producción.
consequences: >-
  Dos mecanismos distintos quedaron abiertos: la aceptación de una operación ausente o no imprimible
  y la aceptación de un separador de enrutamiento inválido con efecto real. La corrección pertenece
  al consumidor del contrato, no al test que la detecta.
documentation_impact: >-
  `docs/security.md` y `libs/executor/docs/TESTS.md` reciben addenda con el resultado y la ubicación
  actual del fixture, sin reescribir mediciones anteriores; `docs/security.md` incluye el bloque de
  deuda técnica.
testing: >-
  Esta RFC es el encargo de un test. Su comprobación es la ejecución aislada y repetible del test
  que encarga, más las suites completas de los dos árboles para acreditar que no se pierde ningún
  verde.
acceptance_criteria:
- id: C1
  condition: Se auditó el repositorio antes de crear código y se reutilizaron los tests IPC, codec y contrato existentes cuando correspondía.
  covers: [G1]
  verification: La tabla de cobertura localizada con la decisión tomada en cada caso y la comparación textual de los cuerpos preexistentes.
- id: C2
  condition: El payload malformado atraviesa el flujo real de IPC y codec, del constructor al handler.
  covers: [G2]
  verification: El recorrido compuesto y declarado, con la comprobación de bytes y de ambos codecs exteriores antes del dispatch.
- id: C3
  condition: La validación del contrato rechaza el mensaje antes de la lógica de negocio.
  covers: [G3, G5]
  verification: El registro de rechazo `malformed_wire` con su error y su subcódigo, y cero registros de admisión, de Executor y de handler.
- id: C4
  condition: El mensaje no se procesa como una solicitud válida y no produce efectos laterales.
  covers: [G5]
  verification: 'Las comprobaciones de integridad del recurso controlado: inventario, dispositivo e inodo, modo, tamaño, mtime y ctime, y contenido completo.'
- id: C5
  condition: Existe un control positivo con un mensaje válido que alcanza la ejecución real.
  covers: [G6]
  verification: El caso válido con admisión, Executor, Policy y handler recorridos y el archivo temporal eliminado como corresponde.
- id: C6
  condition: El rechazo contractual no se confunde con una autorización denegada ni con un error de transporte.
  covers: [G4]
  verification: Las operaciones malformadas que alcanzan admisión no se presentan como denegadas por Policy, y los frames exteriores son correctos.
- id: C7
  condition: El test es determinista, autocontenido y ejecutable de forma aislada, sin red, sin LLM, sin servicios externos y sin sleeps.
  covers: [G2]
  verification: Los comandos literales de ejecución aislada y las veinte repeticiones con orden aleatorio y semilla fija por árbol.
- id: C8
  condition: Cualquier bypass o comportamiento inesperado queda documentado como hallazgo de seguridad, sin corrección de producción dentro de este encargo.
  covers: [G7]
  verification: Los registros FND asociados a la ejecución y la ausencia de cambios en código de producción.
references:
- path: 'docs/analisis/tests/RFC-T006 — Security Test 06: Invalid IPC Message Is Rejected by Contract Validation.md'
  role: Documento real de origen en el repositorio COSA, con su sección de resultado; este archivo es su registro adaptado a HACTORS.
- path: 'docs/analisis/tests/RFC-T006 — Security Test 06: Invalid IPC Message Is Rejected by Contract Validation - Summary.md'
  role: Resumen local del resultado real de la ejecución.
- path: RFC-A00001
  role: Análisis que consume estos dos hallazgos, los clasifica y decide su corrección.
- path: TEST-00002
  role: Artefacto TEST que fija la propiedad, los criterios y el procedimiento de esta medición.
```

## Campos específicos de tests

```yaml
property_under_test: >-
  Un mensaje IPC cuyo payload no cumple el contrato es rechazado por la validación contractual antes
  de alcanzar la lógica de negocio, la admisión, el Executor o el handler, y no produce efectos
  laterales. Payload inválido no es una solicitud COSA válida.
fixture: >-
  Fixture de seguridad compartido extraído sin cambiar su contenido, con el montaje de Policy,
  Capability, Executor y SAL reutilizado; socketpair AF_UNIX/SOCK_STREAM con un adaptador mínimo de
  sesión local; recurso temporal controlado bajo un directorio protegido que se limpia incluso tras
  fallos; autorización expresa de la operación del control positivo antes de cada caso; contadores y
  registros ya existentes como sinks. Deadlines de lectura y escritura de 200 ms y timeout CTest de
  20 s.
stimuli:
- S1 — Cuerpo vacío.
- S2 — Cabecera truncada.
- S3 — Versión desconocida.
- S4 — Campos reservados no nulos.
- S5 — Recurso de tamaño excesivo.
- S6 — Byte de recurso ausente.
- S7 — Operación ausente.
- S8 — Operación con caracteres no imprimibles.
- S9 — Separador de enrutamiento sustituido por 0x1F en un cuerpo por lo demás válido.
- 'S10 — Control positivo: cuerpo válido equivalente que debe alcanzar el handler real.'
security_matrix:
- case: Geometría, versión, reservados y capacidad
  stimulus: S1 a S6
  boundary: Codec y validación contractual
  observation: Rechazo `Malformed` con un registro inbound de rechazo, cero registros de admisión, de Executor y de handler, recurso íntegro.
  limit: Acredita el rechazo antes del dispatch en la composición de un único proceso, no en una topología desplegada.
- case: Operación ausente o no imprimible
  stimulus: S7 y S8
  boundary: Decoder → endpoint → admisión
  observation: El decoder acepta y entrega la vista; el endpoint la considera inbound aceptado e identidad verificada; admisión responde operación desconocida. Sin ejecución ni efecto, pero sin rechazo contractual y con el contador de denegaciones en cero.
  limit: No es rechazo antes de admisión; la naturaleza del defecto es de contrato, no de autorización.
- case: Separador de enrutamiento inválido
  stimulus: S9
  boundary: Dispatcher y endpoint
  observation: El separador 0x1F se acepta, el cuerpo válido se ejecuta, ocho registros normales, una ejecución y archivo eliminado.
  limit: 'Es aceptación de estructura inválida, no bypass de autorización: la operación estaba expresamente autorizada. No prueba alcance desde un peer no autenticado.'
- case: Control positivo
  stimulus: S10
  boundary: Recorrido legítimo completo
  observation: Cuerpo válido aceptado y ejecutado por admisión, Executor, Policy y el handler real, con el archivo temporal eliminado.
  limit: Acredita que el recorrido funciona y que los rechazos anteriores no son una denegación universal.
regressions: >-
  Los tests de codec, frame, contrato de solicitud, pipeline inbound, dispatcher seguro, fundamento
  del Executor y admisión de capabilities se conservan y pasan en ambos árboles. El test de la
  ejecución de capability no autorizada conserva sus dos casos verdes tras la extracción del
  fixture. No se modifica ningún test de seguridad existente para acomodar resultados.
ownership: >-
  Consume libs/common, libs/server y kernel como superficies observadas; no crea autoridades ni
  validadores paralelos. Cada observación proviene de su dueño: el rechazo del codec, el recorrido
  del dispatcher, la decisión de admisión, la ejecución del Executor y el estado del recurso del
  espacio de trabajo controlado.
evidence: >-
  Árbol y revisión examinados, plataforma, comandos literales de construcción y de ejecución aislada
  en los dos árboles, repeticiones con orden aleatorio y semilla fija, códigos de retorno, duración,
  resultado por caso, registros por etapa y comprobaciones de integridad del recurso. La medición
  concreta vive en los registros EVD asociados a su ejecución, no en este documento.
```

## Resultado observado

La ejecución real de esta RFC produjo dos hallazgos de naturaleza distinta:

- **Operación ausente o no imprimible aceptada por el decoder** (`FND-00002`). El encoder y los
  setters la rechazan; `decode_agent_request` comprueba la geometría y entrega la vista sin esa
  validación, y el endpoint la remite a admisión. Naturaleza del fallo declarada por el análisis:
  deficiencia del contrato. Corrección contratada en `RFC-A00001-F00001`.
- **Separador de enrutamiento inválido aceptado con efecto real** (`FND-00003`). El dispatcher
  detiene el scan también ante `0x1F` sin exigir NUL y el endpoint salta un byte sin verificarlo; el
  resultado es una ejecución autorizada real. Naturaleza del fallo: deficiencia del contrato y de
  separación de responsabilidades. Corrección contratada en `RFC-A00001-F00001`.

Diez casos, siete verdes y tres rojos en cada árbol; las suites completas sin otros fallos. La
definición de Done del documento real no se cumple y no se declara completada: el estado registrado
es `tested`. El análisis posterior corrigió una atribución de este documento —el rechazo de la
operación desconocida es de la familia de aplicación, no de validación— y esa corrección consta en
la evidencia de `RFC-A00001`, no aquí.
