```yaml
id: PLAN-00001
title: 'Corrección secuenciada de los hallazgos T005, T006 y T007'
origin: RFC-A00001
status: proposed
date: '2026-09-17'
proposed_by: agent
```

# PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007

Estructura y campos: `specs/templates/PLAN_TEMPLATE.md`. Su instancia de ejecución es un `plan_run`
dentro del `rfc_run` de la RFC que lo produce, conforme a
`specs/HACTORS_SYSTEM.md#10-plan_run-ejecución-de-un-plan`; la instancia no copia pasos, gates ni
aprobación. Un plan no declara campo `actions:`: las acciones que su ejecución motiva se registran en
la RFC que lo produce.

Nota de procedencia: en el corpus real no existió ningún documento PLAN. La secuencia vivía dentro de
la propia RFC-A00001, en su campo `implementation_plan`, y las fases se ejecutaron sin un artefacto
separado que las ordenara. HACTORS lo exige porque el `rfc_run` de una RFC derivada solo puede tener
como padre un `plan_run` (`specs/HACTORS_SYSTEM.md#9-rfc_run-ejecución-de-una-rfc`), y las tres RFC
derivadas que esta simulación registra —F00001, F00002 y A00001— necesitan ese padre. Este documento
es la transcripción de aquel campo al artefacto que el sistema reconoce, con `date` igual a la de su
RFC de origen porque ésa es la fecha observable del contenido que transcribe.

Nota de estado: se escribe `status: proposed`, no `approved`. La aprobación de un plan es una
decisión de [actor: human] (`specs/DECISIONS.md`, `specs/templates/PLAN_TEMPLATE.md#relación-con-decisiones`)
y no quedó registro de ella en el corpus real. Declarar `approved` fabricaría una autorización que no
existe. La consecuencia es una tensión declarada y no resuelta aquí: los pasos 1 a 3 sí se ejecutaron
históricamente, y PLAN_TEMPLATE reserva la ejecución al estado `approved` mientras su lista de
restricciones solo prohíbe explícitamente ejecutar en `draft` o `rejected`. Quien ostente la propiedad
del proyecto puede cerrarla con
`hactors transition --artifact "projects/cosa/plans/PLAN-00001 — Corrección secuenciada de los hallazgos T005, T006 y T007.md" --to approved`,
o reducirla declarando que la ejecución histórica precedió a la existencia del artefacto.

## Cuerpo

```yaml
context: >-
  RFC-A00001 analizó tres hallazgos de seguridad medidos sobre el árbol real y concluyó que no son
  tres defectos independientes sino la manifestación de dos cadenas causales distintas: RC-1 y RC-2
  sostienen T006, RC-3b sostiene T007, y RC-4 junto con RC-3a sostienen T005. La restricción que
  ordena el plan es arquitectónica, no de comodidad: la Fase 2 debe preceder a la Fase 3 porque
  mientras la identidad se represente con un descriptor de fichero, el binding de la Fase 2 es de
  primer llegado y un sujeto de confinamiento no lo refuerza; y la Fase 1 debe preceder a la Fase 2
  por atribución de tests, ya que ambas fases tocan la ruta de entrada y mezclarlas impide decidir
  qué corrección produjo cada verde. La tercera restricción es que las correcciones no pueden
  modificar los tests que las miden sin autorización explícita, así que cada fase declara qué caso
  cambia de rojo a verde y qué casos deben permanecer intactos.
objectives:
- id: O1
  description: Cerrar T006 verificando el contrato wire en el consumidor, de modo que un mensaje malformado no pueda convertirse en una solicitud válida.
- id: O2
  description: Cerrar T007 haciendo que una identidad lógica no quede representada por dos descriptores verificados simultáneos.
- id: O3
  description: Establecer las condiciones previas que hacen decidible la corrección de T005, que es la única que exige un cambio de arquitectura y no solo de implementación.
- id: O4
  description: Mantener en todo momento la vía mediada completa y los casos de control positivo, de forma que ninguna corrección se consiga debilitando la ruta legítima.
steps:
- id: step_001
  description: Fase 1 del implementation_plan de RFC-A00001, contrato wire verificado en el consumidor; cubre los hallazgos T006-F1 y T006-F2 sobre las causas RC-1 y RC-2.
  dependencies: []
  expected_artifact: RFC-A00001-F00001 implementada, con su test de contrato y su evidencia de verificación.
  advancement_criterion: AC1.
  derived_rfc: RFC-A00001-F00001
- id: step_002
  description: Fase 2 del implementation_plan, binding exclusivo identidad↔descriptor dentro del lock de sesiones existente, antes de consultar la allowlist y antes del grant de capability.
  dependencies: [step_001]
  expected_artifact: RFC-A00001-F00002 implementada, con el nuevo motivo de rechazo, su línea de auditoría y su registro de traza.
  advancement_criterion: AC2.
  derived_rfc: RFC-A00001-F00002
- id: step_003
  description: Auditoría de arquitectura y viabilidad del sujeto acotado que T005 requiere, sobre el árbol real, sin modificar código de producción ni crear commits.
  dependencies: [step_002]
  expected_artifact: RFC-A00001-A00001 ejecutada, con su informe de auditoría y su evidencia conservada.
  advancement_criterion: AC3.
  derived_rfc: RFC-A00001-A00001
- id: step_004
  description: 'Paso 3.1 del implementation_plan, la decisión de despliegue previa a todo código. Es el punto bloqueante y no es técnico: fija qué sale del proceso anfitrión, con qué credenciales y con qué dominio de confinamiento.'
  dependencies: [step_003]
  expected_artifact: Un ADR que registre la decisión adoptada entre las alternativas de la auditoría y sus consecuencias sobre el fichero de topología y la raíz de composición.
  advancement_criterion: AC4.
  derived_rfc: null
- id: step_005
  description: Paso 3.2, unificar las mutaciones de ficheros en el trabajador confinado, llevando la eliminación por el mismo camino que la apertura para escritura. Exige extender la whitelist del hijo, que hoy es de tres syscalls, o reestructurar el trabajador para recibir el descriptor de la región ya abierto en un número fijo.
  dependencies: [step_004]
  expected_artifact: La mutación de ficheros del SAL ejecutándose íntegramente en el trabajador confinado, con su whitelist revisada.
  advancement_criterion: AC5.
  derived_rfc: null
- id: step_006
  description: 'Paso 3.3, producir sujetos distinguibles: spawn por servicio con el confinamiento instalado entre el fork y el execvp, reutilizando la maquinaria existente que ya establece la prohibición de nuevos privilegios, más un usuario por endpoint si step_004 lo permite.'
  dependencies: [step_004]
  expected_artifact: Un proceso OS por servicio con su dominio de confinamiento y, si la decisión lo admite, sus credenciales propias.
  advancement_criterion: AC5.
  derived_rfc: null
- id: step_007
  description: Paso 3.4, retirar capacidad al proceso anfitrión con un filtro propio del servidor, con un ruleset de paths, o con ambos. Solo es seguro después de step_005, porque antes rompería la ruta legítima de eliminación.
  dependencies: [step_005]
  expected_artifact: El proceso anfitrión sin la capacidad de emitir syscalls mutantes sobre los recursos protegidos.
  advancement_criterion: AC5.
  derived_rfc: null
- id: step_008
  description: 'Paso 3.5, reproducir el ataque entre procesos OS independientes: el actor comprometido en un PID propio, contra un recurso protegido, con la vía mediada denegada y la syscall directa fallando.'
  dependencies: [step_006, step_007]
  expected_artifact: TEST-00001 ejecutado con el actor en un proceso OS independiente, con la medición completa del criterio de cierre de la Fase 3 y el registro administrativo de la deuda.
  advancement_criterion: AC5.
  derived_rfc: null
decision_gates:
- id: gate_001
  decides: El alcance, los contratos y los criterios de la Fase 1, y la autorización para dar por cerrada su verificación cuando el criterio original de repetibilidad global no se cumpla por una causa ajena.
  actor: human
  approval_criterion: Que el test de contrato pase 10/10 en ambos árboles sin modificar ninguna línea de test, que las suites completas no pierdan ningún verde respecto de la baseline declarada y que la desviación sobre el criterio original quede escrita y aceptada.
  blocks: [step_001]
- id: gate_002
  decides: 'El alcance y los contratos de la Fase 2, y el resultado del prechequeo obligatorio: verificar antes de implementar que ningún servidor del árbol abre hoy dos conexiones con el mismo ServerId.'
  actor: human
  approval_criterion: Que el prechequeo conste por escrito, que el test de suplantación pase 5/5 en ambos árboles, que los cuatro casos verdes anteriores sigan verdes sin modificación y que la limitación de conexiones medio abiertas y su destino arquitectónico queden declarados.
  blocks: [step_002]
- id: gate_003
  decides: 'El modelo de alojamiento y de credenciales de la Fase 3, que es el paso 3.1: qué servicios salen del proceso anfitrión, si se adopta un usuario por endpoint, quién aprovisiona esas cuentas y qué ocurre con los recursos legítimos que hoy pertenecen a un único uid.'
  actor: human
  approval_criterion: Que la alternativa elegida entre las que la auditoría clasifique como viables quede registrada en un ADR con sus consecuencias sobre el fichero de topología, la raíz de composición y el despliegue, y que se acepte explícitamente el riesgo de compatibilidad medido que conlleva.
  blocks: [step_005, step_006, step_007, step_008]
- id: gate_004
  decides: 'La autorización de los cambios de contrato que la Fase 3 declara necesarios: el modelo de alojamiento de la interfaz de servidor, de dentro del proceso a fuera; el fichero de topología si se adopta un usuario por endpoint; la whitelist del trabajador confinado; y posiblemente el nombre o la documentación de la abstracción de proceso.'
  actor: human
  approval_criterion: Que cada contrato afectado esté enumerado, que su nueva forma esté escrita antes de implementarla y que no se autorice ningún contrato que no figure en la enumeración.
  blocks: [step_005, step_006, step_007]
- id: gate_005
  decides: La autorización explícita para modificar el test de proceso comprometido, que debe pasar de un hilo a un proceso OS independiente para demostrar lo que hoy no está demostrado.
  actor: human
  approval_criterion: Que la modificación preserve la propiedad original del TEST o que, si la cambia, se cree un TEST nuevo con su antecedente declarado en lugar de alterar el existente.
  blocks: [step_008]
advancement_criteria:
- id: AC1
  condition: >-
    El test de contrato de T006 pasa 10/10 en ambos árboles sin que se haya modificado ninguna línea
    de test; las suites completas no pierden ningún verde respecto de la baseline 110/113 Ninja y
    107/110 Makefiles, y los únicos rojos pasan a ser T005 y T007; F1 y F2 incrementan el contador
    de denegaciones y producen un registro estructurado de rechazo; el control positivo sigue
    eliminando su fichero con ocho registros ordenados; y veinte repeticiones en orden aleatorio con
    semilla 42 reproducen el resultado en cada árbol.
- id: AC2
  condition: >-
    El test de suplantación de identidad pasa 5/5 en ambos árboles; los cuatro casos verdes
    anteriores siguen verdes sin modificación; las suites completas no pierden ningún verde y el
    único rojo restante es T005; el caso de segunda conexión produce un registro de registro de peer
    con veredicto de colisión, cero grants nuevos, cero registros de admisión, de Executor y de
    handler, y el fingerprint del recurso intacto; la conexión original del atacante sigue
    resolviendo como su propia identidad; veinte repeticiones aleatorias con semilla 42 por árbol
    reproducen el resultado; y queda declarada por escrito la limitación de atribución junto con el
    destino arquitectónico que la cierra.
- id: AC3
  condition: >-
    La auditoría entrega el informe con sus registros clasificados por tipo, la matriz de decisiones
    con cada respuesta marcada como hecho medido o inferencia, las causas raíz que faltaban, un orden
    de validación recomendado, la condición de aceptación que cerraría T005, los riesgos y la
    evidencia conservada e identificable; y no modifica código de producción, tests, política de
    seguridad, configuración versionada ni documento de entrada, ni crea commits.
- id: AC4
  condition: >-
    La decisión de despliegue consta en un ADR aprobado por [actor: human], nombra el mecanismo de
    confinamiento elegido con su viabilidad medida, declara el modelo de credenciales y resuelve el
    destino de los recursos legítimos que hoy dependen del uid único de la raíz de composición.
- id: AC5
  condition: >-
    El criterio de cierre de la Fase 3 de RFC-A00001 se cumple en su totalidad: TEST-00001 pasa en
    ambos árboles con el actor en un proceso OS independiente, midiendo solicitud mediada denegada
    con cero ejecuciones, syscall directa sobre el mismo recurso fallando con el errno o la señal
    declarados, recurso intacto en contenido, inode, modo, tamaño, marcas de tiempo e inventario, y
    control positivo eliminando el mismo archivo por el Executor con ocho registros; las suites
    completas quedan sin ningún rojo y sin perder verdes respecto de la baseline previa; veinte
    repeticiones aleatorias por árbol; la documentación de seguridad re-anclada; la deuda registrada
    del hallazgo marcada como cerrada y el addendum de T005 actualizado con la medición que lo
    respalda.
risks:
- id: P1
  description: Que la Fase 1 se dé por cerrada sin cumplir su criterio original de repetibilidad global por un fallo ajeno a su alcance.
  probability: Alta, y de hecho ocurrió.
  impact: Medio. Deja una desviación no resuelta sobre un criterio escrito, que solo es aceptable si se declara y la aprueba gate_001.
  mitigation: Registrar la desviación como evidencia con su causa medida, no como éxito, y someterla a gate_001 en lugar de asumirla.
- id: P2
  description: Que gate_003 no se decida y la Fase 3 quede bloqueada indefinidamente.
  probability: Alta. Es el punto bloqueante y no es técnico.
  impact: Alto. T005 permanece abierto y con él la TASK que lo registra no puede cerrar.
  mitigation: Ejecutar step_003 sin esperar la decisión, de modo que el bloqueo quede acotado a la decisión y no a la falta de información para tomarla; y mantener el hallazgo abierto y visible en lugar de rebajarlo.
- id: P3
  description: Que se endurezca solo una de las dos rutas de producción, quedando la otra como vía de bypass equivalente.
  probability: Media.
  impact: Alto. La propiedad no se restaura y la medición la da por restaurada si el test solo cubre una ruta.
  mitigation: Exigir en cada criterio que el rechazo se mida en cada ruta de producción por separado, como hace TEST-00002 con el separador de encaminamiento.
- id: P4
  description: Que la falta de repetibilidad global por un timeout ajeno impida distinguir un fallo propio de uno preexistente.
  probability: Alta, ya observada en la verificación de la Fase 1 con ThreadPoolExecutorTest.
  impact: Medio.
  mitigation: Medir la baseline antes y después, y atribuir cada rojo a su causa con la selección acotada de entradas en lugar de con la suite completa.
- id: P5
  description: Que convertir el actor de T005 en un proceso OS independiente debilite la propiedad en lugar de reforzarla, por ejemplo confinando también el recurso o el verificador.
  probability: Media.
  impact: Alto, porque produciría un verde que no demuestra nada.
  mitigation: gate_005 y el criterio de control negativo de TEST-00001, que exige que el bypass se reproduzca en el fixture aislado antes de dar por válida la denegación.
- id: P6
  description: Que algún servidor del árbol abra ya hoy dos conexiones con el mismo ServerId, de modo que la Fase 2 rompa una ruta legítima.
  probability: Baja pero no medida.
  impact: Alto.
  mitigation: Es el prechequeo obligatorio que gate_002 exige resolver antes de implementar; si aparece un caso, se decide antes de escribir código.
derived_rfcs:
- id: RFC-A00001-F00001
  type: F
  purpose: Verificar el contrato wire en el consumidor para cerrar T006-F1 y T006-F2.
  relation: derives
- id: RFC-A00001-F00002
  type: F
  purpose: Establecer el binding exclusivo identidad↔descriptor para cerrar T007.
  relation: derives
- id: RFC-A00001-A00001
  type: A
  purpose: Auditar la arquitectura y la viabilidad del sujeto acotado que T005 requiere, sin implementar la corrección.
  relation: derives
references:
- 'projects/cosa/rfcs/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md, cuyo campo implementation_plan es la fuente de esta secuencia.'
- 'projects/cosa/rfcs/RFC-T00005 — Security Test 05: Compromised Process Cannot Bypass Executor.md'
- 'projects/cosa/rfcs/RFC-T00006 — Security Test 06: Invalid IPC Message Is Rejected by Contract Validation.md'
- 'projects/cosa/rfcs/RFC-T00007 — Security Test 07: Identity Spoofing Does Not Grant Authorization.md'
- 'projects/cosa/tests/TEST-00001.md, TEST-00002.md y TEST-00003.md, que fijan las propiedades que los criterios de avance miden.'
- 'specs/LIFECYCLE.md#plan y specs/templates/PLAN_TEMPLATE.md, por los estados y las restricciones que aplican a este documento.'
```

## Relación con la RFC de origen

Este plan no sustituye a RFC-A00001 ni reescribe su análisis: ordena su ejecución. Las tres RFC
derivadas conservan su identificador y su ciclo de vida independientes, y su arista `derives` se
declara en el campo `origin` de cada una, no aquí; `derived_rfcs` es la propuesta del plan, no el
registro de la arista. La contención tampoco acredita la declaración: que un `rfc_run` viva dentro
del `plan_run` de este plan no prueba que su RFC figure en `derived_rfcs`.

El grafo del proyecto refleja esta relación con una arista `derives` por cada RFC derivada, desde
RFC-A00001 hacia ella, y no produce ninguna arista por el `origin` de un PLAN ni por la contención de
las instancias, conforme a `specs/HACTORS_SYSTEM.md#3-grafo-de-relaciones`.
