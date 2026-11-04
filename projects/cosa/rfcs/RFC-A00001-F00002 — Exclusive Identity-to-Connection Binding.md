```yaml
rfc: RFC-A00001-F00002
title: 'Exclusive Identity-to-Connection Binding'
type: F
scope: >-
  El registro de identidad y el binding de conexión del dominio IPC gestionado: afecta a libs/server
  y a las estructuras internas de sesión y peer, así que vive en rfcs/ de la raíz del proyecto.
status: draft
date: '2026-09-18'
proposed_by: agent
origin: RFC-A00001
supersedes: null
superseded_by: null
depends_on:
- RFC-A00001-F00001
affected_modules:
- libs/server
- kernel
- tests
relations: []
```

# RFC-A00001-F00002 — Exclusive Identity-to-Connection Binding

Estructura y campos: `specs/templates/RFC_TEMPLATE.md` y `specs/templates/RFC-F_TEMPLATE.md`.
Convenciones de identidad y relaciones: `specs/RFC.md`; estados y transiciones: `specs/LIFECYCLE.md`.

Registro en HACTORS del documento real `docs/analisis/tests/RFC-T007-F1 — Exclusive
Identity-to-Connection Binding.md` del repositorio COSA, nombre histórico que se conserva aquí como
referencia y no como identidad. Su cabecera real declara `Origen: RFC-A00001`, `Test objetivo:
RFC-T007` y `Prerequisito: RFC-T006-F1 implementada`; en HACTORS eso se traduce en `origin` hacia
`RFC-A00001`, que prefija la identidad conforme a `specs/RFC.md#derivación-y-numeración`, y en
`depends_on` hacia `RFC-A00001-F00001`. `date` es la fecha observable del archivo fuente.

`status: draft` reproduce el estado documental real: la RFC siguió en DRAFT y no tiene resumen
propio. El trabajo que contrata se observó implementado en el código examinado por la auditoría del
2026-09-20, y ese hecho vive en su `rfc_run` y en la evidencia de la auditoría, no en este campo;
avanzar el estado documental es una transición de `[actor: human]` que aquí no se produce.

## Cuerpo común

```yaml
context: >-
  RFC-T00007 midió que el mismo proceso abrió una segunda conexión, la registró con la identidad
  privilegiada, obtuvo su capability y eliminó el recurso protegido. Las credenciales del peer se
  obtenían correctamente y la identidad reclamada se verificaba contra la política estática; lo que
  faltaba era exclusividad sobre la identidad registrada. RFC-A00001 lo asignó a su fase 2.
problem_statement: >-
  Una misma identidad lógica puede vincularse a varios descriptores activos del mismo sujeto de
  sistema operativo. La vulnerabilidad no consiste en falsificar las credenciales del peer, sino en
  adquirir una identidad ya autorizada mediante una segunda conexión, antes de que el registro pueda
  ser rechazado.
goals:
- G1 — Imponer la invariante de que, en cualquier instante, como máximo un descriptor activo representa una identidad lógica dada.
- G2 — Rechazar el registro duplicado antes de completar el registro y la autorización de la nueva identidad, de forma atómica respecto al estado gestionado.
- G3 — Liberar el binding cuando el descriptor propietario desaparece, sin impedir un registro posterior legítimo.
- 'G4 — Conservar el comportamiento permitido para identidades distintas: no introducir la restricción global de una identidad por UID.'
- 'G5 — Mantener separadas las responsabilidades: la política responde a si un UID puede representar una identidad, y el gestor del IPC a si esa identidad ya está representada por otra conexión activa.'
- G6 — Conservar intactos los tests protegidos y demostrar que el escenario histórico deja de ser reproducible.
non_goals:
- Aislamiento entre procesos o entre UIDs del sistema operativo, namespaces, cambio de credenciales, descarte de capabilities, Landlock, seccomp, prohibición de nuevos privilegios, sandboxing de servidores ni confinamiento del sistema de archivos.
- Resolver T005, que permanece abierto después de esta RFC y exige la fase 3.
- Atribución criptográfica de identidad ni binding permanente entre identidad y PID.
- El modelo de despliegue de un UID por servidor, que es una decisión del propietario.
- Cambios propios de la fase 3.
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional:
  - specs/RFC.md
  - specs/TESTS.md
  - specs/EVIDENCE.md
  - specs/FINDING.md
  - specs/CONCURRENCY.md
proposed_architecture: >-
  Un único punto de enforcement en el tratamiento del frame de control del gestor del IPC, sobre el
  estado de peers y sesiones ya existente y bajo el mismo lock que lo protege, para que no exista una
  ventana entre la comprobación de identidad libre y el establecimiento del binding. El descriptor
  que intenta registrarse no entra en conflicto consigo mismo cuando el flujo es una revalidación
  legítima del mismo binding.
abi_api_contracts: >-
  Se evita el cambio de API pública. El contrato observable nuevo es la regla de exclusividad del
  registro: una identidad ya vinculada a otro descriptor activo produce rechazo de registro, sin
  capacidad concedida y sin ejecución autorizada, y el binding existente permanece intacto.
new_module: null
ownership_changes: >-
  La unicidad del binding identidad↔descriptor pasa de la allowlist de política a la tabla de peers,
  que es quien la posee y quien ya opera bajo su lock. La política estática de identidad de peer no
  adquiere estado de conexiones ni tabla de peers, y no se convierte en un binding con estado.
dependency_rules: >-
  No se introducen abstracciones globales nuevas cuando el estado existente basta. No se incluye
  estado de sesión en los módulos de política ni se acopla el gestor del IPC con la autorización.
actions:
  - id: ACT-00007
    type: implementation
    status: completed
    actor: agent
    depends_on: []
    deliverable: kernel/src/IPCManager.cpp
    evidence:
    - EVD-00006
  - id: ACT-00008
    type: test
    status: completed
    actor: agent
    depends_on:
    - ACT-00007
    deliverable: tests/security_t007_f1/ExclusiveIdentityBindingTest.cpp
    evidence:
    - EVD-00006
  - id: ACT-00009
    type: evidence
    status: pending
    actor: agent
    depends_on:
    - ACT-00007
    - ACT-00008
    deliverable: ''
    evidence: []
migration_plan: >-
  No aplicable: no hay migración de datos ni de esquema. El ciclo de vida del binding se libera con
  la desconexión del descriptor propietario.
benefits:
  architectural: >-
    Cierra la adquisición de autoridad por duplicación de conexión y deja nombrado, sin resolverlo,
    el problema más profundo que comparten T005 y T007: la correspondencia entre identidad lógica,
    proceso de sistema operativo y dominio de confinamiento.
  engineering: >-
    Reutiliza el estado y el lock existentes, con pruebas específicas de la invariante y sin seams
    que alteren el comportamiento de producción.
  ai: >-
    La invariante y el criterio de no-cierre están enunciados de forma decidible, así que un ejecutor
    automatizado no puede declarar el cierre por un rechazo posterior al registro ni por una
    comparación de PID sin binding.
risks:
- id: R1
  risk: Que la comprobación quede fuera del lock y exista una ventana de carrera entre dos conexiones.
  mitigation: La comprobación y el establecimiento del binding son atómicos respecto al estado gestionado, y se prueba con intentos duplicados concurrentes repetidos.
- id: R2
  risk: Que el cierre se declare por un rechazo posterior a la adquisición de capability, o por una nueva verificación de identidad en el endpoint.
  mitigation: El criterio de no-cierre enumera explícitamente esos sustitutos y exige demostrar la ausencia de capability, de ejecución autorizada y de efecto sobre el recurso.
- id: R3
  risk: Que se introduzca un binding por PID como mecanismo principal.
  mitigation: El PID se conserva solo como prueba de vida; está sujeto a reutilización y no resuelve la atribución entre conexiones.
- id: R4
  risk: Que se restrinja globalmente a una identidad por UID, cambiando el modelo de despliegue.
  mitigation: El caso de dos identidades distintas registrables de forma independiente es obligatorio y el cambio de modelo queda fuera de alcance.
alternatives_considered:
- id: A1
  alternative: Binding permanente entre identidad y PID.
  rejection: El PID se reutiliza, no se conserva como binding persistente y no resuelve la atribución entre conexiones del mismo sujeto.
- id: A2
  alternative: Estado de binding en la política estática de identidad de peer.
  rejection: Convertiría una decisión de autorización en un estado con ciclo de vida; son responsabilidades distintas y la política no posee la tabla de peers.
- id: A3
  alternative: Verificar de nuevo la identidad en el endpoint del agente y rechazar el mensaje tras el registro.
  rejection: 'Es el criterio de no-cierre explícito: la autoridad ya se habría adquirido y el problema quedaría convertido en un no autorizado posterior.'
- id: A4
  alternative: Documentar que las identidades deberían ser únicas.
  rejection: Depende de que los clientes sean honestos; no es enforcement.
consequences: >-
  T007 queda cerrado como hallazgo de binding, pero no constituye aislamiento de sujeto de sistema
  operativo. La fase 3 sigue siendo necesaria y T005 permanece abierto después de esta RFC.
documentation_impact: >-
  El reparto de responsabilidad entre la política y el gestor del IPC debe quedar documentado, junto
  con la limitación de atribución que esta fase no resuelve.
testing: >-
  Seis casos propios: registro único permitido, registro duplicado rechazado, identidades distintas
  independientes, binding liberado tras la desconexión, binding existente superviviente al rechazo y
  tentativas duplicadas repetidas bajo concurrencia. Los tests protegidos se ejecutan sin
  modificación y el caso histórico se conserva como regresión.
acceptance_criteria:
- id: C1
  condition: Existe enforcement de exclusividad en el gestor del IPC y la comprobación ocurre bajo el lock que protege el estado de sesiones.
  covers: [G1, G2]
  verification: La localización del punto de enforcement y la prueba de intentos duplicados concurrentes sin ventana en la invariante.
- id: C2
  condition: Una identidad no puede estar vinculada a dos descriptores activos y el registro duplicado se rechaza antes de conceder autoridad.
  covers: [G1, G2]
  verification: La prueba de registro duplicado con comprobación de capability no adquirida, operación protegida no ejecutada y recurso intacto.
- id: C3
  condition: El binding se libera correctamente al desconectar el descriptor propietario y un registro posterior de la misma identidad se permite.
  covers: [G3]
  verification: La prueba de ciclo de vida del binding.
- id: C4
  condition: Dos identidades distintas conservan el comportamiento permitido y no se introduce la restricción global de una identidad por UID.
  covers: [G4]
  verification: La prueba de identidades independientes.
- id: C5
  condition: El binding existente sobrevive al rechazo del duplicado y la conexión rechazada no puede utilizar su autoridad.
  covers: [G1]
  verification: La prueba de supervivencia del binding tras el rechazo.
- id: C6
  condition: No se introduce estado de binding en la política estática ni binding por PID, y no se incorporan cambios de la fase 3.
  covers: [G5]
  verification: La revisión del cambio de producción y el árbol de trabajo limpio salvo los cambios autorizados.
- id: C7
  condition: Los tests protegidos permanecen intactos y el escenario histórico de adquisición de identidad por segunda conexión deja de ser reproducible.
  covers: [G6]
  verification: La ejecución sin modificación de los tests protegidos y la comprobación de que el caso histórico pasa.
- id: C8
  condition: La causalidad queda demostrada revirtiendo solo el cambio de producción y reproduciendo de nuevo el fallo original.
  covers: [G6]
  verification: La secuencia causal completa y la vuelta al estado anterior al restaurar el cambio.
references:
- path: 'docs/analisis/tests/RFC-T007-F1 — Exclusive Identity-to-Connection Binding.md'
  role: Documento real de origen en el repositorio COSA; este archivo es su registro adaptado a HACTORS.
- path: RFC-A00001
  role: Análisis de origen, cuya fase 2 contrata esta corrección y fija su criterio de cierre.
- path: RFC-T00007
  role: RFC de tests cuya medición originó el hallazgo de binding que esta RFC cierra.
- path: RFC-A00001-F00001
  role: 'Prerequisito declarado: la fase 1 debe estar implementada antes, por atribución de tests.'
- path: TEST-00003
  role: Artefacto TEST cuya ejecución verifica el resultado; el vínculo lo declara su instancia, no este documento.
```

## Campos específicos de feature

```yaml
follow_up_rfcs:
- type: A
  purpose: >-
    Auditoría del sujeto de sistema operativo acotado, que resuelve la correspondencia entre
    identidad lógica, proceso y dominio de confinamiento. Ya existe y se registra como
    RFC-A00001-A00001, derivada del mismo análisis; no se propone aquí una segunda.
- type: T
  purpose: >-
    Verificación independiente de la invariante de exclusividad. No se propone como RFC nueva: la
    propiedad ya la fija TEST-00003, derivado de RFC-T00007, y su ejecución es la que acredita el
    cierre.
```

## Resultado observado

Esta fase no tiene resumen propio en el corpus real y su documento no fue editado, así que el estado
observado se acredita de forma indirecta y se declara como tal: el informe de la auditoría del
2026-09-20 (`RFC-A00001-A00001`) registra como hecho, al examinar el código, que la búsqueda de otra
conexión verificada con la misma identidad se realiza bajo el lock de sesiones y que se mantiene la
invariante de como máximo un binding activo por identidad, y lista la prueba de binding exclusivo de
identidad entre las entradas ejecutadas. Con eso se afirma que la corrección estaba implementada
antes de esa fecha, no que sus criterios de cierre se verificaran con la secuencia causal que esta
RFC exige. Por eso ACT-00009, la campaña de verificación dedicada que acreditaría esos criterios,
sigue en `pending` con su entregable vacío, aunque ACT-00007 y ACT-00008 de las que depende estén
`completed`: la corrección existe y su prueba propia pasa, pero la verificación que esta RFC pide
no se llegó a registrar.

T005 permanece abierto después de esta fase, conforme a su propio alcance.
