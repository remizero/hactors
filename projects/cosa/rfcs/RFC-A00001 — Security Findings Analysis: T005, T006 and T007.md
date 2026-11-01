```yaml
rfc: RFC-A00001
title: 'Security Findings Analysis: T005, T006 and T007'
type: A
scope: Varios módulos y contratos entre ellos; por eso vive en rfcs/ de la raíz del proyecto.
status: under_review
date: '2026-09-17'
proposed_by: agent
origin: null
supersedes: null
superseded_by: null
depends_on: []
affected_modules:
- libs/common
- libs/core
- libs/server
- libs/process
- libs/sal/linux
- kernel
- init
- config
- docs
relations: []
```

# RFC-A00001 — Security Findings Analysis: T005, T006 and T007

Estructura y campos: `specs/templates/RFC_TEMPLATE.md` y `specs/templates/RFC-A_TEMPLATE.md`.
Convenciones de identidad y relaciones: `specs/RFC.md`; estados y transiciones: `specs/LIFECYCLE.md`.

`relations` queda vacío a propósito, no por olvido. La relación con las tres RFC-T que originan los
hallazgos es `informs` en dirección `RFC-Txxx → RFC-A00001`, y esa arista la declara el documento
informante, no el informado, porque en la lista de un documento el origen es implícito
(`specs/HACTORS_SYSTEM.md`, «Relaciones del proyecto»). Esas tres RFC no están registradas en este
proyecto; registrarlas y representar las aristas es un entregable pendiente de `TASK-00001`. Las
fuentes constan entretanto en `data_sources`, que no produce aristas.

## Cuerpo común

```yaml
context: >-
  Los tests de seguridad RFC-T005, RFC-T006 y RFC-T007 de COSA encontraron hallazgos reales y
  reproducibles sobre el árbol `dev` en `c0c5610`. No son tres fallos del mismo tipo, y tratarlos
  como tales produciría un plan equivocado.
problem_statement: >-
  Tres propiedades de seguridad declaradas por COSA no se sostienen. Un actor comprometido elimina
  un recurso protegido con una syscall directa después de que el Executor denegara la operación
  (T005). Un cuerpo que incumple el contrato atraviesa el decoder y llega a admisión, y sustituir
  el NUL de enrutamiento por 0x1F produce una ejecución autorizada real (T006-F1 y T006-F2). Una
  segunda conexión del mismo PID se registra con otra identidad, obtiene su capability y elimina el
  recurso (T007). Se desconoce qué componente debe corregir cada caso y en qué orden.
goals:
- G1 — Reconstruir cada hallazgo y clasificar su naturaleza sin dar por supuesto que el componente que lo detecta es el que debe corregirlo.
- G2 — Trazar cada hallazgo hasta el código de producción que lo permite y hasta el componente responsable de impedirlo.
- G3 — Determinar el impacto arquitectónico, la frontera de confianza atravesada y la autoridad aceptada sin validación.
- G4 — Correlacionar los tres hallazgos y establecer qué corrección debe preceder a otra, sin duplicar soluciones.
- G5 — Evaluar alternativas de corrección por causa raíz y seleccionar con motivo, no por tamaño.
- G6 — Producir un plan de implementación por fases, cada una con sus once apartados.
- G7 — Identificar los riesgos de implementar las correcciones propuestas.
- G8 — Declarar la información insuficiente en lugar de inferirla.
non_goals:
- Modificar código de producción, modificar tests o crear commits de implementación.
- Ejecutar una implementación parcial de las soluciones.
- Decidir el modelo de despliegue de los servidores, que es una decisión del propietario y no un hecho derivable.
- Sustituir a RFC-T009; esta RFC define su contenido técnico y su orden interno, pero T009 sigue siendo la que lo autorice y lo cierre.
- Cerrar las deudas preexistentes que no son dependencia del plan.
- Unificar T006 con RC-4; sus causas son de contrato, no de sujeto, y fusionarlas acoplaría módulos que no comparten frontera.
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional:
  - specs/RFC.md
  - specs/LIFECYCLE.md
  - specs/TESTS.md
  - specs/FINDING.md
  - specs/EVIDENCE.md
  - specs/SUMMARY.md
proposed_architecture: >-
  No aplicable a una RFC de análisis. El cambio arquitectónico que cada corrección requiere se
  declara en el apartado `architectural_change` de su fase, y el objeto que falta en COSA —un
  principal acotado— se nombra en RC-4. Diseñarlo e implementarlo corresponde a las RFC derivadas.
abi_api_contracts: >-
  No aplicable: esta RFC no crea ni modifica contratos. Los que cada fase cambiaría, extendería o
  mantendría se declaran en su apartado `contracts`, incluida la indicación expresa de ruptura.
new_module: null
ownership_changes: >-
  Las tres correcciones mueven la responsabilidad al componente que posee la frontera, y en ningún
  caso coincide con el que detectó el fallo. La garantía del contrato wire pasa del productor al
  consumidor. La unicidad del binding identidad↔descriptor pasa de la allowlist a la tabla de
  peers, que es quien la posee y quien ya opera bajo su lock. El confinamiento pasa del trabajador
  efímero de un solo propósito al spawn de init y al proceso que sostiene la identidad.
dependency_rules: >-
  No aplicable a una RFC de análisis: no se alteran las reglas de dependencia entre módulos. El
  orden necesario entre correcciones se declara en `dependencies` de cada fase y se desarrolla en
  «Correlación y dependencias».
actions: []
migration_plan: >-
  No aplicable: no hay migración de datos ni de esquema. El plan es `implementation_plan.phases`.
benefits:
  architectural: >-
    Nombra el objeto que falta —un principal acotado que sea a la vez la identidad, el proceso OS y
    el dominio de confinamiento— y convierte la arista prohibida del mapa de fronteras de
    docs/security.md de prohibición declarada en prohibición estructural.
  engineering: >-
    Dos de las tres fases son abordables hoy, con cambios acotados y sin contratos nuevos: la Fase 1
    reutiliza una función de validación que ya existe en el mismo fichero que el decoder, y la Fase
    2 añade una comprobación dentro de una sección crítica que ya opera sobre datos que ya están.
  ai: >-
    Cada fase queda especificada con los once apartados y con su criterio de cierre medible,
    suficiente para ejecutarla como RFC de corrección independiente sin reconstruir el análisis.
risks:
- id: R1
  risk: Corregir el test sin corregir la vulnerabilidad.
  phases: [1, 2, 3]
  materialization: Adaptar las aserciones de security_t006, security_t007 o T005 para que pasen.
  mitigation: Los tres criterios de cierre exigen verde sin modificar el test, salvo donde el plan declara la modificación como consecuencia autorizada en la RFC de implementación.
- id: R2
  risk: Cerrar con una solución insuficiente.
  phases: [3]
  materialization: Encauzar remove por el trabajador confinado de forma aislada, o instalar seccomp en el anfitrión sin haber movido antes las mutaciones; el actor sigue pudiendo emitir la syscall directa.
  mitigation: Esas dos correcciones se rechazan de forma razonada en «Alternativas de corrección»; el criterio de cierre de la Fase 3 mide la syscall directa fallando, no el handler confinado.
- id: R3
  risk: Duplicar enforcement.
  phases: [1]
  materialization: Validar el cuerpo también en AgentEndpoint, o comprobar el separador también allí.
  mitigation: Un solo punto por contrato, el decoder para el cuerpo y los extractores para el framing.
- id: R4
  risk: Mover responsabilidades al componente equivocado.
  phases: [2]
  materialization: Poner la unicidad en la allowlist, que no ve la tabla de peers y no puede expresarla.
  mitigation: La unicidad es una propiedad de la tabla de bindings; va en el componente que la posee y que ya la bloquea.
- id: R5
  risk: Introducir nuevas fronteras de confianza incorrectas.
  phases: [3]
  materialization: Confiar en que el binario lanzado instala su propio confinamiento, o en un pid_t aportado por el propio servicio.
  mitigation: El confinamiento se instala entre el fork y el execvp, en init; el PID lo lee el kernel del transporte, nunca del peer.
- id: R6
  risk: Crear bypasses alternativos.
  phases: [1]
  materialization: Endurecer solo la ruta del kernel y dejar permisiva la del servidor; son dos rutas de producción vivas.
  mitigation: La alternativa seleccionada exige las dos rutas, y el criterio de cierre pide un test de integración por ruta.
- id: R7
  risk: Generar compatibilidad accidental con comportamientos inseguros.
  phases: [1]
  materialization: Conservar el fallback canónico de manera que un separador inválido con longitud cero caiga en él.
  mitigation: Distinguir los tres casos del framing y testear el de routing ausente por separado del de routing mal terminada.
- id: R8
  risk: Romper IPC existente.
  phases: [1, 2]
  materialization: Un consumidor que dependa de decodificar una operación vacía, o un servidor que abra dos conexiones con el mismo ServerId.
  mitigation: El único productor medido de routed payloads valida antes de escribir; la comprobación previa de la segunda condición es obligatoria y está listada en la Fase 2.
- id: R9
  risk: Introducir estados inconsistentes.
  phases: [2]
  materialization: Rehúsar el registro y dejar la capability concedida, o el descriptor verificado a medias.
  mitigation: El rechazo va antes del grant y dentro del mismo lock.
- id: R10
  risk: Introducir una denegación de servicio como efecto de la corrección.
  phases: [2]
  materialization: La exclusividad convierte la suplantación silenciosa en bloqueo del legítimo; si el suplantado no está vivo, el atacante reclama primero su identidad.
  mitigation: Declarado como límite de la alternativa seleccionada; el criterio de cierre de la Fase 2 lo registra por escrito y nombra el destino arquitectónico que lo resuelve.
- id: R11
  risk: Confundir malformed con unauthorized.
  phases: [1]
  materialization: Publicar el rechazo de contrato como un enrutamiento denegado o como una denegación de capability.
  mitigation: Subcódigo y registro de auditoría propios, distinguibles de los motivos existentes.
- id: R12
  risk: Perder visibilidad en las métricas.
  phases: [1]
  materialization: Un rechazo nuevo que no incremente ningún contador, repitiendo en un sitio nuevo una deuda ya registrada.
  mitigation: La categoría del rechazo nuevo debe ser de las que el punto de auditoría cuenta como denegación.
- id: R13
  risk: Regresión en T008.
  phases: [3]
  materialization: El paso que unifica las mutaciones toca el fichero donde vive la corrección de open_append.
  mitigation: T008 entra en la regresión obligatoria de la Fase 3 y se conserva el vocabulario de errno por enlace de tres vías.
- id: R14
  risk: Cierre parcial no declarado.
  phases: [3]
  materialization: Mantener parte de la composición dentro del proceso del kernel y declarar T005 cerrada.
  mitigation: Lo que queda dentro sigue sin estar confinado y debe decirse; un cierre parcial no declarado es peor que una deuda declarada.
- id: R15
  risk: Deuda de rendimiento.
  phases: [3]
  materialization: Un fork por mutación de fichero en un proyecto con disciplina zero-alloc y zero-copy en el hot path.
  mitigation: Medir antes de adoptar; es una restricción permanente del proyecto y la Fase 3 la toca de frente.
alternatives_considered:
- root_cause: RC-1
  selected: A1
  alternatives:
    A1:
      componente: El decoder del contrato, en libs/common.
      mecanismo: Aplicar sobre la vista de la operación la regla de validez que ya existe en el mismo TU y devolver el estado de operación inválida.
      ventaja: Único punto por el que pasa todo consumidor; reutiliza la regla existente en lugar de duplicarla; zero-copy y zero-alloc intactos, una pasada sobre un número acotado de bytes.
      riesgo: Cambia la postcondición documentada del decoder.
      contratos: El estado de operación inválida ya existe y lo devuelve el encoder, así que no hay valor nuevo; cambia el conjunto de errores que el decoder puede producir.
      compatibilidad: Un llamador en producción y tres ficheros de test; los casos de T006 que hoy esperan éxito pasan a esperar rechazo, que es el hallazgo corregido y no una regresión.
      seguridad: Cierra F1 en la frontera correcta.
      complejidad: Baja.
      efectos_secundarios: El rechazo solo pasa a categoría de seguridad si el endpoint traduce el estado; hay que decidirlo, y es el punto 4 del cambio de implementación de la Fase 1.
    A2:
      componente: El endpoint del kernel.
      mecanismo: Comprobar la operación del cuerpo ya decodificado.
      ventaja: No toca libs/common.
      riesgo: Pone conocimiento de contrato en un componente cuya documentación declara que no tiene veredicto propio.
      contratos: Ninguno.
      compatibilidad: Como A1, en menor medida.
      seguridad: Cierra F1 solo en la ruta del kernel.
      complejidad: Baja.
      efectos_secundarios: Un segundo consumidor futuro repite el hueco.
    A3:
      componente: Los dos anteriores.
      mecanismo: A1 más A2.
      ventaja: Defensa en profundidad.
      riesgo: Duplica enforcement, que es uno de los riesgos que la orden de trabajo pide vigilar.
      contratos: Como A1.
      compatibilidad: Como A1.
      seguridad: Cierra F1.
      complejidad: Baja.
      efectos_secundarios: Divergencia eventual entre las dos copias.
  rejection: A2 se rechaza por ubicación, porque mover responsabilidades al componente equivocado es un riesgo declarado; A3, por duplicación.
- root_cause: RC-2
  selected: B1 ahora, con B3 como destino declarado y decisión separada.
  alternatives:
    B1:
      componente: Los dos extractores de la routing string, en libs/core y libs/server.
      mecanismo: Distinguir tres casos, sin bytes de routing con el fallback canónico que se conserva, terminada en NUL como válida, y parada en un byte distinto de NUL o en fin de buffer con bytes presentes como rechazo.
      ventaja: Enforcement en el componente dueño del scan y cobertura de las dos rutas de producción.
      riesgo: Cambio de firma, porque una vista no puede expresar fallo; hay que pasar a un tipo que sí y adaptar los cuatro llamadores.
      contratos: Las dos funciones son privadas de TU, así que no son contratos públicos; sí cambia el observable, un frame mal separado produce rechazo en vez de entrega.
      compatibilidad: El único productor medido escribe un NUL real y ya está fijado por aserciones, así que ningún productor legítimo del árbol se rompe; debe conservarse el REQUEST sin routing string.
      seguridad: Cierra F2 en las dos rutas.
      complejidad: Media-baja.
      efectos_secundarios: El rechazo necesita un subcódigo y un registro de auditoría propios, distinguibles del enrutamiento denegado.
    B2:
      componente: El endpoint del kernel.
      mecanismo: Verificar el byte separador antes de re-derivar aritméticamente el offset del cuerpo.
      ventaja: Mínimo, local y sin cambio de firma.
      riesgo: Deja permisiva la ruta del servidor; el test de T006 compone las dos y seguiría rojo.
      contratos: Ninguno.
      compatibilidad: Como B1.
      seguridad: Cierra F2 solo en la ruta del kernel.
      complejidad: Baja.
      efectos_secundarios: Falsa sensación de cierre.
    B3:
      componente: Un hogar compartido nuevo más los dos consumidores.
      mecanismo: Como B1, con una sola implementación.
      ventaja: Elimina la duplicación, que es la causa arquitectónica; una sola autoridad para el layout del frame.
      riesgo: Refactor de dependencias entre módulos que hoy ni siquiera comparten tipos de entrada.
      contratos: Nuevo contrato de módulo.
      compatibilidad: Como B1.
      seguridad: Cierra F2 y la clase de defecto.
      complejidad: Media-alta.
      efectos_secundarios: Toca el grafo de dependencias.
  rejection: >-
    B2 se rechaza como solución única por incompleta y como añadido a B1 por duplicar enforcement.
    B3 es lo arquitectónicamente correcto, porque la duplicación no es cosmética sino dos rutas
    vivas hacia handlers distintos, pero cambia dependencias de módulo y eso es un cambio de
    contrato que exige autorización propia; se registra como deuda de diseño y no se cuela en la
    Fase 1.
- root_cause: RC-3
  selected: C1 como enforcement inmediato, con C3 como destino arquitectónico.
  alternatives:
    C1:
      componente: El registro de peers en el gestor de IPC del kernel.
      mecanismo: Bajo el lock existente y antes del grant, recorrer la tabla y rehusar si otra entrada viva ya sostiene la identidad reclamada.
      ventaja: Sin cambio de contratos, con los datos ya disponibles en el registro del peer; atómico bajo un lock existente; el binding se libera al caer el descriptor, así que un reinicio legítimo no queda bloqueado.
      riesgo: Convierte la suplantación silenciosa en denegación de servicio y hace la identidad exclusiva, no correcta.
      contratos: Ninguno en la política de identidad; sí en el observable del registro de peer, un motivo de rechazo adicional sobre un handler que ya tiene cuatro.
      compatibilidad: Un solo descriptor registrado por identidad; ningún servidor del árbol abre hoy dos conexiones con el mismo ServerId, y hay que verificarlo antes de darlo por cierto.
      seguridad: Cierra el ataque medido.
      complejidad: Baja.
      efectos_secundarios: Hay que decidir el subcódigo y si el rechazo se audita con un veredicto nuevo.
    C2:
      componente: La política de identidad y quien aporte el PID.
      mecanismo: Incluir el PID en la clave del binding y rehusar una segunda identidad por PID o un segundo binding por identidad.
      ventaja: Expresa literalmente que el principal es el proceso.
      riesgo: La reutilización de PIDs del SO puede autorizar a un proceso distinto con una entrada obsoleta, y exige que el kernel sepa qué PID tendrá cada servicio cuando quien los lanza es init, un hueco de información entre procesos que hoy no tiene canal.
      contratos: Cambia la interfaz de la política de identidad o le añade estado de tabla.
      compatibilidad: Rompe cualquier composición que registre la misma identidad desde varios procesos, tests incluidos.
      seguridad: Cierra el ataque medido y el de primer llegado, si el origen del PID es de confianza.
      complejidad: Alta.
      efectos_secundarios: Ninguno adicional registrado.
    C3:
      componente: El fichero de topología, la autorización de topología y el gestor de procesos de init.
      mecanismo: Cada servicio corre bajo su propio usuario; init cambia de usuario antes de ejecutar y la allowlist discrimina de verdad.
      ventaja: Es la única que también fortalece T005, porque un usuario distinto por servicio es una frontera OS real y más barata que los namespaces; cierra RC-3a y reduce RC-4.
      riesgo: Necesita usuarios del sistema, un cambio de usuario en init que hoy no existe, y cambiar el fichero de topología; es una decisión de despliegue.
      contratos: Cambia el contrato del fichero de topología con un campo de usuario por endpoint.
      compatibilidad: Rompe el despliegue actual de un solo usuario.
      seguridad: Cierra los dos ataques y añade aislamiento OS.
      complejidad: Alta.
      efectos_secundarios: init pasa a necesitar privilegios para cambiar de usuario.
    C4:
      componente: La documentación de seguridad y la especificación de T007.
      mecanismo: Declarar que dentro de un UID todas las identidades son equivalentes.
      ventaja: Cero código.
      riesgo: Abandona la propiedad en lugar de satisfacerla; la política sensible a identidad pasa a ser decorativa frente a un atacante del mismo UID, que es justo lo que el diseño de T007 usa como única frontera entre los dos actores.
      contratos: Ninguno.
      compatibilidad: Rompe el invariante de identidad verificada y el mapa de amenazas tal como están escritos.
      seguridad: No cierra nada.
      complejidad: Nula.
      efectos_secundarios: Deuda de coherencia documental permanente.
  rejection: >-
    C2 se rechaza porque su riesgo de reutilización de PID y su hueco de información entre init y el
    kernel no compensan frente a C1 más C3. C4 se rechaza porque reescribir la especificación para
    declarar que el principal es el UID cerraría el test sin cerrar la vulnerabilidad.
  limitation: >-
    C1 garantiza unicidad, no atribución: tras ella, quién sostiene una identidad sigue siendo quien
    llegó primero. La propiedad de T007 queda satisfecha en su letra y solo parcialmente en su
    espíritu; únicamente C3 la completa. Es la clase de garantía incompleta que no debe disfrazarse
    de cierre.
- root_cause: RC-4
  selected: D1 como eje, con D3 como complemento y D4 como prerequisito interno de la Fase 3.
  alternatives:
    D1:
      componente: El gestor de procesos de init y la maquinaria de confinamiento existente del SAL.
      mecanismo: Instalar los límites de recursos, la prohibición de nuevos privilegios y el filtro entre el fork y el execvp, o vía lanzador.
      ventaja: Reutiliza un confinamiento ya implementado y testeado, y es la mitigación que el modelo de seguridad prescribe para un servidor comprometido.
      riesgo: Cambia el modelo de alojamiento; hoy la composición es en el proceso y todo servidor pasaría a hablar IPC para todo.
      contratos: Cambia el modelo de la interfaz de servidor, de dentro del proceso a fuera.
      complejidad: Alta.
      veredicto: Candidato principal.
    D2:
      componente: El mismo, más el montaje.
      mecanismo: Crear namespaces de montaje, PID y red y pivotar la raíz a la región protegida.
      ventaja: Es la más fuerte; el recurso protegido deja de ser visible.
      riesgo: Necesita privilegios o user namespaces, y no hay una sola línea de namespaces en el árbol.
      contratos: Como D1, más el despliegue.
      complejidad: Muy alta.
      veredicto: Candidato si el despliegue lo permite.
    D3:
      componente: El arranque del proceso anfitrión.
      mecanismo: Un ruleset de Landlock sobre la región protegida, sin fork.
      ventaja: Sin fork y sin privilegios, se instala sobre el proceso que formula la solicitud, que es justo el hueco que T005 mide.
      riesgo: Exige un kernel reciente, no hay código de Landlock en el árbol y solo cubre ficheros.
      contratos: Nuevo mecanismo en el SAL.
      complejidad: Media.
      veredicto: Complemento valioso de D1.
    D4:
      componente: La mutación de ficheros del SAL.
      mecanismo: Que la eliminación ocurra en el trabajador confinado, como ya ocurre con la apertura para escritura.
      ventaja: Pequeña, y hace coherente el tratamiento de las dos mutaciones, que hoy diverge.
      riesgo: No cierra T005; el ataque es la syscall directa del actor, no una llamada al componente mediado.
      contratos: Ninguno.
      complejidad: Baja.
      veredicto: Prerequisito de D5, no alternativa.
    D5:
      componente: El arranque del proceso anfitrión.
      mecanismo: Una whitelist de syscalls en el proceso que sostiene la identidad.
      ventaja: Ataca directamente la syscall arbitraria desde el proceso anfitrión.
      riesgo: >-
        Inviable tal cual: el único filtro del árbol es de tres syscalls y vive en un hijo de un
        solo disparo, y un filtro que permita la región y prohiba el resto no puede expresarlo,
        porque el mecanismo ve números y escalares y no rutas; habría que negar por completo las
        syscalls de eliminación y se rompería la ruta legítima.
      contratos: Nuevo mecanismo en el SAL.
      complejidad: Alta y mal definida.
      veredicto: Solo viable tras D4.
  rejection: >-
    D4 aislado no cierra T005: confinar el handler confina aún más la vía mediada mientras el actor
    sigue pudiendo emitir la syscall directa por su cuenta. Es el caso literal del riesgo de
    corregir el test sin corregir la vulnerabilidad. Sí merece hacerse por coherencia propia, pero
    debe etiquetarse como lo que es. D4 es además prerequisito de D5 y no su alternativa, porque
    para retirar la syscall al proceso anfitrión hay que haber movido antes la mutación legítima a
    otro sitio, y ese sitio es el trabajador confinado, cuya whitelist hay que extender, lo que es
    un diseño y no un enrutamiento. D5 sin D4 se rechaza por inviable. D1 sin la Fase 2 es
    contraproducente. La elección entre D1 y D2 depende de la decisión de despliegue y no puede
    tomarse en esta RFC.
  limitation: >-
    Para RC-4 la evaluación registrada tiene siete atributos y un veredicto, no los nueve que pide
    la orden de trabajo: compatibilidad, seguridad y efectos secundarios no se evaluaron por
    separado para D1 a D5. Se declara en lugar de completarlo por inferencia.
consequences: >-
  Tres correcciones derivadas, dos abordables hoy y una bloqueada por una decisión de despliegue
  que no es técnica. La exclusividad del binding introduce una denegación de servicio posible,
  declarada como límite y no resuelta. Quedan registradas las deudas que el plan no cierra y tres
  defectos de documentación medidos durante el análisis.
documentation_impact: >-
  Tres defectos medidos en «Defectos de documentación». Además, el criterio de cierre de la Fase 3
  exige re-anclar la arista prohibida del mapa de fronteras y el punto del modelo de seguridad que
  declara la autoridad establecida solo por registro, y actualizar el addendum de T005 para decir
  que la deuda quedó eliminada, con la medición que lo respalda. Los addenda se fechan, no se
  reescriben.
testing: >-
  Esta RFC es de análisis: produce sus propios entregables y comprobaciones y no simula
  compilaciones ni pruebas de COSA. Sus comprobaciones son la verificación línea a línea del código
  de producción, las búsquedas negativas en todo el árbol y la reproducción ya medida por los tres
  tests. Los tests que cada fase debe modificar, añadir y preservar se declaran en su apartado
  `tests`, y el protocolo común de verificación, en «Criterios de cierre y verificación».
acceptance_criteria:
- id: C1
  condition: El informe contiene los doce apartados que exige la orden de trabajo.
  covers: [G1, G2, G3, G4, G5, G6, G7, G8]
  verification: La tabla de «Apartados del informe» asigna cada uno a su lugar en esta RFC o en su resumen.
- id: C2
  condition: Existe la matriz de trazabilidad RFC-Txxx → hallazgo → causa raíz → componente → corrección → tests → fase.
  covers: [G2, G4, G6]
  verification: La sección «Matriz de trazabilidad», con sus siete columnas y una fila por hallazgo.
- id: C3
  condition: Cada causa raíz tiene su evidencia y su componente afectado.
  covers: [G2, G3]
  verification: Los cuatro elementos de `root_causes`, cada uno con `component` y `evidence`.
- id: C4
  condition: El plan está dividido en fases y cada fase especifica los once apartados.
  covers: [G6]
  verification: Los tres elementos de `implementation_plan.phases`, comprobados contra la lista de RFC-A_TEMPLATE.md.
- id: C5
  condition: Toda causa raíz tiene sus alternativas evaluadas y una selección motivada; donde la evaluación registrada es incompleta, se declara en lugar de completarla por inferencia.
  covers: [G5]
  verification: Los cuatro elementos de `alternatives_considered`, con su `selected`, su `rejection` y, en RC-4, su `limitation`.
- id: C6
  condition: La información insuficiente se declara explícitamente en lugar de inferirla.
  covers: [G8]
  verification: La sección «Información insuficiente», con sus cuatro puntos y el hecho ya resuelto.
- id: C7
  condition: No se modifica código de producción, no se modifican tests y no se crean commits de implementación.
  covers: [G1, G2, G3, G4, G5, G6, G7, G8]
  verification: El alcance de esta RFC es documental; lo acredita el estado del árbol de COSA, que no cambia por este análisis.
- id: C8
  condition: Ningún hallazgo se cierra únicamente porque su test pueda hacerse pasar.
  covers: [G5, G7]
  verification: Los rechazos razonados de la alternativa C4 de RC-3 y de D4 aislado y D5 sin D4, y R1 y R2 con su mitigación.
references:
- path: 'docs/analisis/analysis/RFC-A00001 — Security Findings Analysis: T005, T006 and T007.md'
  role: Orden de trabajo que fija los doce apartados del informe y las restricciones de esta RFC.
- path: 'docs/analisis/analysis/RFC-A00001 — Security Findings Analysis: T005, T006 and T007 - Summary.md'
  role: Informe producido, con la narrativa y las mediciones que esta RFC no reproduce.
- path: tasks/TASK-00001.md
  role: TASK que registra este análisis y su memoria derivada en el proyecto.
```

Los identificadores `C1` a `C8` de `acceptance_criteria` son los que referencia `TASK-00001`. No
deben confundirse con las alternativas `A1` a `A3`, `B1` a `B3`, `C1` a `C4` y `D1` a `D5` de
`alternatives_considered`, que conservan la numeración del análisis original y se nombran siempre
dentro de su causa raíz.

`actions` queda vacío. Las tres fases del plan no son acciones derivadas de esta RFC de análisis,
sino el contenido de las RFC de corrección que de ella se deriven; cada una conservará su
identificador y su relación `derives` con esta. Registrar una acción consume el contador `action`
del manifest del proyecto y corresponde a `hactors create-action`, no a la redacción del documento.

## Campos específicos de análisis

```yaml
analysis_scope: >-
  Los tres hallazgos de seguridad medidos por RFC-T005, RFC-T006 y RFC-T007 sobre COSA, y el código
  de producción que los permite. Se examinan la validación del contrato wire en libs/common, el
  layout del frame y sus dos rutas de consumo en libs/core, libs/server y kernel, la resolución y
  el registro de la identidad de peer en kernel, y la creación y el confinamiento del sujeto que
  ejecuta en init, libs/process y libs/sal/linux. Quedan fuera el Executor, la Policy y la admisión
  por capability, verificados como correctos, y las deudas preexistentes que no son dependencia del
  plan.
data_sources:
- 'docs/analisis/tests/RFC-T005 — Security Test 05: Compromised Process Cannot Bypass Executor - Summary.md'
- 'docs/analisis/tests/RFC-T006 — Security Test 06: Invalid IPC Message Is Rejected by Contract Validation - Summary.md'
- 'docs/analisis/tests/RFC-T007 — Security Test 07: Identity Spoofing Does Not Grant Authorization - Summary.md'
- 'docs/analisis/tests/RFC-T005 — Security Test 05: Compromised Process Cannot Bypass Executor.md'
- 'docs/analisis/tests/RFC-T006 — Security Test 06: Invalid IPC Message Is Rejected by Contract Validation.md'
- 'docs/analisis/tests/RFC-T007 — Security Test 07: Identity Spoofing Does Not Grant Authorization.md'
- docs/security.md, con sus addenda de T005, T006, T007 y T008.
- El TODO.md de la raíz de COSA, por las deudas preexistentes que hay que distinguir de las dependencias.
- El código de producción del árbol `dev` en `c0c5610`, verificado línea a línea para este informe.
methodology: >-
  Reconstrucción de hechos a partir de los tests y de sus documentos de especificación; verificación
  línea a línea del código de producción y búsquedas negativas en todo el árbol; separación
  explícita, para cada hallazgo, entre síntoma observado, causa técnica, causa arquitectónica y
  consecuencia de seguridad; correlación entre hallazgos para evitar soluciones duplicadas;
  evaluación de alternativas por causa raíz; y declaración de la información insuficiente en lugar
  de inferirla. Ningún cambio se propone a partir del nombre de una clase ni de la intención
  documentada; se verifica el comportamiento real del código, y no se asume que el componente que
  detecta el fallo sea el que debe corregirlo.
root_causes:
- id: RC-1
  statement: El contrato del cuerpo se valida al producir, no al consumir.
  findings: [T006-F1]
  component: El decoder de AgentRequest en libs/common, que no llama a la regla de validez de la operación pese a existir, ser correcta y estar en el mismo TU.
  evidence: La regla existe y la usan el setter y el encoder; el decoder valida solo geometría —tamaño mínimo, versión, bytes reservados, longitudes y buffer— y construye las vistas sobre el wire sin inspeccionar un solo byte del contenido. La asimetría está documentada en el propio fichero como si fuera el diseño.
  boundary: El socket entre el servidor y el kernel.
  unvalidated_authority: Los bytes del cuerpo, porque quien los escribió es un encoder que sí valida, pero está en otro proceso y por tanto fuera del dominio de confianza.
- id: RC-2
  statement: El layout del frame no tiene dueño único y el separador de enrutamiento se infiere en lugar de verificarse.
  findings: [T006-F2]
  component: Dos extractores independientes y byte a byte equivalentes, uno en libs/core y otro en libs/server, más una re-derivación aritmética del offset del cuerpo en el endpoint del kernel.
  evidence: El bucle de scan se detiene en tres condiciones distintas —NUL, byte de control y fin de buffer— y en las tres devuelve el prefijo acumulado como si fuera una routing string válida; ninguna rama comprueba que el byte que lo detuvo sea NUL. El endpoint suma un byte al offset sin inspeccionarlo nunca. El productor sí escribe un NUL real y sus tests ya lo fijan con aserciones.
  boundary: El socket entre el servidor y el kernel.
  unvalidated_authority: La estructura del frame, garantizada por el productor y testeada en el productor, pero no exigida en ningún consumidor.
  note: >-
    RC-1 y RC-2 son dos instancias de la misma forma —una garantía sostenida en el lado equivocado
    de una frontera de confianza— sobre dos contratos distintos y en tres módulos distintos.
    Comparten diagnóstico y test, no código, y por eso son una sola fase con dos partes y no una
    fusión artificial.
- id: RC-3
  statement: La identidad es una reclamación autorizada contra un atributo OS demasiado grueso, y el binding no es exclusivo.
  findings: [T007-F1]
  component: >-
    Dos mitades que se corrigen en sitios distintos. RC-3a, la granularidad: la allowlist se indexa
    por uid y ServerId con un único uid para toda la topología, en la raíz de composición del
    kernel, en la autorización de topología y en la política de identidad. RC-3b, la exclusividad:
    la elegibilidad de registro es por descriptor en el gestor de IPC, sin unicidad de la identidad
    reclamada entre los descriptores vivos.
  evidence: >-
    El PID se comprueba como prueba de vida y se descarta, así que la clave efectiva de la allowlist
    es el par uid e identidad reclamada; todos los endpoints de la topología se registran con el
    mismo uid. La única condición de elegibilidad de registro es que ese descriptor aún no se haya
    registrado: nada consulta si la identidad ya está vinculada a otro descriptor vivo. RC-3b es la
    que produce el ataque medido y la que se puede cerrar sin cambiar contratos; RC-3a es la que
    determina si el cierre es completo o solo del caso medido.
  boundary: El registro de peer en el transporte, y la allowlist que lo autoriza.
  unvalidated_authority: >-
    La reclamación de identidad de un proceso del mismo usuario, aceptada porque la allowlist no
    distingue sujetos. Lo que el transporte verifica contra el kernel es correcto, pero no distingue
    al atacante del suplantado.
  note: >-
    La unicidad de un binding es una propiedad de la tabla de bindings, no de la allowlist: la
    interfaz de la política es constante, recibe credenciales e identidad reclamada y no ve la
    tabla, así que no puede expresar que esa identidad ya está viva en otro descriptor, y dárselo
    filtraría estado de tabla hacia un objeto cuya responsabilidad es decidir sobre la allowlist.
- id: RC-4
  statement: COSA no tiene un sujeto acotado; la entidad que sostiene la autoridad no es la entidad que está acotada.
  findings: [T005, T007]
  component: >-
    Falta un objeto que sea a la vez la identidad, el proceso OS y el dominio de confinamiento.
    COSA tiene identidades, credenciales de peer, tokens de capability y un trabajador efímero
    confinado, pero ningún principal acotado.
  evidence: >-
    En T007 la autoridad es el ServerId con su capability de sesión y el enforcement es el
    descriptor, con un binding por descriptor, no exclusivo y renovable a voluntad. En T005 la
    autoridad es de nuevo el ServerId con su capability y el enforcement es el hijo efímero del
    trabajador confinado, vinculado solo para la apertura para escritura, mientras la eliminación y
    todo lo demás quedan fuera. El proceso que sostiene la identidad es un hilo en el espacio de
    direcciones del creador, el confinamiento se instala en el hijo de un fork y nunca en el proceso
    que formula la solicitud, la mutación de ficheros se ejecuta en el proceso anfitrión, y entre el
    fork y el execvp del gestor de procesos de init no se instala ningún confinamiento.
  boundary: La frontera del proceso OS, que hoy no existe como frontera propia de COSA.
  unvalidated_authority: >-
    La autoridad concedida a un ServerId y confiada a un proceso, sin que nada vincule el sujeto de
    la autoridad con el sujeto del confinamiento.
  chain: 'ServerId ──(?)── proceso OS ──(?)── dominio de confinamiento; T007 es el primer eslabón roto y T005 el segundo.'
  note: >-
    De aquí sale la dependencia dura del plan: cerrar el segundo eslabón sin cerrar el primero
    desplaza el ataque de T005 hacia el de T007. Un servidor confinado en su propio proceso OS que
    pueda abrir una segunda conexión y reclamar otro ServerId no ha ganado nada: ha cambiado la
    syscall directa por pedirla con otra identidad, que es exactamente la vía mediada que el
    confinamiento no limita. T006 no participa de RC-4.
implementation_plan:
  phases:
  - id: fase-1
    name: Contrato wire verificado en el consumidor
    objective: >-
      Restaurar la propiedad de que un payload inválido no es una solicitud COSA válida: que todo
      mensaje cuyo cuerpo o cuyo framing incumpla el contrato se rechace antes de la admisión, sin
      alcanzar la lógica de negocio y sin producir efecto.
    rfcs_covered: [RFC-T006]
    findings: [T006-F1, T006-F2]
    root_causes: [RC-1, RC-2]
    components:
    - El decoder y su cabecera en libs/common, para validar el contenido y documentar la nueva postcondición.
    - El extractor de la routing string de libs/core y sus dos llamadores.
    - El extractor de la routing string de libs/server y sus dos llamadores.
    - El endpoint del kernel, para traducir el nuevo estado a una categoría de error y registrarla.
    - Tests existentes a revisar en libs/common, libs/server y libs/core, y los dos tests de seguridad que usan el decoder.
    architectural_change: >-
      Mover la garantía del contrato del productor al consumidor. La frontera de confianza es el
      socket: lo que el encoder valida en un proceso no es una propiedad del wire en otro. Es la
      generalización del invariante que ya prohíbe tomar la identidad de una cabecera, aplicada a
      los campos de contrato. Secundariamente, establecer que un scan que se detiene no ha
      encontrado un terminador, que es el supuesto implícito que hace equivalente un NUL y un byte
      de control.
    implementation_change:
    - 'Decoder: aplicar la regla de validez existente sobre la vista de la operación antes de devolverla y producir el estado de operación inválida, sin copia ni asignación.'
    - 'Extractores: distinguir tres casos y no colapsarlos — routing ausente conserva el fallback canónico porque es una forma de frame legítima; terminada en NUL devuelve la vista; parada en un byte de control distinto de NUL o en fin de buffer con bytes presentes rechaza. Exige cambiar el tipo de retorno de las dos funciones privadas y adaptar sus cuatro llamadores.'
    - 'Rechazo en el pipeline: convertirlo en un código devuelto antes de cualquier entrega, con su línea de auditoría y su registro de traza propios; no reutilizar el motivo de enrutamiento denegado, porque mezclarlos perdería la distinción en la pista.'
    - 'Categoría del error: decidir y documentar qué categoría produce cada rechazo nuevo, de forma que cuente como denegación; un rechazo que no cuente reproduce una deuda ya registrada en un sitio nuevo.'
    enforcement: >-
      Exactamente dos puntos, ambos en el consumidor: el decoder para el cuerpo y los dos
      extractores para el framing. Ninguno en el productor, que ya cumple y ya está testeado, y
      ninguno en el endpoint más allá de traducir el estado, para no duplicar.
    contracts: >-
      No se crea ninguno. El estado de operación inválida ya existe. Cambian dos postcondiciones
      documentadas: la del decoder, que ahora puede rechazar por contenido, y la de los dos
      extractores, que ahora pueden fallar. Las dos funciones de extracción son privadas de TU, así
      que el cambio de firma no es un cambio de contrato público. La firma del decoder no cambia.
    compatibility:
      preserved:
      - Todo frame producido por el constructor de mensajes del servidor, que escribe un NUL real y ya está fijado por aserciones.
      - El REQUEST y el EVENT sin routing string y su fallback al nombre canónico.
      - Los rechazos por cuerpo malformado que T006 ya verifica como correctos, el control positivo y las zero-copy del decoder.
      rejected:
      - Operación vacía o con bytes no imprimibles en el cuerpo.
      - Separador distinto de NUL.
      - Routing string sin terminar.
      measured_risk: >-
        El único productor de routed payloads del árbol es el constructor de mensajes del servidor,
        con dos llamadores; no hay un tercer productor que dependa del comportamiento permisivo.
    tests:
      to_modify: >-
        Los casos del test del contrato que decodifican cuerpos con operación inválida esperando
        éxito, si existen; hay que comprobarlo antes de tocar nada, porque si no existen la
        cobertura nueva es aditiva.
      to_add_unit:
      - El decoder rechaza una operación vacía, una con un byte de control y una con un byte por encima del rango imprimible, y acepta el límite máximo imprimible.
      - Los extractores rechazan un byte de control como separador y una routing string sin terminar, y aceptan routing ausente devolviendo el nombre canónico y un NUL real.
      to_add_integration:
      - Un frame con separador ilegítimo rechazado en la ruta del pipeline de entrada y en la del despachador de mensajes, por separado, porque son dos rutas de producción.
      must_pass_unmodified: >-
        Los diez casos del test de seguridad de T006. Modificarlos está prohibido por las
        restricciones de esta RFC: el verde tiene que venir de producción.
      regression: >-
        El test de seguridad de T007 usa el decoder; sus cuatro casos verdes deben seguir verdes.
    dependencies: >-
      Ninguna. Es la primera porque es la más acotada, la única sin cambio de contratos, y porque
      hacerla antes evita ambigüedad de atribución en T007.
    closure_criterion: >-
      El test de validación de contrato pasa 10/10 en ambos árboles sin que se haya modificado ni
      una línea del test; las suites completas no pierden ningún verde respecto de la baseline
      110/113 en Ninja y 107/110 en Makefiles, y los únicos rojos pasan a ser T005 y T007; los
      casos F1 y F2 incrementan el contador de denegaciones y producen un registro estructurado de
      rechazo; el control positivo sigue eliminando su archivo con ocho registros ordenados; y 20
      repeticiones con orden aleatorio y semilla 42 reproducen el mismo resultado en cada árbol.
  - id: fase-2
    name: Binding exclusivo identidad↔descriptor
    objective: >-
      Restaurar la propiedad de que una identidad autoafirmada no es una identidad autoritativa en
      la vía de registro: que una identidad verificada corresponda a un único sujeto vivo y que una
      conexión nueva no pueda adquirir una identidad que ya sostiene otra.
    rfcs_covered: [RFC-T007]
    findings: [T007-F1]
    root_causes: [RC-3b]
    components:
    - El gestor de IPC del kernel, en su rama de elegibilidad de registro y su enumeración de resultados.
    - La cabecera del registro de peer, que no necesita campos nuevos pero sí la documentación de la nueva invariante de la tabla.
    - La liberación del registro al caer el descriptor, para verificar que sigue siendo correcta y que la revocación de la capability de sesión continúa.
    - No la política de identidad, no su interfaz, no la autorización de topología y no la raíz de composición, porque la allowlist decide quién puede reclamar qué y la tabla decide quién lo sostiene ahora.
    architectural_change: >-
      Convertir una confianza implícita en garantía explícita. Hoy el kernel asume que una entrada
      de la allowlist se corresponde con un único sujeto vivo; esa suposición no está escrita en
      ningún sitio ni la comprueba nadie. Tras el cambio, la tabla de peers sostiene una invariante
      nombrada —a lo sumo un descriptor verificado por ServerId— comprobada atómicamente en el único
      punto que crea bindings. Es también el primer eslabón del principal acotado: el binding
      identidad↔descriptor se convierte en identidad↔sujeto y la Fase 3 le añade el PID y el dominio
      de confinamiento sin reescribirlo. Ése es el requisito de diseño que esta fase debe respetar:
      la comprobación debe expresarse sobre el sujeto, no sobre el descriptor, para que sustituir el
      sujeto por un proceso no obligue a rediseñarla.
    implementation_change:
    - 'Dentro del lock de sesiones existente, antes de consultar la allowlist y antes del grant de capability, recorrer la tabla buscando otra entrada con un descriptor distinto que esté verificada y sostenga la identidad reclamada. La tabla tiene capacidad acotada, así que el recorrido no asigna.'
    - 'Si existe, rehusar con un resultado nuevo de la enumeración, su línea de auditoría y su registro de traza con un veredicto distinguible de los existentes; la identidad reclamada y la que ya la sostiene deben quedar en el registro, porque es la evidencia que un operador necesita.'
    - 'Si no existe, continuar exactamente como hoy.'
    enforcement: >-
      En el punto que crea el binding, bajo el lock de sesiones y antes del grant. Es el único punto
      del sistema que crea un binding identidad↔descriptor, así que es el único donde la invariante
      puede garantizarse. Ningún enforcement en el pipeline de entrada ni en el endpoint: una vez
      que el binding es exclusivo, la resolución por descriptor ya es correcta y no hay que tocarla.
    contracts: >-
      Ninguno cambia. La interfaz de la política de identidad conserva su firma y su semántica.
      Cambia el observable del registro de peer con un motivo de rechazo adicional; si se considera
      que eso es un contrato de protocolo, es un contrato extensible por diseño, porque el handler
      ya tiene cuatro motivos de rechazo distintos, y no requiere autorización de cambio de firma.
    compatibility:
      preserved:
      - El registro legítimo de un descriptor no verificado y el re-registro tras una desconexión limpia.
      - La revocación de la capability de sesión al caer el descriptor.
      - La resolución de identidad por descriptor y su revalidación de la capability de sesión.
      - Los rechazos de cabecera y de cuerpo, que son los que sostienen los cuatro casos verdes de T007.
      rejected:
      - Un segundo descriptor verificado con el mismo ServerId.
      declared_limitation: >-
        Una conexión medio abierta, cuyo peer murió sin un cierre observable, retiene el binding
        hasta que el pipeline la detecta; durante esa ventana un reinicio legítimo del servicio
        sería rehusado. Es una propiedad preexistente de la tabla que esta fase hace visible al
        convertir la colisión en rechazo, pertenece a la familia de carreras que el modelo de
        seguridad ya lista y no se resuelve aquí.
      mandatory_precheck: >-
        Verificar antes de implementar que ningún servidor del árbol abre hoy dos conexiones con el
        mismo ServerId. Si alguno lo hace, esta fase lo rompe y hay que decidirlo antes.
    tests:
      to_modify: >-
        El caso del ataque por segunda conexión espera hoy el rojo y tras esta fase debe esperar el
        rechazo. Las restricciones de esta RFC prohíben modificar tests, así que esa modificación no
        es de esta fase: se declara como consecuencia necesaria y se autoriza en la RFC de
        implementación.
      to_add_unit:
      - Un segundo descriptor con una identidad ya viva se rechaza y se audita.
      - Un segundo descriptor con una identidad libre se acepta; es el caso de primer llegado, que la alternativa seleccionada no resuelve y que conviene fijar como comportamiento conocido.
      - Desconexión y re-registro se aceptan.
      - El rechazo no crea capability de sesión ni marca el descriptor como verificado.
      - La conexión original del atacante sigue resolviendo como su propia identidad después del rechazo.
      to_add_integration:
      - El ataque completo de T007, con dos procesos reales, credenciales del transporte y registro, y el recurso intacto.
      must_pass_unmodified: >-
        Los cuatro casos verdes de T007, los tests de la política de identidad, de la autorización de
        topología, de la seguridad del pipeline de entrada, de las credenciales de peer y del smoke
        de seguridad por IPC.
    dependencies: >-
      La Fase 1 antes, por atribución de tests. Debe preceder a la Fase 3 por la razón
      arquitectónica de RC-4.
    closure_criterion: >-
      El test de suplantación de identidad pasa 5/5 en ambos árboles; los cuatro casos verdes
      anteriores siguen verdes sin modificación; las suites completas no pierden ningún verde y el
      único rojo restante es T005; el caso de segunda conexión produce un registro de registro de
      peer con veredicto de colisión, cero grants nuevos, cero registros de admisión, de Executor y
      de handler, y el fingerprint del recurso intacto; la conexión original del atacante sigue
      resolviendo como su identidad; 20 repeticiones aleatorias con semilla 42 por árbol reproducen
      el resultado; y queda declarada por escrito la limitación de atribución junto con el destino
      arquitectónico que la cierra.
  - id: fase-3
    name: Sujeto de confinamiento, el proceso OS
    objective: >-
      Restaurar la propiedad de T005: que la ejecución efectiva de una operación no pueda
      producirse por un camino que evite el Executor. Equivalentemente, que el sujeto que sostiene
      una identidad no pueda emitir syscalls con efectos sobre recursos protegidos fuera de la vía
      mediada.
    rfcs_covered: [RFC-T005]
    findings: [T005]
    root_causes: [RC-4, RC-3a]
    components:
    - El spawn del gestor de procesos de init, que hoy no confina nada entre el fork y el execvp.
    - La maquinaria de confinamiento existente del SAL de Linux, hoy de un solo propósito.
    - La mutación de ficheros del SAL, que se ejecuta en el proceso anfitrión, y el handler que la publica sin sandbox.
    - El fichero de topología y su carga, si se adopta un usuario por endpoint.
    - La raíz de composición del kernel, con su único uid para toda la topología.
    - La abstracción de proceso, cuyo papel hay que decidir porque hoy es un hilo y el nombre promete algo que no entrega; o se renombra, o se documenta como concurrencia intra-proceso y se prohíbe su uso como sujeto de seguridad.
    architectural_change: >-
      Crear el principal acotado: una tupla de identidad, PID y dominio de confinamiento que init
      establezca en el spawn, que el kernel verifique en el registro y que ninguna de las dos partes
      pueda reclamar por separado. Cierra los dos eslabones de la cadena rota y convierte la arista
      prohibida del mapa de fronteras de prohibición declarada en prohibición estructural: la arista
      deja de existir porque el sujeto no puede emitirla.
    implementation_change:
    - '3.1 Decisión de despliegue, previa a todo código; es el punto bloqueante y no es técnico.'
    - '3.2 Unificar las mutaciones en el trabajador confinado, llevando la eliminación por el mismo camino que la apertura para escritura. Exige extender la whitelist del hijo, que hoy es de tres syscalls, o reestructurar el trabajador para que reciba el descriptor de la región ya abierto en un número fijo. Sin este paso, el 3.4 rompe la ruta legítima.'
    - '3.3 Producir sujetos distinguibles: spawn por servicio con el confinamiento instalado entre el fork y el execvp, reutilizando la maquinaria existente, que ya establece la prohibición de nuevos privilegios, prerequisito de cualquier filtro. Acompañar de un usuario por endpoint si la decisión 3.1 lo permite, que es lo que cierra RC-3a y lo que hace que el binding de la Fase 2 deje de ser de primer llegado.'
    - '3.4 Retirar capacidad al proceso anfitrión, con un filtro propio del servidor, con un ruleset de paths, o con ambos. Solo después de 3.2.'
    - '3.5 Reproducir el ataque entre procesos OS independientes, que es lo que T005 no pudo demostrar: el actor comprometido en un PID propio, contra un recurso protegido, con la vía mediada denegada y la syscall directa fallando.'
    enforcement: >-
      En la frontera del proceso OS, en dos puntos: antes del execvp en el spawn de init, con los
      límites de recursos, la prohibición de nuevos privilegios y el filtro o las credenciales, y en
      el trabajador confinado para cada mutación. No en el Executor, no en la Policy y no en la
      admisión por capability: los tres funcionan ya y reforzarlos no añade nada.
    contracts: >-
      Sí cambian, y hay que autorizarlo explícitamente: el modelo de alojamiento de la interfaz de
      servidor, de dentro del proceso a fuera; el fichero de topología si se adopta un usuario por
      endpoint, cambio que la raíz de composición ya documenta; la whitelist del trabajador
      confinado, que pasa de tres syscalls a los que el paso 3.2 necesite; y posiblemente el nombre
      o la documentación de la abstracción de proceso.
    compatibility:
      preserved:
      - La vía mediada completa, de la capability a la Policy, al Executor y al SAL.
      - El control positivo de T005, donde la misma solicitud autorizada elimina el archivo por el Executor con ocho registros.
      - La semántica de la apertura para escritura, incluido el rechazo por exceso de enlaces que corrigió T008, y el vocabulario de errno por enlace de tres vías.
      rejected:
      - Cualquier syscall mutante emitida por un servidor fuera del trabajador confinado.
      measured_risk: >-
        Es el riesgo de compatibilidad mayor del plan: si la composición dentro del proceso del
        kernel se mantiene para algo, hay que decidir qué queda dentro y qué sale, y lo que queda
        dentro sigue sin estar confinado. Un cierre parcial no declarado es peor que una deuda
        declarada.
    tests:
      to_modify: >-
        El test de proceso comprometido, que debe pasar de un hilo a un proceso OS independiente
        para demostrar lo que hoy no está demostrado. Requiere autorización explícita.
      to_add_unit:
      - El spawn confinado, en el que el servicio arranca y funciona bajo filtro.
      - La eliminación mediada a través del trabajador confinado, como control positivo y con un indicador de sandbox distinto del actual.
      - Una syscall mutante directa desde un servidor falla, con el errno o la señal declarados según el mecanismo elegido.
      to_add_integration:
      - La reproducción multiproceso completa del ataque de T005.
      - Si se adopta un usuario por endpoint, que un servicio no pueda reclamar la identidad de otro porque su usuario no está en la allowlist para ella.
      must_pass_unmodified: >-
        No aplica como categoría: esta fase modifica por necesidad el test de T005, con
        autorización explícita.
      regression: >-
        Obligatoria en T001, T002, T003, T004, T006, T007, T008 y el smoke de seguridad por IPC, en
        ambos árboles. T008 en particular, porque su corrección vive en el fichero que toca el paso
        3.2.
    dependencies: >-
      La Fase 2 completada, por la razón arquitectónica de RC-4. Dentro de la fase: 3.1 antes que
      3.2, y 3.2 antes que 3.4; 3.3 en paralelo con 3.2; 3.5 al final, porque es el criterio de
      cierre. Consume RFC-T009 como dependencia externa declarada: esta RFC define su contenido
      técnico y su orden interno, pero T009 sigue siendo la que lo autorice y lo cierre.
    closure_criterion: >-
      El test de proceso comprometido pasa en ambos árboles con el actor en un proceso OS
      independiente, midiendo: solicitud mediada denegada con cero ejecuciones; syscall directa
      sobre el mismo recurso fallando con el errno o la señal declarados; recurso intacto en
      contenido, inode, modo, tamaño, marcas de tiempo e inventario; control positivo eliminando el
      mismo archivo por el Executor con ocho registros; suites completas sin ningún rojo y sin perder
      verdes respecto de la baseline previa; 20 repeticiones aleatorias por árbol; y la documentación
      de seguridad re-anclada para reflejar que la arista prohibida ya no existe. Cierre
      administrativo: la deuda registrada del hallazgo marcada como cerrada y el addendum de T005
      actualizado para decir que quedó eliminada, con la medición que lo respalda.
```

## Defectos de documentación

No son hallazgos de seguridad, pero son referencias falsas en documentos versionados y hay que
corregirlas en la misma fase que toque la zona.

1. **Categoría de error mal nombrada en F1.** La documentación de seguridad y el resumen de T006
   afirman que el rechazo de F1 llega como una categoría de validación. El valor numérico que ambos
   citan decodifica a la categoría de aplicación y al subcódigo de operación desconocida; la
   validación es otra categoría. El número es correcto y el nombre no, e importa porque la categoría
   de aplicación es precisamente la que el punto de auditoría no cuenta como denegación. El código
   esperado tras la corrección sí está bien citado.
2. **Alcance del filtro seccomp del trabajador confinado.** Ningún documento del árbol lo enumera.
   Es relevante porque descarta una corrección aparentemente obvia: la whitelist son exactamente
   tres syscalls y todo lo demás mata el proceso, de modo que las dos syscalls que aparecen en el
   cuerpo del trabajador son sondas diseñadas para morir. El hijo confinado es un trabajador de
   escritura de un solo disparo y no puede eliminar.
3. **La deuda de T005 ya estaba catalogada.** El mapa de fronteras y el punto del modelo de
   seguridad que declara la autoridad establecida solo por registro ya la describían, y el addendum
   de T005 lo reconoce. Conviene que la Fase 3 los cite como origen en lugar de presentar el
   hallazgo como nuevo, para evitar que un lector futuro vuelva a descubrirlo.

## Correlación y dependencias

Los tres hallazgos no son independientes ni comparten una única causa. T006 lo es de verdad
respecto de T005 y T007: no comparten componente, ni contrato, ni frontera. T005 y T007 comparten
causa arquitectónica vía RC-4, pero no código: comparten el objeto que hay que crear y por eso deben
diseñarse juntas aunque se implementen separadas. T006-F1 y T006-F2 comparten forma —una garantía
sostenida en el productor— pero no causa: son dos contratos distintos en módulos distintos y se
corrigen con cambios distintos en ficheros distintos.

| | T005 | T006-F1 | T006-F2 | T007 |
|---|---|---|---|---|
| **T005** | — | Independiente | Independiente | Causa común RC-4 y dependencia de orden, Fase 2 antes que Fase 3 |
| **T006-F1** | Independiente | — | Misma forma y distinto contrato; misma fase y mismo test | Independiente |
| **T006-F2** | Independiente | Ídem | — | Independiente; mismo fichero y distinta frontera |
| **T007** | Ídem | Independiente | Independiente | — |

Ninguna corrección de T006 resuelve nada de T005 ni de T007: el ataque de T007 usa frames
estructuralmente válidos, así que endurecer el contrato no lo toca, y el de T005 no usa IPC en
absoluto. La única resolución cruzada real del trío es de dependencia y no de cobertura: la Fase 2
resuelve T007 y es prerequisito de que la Fase 3 resuelva T005 de verdad.

La Fase 1 tiene un efecto lateral útil que no debe presentarse como lo que no es: al traducir el
rechazo nuevo a una categoría de seguridad, los casos F1 pasan a incrementar el contador de
denegaciones. No es la corrección general de la deuda del contador, que sigue abierta para otras
categorías.

```text
Fase 1  (RC-1 + RC-2, T006)  ─── independiente ───┐
                                                   │  orden por atribución de tests
Fase 2  (RC-3b, T007)  ◀───────────────────────────┘
   │
   │  prerrequisito arquitectónico: sin binding exclusivo,
   │  el confinamiento desplaza el bypass hacia la suplantación
   ▼
Fase 3  (RC-4 + RC-3a, T005 / RFC-T009)
   │
   ├─ 3.1  decisión de despliegue ── BLOQUEANTE, no técnica
   ├─ 3.2  mover las mutaciones de fichero al trabajador confinado
   │        └─ requiere extender la whitelist del hijo
   └─ 3.4  retirar syscalls mutantes al proceso anfitrión
            └─ requiere 3.2 completado, o rompe la ruta legítima
```

El orden Fase 1 antes que Fase 2 no es de código sino de atribución: el test de seguridad de T007
usa el decoder y sus hijos envían frames producidos por el código real, así que endurecer el
contrato después de tocar identidad produciría un rojo nuevo que podría leerse como regresión de
identidad. Hacerlo al revés obliga a distinguir dos motivos de rechazo en el mismo test; es un orden
barato que evita una ambigüedad cara.

Existe una única modificación arquitectónica que cerraría RC-3 y RC-4 a la vez: el principal acotado
de RC-4. No cerraría RC-1 ni RC-2 y no debe intentarse, porque un principal acotado no dice nada
sobre si un byte del wire es imprimible. Pese a compartir el objeto, la Fase 2 y la Fase 3 no se
fusionan: la Fase 2 es verificable hoy, sin cambiar contratos y con datos que ya existen, mientras
que la Fase 3 depende de una decisión de despliegue y cambia el modelo de alojamiento. Fusionarlas
convertiría un cierre pequeño y seguro en un bloqueo grande. Lo que sí deben compartir es el diseño.

Deudas preexistentes que **no** son dependencias y no deben colarse en el plan: la canonicalización
del recurso antes de comparar prefijos, el contador de denegaciones completo, el puente de respuesta
ausente pero anunciado, la distinción entre violación de frontera y fallo de I/O en la pista de
auditoría y la tabla de descriptores heredada por el hijo confinado. La Fase 3 toca la última —un
spawn confinado es el sitio natural para cerrarla— y debe declararlo, pero no es su criterio de
cierre.

## Matriz de trazabilidad

`RFC-Txxx → hallazgo → causa raíz → componente → corrección → tests → fase`

| RFC | Hallazgo | Causa raíz | Componente | Corrección | Tests | Fase |
|---|---|---|---|---|---|---|
| T006 | **F1** una operación ausente y una no imprimible atraviesan el decoder y llegan a admisión | **RC-1** el contrato se valida solo en el encoder | El decoder del cuerpo en libs/common, frente a la regla de validez que ya existe en el mismo TU | **A1** aplicar esa regla en el decoder y producir el estado de operación inválida | El test del contrato, más unitarios nuevos del decoder y los tres casos rojos del test de seguridad | **1** |
| T006 | **F2** un separador ilegítimo en vez de NUL produce una ejecución autorizada | **RC-2** el layout del frame no tiene dueño único y el scan no verifica el terminador | Los dos extractores de la routing string, en libs/core y libs/server, más la re-derivación aritmética del offset en el endpoint | **B1** extractores estrictos en las dos rutas, más un rechazo auditado antes de la entrega | Unitarios del extractor con los tres casos, más integración por ruta y los tres casos rojos del test de seguridad | **1** |
| T006 | El contador de denegaciones queda en cero ante el rechazo de F1 | Derivado de RC-1: el rechazo llega en una categoría que el punto de auditoría no cuenta | El punto de auditoría de resultado del endpoint | Traducir el rechazo nuevo a la categoría de seguridad, que sí cuenta. No es la corrección general de la deuda del contador | La aserción de contador en los casos F1 | **1** |
| T007 | **T007-F1** una segunda conexión del mismo PID se registra con otra identidad, obtiene su capability y elimina el recurso | **RC-3b** la elegibilidad de registro es por descriptor, sin unicidad de la identidad viva | La rama de elegibilidad del gestor de IPC; los datos ya están en el registro del peer | Alternativa **C1** de RC-3, rehusar bajo el lock de sesiones si otro descriptor vivo ya sostiene la identidad, con resultado y veredicto de auditoría propios | El caso del ataque por segunda conexión, más unitarios de unicidad, re-registro y primer llegado, y los cuatro verdes sin tocar | **2** |
| T007 | La allowlist no distingue sujetos: un único usuario para toda la topología | **RC-3a** la clave es el par usuario e identidad reclamada | La raíz de composición del kernel, la autorización de topología y la política de identidad | Alternativa **C3** de RC-3, un usuario por endpoint y cambio de usuario en init; acoplado a la Fase 3 porque ambos exigen sujetos distinguibles | Que un servicio no pueda reclamar la identidad de otro | **3** |
| T005 | Tras la denegación de capability y cero ejecuciones, una syscall directa elimina el recurso | **RC-4** el sujeto de la autoridad no es el sujeto del confinamiento | La abstracción de proceso, que es un hilo; el confinamiento, instalado solo en el hijo; el spawn de init, que no confina nada; y la mutación de ficheros, que se ejecuta en el anfitrión | **D1** con **D3** de complemento y **D4** como prerequisito interno; rechazados D4 aislado y D5 sin D4 | El test de proceso comprometido reescrito a un PID independiente, más spawn confinado, syscall directa fallando y la regresión de T001 a T008 | **3** |
| T005 | La eliminación no ejecuta el trabajador confinado mientras la apertura para escritura sí | Coherencia interna del SAL; **no** es la causa del hallazgo | La mutación de ficheros del SAL y el handler que la publica sin sandbox | **D4** encauzar la eliminación por el trabajador confinado; exige extender su whitelist | El control positivo de la eliminación con un indicador de sandbox distinto, más la regresión de T008 | **3**, paso 3.2 |

## Información insuficiente

Cuatro puntos que se declaran en lugar de inferirse.

1. **El modelo de despliegue es una decisión, no un hecho derivable.** La documentación de seguridad
   dice que los servidores son en el proceso hoy y separados según la configuración prevista, y la
   raíz de composición los compone en el proceso. Ambos modelos coexisten en la documentación y solo
   uno en el código. La Fase 3 no puede diseñarse sin que el propietario decida cuál es el destino,
   y esto bloquea el paso 3.1 y por tanto toda la Fase 3. No bloquea el registro ni la validación de
   este análisis.
2. **La viabilidad de un filtro seccomp sobre un proceso anfitrión real.** El único filtro del árbol
   es de tres syscalls y vive en un hijo de un solo disparo. Qué whitelist permite que un servidor
   real arranque y funcione no está medido, y D5 depende de esa medición.
3. **Que el filtro pueda discriminar la syscall de eliminación por su descriptor de directorio.** Es
   cierto que ese descriptor es un escalar visible para el mecanismo, y por tanto que un filtro
   puede restringir la syscall a un descriptor concreto. No está verificado en este árbol y no hay
   precedente en el código, porque el filtro actual solo compara números de syscall. El paso 3.2
   necesita un experimento previo.
4. **La disponibilidad y adecuación del mecanismo de restricción por paths.** No hay código en el
   árbol; sus requisitos de kernel, su interacción con la prohibición de nuevos privilegios y su
   cobertura real frente al ataque de T005 no están analizados. Conviene señalar que por sí solo no
   cerraría T005: restringe por ruta y el recurso atacado está dentro de una ruta permitida.

Un quinto punto que sí está resuelto y conviene registrar para no volver a investigarlo: **la Fase 2
no necesita datos nuevos.** El registro del peer ya conserva las credenciales completas incluido el
PID, la tabla ya está bajo su lock, el registro ya se hace dentro de esa sección crítica y la
liberación del descriptor ya revoca la capability de sesión. Lo único que falta es la regla.

## Criterios de cierre y verificación

Los criterios completos están en `closure_criterion` de cada fase. El protocolo de verificación es
común a las tres y ya está establecido en la serie: dos configuraciones de build y sus dos suites
completas, el test de la fase en cada una, y 20 repeticiones con orden aleatorio y semilla fija por
árbol.

Cuatro condiciones transversales:

1. **Ambos árboles.** El delta de cada fase se declara en registros de la herramienta de pruebas,
   recordando que un registro no es un caso.
2. **Baseline explícita.** La vigente es 110/113 y 107/110 con los tres tests de seguridad en rojo.
3. **Prueba de causalidad.** Revertir la corrección, comprobar que exactamente el caso esperado se
   pone rojo, restaurar y verificar que el contenido y el diff vuelven a ser idénticos.
4. **Addenda fechado, no reescritura.** La documentación de seguridad recibe una sección fechada por
   fase y los documentos de tests de los módulos afectados, un addendum. Las mediciones anteriores no
   se reescriben.

Deudas que estas tres fases no cierran y deben seguir declaradas: la canonicalización del recurso
antes de comparar prefijos; el contador de denegaciones completo, del que la Fase 1 resuelve solo sus
propios casos; el puente de respuesta ausente pero anunciado; la tabla de descriptores heredada por
el hijo confinado; la distinción entre violación de frontera y fallo de I/O en la pista de auditoría;
un caso de eliminación sobre hoja con enlace duro que está razonado y no medido; y tres nuevas de
este análisis —la ventana de binding retenido por una conexión medio abierta, la duplicación de los
dos extractores de routing y los tres defectos de documentación.

## Apartados del informe

El resultado esperado de la orden de trabajo exige doce apartados. Están repartidos entre esta RFC,
que lleva lo estructurado y normativo, y su resumen, que lleva la narrativa y las mediciones y remite
a esta RFC en lo estructurado.

| # | Apartado | Lugar |
|---|---|---|
| 1 | Resumen ejecutivo de los hallazgos | Resumen |
| 2 | Análisis individual de RFC-T005 | Resumen |
| 3 | Análisis individual de RFC-T006 | Resumen |
| 4 | Análisis individual de RFC-T007 | Resumen |
| 5 | Causas raíz identificadas | `root_causes`, más «Defectos de documentación» |
| 6 | Correlación entre los tres hallazgos | «Correlación y dependencias» |
| 7 | Dependencias entre correcciones | «Correlación y dependencias» y `dependencies` de cada fase |
| 8 | Alternativas de solución consideradas | `alternatives_considered` |
| 9 | Plan de implementación por fases | `implementation_plan.phases` |
| 10 | Matriz de trazabilidad | «Matriz de trazabilidad» |
| 11 | Riesgos de implementación | `risks` |
| 12 | Criterios de cierre y verificación | `closure_criterion` de cada fase y «Criterios de cierre y verificación» |
