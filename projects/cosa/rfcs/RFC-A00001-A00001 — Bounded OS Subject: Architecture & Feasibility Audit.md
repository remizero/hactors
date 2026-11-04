```yaml
rfc: RFC-A00001-A00001
title: 'Bounded OS Subject: Architecture & Feasibility Audit'
type: A
scope: >-
  Auditoría de arquitectura y viabilidad del sujeto de sistema operativo acotado: examina init,
  libs/process, libs/sal/linux, kernel y los tests de seguridad, sin cambiar ninguno, así que vive
  en rfcs/ de la raíz del proyecto.
status: draft
date: '2026-09-20'
proposed_by: agent
origin: RFC-A00001
supersedes: null
superseded_by: null
depends_on:
- RFC-A00001-F00001
- RFC-A00001-F00002
affected_modules:
- init
- libs/process
- libs/sal/linux
- kernel
- tests
relations: []
```

# RFC-A00001-A00001 — Bounded OS Subject: Architecture & Feasibility Audit

Estructura y campos: `specs/templates/RFC_TEMPLATE.md` y `specs/templates/RFC-A_TEMPLATE.md`.
Convenciones de identidad y relaciones: `specs/RFC.md`; estados y transiciones: `specs/LIFECYCLE.md`.

Registro en HACTORS del documento real `docs/analisis/tests/RFC-T009 — Bounded OS Subject:
Architecture & Feasibility Audit.md` del repositorio COSA, nombre histórico que se conserva aquí
como referencia y no como identidad. Su cabecera real declara `Origin: RFC-A00001`, `Related
security finding: RFC-T005` y `Prerequisites: RFC-T006-F1, RFC-T007-F1`; en HACTORS eso se traduce
en `origin` hacia `RFC-A00001`, que prefija la identidad conforme a
`specs/RFC.md#derivación-y-numeración`, y en `depends_on` hacia las dos correcciones ya registradas.
El hallazgo relacionado no se declara aquí como arista propia: `informs` va de la fuente al
artefacto informado, y la relación normativa que sí corresponde la expresa `FND-00001` con su
`affects` hacia esta RFC. `date` es la fecha del informe de auditoría que la ejecuta.

`status: draft` reproduce el estado documental real: la RFC siguió en DRAFT y no fue editada. El
tipo es `A` porque la propia cabecera real declara `Implementation: OUT OF SCOPE` y porque el
entregable es un informe, no un cambio de producción. El trabajo que produjo ese informe vive en su
`rfc_run` y en su evidencia; avanzar el estado documental es una transición de `[actor: human]` que
aquí no se produce.

## Cuerpo común

```yaml
context: >-
  RFC-T00005 midió que, tras una denegación de la admisión y sin alcanzar el executor, el mismo
  actor eliminó el recurso protegido con una llamada directa al sistema operativo. RFC-A00001
  identificó esa ausencia de enforcement y la adquisición de identidad por segunda conexión de
  RFC-T00007 como dos manifestaciones de una misma causa arquitectónica: la correspondencia entre
  identidad lógica, proceso de sistema operativo y dominio de confinamiento no está establecida. Su
  fase 3 contrata esta auditoría.
problem_statement: >-
  No se sabe qué entidad posee hoy la autoridad efectiva en COSA, qué proceso de sistema operativo
  la ejecuta realmente, ni qué mecanismos de Linux son viables para acotarla. Sin esos hechos no
  puede formularse una RFC de implementación, y cualquier cambio de confinamiento se haría sobre
  supuestos no verificados.
goals:
- G1 — Determinar qué entidad posee hoy la autoridad efectiva y qué proceso del sistema operativo la ejecuta.
- G2 — Documentar la relación real entre identidad lógica, conexión IPC, proceso y dominio de confinamiento, distinguiendo lo demostrado de lo supuesto.
- G3 — Establecer la viabilidad de seccomp, de Landlock y del filtrado por descriptor de directorio para la carga real de los servidores.
- G4 — Documentar las alternativas de modelo de despliegue con sus privilegios, impacto operativo, propiedades de seguridad e implicaciones para T005 y T007.
- G5 — Auditar el ciclo de vida del proceso desde Init hasta la terminación, la herencia de descriptores y las capacidades reales de integridad de arranque y de parada.
- G6 — Responder las decisiones arquitectónicas D1–D11, definir la frontera de implementación de la futura RFC y fijar qué evidencia cerraría T005.
non_goals:
- Implementar aislamiento de procesos, modificar políticas de seccomp, añadir Landlock, cambiar la configuración de UID/GID, introducir namespaces o contenedores.
- Modificar el ciclo de vida de Init, el binding de identidad del IPC, la validación de contrato de T006 o los tests de T005.
- Afirmar que T005 está resuelto, rediseñar la arquitectura de procesos de COSA o introducir un marco de seguridad global nuevo.
- Cambiar APIs públicas, salvo lo que exigiera únicamente instrumentación de auditoría, que aquí no se produjo.
- Resolver los problemas descubiertos fuera de este alcance, que se registran como deuda en lugar de implementarse de forma oportunista.
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional:
  - specs/RFC.md
  - specs/TESTS.md
  - specs/EVIDENCE.md
  - specs/FINDING.md
proposed_architecture: >-
  Ninguna. Esta RFC no propone una arquitectura instalada: reconstruye la actual contra el código de
  producción y entrega una representación recomendada del sujeto, junto con la frontera de módulos
  que debería cambiar una RFC de implementación posterior. La representación recomendada es una
  encarnación de lanzamiento de un proceso del sistema operativo, con todos sus hilos y sus
  descendientes permitidos sujetos al mismo límite, asociada a un principal lógico y a una
  generación, y no un UUID, un UID, un PID ni un descriptor aislado.
abi_api_contracts: >-
  No aplicable y no se inventa: la auditoría no cambia contratos. El único contrato observable que
  produce es documental, la clasificación de cada conclusión como hecho, inferencia, premisa o
  cuestión sin resolver, y el reparto de ABI de Landlock y de propiedades de seccomp que la futura
  implementación debe negociar sin degradarse en silencio.
new_module: null
ownership_changes: >-
  Recomendados, no aplicados. Init y su supervisor pasan a poseer la encarnación del sujeto y su
  generación; el kernel pasa a poseer el binding y las capabilities dependientes de esa encarnación,
  sin dos registros independientes que no se reconcilien. La autoridad sobre el techo del sistema de
  archivos y de las llamadas al sistema pasa a instalarse antes de entregar el control al ejecutable
  no confiable.
dependency_rules: >-
  La capa de contrato de mensaje, la de identidad y conexión y la de sujeto y dominio se mantienen
  separadas por responsabilidad: esta RFC no vuelve a interpretar cargas útiles, no permite
  identidades por declarar un PID ni sustituye el guard de exclusividad por un filtro de sistema de
  archivos. Se identifica dónde se solapan hoy esas capas.
actions:
  - id: ACT-00010
    type: analysis
    status: completed
    actor: agent
    depends_on: []
    deliverable: docs/analisis/tests/RFC-T009 — Bounded OS Subject - Audit Report.md
    evidence:
    - EVD-00007
    - EVD-00008
  - id: ACT-00011
    type: evidence
    status: completed
    actor: agent
    depends_on:
    - ACT-00010
    deliverable: docs/analisis/tests/RFC-T009-evidence-2026-09-20.tar.gz
    evidence:
    - EVD-00007
migration_plan: >-
  No aplicable: no hay migración de datos ni de esquema. El informe define el orden de validación
  recomendado para la futura implementación y las condiciones de entrada que deben fijarse antes de
  cambiar producción.
benefits:
  architectural: >-
    Convierte la intuición de que falta aislamiento en un inventario de hechos medidos: qué existe,
    qué autoridad conserva, qué mecanismo es viable y qué decisión de despliegue falta. Permite
    escribir la RFC de implementación sin repetir la investigación.
  engineering: >-
    Evita el trabajo inútil: descarta el modelo de UID compartido como única frontera, descarta
    reutilizar el filtro del writer para un servidor, y muestra que la validación de rutas no es
    confinamiento ni que la existencia de un archivo prueba la integridad de su contenido.
  ai: >-
    Cada conclusión lleva su clase, así que un ejecutor automatizado no puede elevar una inferencia a
    hecho ni declarar cerrada una cuestión sin resolver; las condiciones de cierre de T005 están
    enumeradas de forma decidible.
risks:
- id: R1
  risk: Que el bypass directo medido en T005 se considere resuelto por esta auditoría.
  mitigation: El informe declara explícitamente que T005 permanece abierto y reproduce su fallo; enumera la evidencia necesaria para cerrarlo y afirma que no basta con enrutar por el espacio de archivos controlado.
- id: R2
  risk: Que se despliegue una allowlist de llamadas al sistema improvisada sin cobertura de arranque, operación, error y apagado.
  mitigation: La política concreta queda sin resolver; se exige trazado o instrumentación equivalente por binario, libc y configuración, y pruebas de carga, fallo y salida antes de habilitar un perfil.
- id: R3
  risk: Que se interprete Landlock como revocación de autoridad ya adquirida.
  mitigation: La prueba medida muestra que un descriptor de archivo preabierto conserva escritura y truncado, y que un hardlink preexistente dentro del árbol concedido modifica un inode exterior; se exige higiene de descriptores y de árboles.
- id: R4
  risk: Que la integridad de arranque y de parada se presente como prevención de un compromiso activo.
  mitigation: Se declara como atribución y detección, no como enforcement en ejecución, y se advierte que tras la muerte del proceso ya no hay inventario de descriptores, credenciales ni filtros finales.
- id: R5
  risk: Que el listener administrativo heredado por los servidores y el control sin autenticación de peer queden sin tratar.
  mitigation: Se registran como deuda con su evidencia y se asignan a la frontera de descriptores y al control administrativo de la futura implementación.
- id: R6
  risk: Que la auditoría se tome como autorización para provisionar cuentas o elevar privilegios.
  mitigation: La elección operativa entre modelos de despliegue queda sin resolver y se declara que el host medido no tenía capacidades efectivas de cambio de UID ni se intentó elevar privilegios.
alternatives_considered:
- id: A1
  alternative: Modelo de despliegue con UID compartido como única frontera.
  rejection: 'Es el estado actual y es insuficiente: mismo control de acceso discrecional, mismos grupos y acceso potencial a recursos y canales de otros servicios; T005 se reproduce.'
- id: A2
  alternative: Un UID o GID distinto por servicio como requisito lógico del confinamiento.
  rejection: No es requisito de Landlock ni de seccomp; no revoca descriptores heredados y permisos amplios pueden anular la separación. Queda como complemento defendible para un despliegue con actores mutuamente desconfiados, no como sustituto del dominio.
- id: A3
  alternative: Reescribir las llamadas directas del actor para que pasen por el espacio de archivos controlado.
  rejection: No quita la autoridad del host al actor; un dirfd es una referencia útil para resolver una operación, no un confinamiento de las resoluciones posteriores.
- id: A4
  alternative: Reutilizar el filtro seccomp del writer de bytes para los servidores.
  rejection: Es una allowlist de tres llamadas al sistema para un hijo que solo escribe; instalado antes de exec mataría el propio exec y después del loader impediría lectura IPC, memoria, hilos y temporizadores.
consequences: >-
  La propiedad de confinamiento del actor sigue sin existir en producción y T005 continúa abierto.
  Quedan explicitados el sujeto actual, las aristas que faltan, la frontera de proceso requerida, las
  alternativas de Linux y de despliegue, las decisiones D1–D11 y la evidencia necesaria para el
  cierre. Siete cuestiones sin resolver son condiciones de entrada del trabajo futuro, no resultados
  de esta auditoría.
documentation_impact: >-
  El informe debe conservarse como entrada de la RFC de implementación. Además, los mensajes y
  comentarios embebidos en el código pueden describir garantías mayores que las reales, así que esas
  afirmaciones deben revisarse cuando se documente la implementación y no tomarse como evidencia.
testing: >-
  La auditoría no añade tests ni modifica los existentes. Ejecuta una selección focalizada de doce
  entradas para comprobar que ninguna frontera de producción se movió, y dos ejecuciones temporales
  de los binarios reales de Init, kernel y servidor de ejemplo, más dos sondas controladas de
  Landlock y de observación del proceso en tiempo de ejecución. No es una suite completa y no debe
  leerse como baseline.
acceptance_criteria:
- id: C1
  condition: El sujeto de seguridad actual queda explícitamente identificado y se documenta el ciclo de vida real del proceso desde Init hasta la terminación.
  covers: [G1, G2]
  verification: Las secciones del informe sobre el modelo de sujeto y el ciclo de vida, con sus referencias de código y la clasificación de cada afirmación.
- id: C2
  condition: Se documentan la relación IPC de identidad actual y la frontera de confinamiento existente, y se establece la viabilidad de seccomp, de unlinkat/dirfd y de Landlock.
  covers: [G2, G3]
  verification: Las secciones de mecanismos actuales, de relaciones identidad/proceso/dominio y las tres de viabilidad, con el veredicto clasificado de cada mecanismo.
- id: C3
  condition: Las alternativas de modelo de despliegue quedan documentadas con sus privilegios, impacto operativo y de compatibilidad, propiedades de seguridad, complejidad de migración e implicaciones para T005 y T007.
  covers: [G4]
  verification: La tabla comparativa de los tres modelos y la decisión D4 con su condición de aprobación pendiente.
- id: C4
  condition: Se audita el comportamiento de los descriptores heredados y se documentan las capacidades reales de integridad de arranque y de parada.
  covers: [G5]
  verification: El inventario de descriptores por clase con su comportamiento ante fork y exec, y las dos secciones de integridad con la información esperada frente a la observada.
- id: C5
  condition: La separación de responsabilidades entre el contrato de mensaje, el binding de identidad y el sujeto se preserva explícitamente, y se identifica dónde se solapan hoy.
  covers: [G2]
  verification: La sección de preservación de las capas anteriores y el registro de hechos sobre el orden real de validación en la tubería de entrada.
- id: C6
  condition: Queda definida la evidencia necesaria para cerrar T005 y la frontera de implementación de la futura RFC.
  covers: [G6]
  verification: La condición de aceptación propuesta con sus controles positivos, negativos y casos de bypass derivados, y la tabla de módulos y responsabilidades recomendadas.
- id: C7
  condition: Toda conclusión principal está clasificada como hecho, inferencia, premisa o cuestión sin resolver, y las decisiones D1–D11 están respondidas.
  covers: [G6]
  verification: El registro de clases con sus diez hechos, cinco inferencias, tres premisas y siete cuestiones sin resolver, y la tabla de decisiones con el estado y la condición de cada una.
- id: C8
  condition: Ningún mecanismo de seguridad de producción cambió como parte de la auditoría.
  covers: [G1, G2, G3, G4, G5, G6]
  verification: El cierre de alcance del informe, la reproducción del fallo de T005 y el paso de las otras once entradas de la selección focalizada en ambos árboles.
references:
- path: 'docs/analisis/tests/RFC-T009 — Bounded OS Subject: Architecture & Feasibility Audit.md'
  role: Documento real de origen en el repositorio COSA; este archivo es su registro adaptado a HACTORS.
- path: 'docs/analisis/tests/RFC-T009 — Bounded OS Subject - Audit Report.md'
  role: Informe entregado por esta auditoría, con el registro de clases, la matriz de decisiones y el índice de evidencia.
- path: 'docs/analisis/tests/RFC-T009-evidence-2026-09-20.tar.gz'
  role: Paquete de evidencia de ejecución conservada, treinta y seis archivos con su manifiesto de hashes.
- path: RFC-A00001
  role: Análisis de origen, cuya fase 3 contrata esta auditoría y fija su criterio de cierre.
- path: RFC-T00005
  role: RFC de tests cuyo hallazgo permanece abierto; la relación normativa la expresa FND-00001 con su affects hacia esta RFC.
- path: RFC-A00001-F00001
  role: 'Prerequisito declarado: la frontera de contrato de mensaje debe estar implementada antes.'
- path: RFC-A00001-F00002
  role: 'Prerequisito declarado: la exclusividad del binding identidad-conexión debe estar implementada antes.'
- path: TEST-00001
  role: Artefacto TEST cuya ejecución reproduce el bypass y acredita que no se movió ninguna frontera; el vínculo lo declara su instancia, no este documento.
```

## Campos específicos de análisis

```yaml
analysis_scope: >-
  El modelo de ejecución real de COSA en Linux: Init y su supervisor, la creación y el ciclo de vida
  del proceso, el intervalo entre fork y exec, el sandbox existente, la resolución de rutas y el
  borrado en el espacio de archivos controlado, la aceptación y el registro de identidad en el
  kernel, la herencia de descriptores y las capacidades de integridad de arranque y de parada. Fuera
  del alcance queda todo cambio de producción y toda política concreta de servidor.
data_sources:
- path: 'docs/analisis/tests/RFC-T009 — Bounded OS Subject: Architecture & Feasibility Audit.md'
  role: Entrada de la auditoría, sin modificar.
- path: init/src/PosixProcessManager.cpp
  role: fork, execvp, herencia, errores y señales del lanzamiento.
- path: init/src/InitSystem.cpp
  role: Composición y ciclo de vida del supervisor.
- path: init/src/Supervisor.cpp
  role: Registro, tiempos, healthcheck, parada y escalado.
- path: init/src/ControlServer.cpp
  role: Control administrativo y su endpoint sin autenticación de peer.
- path: libs/process/src/Process.cpp
  role: El controlador que ejecuta en un hilo dentro del proceso que lo aloja.
- path: libs/sal/linux/src/LinuxSandbox.cpp
  role: Filtro exacto del writer, fork, límites, espera y arquitectura soportada.
- path: libs/sal/linux/src/ControlledFilespace.cpp
  role: Resolución por componentes, guarda de hardlink y separación entre borrado y append.
- path: libs/sal/linux/src/SandboxedFileHandler.cpp
  role: Punto donde el borrado no entra en el sandbox del writer.
- path: kernel/src/KernelApp.cpp
  role: Composición y UID con el que se autorizan los endpoints de la topología.
- path: kernel/src/StaticPeerIdentityPolicy.cpp
  role: Comparación de UID e identidad reclamada, sin contraste con un proceso esperado por Init.
- path: kernel/src/IPCManager.cpp
  role: Registro, exclusividad bajo el lock de sesiones y revocación en teardown.
- path: libs/sal/linux/src/net/PosixUnixSocket.cpp
  role: Consulta de credenciales del peer sobre el socket aceptado.
- path: libs/sal/linux/src/net/PosixUnixListener.cpp
  role: Flags de creación y accept4.
- path: libs/core/src/InboundPipeline.cpp
  role: Orden real de validación de frame, control, identidad y contratos operacionales.
- path: tests/security_t001/UnauthorizedCapabilityExecutionTest.cpp
  role: Worker y actor usados por T005, y sus aserciones de conservación.
- path: system.toml
  role: Workloads y despliegue auditado; no equivale a una traza de llamadas al sistema.
- path: /proc
  role: Credenciales, hilos, descriptores y sockets Unix observados en las dos ejecuciones temporales.
- path: /usr/include/linux/landlock.h
  role: ABI, flags, estructuras y semántica de errno; copias locales incluidas en el paquete de evidencia.
methodology: >-
  Reconstrucción de hechos contra el código de producción de una revisión concreta, sin editarlo;
  observación directa del proceso en dos ejecuciones temporales de los binarios reales; dos sondas
  controladas, una de Landlock y otra de observación en tiempo de ejecución, ejecutadas sin
  privilegios efectivos sobre fixtures propias; selección focalizada de doce entradas de prueba para
  comprobar que ninguna frontera se movió; y clasificación obligatoria de cada conclusión como
  hecho, inferencia, premisa o cuestión sin resolver. Los intentos fallidos de instrumentación se
  conservan y se describen, no se ocultan.
root_causes:
- id: RC-4
  cause: >-
    No existe una entidad que reúna identidad lógica de COSA, proceso lanzado y dominio de
    confinamiento. Hay tres entidades distintas: el objeto de proceso que ejecuta un controlador en un
    hilo, los procesos Linux que Init crea con fork y execvp, y el hijo temporal que el sandbox crea
    para escribir bytes. El último no encierra a los anteriores.
  component: init, libs/process, libs/sal/linux
  evidence: >-
    Hechos F01 y F02 del registro del informe; el arranque real confirma que Init, kernel y el
    servidor de ejemplo conservaron credenciales, el descriptor escribible inyectado y una variable
    marcadora, y que todos sus hilos observados tenían prohibidos los nuevos privilegios en cero y
    seccomp en cero.
- id: RC-3a
  cause: >-
    El confinamiento actual es por operación y parcial: el append termina en un hijo con límites,
    prohibición de nuevos privilegios y una allowlist de tres llamadas al sistema, mientras que el
    borrado ejecuta unlinkat directamente en el proceso llamador, que en la composición de producción
    es el kernel.
  component: libs/sal/linux
  evidence: >-
    Hechos F03 y F05 del registro; la reproducción de T005 con denegación de la admisión, executor no
    alcanzado y unlink directo exitoso con UID y GID del usuario ordinario.
- id: RC-5
  cause: >-
    La herencia de descriptores no está acotada: el listener administrativo de Init y el descriptor
    escribible de la sonda sobrevivieron a exec en los tres procesos sin el flag de cierre al
    ejecutar, y el writer no depura la tabla heredada ni inspecciona el número de descriptor.
  component: init, libs/sal/linux
  evidence: >-
    Hechos F06 y F07 del registro; la segunda ejecución correlacionó el descriptor con la tabla de
    sockets Unix del kernel y con su pathname.
- id: RC-6
  cause: >-
    El lanzamiento no acredita nada: Init registra el resultado de fork y opcionalmente un healthcheck
    de archivo, pero no confirma exec, instalación de credenciales, confinamiento ni binding, y la
    ruta de parada no conserva todo el estado de espera para comparación posterior.
  component: init
  evidence: >-
    Hecho F02 y las tablas de información esperada frente a observada; hecho R07 del registro de
    riesgos con sus comprobaciones no provocadas.
implementation_plan:
  phases:
  - name: fase-3a
    objective: >-
      Fijar las condiciones de entrada que la auditoría deja sin resolver: el TCB admitido, el modelo
      de despliegue, los recursos protegidos y la autoridad legítima de cada servidor, los perfiles
      de llamadas al sistema por binario y fase, el protocolo de traspaso de sujeto entre Init y el
      kernel, la política integral de proceso, IPC, red y descriptores, y el mínimo de kernel y de ABI
      admitido. Corresponde a los pasos 1 y 2 del orden de validación recomendado.
    rfcs_covered: []
    findings: [T005]
    root_causes: [RC-4, RC-5]
    components: [init, kernel, topología y configuración]
    architectural_change: >-
      Decisión explícita del sujeto como encarnación de lanzamiento y del traspaso autenticado entre
      Init y el kernel, con generación no reciclada. Sin cambio de código.
    implementation_change: Fuera de alcance de esta RFC. Ninguno en esta fase.
    enforcement: >-
      Cierre de la herencia de autoridad, incluido el control administrativo, y lista explícita de
      descriptores retenidos con cierre del resto y flag de cierre al ejecutar por defecto.
    contracts: >-
      El contrato de sujeto, de perfil y de descriptores que debe expresar la configuración de
      lanzamiento. Sin ruptura: todavía no se cambia ninguna API.
    compatibility: >-
      La elección operativa entre los modelos de despliegue condiciona privilegios, propiedad de
      sockets, logs y configuración; no se autoriza elevar privilegios ni provisionar cuentas desde
      esta auditoría.
    tests: >-
      Ninguno nuevo. Las siete cuestiones sin resolver son condiciones de aceptación del trabajo
      futuro, no resultados medidos.
    dependencies: >-
      Las fases 1 y 2 completadas, porque la frontera de contrato y la exclusividad del binding deben
      existir antes de añadir el techo del sistema operativo.
    closure_criterion: >-
      Cada cuestión sin resolver tiene decisión registrada y aprobada por el propietario, y el mínimo
      de kernel y de ABI admitido está fijado sin degradación silenciosa.
  - name: fase-3b
    objective: >-
      Instalar el confinamiento antes de entregar el control al ejecutable no confiable: bootstrap
      fail-closed en el hijo del servicio, credenciales y dominio comprobables, y validación de los
      perfiles Linux en arranque, régimen permanente, error y apagado de cada carga de trabajo,
      cubriendo hilos y descendientes. Corresponde a los pasos 3, 4 y 5 del orden recomendado.
    rfcs_covered: []
    findings: [T005]
    root_causes: [RC-4, RC-3a, RC-6]
    components: [init, libs/sal/linux, kernel]
    architectural_change: >-
      El dominio de confinamiento pasa a ser propiedad del lanzamiento y no de la operación: Landlock
      para las operaciones manejadas, perfil de llamadas al sistema por carga y fase, y control de
      acceso discrecional según el despliegue elegido.
    implementation_change: Fuera de alcance de esta RFC. Se contratará en la RFC derivada futura.
    enforcement: >-
      Instalación previa al exec no confiable, con fallo cerrado ante cualquier requisito de seguridad
      no soportado y sin fallback permisivo; ningún reconocimiento emitido por código ya no confiable
      certifica su propio sandbox.
    contracts: >-
      Derechos de Landlock negociados por perfil, incluidos los que no se conceden pero deben
      manejarse; allowlist de llamadas al sistema compatible con loader, IPC, hilos y red; contrato
      de descriptores al lanzamiento.
    compatibility: >-
      Los componentes internos que sigan compartiendo proceso con el kernel pertenecen a su dominio de
      confianza y no adquieren aislamiento por tener otro identificador de servidor.
    tests: >-
      Proceso real lanzado por el mecanismo productivo, fallos de bootstrap, herencia y regresión de
      las fases anteriores. T005 ejecutado sobre ese sujeto, con controles de mediación conservados.
    dependencies: fase-3a completa.
    closure_criterion: >-
      Se cumple la condición de aceptación propuesta en el informe: atacante en un proceso distinto
      del mediador lanzado por el mecanismo de producción, denegación previa real, intento directo
      sobre la ruta realmente protegida con errno o señal y mecanismo responsable atribuidos, sujeto y
      perfil registrados por el bootstrap confiable, controles negativos y positivos, y los casos de
      bypass derivados —ruta absoluta, traversal y symlink, hardlinks preexistentes y nuevos, dirfd
      exterior, archivo preabierto o recibido, herencia por fork y exec, acceso a memoria o IPC de un
      proceso más privilegiado y control de Init—.
  - name: fase-3c
    objective: >-
      Demostrar revocación, reinicio y cierre de dominio, no solo una parada feliz: eventos asociados
      a la generación, invalidación del binding al invalidar el sujeto, contabilización de los
      miembros permitidos y auditoría de anomalías. Corresponde al paso 6 del orden recomendado.
    rfcs_covered: []
    findings: [T005]
    root_causes: [RC-4, RC-6]
    components: [init, kernel]
    architectural_change: >-
      La generación pasa a ser la referencia estable del sujeto: un reinicio crea otra generación y la
      conexión y la capability de la anterior no se heredan como válidas.
    implementation_change: Fuera de alcance de esta RFC.
    enforcement: >-
      Revocación del acceso IPC al invalidar el sujeto y demostración de que no quedan miembros del
      dominio cuando no se permiten descendientes.
    contracts: >-
      Eventos verificables de creación, bootstrap, binding, revocación, señales solicitadas, estado de
      espera y cierre del dominio.
    compatibility: >-
      No se promete atestación retrospectiva: tras la muerte del proceso ya no hay inventario de
      descriptores, credenciales ni filtros finales, y una huella de la configuración instalada es
      evidencia de instalación, no introspección.
    tests: >-
      Revocación, reinicio y cierre de dominio con pruebas controladas, incluido el relanzamiento
      durante la espera, que no fue medido aquí.
    dependencies: fase-3b completa.
    closure_criterion: >-
      El conjunto actual de tests no se elimina ni se modifica para conseguir verde; su adaptación
      conserva la propiedad original de T005 y declara qué variante de actor mide.
```

## Resultado observado

La auditoría se ejecutó y entregó su informe el 2026-09-20 sobre la revisión
`1d58d531452d04a5c10f2ab61ea1b72567d93307` de la rama `dev`. La investigación arquitectónica quedó
completada, con dependencias de implementación explícitas.

- **T005 permanece abierto y se reprodujo su fallo.** En la reproducción, la admisión negó la
  operación, no se alcanzó el executor y el mismo actor eliminó directamente el archivo mediante
  `unlink` con UID y GID 1000.
- **Viabilidad:** Landlock quedó clasificado como viable con restricciones para limitar nuevas
  operaciones de sistema de archivos, y seccomp como viable con restricciones para reducir la
  superficie de llamadas al sistema, con el filtro actual inservible para lanzar un servidor. La
  prueba local de Landlock, ABI 6, bloqueó las operaciones fuera del árbol autorizado pero preservó
  la escritura y el truncado mediante un descriptor previamente abierto y la escritura a un inode
  externo mediante un hardlink preexistente permitido. No se probó un perfil completo de COSA.
- **Decisiones:** D1–D11 están respondidas y todas clasificadas como inferencia, no como mecanismos
  instalados. U01–U07 quedan sin resolver y son condiciones de entrada del trabajo futuro.
- **Medición:** builds dirigidos correctos en ambos árboles; selección focalizada de doce entradas,
  11/12 en cada árbol con T005 fallando en ambos, salida 8 de cada ejecución de pruebas. No es un
  baseline de toda la suite. Dos ejecuciones temporales de los binarios reales completaron registro,
  demo de aplicación y apagado con salida 0.
- **Alcance:** no se cambió ninguna fuente de producción, test, política de seguridad, configuración
  versionada ni el documento de entrada. No se creó commit.

El documento real siguió en DRAFT y no fue editado: el informe se entregó como archivo aparte y el
directorio que lo contiene está deliberadamente fuera del control de versiones del repositorio COSA,
así que un estado de trabajo limpio allí no significa que estos entregables no existan.

La consecuencia para HACTORS es que `FND-00001` continúa `open` con severidad `critical`, y que la
TASK de origen no puede cerrarse mientras lo esté.
