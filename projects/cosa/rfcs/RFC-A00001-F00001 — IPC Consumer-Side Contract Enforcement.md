```yaml
rfc: RFC-A00001-F00001
title: 'IPC Consumer-Side Contract Enforcement'
type: F
scope: >-
  El lado consumidor del contrato wire de una solicitud de agente: el decoder del cuerpo y los dos
  extractores de enrutamiento de producción. Atraviesa libs/common, libs/core y libs/server, así que
  vive en rfcs/ de la raíz del proyecto.
status: draft
date: '2026-09-18'
proposed_by: agent
origin: RFC-A00001
supersedes: null
superseded_by: null
depends_on: []
affected_modules:
- libs/common
- libs/core
- libs/server
- kernel
- tests
relations: []
```

# RFC-A00001-F00001 — IPC Consumer-Side Contract Enforcement

Estructura y campos: `specs/templates/RFC_TEMPLATE.md` y `specs/templates/RFC-F_TEMPLATE.md`.
Convenciones de identidad y relaciones: `specs/RFC.md`; estados y transiciones: `specs/LIFECYCLE.md`.

Registro en HACTORS del documento real `docs/analisis/tests/RFC-T006-F1 — IPC Consumer-Side Contract
Enforcement.md` del repositorio COSA, nombre histórico que se conserva aquí como referencia y no
como identidad. Su cabecera real declara `Origen: RFC-A00001` y `Test objetivo: RFC-T006`; en
HACTORS la identidad conserva el prefijo de su origen conforme a `specs/RFC.md#derivación-y-numeración`,
así que deriva de `RFC-A00001` y no de `RFC-T00006`, que es la RFC cuya medición la motiva y consta
en `references`. `date` es la fecha observable del archivo fuente.

`status: draft` reproduce el estado documental real: la RFC del propietario siguió en DRAFT y no fue
editada, aunque su contenido se implementó y se verificó el 2026-09-18. HACTORS separa el estado
documental del de ejecución, así que el trabajo observado vive en su `rfc_run` y no en este campo;
avanzar el estado documental es una transición de `[actor: human]` que aquí no se produce.

## Cuerpo común

```yaml
context: >-
  RFC-T00006 midió dos defectos del contrato wire del lado consumidor: una operación ausente o no
  imprimible atraviesa el decoder y llega a admisión, y un separador de enrutamiento distinto de NUL
  es aceptado por las rutas de producción con una ejecución autorizada real. RFC-A00001 los clasificó
  como deficiencia del contrato y los asignó a su fase 1, la más acotada y la única sin cambio de
  contratos.
problem_statement: >-
  El productor valida y escribe el contrato correctamente, pero el consumidor confía. Sin
  validación en el consumidor, un payload que incumple el contrato se convierte en una solicitud
  procesable, y endurecer solo una de las dos rutas de producción dejaría un bypass diferencial.
goals:
- G1 — Que `decode_agent_request` aplique la validación de operación que ya existe, sin cambiar su firma pública ni su comportamiento zero-copy.
- G2 — Que los dos extractores de enrutamiento de producción acepten únicamente un NUL real como terminador y rechacen un routing sin terminador.
- 'G3 — Conservar explícitamente el caso legítimo de routing ausente con fallback al nombre canónico: routing ausente no equivale a routing malformado.'
- G4 — Que los rechazos nuevos se traduzcan a la categoría de contrato malformado, para que entren en el mecanismo de auditoría de rechazos y en su contador.
- G5 — Que los diez casos del test de seguridad pasen sin modificar ni una línea del test.
- G6 — No perder ningún verde existente en las suites completas de los dos árboles de construcción.
non_goals:
- Resolver T005 ni T007, la exclusividad identidad↔descriptor, la identidad↔PID, el aislamiento mediante procesos OS, seccomp adicional, Landlock, Sandbox, la política estática de identidad de peer, la autorización de topología ni `IPCManager`.
- Implementar el extractor compartido, que el análisis identifica como destino arquitectónico pero mantiene separado de esta corrección.
- Arreglar de forma global la deuda de observabilidad preexistente; solo garantizar que los rechazos nuevos no reproduzcan el mismo agujero.
- Modificar los tests de seguridad para conseguir verde.
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional:
  - specs/RFC.md
  - specs/TESTS.md
  - specs/EVIDENCE.md
  - specs/FINDING.md
  - specs/TRANSACTIONS.md
proposed_architecture: >-
  Dos puntos de enforcement y ningún tercero: la validación del cuerpo en el decoder y el
  endurecimiento de cada extractor de enrutamiento en su propia ruta. La responsabilidad queda
  repartida —cuerpo de la solicitud al decoder, framing y routing al extractor, traducción del
  rechazo al endpoint del agente, producción del frame al constructor de mensajes— y no se añade una
  validación equivalente en el endpoint. El rechazo ya decidido se notifica por una faceta
  descubrible que no recibe el payload, no autoriza, no devuelve veredicto y no puede habilitar
  entrega.
abi_api_contracts: >-
  Sin ruptura de ABI ni de API existente. La firma pública del decoder no cambia y se conserva el
  comportamiento zero-copy: sin copias, sin asignaciones dinámicas y sin una segunda implementación
  del validador. Los dos extractores pasan a devolver un opcional cuya ausencia significa
  malformado, de modo que éxito implica terminación con NUL real; el estado de ausencia lo
  representa cada llamante. Se añade una cabecera pública nueva con la faceta de observación del
  rechazo contractual, exportada en el conjunto de archivos de su módulo.
new_module: null
ownership_changes: >-
  La garantía del contrato wire pasa del productor al consumidor, que es quien posee la frontera por
  la que entra. El contador de rechazos del endpoint pasa a incluir los rechazos de enrutamiento
  dirigidos a ese endpoint, junto con los suyos propios; no es un contador global de IPC y no se
  declara como tal.
dependency_rules: >-
  Ninguna cabecera del núcleo se incluye desde las bibliotecas de núcleo de entrada ni de servidor.
  No se crea un registro global de observadores ni una API de registro, y no se modifica el
  constructor ni el cableado de la raíz de composición.
actions:
  - id: ACT-00001
    type: implementation
    status: completed
    actor: agent
    depends_on: []
    deliverable: libs/common/src/AgentRequest.cpp
    evidence:
    - EVD-00005
  - id: ACT-00002
    type: implementation
    status: completed
    actor: agent
    depends_on: []
    deliverable: libs/core/src/InboundPipeline.cpp; libs/server/src/MessageDispatcher.cpp
    evidence:
    - EVD-00005
  - id: ACT-00003
    type: implementation
    status: completed
    actor: agent
    depends_on: []
    deliverable: libs/server/include/cosa/server/IInboundContractRejectionObserver.h;
      kernel/include/cosa/kernel/AgentEndpoint.h
    evidence:
    - EVD-00005
  - id: ACT-00004
    type: test
    status: completed
    actor: agent
    depends_on: []
    deliverable: kernel/tests/InboundContractRejectionTest.cpp; libs/core/tests/InboundPipelineSecurityTest.cpp;
      libs/common/tests/AgentRequestTest.cpp; libs/server/tests/IMessageDispatcherTest.cpp
    evidence:
    - EVD-00005
  - id: ACT-00005
    type: documentation
    status: pending
    actor: agent
    depends_on: []
    deliverable: ''
    evidence: []
  - id: ACT-00006
    type: evidence
    status: completed
    actor: agent
    depends_on:
    - ACT-00001
    - ACT-00002
    - ACT-00003
    - ACT-00004
    deliverable: docs/analisis/tests/RFC-T006-F1 — IPC Consumer-Side Contract Enforcement
      - Summary.md
    evidence:
    - EVD-00005
migration_plan: >-
  No aplicable: no hay migración de datos ni de esquema. El cambio es de validación y de
  observabilidad del rechazo.
benefits:
  architectural: >-
    Ataca las causas raíz del contrato —validación ausente en el consumidor y terminador ambiguo— y
    nada más, sin acoplar módulos que no comparten frontera.
  engineering: >-
    Reutiliza el validador existente del contrato y los registros estructurados ya presentes, y añade
    pruebas propietarias a través de superficies públicas sin abrir métodos solo para tests.
  ai: >-
    El criterio de cierre es medible y los intocables están enumerados, así que un ejecutor
    automatizado no puede fabricar el resultado modificando el test ni la identidad del atacante.
risks:
- id: R1
  risk: Modificar los tests para conseguir verde.
  mitigation: Los diez casos del test de seguridad son intocables y su hash se compara antes y después.
- id: R2
  risk: Duplicar el enforcement en el endpoint del agente.
  mitigation: Dos puntos de enforcement declarados; el endpoint conserva su validación y decisión actuales.
- id: R3
  risk: Endurecer solo una de las dos rutas de producción.
  mitigation: Pruebas de integración por separado para cada ruta con el mismo separador inválido.
- id: R4
  risk: Convertir el routing ausente en malformado.
  mitigation: El fallback canónico se conserva explícitamente y tiene sus propios casos.
- id: R5
  risk: Clasificar un rechazo de contrato como ruta denegada o no autorizado.
  mitigation: La traducción exige la categoría de contrato malformado y su valor literal.
- id: R6
  risk: Degradar el diseño zero-copy del decoder con asignaciones o copias.
  mitigation: Se reutiliza el validador sobre la vista prestada y se comprueba el aliasing.
alternatives_considered:
- id: A1
  alternative: Reforzar la validación en el productor.
  rejection: El productor ya valida y escribe NUL correctamente; duplicar esa responsabilidad no soluciona el problema descubierto.
- id: A2
  alternative: Un extractor compartido entre las dos rutas.
  rejection: Fuera de alcance por decisión del análisis; se mantiene separada de esta corrección y queda como destino arquitectónico.
- id: A3
  alternative: Devolver el estado de operación inválida en el rechazo del decoder.
  rejection: El test intocable exige la categoría de contrato malformado para todas las mutaciones; prevalecen la prohibición de tocar los tests y la traducción al mecanismo de auditoría de rechazos.
consequences: >-
  Los dos hallazgos de contrato quedan cerrados en el consumidor. El criterio de cierre de la fase 1
  en RFC-A00001 —el que PLAN-00001 transcribe como AC1— espera que los únicos rojos pasen a ser T005
  y T007, y esa cláusula se cumple; la que no se cumple es su repetibilidad global de veinte
  iteraciones, por un agotamiento de tiempo ajeno a este alcance. El documento real de origen sí
  esperaba, en sus apartados 10 y 11, que T005 quedara como único rojo y T007 pasara a verde; eso no
  ocurrió, y el propietario decidió mantener el alcance F1/F2 con los dos rojos visibles en lugar de
  declarar cumplido ese criterio más estricto. Las dos desviaciones se declaran en lugar de
  reinterpretar el criterio.
documentation_impact: >-
  El comentario de cabecera que describía al decoder como validador de geometría era falso y se
  corrige. Las addenda de la documentación de seguridad y de tests del executor ya registran el
  resultado de la medición anterior. Queda pendiente el addendum de esta fase en los documentos
  versionados que describen lo que se tocó —docs/security.md, libs/common/docs/TESTS.md,
  libs/core/docs/TESTS.md y kernel/docs/TESTS.md— y en libs/server, que solo tiene docs/SERVER.md
  y no un documento de tests; lo lleva ACT-00005, que sigue en pending.
testing: >-
  Pruebas unitarias del decoder y de cada extractor en sus módulos propietarios, más pruebas de
  integración por separado de las dos rutas con un frame real codificado por socketpair, y una
  prueba de contrato con el endpoint y el gestor de IPC reales. Las suites completas de los dos
  árboles acreditan que no se pierde ningún verde.
acceptance_criteria:
- id: C1
  condition: El decoder rechaza una operación vacía, cualquier byte de control y cualquier byte no imprimible alto, y acepta una operación válida y la operación máxima imprimible.
  covers: [G1]
  verification: Los casos unitarios del decoder y la comprobación de que las vistas siguen apuntando al buffer original.
- id: C2
  condition: Los dos extractores aceptan únicamente un NUL real como terminador y rechazan un byte de control o alto antes del NUL y una cola sin terminador al final del buffer.
  covers: [G2]
  verification: Los casos unitarios y de integración de cada ruta por separado.
- id: C3
  condition: El routing ausente y el NUL inicial conservan el fallback al nombre canónico.
  covers: [G3]
  verification: Los casos de ausencia y de routing vacío en las dos rutas.
- id: C4
  condition: Los rechazos nuevos se traducen a la categoría de contrato malformado, producen su registro estructurado e incrementan el contador de rechazos del endpoint destinatario.
  covers: [G4]
  verification: El valor literal del error, el registro correlacionado y el contador en la prueba de contrato.
- id: C5
  condition: El test de seguridad del contrato pasa 10/10 en ambos árboles sin que se haya modificado ninguna línea de los archivos intocables.
  covers: [G5]
  verification: El resultado del test y la comparación de hash de los archivos protegidos antes y después.
- id: C6
  condition: Ningún verde existente se pierde en las suites completas de los dos árboles y no aparece ningún rojo nuevo.
  covers: [G6]
  verification: Las cifras de las suites completas frente a su baseline y la identidad de las unidades de prueba en rojo.
- id: C7
  condition: El resultado es reproducible con orden aleatorio y semilla fija en ambos árboles.
  covers: [G5, G6]
  verification: Las repeticiones por suite y por CTest, con sus semillas reales por iteración.
- id: C8
  condition: La causalidad del cambio queda demostrada revirtiendo y restaurando la corrección.
  covers: [G1, G2]
  verification: La reproducción del rojo esperado sin la corrección, el verde con ella, y la identidad de hash y el diff limpio al restaurar.
references:
- path: 'docs/analisis/tests/RFC-T006-F1 — IPC Consumer-Side Contract Enforcement.md'
  role: Documento real de origen en el repositorio COSA; este archivo es su registro adaptado a HACTORS.
- path: 'docs/analisis/tests/RFC-T006-F1 — IPC Consumer-Side Contract Enforcement - Summary.md'
  role: Resultado real de la implementación del 2026-09-18, con la forma del cambio y la verificación medida.
- path: RFC-A00001
  role: Análisis de origen, cuya fase 1 contrata esta corrección y fija su criterio de cierre.
- path: RFC-T00006
  role: RFC de tests cuya medición originó los dos hallazgos que esta RFC cierra.
- path: TEST-00002
  role: Artefacto TEST cuya ejecución verifica el resultado; el vínculo lo declara su instancia, no este documento.
```

## Campos específicos de feature

```yaml
follow_up_rfcs:
- type: T
  purpose: >-
    Verificación independiente del contrato corregido en el consumidor. No se propone como RFC nueva:
    la propiedad ya la fija TEST-00002, derivado de RFC-T00006, y su ejecución es la que acredita el
    cierre.
- type: D
  purpose: >-
    Documentación del reparto de responsabilidad del contrato y del alcance real del contador de
    rechazos. Pendiente; no se registra aquí como RFC derivada porque esta simulación no la produce.
```

## Resultado observado

Implementada y verificada el 2026-09-18 sobre el árbol `dev`, sin commit: los dos puntos de
enforcement quedaron endurecidos en ambas rutas de producción y el test de seguridad del contrato
pasó de 7/10 a 10/10 sin modificar ningún test protegido —nueve archivos intocables con hash
idéntico antes y después—. Las suites completas pasaron de 129/132 a 131/133 en Ninja y de 126/129 a
128/130 en Makefiles; los dos rojos restantes son exactamente los de la baseline y fallan en las
mismas unidades de prueba.

Dos desviaciones se declaran en lugar de reinterpretarse:

1. **El criterio más estricto del documento real no se cumple.** Sus apartados 10 y 11 esperaban que
   T005 quedara como único rojo y T007 pasara a verde; T007 seguía rojo porque su corrección
   pertenece a la fase 2. El propietario decidió mantener el alcance F1/F2 y dejar ambos rojos
   visibles, sin declarar cumplido ese criterio. El criterio de la fase 1 en `RFC-A00001`, que espera
   exactamente esos dos rojos, sí se cumple en esa cláusula. Los dos hallazgos de contrato quedaron
   cerrados.
2. **La repetibilidad global no se cumple**, que es la cláusula pendiente tanto de `AC1` de
   `PLAN-00001` como del criterio de la fase 1. Un timeout de una suite de ejecución enlazada, ajena a
   este alcance, impide acreditar las veinte repeticiones del conjunto completo; la repetibilidad de
   las suites propias sí se midió. `gate_001` es quien autorizaría dar por cerrada la verificación con
   esa desviación, y su decisión no consta registrada.

La baseline documentada en la RFC real (110/113 y 107/110) estaba obsoleta por RFC-T008; las cifras
medidas son las del resultado. La evidencia completa vive en los registros EVD asociados a su
`test_run`, no en este documento.
