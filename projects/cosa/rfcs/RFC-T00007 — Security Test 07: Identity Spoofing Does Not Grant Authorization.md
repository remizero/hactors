```yaml
rfc: RFC-T00007
title: 'Security Test 07: Identity Spoofing Does Not Grant Authorization'
type: T
scope: >-
  La frontera entre la identidad autoafirmada de una solicitud y la identidad autoritativa que usa
  la autorización; atraviesa libs/server, libs/core, libs/common y kernel, así que vive en rfcs/ de
  la raíz del proyecto.
status: tested
date: '2026-09-15'
proposed_by: agent
origin: null
supersedes: null
superseded_by: null
depends_on: []
affected_modules:
- libs/server
- libs/core
- libs/common
- kernel
- tests
relations:
- target: RFC-A00001
  relation: informs
```

# RFC-T00007 — Security Test 07: Identity Spoofing Does Not Grant Authorization

Estructura y campos: `specs/templates/RFC_TEMPLATE.md` y `specs/templates/RFC-T_TEMPLATE.md`.
Convenciones de identidad y relaciones: `specs/RFC.md`; estados y transiciones: `specs/LIFECYCLE.md`.

Registro en HACTORS del documento real `docs/analisis/tests/RFC-T007 — Security Test 07: Identity
Spoofing Does Not Grant Authorization.md` del repositorio COSA. La identidad pasa de tres a cinco
cifras conforme a `specs/RFC.md#identidad-y-tipos`, conservando el número real. `relations` declara
la arista `informs` hacia `RFC-A00001`, que el documento informado no puede declarar por sí mismo.
`date` es la fecha observable del archivo fuente.

## Cuerpo común

```yaml
context: >-
  El modelo de identidad y autorización de COSA declara que una identidad autoafirmada no es una
  identidad autoritativa. RFC-T007 encarga medir esa propiedad con un atacante que posee una
  identidad legítima y limitada e intenta presentarse como una identidad privilegiada.
problem_statement: >-
  No estaba demostrado que el atacante no controle la fuente autoritativa de identidad. Un rechazo
  observado no basta: la solicitud podría haberse rechazado por payload inválido, por recurso
  inexistente o por cualquier otra razón ajena al mecanismo anti-spoofing.
goals:
- G1 — Auditar los tests y mecanismos reales de identidad, autenticación, IPC y Policy antes de escribir código, y reutilizar o extender en lugar de duplicar.
- G2 — Identificar la fuente autoritativa de identidad que COSA usa y medir con ese mecanismo real, no con una identidad falsa creada dentro del test.
- G3 — Demostrar la discrepancia entre identidad real, identidad declarada e identidad efectiva, y que Policy evalúa con la efectiva.
- G4 — Comprobar que no se concede ninguna capability privilegiada, que la operación protegida no se ejecuta y que el recurso permanece intacto.
- G5 — Incluir un control positivo donde la identidad legítima privilegiada sí puede realizar la operación.
- 'G6 — Mantener el test aislado de los demás threats: payload estructuralmente válido, proceso atacante válido como proceso COSA.'
non_goals:
- Implementar un sistema de autenticación, un identity provider, mecanismos criptográficos, capabilities, Policy o una arquitectura IPC nuevos.
- Detección genérica de spoofing, fuzzing, LLM, red o servicios externos.
- Cubrir el mensaje IPC malformado, la ejecución de capability no autorizada ni el bypass de proceso comprometido, que pertenecen a RFC-T00006 y RFC-T00005.
- Cambiar el modelo de identidad para que el test pase, ni realizar refactorizaciones generales.
- 'Corregir el defecto productivo que se encuentre: se informa y se deriva a su RFC de corrección.'
required_specifications:
  index: specs/CONTEXT_LOADING.md
  additional:
  - specs/RFC.md
  - specs/TESTS.md
  - specs/EVIDENCE.md
  - specs/FINDING.md
proposed_architecture: >-
  No aplicable a una RFC de tests. Si el mecanismo existente no proporciona una fuente autoritativa
  de identidad suficientemente clara, eso se registra como hallazgo de seguridad o arquitectónico,
  no se resuelve con lógica especial dentro del test.
abi_api_contracts: >-
  No aplicable: esta RFC no crea ni modifica contratos. Consume el mecanismo real por el que COSA
  determina la identidad del originador y lo observa.
new_module: null
ownership_changes: >-
  Ninguno. La unicidad del binding entre identidad y conexión pertenece al componente que posee la
  tabla de peers; esta RFC solo la mide.
dependency_rules: >-
  No aplicable: no se alteran las reglas de dependencia entre módulos. No se introducen mecanismos
  de seguridad paralelos ni se modifican otras áreas de COSA.
actions: []
migration_plan: >-
  No aplicable: no hay migración de datos ni de esquema.
benefits:
  architectural: >-
    Convierte «identidad autoafirmada ≠ identidad autoritativa» de principio declarado en propiedad
    medida, y localiza dónde se rompe cuando se rompe.
  engineering: >-
    Se apoya en la infraestructura de tests existente y en fixtures de identidades controladas, con
    instrumentación mínima solo si ya existe un patrón equivalente.
  ai: >-
    Las tres identidades —real, declarada y efectiva— quedan registradas por separado, así que un
    ejecutor automatizado no puede confundir un rechazo estructural con un rechazo anti-spoofing.
risks:
- id: R1
  risk: Que el test pruebe únicamente que un campo es incorrecto, y no el mecanismo anti-spoofing.
  mitigation: La identidad autoritativa se obtiene por el mecanismo real de COSA y se registra la identidad efectiva por separado de la declarada.
- id: R2
  risk: Que un DENY observado se atribuya al anti-spoofing cuando su causa es otra.
  mitigation: La evidencia exige las tres identidades y el motivo del veredicto, no solo el resultado.
- id: R3
  risk: Que el test demuestre que la operación protegida nunca funciona.
  mitigation: Control positivo con la identidad privilegiada legítima.
- id: R4
  risk: Que se modifique el test para evitar el fallo tras observar una suplantación aceptada.
  mitigation: Cualquier aceptación de una identidad falsificada se registra como hallazgo de seguridad.
alternatives_considered:
- id: A1
  alternative: Crear una identidad falsa dentro del test y afirmar que el sistema la rechazó.
  rejection: 'Prueba un campo, no el mecanismo: no demuestra que el atacante no controle la fuente autoritativa.'
- id: A2
  alternative: Comprobar solo que la solicitud es rechazada.
  rejection: El rechazo puede deberse a payload inválido, recurso inexistente o Policy incorrecta; no es evidencia de anti-spoofing.
- id: A3
  alternative: Añadir variantes artificiales de spoofing no soportadas por mecanismos existentes.
  rejection: La plantilla de tipo lo prohíbe; solo se incluyen las variantes que la arquitectura real permita.
consequences: >-
  Un FAIL de esta RFC es una vulnerabilidad de suplantación de identidad con causa arquitectónica,
  y su corrección no pertenece al test que la detecta sino al componente que posee el binding.
documentation_impact: >-
  El resultado obliga a documentar la fuente autoritativa de identidad y la limitación de
  atribución del test cuando la identidad efectiva no se pueda observar directamente.
testing: >-
  Esta RFC es el encargo de un test. Su comprobación es la ejecución aislada y reproducible del
  test que encarga, con la discrepancia de identidades explícita en su salida.
acceptance_criteria:
- id: C1
  condition: Se auditó el repositorio antes de modificar código y se reutilizó o completó un test existente de identidad o autorización cuando correspondía.
  covers: [G1]
  verification: El registro de la auditoría previa y la ausencia de mecanismos de identidad duplicados.
- id: C2
  condition: El atacante posee una identidad real y limitada, el mensaje es estructuralmente válido y el ataque declara una identidad privilegiada diferente.
  covers: [G6]
  verification: El fixture con las dos identidades conceptuales y el estímulo declarado en los campos específicos.
- id: C3
  condition: Se identificó la fuente autoritativa de identidad y la identidad efectiva sigue siendo la real del atacante.
  covers: [G2, G3]
  verification: La evidencia con identidad real, declarada y efectiva registradas por separado.
- id: C4
  condition: Policy no utiliza la identidad falsificada para autorizar la solicitud y no se concede ninguna capability privilegiada.
  covers: [G3, G4]
  verification: El veredicto de Policy y el recuento de grants nuevos en la evidencia.
- id: C5
  condition: La operación protegida no se ejecuta y el recurso protegido permanece intacto.
  covers: [G4]
  verification: Los registros de admisión, de Executor y de handler, y la comprobación del recurso.
- id: C6
  condition: Existe un control positivo, cuando la arquitectura lo permite, en el que la identidad legítima privilegiada realiza la operación.
  covers: [G5]
  verification: El caso autorizado con ALLOW y ejecución normal.
- id: C7
  condition: El test es determinista, reproducible, autocontenido y ejecutable de forma aislada, sin red, sin LLM, sin servicios externos y sin usuarios reales del sistema.
  covers: [G2]
  verification: El comando literal de ejecución aislada y las repeticiones con orden aleatorio y semilla fija.
- id: C8
  condition: La salida proporciona evidencia explícita del spoofing y de su resultado, y cualquier aceptación de una identidad falsificada queda registrada como hallazgo.
  covers: [G3]
  verification: El bloque estructurado de evidencia de seguridad y el registro FND asociado a la ejecución.
references:
- path: 'docs/analisis/tests/RFC-T007 — Security Test 07: Identity Spoofing Does Not Grant Authorization.md'
  role: Documento real de origen en el repositorio COSA; este archivo es su registro adaptado a HACTORS.
- path: 'docs/analisis/tests/RFC-T007 — Security Test 07: Identity Spoofing Does Not Grant Authorization - Summary.md'
  role: Resultado real de la ejecución, con el caso de segunda conexión en FAIL.
- path: RFC-A00001
  role: Análisis que consume este hallazgo, lo clasifica y decide su corrección.
- path: TEST-00003
  role: Artefacto TEST que fija la propiedad, los criterios y el procedimiento de esta medición.
```

## Campos específicos de tests

```yaml
property_under_test: >-
  Un actor no puede obtener autorización mediante suplantación de identidad: declarar una identidad
  privilegiada en una solicitud estructuralmente válida no modifica la identidad autoritativa que
  COSA usa para evaluarla, ni concede sus capabilities, ni ejecuta la operación protegida.
fixture: >-
  Dos identidades conceptuales —A no privilegiada y atacante, B privilegiada y protegida—, un
  recurso u operación con B → ALLOW y A → DENY, el mecanismo real por el que COSA determina la
  identidad del originador, e instrumentación mínima para observar la identidad efectiva cuando ya
  exista un patrón equivalente en los tests.
stimuli:
- S1 — Solicitud estructuralmente válida de A que declara identidad B sobre una operación protegida.
- 'S2 — Control positivo: solicitud legítima de B sobre la misma operación.'
- 'S3 — Variantes solo si la arquitectura real las permite: campo de identidad, metadata del originador, identidad del contexto IPC y capability asociada a otra identidad.'
security_matrix:
- case: Suplantación en el campo de identidad
  stimulus: S1
  boundary: Identity → Authorization
  observation: Identidad efectiva A, Policy DENY, cero capabilities concedidas, operación no realizada, recurso intacto.
  limit: Concluye sobre el mecanismo de identidad del árbol examinado, no sobre otros orígenes de autoridad.
- case: Control positivo
  stimulus: S2
  boundary: Flujo legítimo completo
  observation: Identidad efectiva B, Policy ALLOW, ejecución normal.
  limit: Acredita que la operación protegida funciona para su dueño.
- case: Segunda conexión del mismo proceso
  stimulus: S3
  boundary: Registro de peer y binding identidad↔descriptor
  observation: Veredicto de colisión, cero grants nuevos, cero registros de admisión, de Executor y de handler.
  limit: La atribución del rechazo se declara por escrito junto con el destino arquitectónico que la cierra.
regressions: >-
  Los cuatro casos verdes anteriores del test se preservan sin modificación; las suites completas
  no pierden ningún verde. No se cambian perfiles ni el modelo de identidad para acomodar
  resultados, y no se modifican otras áreas de COSA.
ownership: >-
  Consume libs/server, libs/core, libs/common y kernel como superficies observadas; no crea
  autoridades ni mecanismos paralelos. Cada observación proviene de su dueño: la identidad
  autoritativa del mecanismo que la determina, el veredicto de Policy, el grant del componente de
  capabilities, el efecto del Executor y el estado del recurso del espacio de trabajo controlado.
evidence: >-
  Árbol y revisión examinados, plataforma, identidades y PID observados, comandos literales de
  ejecución aislada y de las suites completas en los dos árboles de construcción, códigos de
  retorno, duración, resultado por caso y repeticiones con orden aleatorio y semilla fija. La
  medición concreta vive en los registros EVD asociados a su ejecución, no en este documento.
```

## Resultado observado

La ejecución real de esta RFC produjo un hallazgo: el mismo PID abrió una segunda conexión, se
registró con la identidad B, obtuvo la capability de B, Policy resolvió ALLOW y el recurso protegido
fue eliminado. Naturaleza del fallo declarada por el análisis: debilidad arquitectónica, con causa
común con `RFC-T00005` en la ausencia de un sujeto acotado. El resultado se registró en `FND-00004`
y su corrección es la fase 2 del plan de `RFC-A00001`, contratada en `RFC-A00001-F00002`.
