# Vistas derivadas.

Una vista es la proyección de lo ya persistido en un proyecto a un formato de presentación. Existe para leer, calcular y asignar sin recorrer los artefactos a mano; no para registrar nada.

Una vista no es fuente de verdad. El estado de un proyecto se acredita a partir de sus artefactos persistidos, sus estados, sus historiales y sus relaciones, conforme a [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#reconstrucción-del-estado), y ninguna vista participa en esa reconstrucción. La CLI nunca lee una vista: ningún comando resuelve una identidad, un estado ni una relación desde `views/`, así que una vista obsoleta no puede desmentir a su proyecto; solo puede quedarse atrás.

Tampoco es uno de los índices que [PROJECTS.md](PROJECTS.md) prohíbe. Lo que ahí se prohíbe es mantener a mano una tabla duplicada del estado; una vista se regenera entera desde los artefactos en cada operación que la produce. No se edita: se reemplaza.

## El modelo de lectura

`hactors export` proyecta un proyecto a su **modelo de lectura**, un documento JSON que separa el cálculo de la presentación: lo que hay que saber de un proyecto se resuelve una vez, y quien lo dibuja no vuelve a leer los artefactos.

```yaml
schema: hactors-model/1.0
project: ""
description: ""
generated_at: ""
counters: {}
artifacts: []
edges: []
runs: []
problems: []
```

| Campo | Descripción |
|---|---|
| `schema` | Versión del contrato. Quien lo consume comprueba esta antes que ninguna otra cosa. |
| `project` | Nombre del proyecto proyectado. |
| `description` | La de `project.yaml`; vacía si el proyecto no declara ninguna. |
| `generated_at` | `YYYY-MM-DDTHH:MM:SSZ` en UTC, el mismo formato que `created_at` de `project.yaml`. Es la única parte del modelo que cambia entre dos proyecciones de un proyecto sin cambios. |
| `counters` | Los del manifest del proyecto, tal como constan; no se recalculan ni se reparan. |
| `artifacts` | Los artefactos documentales del proyecto, uno por elemento. |
| `edges` | Las aristas de `relations` del manifest del proyecto, proyectadas literalmente: el elemento de [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#relaciones-del-proyecto) sin añadir ni quitar campos. |
| `runs` | Las instancias de ejecución del proyecto, una por elemento. |
| `problems` | Las inconsistencias que `hactors validate` denuncia en este proyecto, con su mismo texto. |

El modelo no proyecta el contexto activo: `projects/.state.yaml` describe la raíz de HACTORS, no un proyecto, y `use-project` y `use-run` ya lo responden.

### Artefactos

```yaml
id: ""
kind: ""
path: ""
title: ""
status: ""
actor: ""
```

`kind` nombra la familia: `task`, `rfc`, `plan`, `adr`, `summary`, `evidence`, `finding` o `harness`. `path` es relativa al proyecto. Un campo vacío es información pendiente en el artefacto, no un defecto de la proyección: el modelo no rellena lo que el artefacto no declara.

Un documento cuyo contenido no se puede leer se proyecta con sus campos vacíos, porque su identidad la da su archivo y el archivo se encontró; el modelo no inventa lo que no pudo leer ni oculta lo que hay. Un documento del que tampoco se puede leer su identidad —una RFC sin `rfc:` o un PLAN sin `id:`— no se proyecta: sin identidad no hay entrada que proyectar. En ambos casos el defecto lo denuncia `problems` cuando `validate` lo comprueba.

El estado y el actor se leen del campo que la plantilla de cada familia define, sin reinterpretarlo:

| Familia | Ubicación | `status` procede de | `actor` procede de |
|---|---|---|---|
| TASK | `tasks/TASK-nnnnn.md` | `execution.status` | `actor` |
| RFC | `rfcs/*.md`, fuera los resúmenes | `status` | No tiene: `proposed_by` registra autoría, no autorización de ejecución |
| Acción derivada | Campo `actions:` de su RFC | `status` | `actor` |
| PLAN | `plans/*.md` y `docs/plans/*.md` | `status` | No tiene |
| ADR | `decisions/ADR-nnnnn — nombre-descriptivo.md` | `status` | No tiene: aceptar una decisión es de [actor: human](DECISIONS.md) |
| SUMMARY | Junto al artefacto que resume | `status` | No tiene |
| EVD | Junto a su origen | No tiene estado | No tiene |
| FND | Junto a su origen | `state` | No tiene |
| HRN | `harnesses/HRN-nnnnn/manifest.yaml` | El de cada versión | No tiene |

Una acción derivada no es un artefacto con archivo propio: vive dentro del campo `actions:` de su RFC, conforme a [RFC_TEMPLATE.md](templates/RFC_TEMPLATE.md#acciones-derivadas), así que se proyecta anidada en la entrada de esa RFC, bajo `actions`, con su `id`, su `type`, su `status` y su `actor`, y sin entrada propia en `artifacts`. Las versiones de un HRN se proyectan anidadas en su catálogo, bajo `versions`, con `version`, `status` y `published`, por la misma razón: su estado vive en el catálogo, conforme a [HARNESS.md](HARNESS.md).

Un TEST no se proyecta: el contrato `hactors-model/1.0` no incluye su familia, aunque su identidad y su ubicación estén definidas en [TESTS.md](TESTS.md#identidad-y-ubicación) y `identity.test_ref` sí se resuelva en [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#integridad-referencial). Sus ejecuciones sí constan, como `test_run` en `runs`.

### Instancias de ejecución

```yaml
id: ""
kind: ""
path: ""
status: ""
reference: ""
parent: ""
blocked_reason: ""
```

`kind` es el tipo de instancia; `path`, su directorio relativo al proyecto; `status` y `blocked_reason`, los de su bloque de estado —`global_state` en un workflow_run y `state` en el resto—; `reference`, la referencia de su `identity` al artefacto que ejecuta, vacía cuando es una asociación pendiente; y `parent`, la instancia que la contiene, vacía en un `workflow_run`, que cuelga del proyecto. La jerarquía es la de [HACTORS_SYSTEM.md](HACTORS_SYSTEM.md#2-estructura-de-directorios-de-ejecución) y se reconstruye con ella, no con el contexto activo.

`reference` se proyecta tal como consta y no se resuelve: una instancia de `test_run` proyecta su `test_ref` sin comprobar que exista el TEST, y el modelo no denuncia lo que `validate` ya denuncia en `problems`.

## Disposición

Los archivos derivados viven en un único directorio `views/`, separado de los artefactos normativos:

```
projects/
├── views/
│   └── index.html          el visor: la lista de los proyectos de la raíz
└── <proyecto>/
    ├── views/
    │   ├── index.html      el tablero de ese proyecto
    │   └── project.json    su modelo de lectura
    ├── manifest.yaml       fuente autoritativa
    └── …                   el resto de la estructura de PROJECTS.md
```

Un directorio `views/` no es un proyecto y no se cuenta como tal al enumerar la raíz. Ningún barrido de artefactos lo recorre: `validate` no examina sus archivos, ni los denuncia, ni los repara, y una vista no resuelve como destino de una relación.

## Los dos comandos

Los dos calculan el modelo desde los artefactos y ninguno lee la salida del otro: `export` escribe el JSON y `render` escribe el HTML. Regenerar uno no regenera el otro, y como ninguno es autoritativo, discrepar entre sí no falsea el proyecto. Los dos crean `views/` si falta y no cambian el estado activo.

`export` exige un proyecto activo y proyecta ese. `render` no lo exige: proyecta la raíz entera, porque un visor que enlazara tableros inexistentes no permitiría consultar los proyectos que no están activos.

| Comando | Escribe | No hace |
|---|---|---|
| `hactors export` | `projects/<proyecto activo>/views/project.json` | No dibuja ninguna vista, no repara lo que proyecta y no filtra las inconsistencias: las proyecta tal como `validate` las denuncia. |
| `hactors render` | El tablero de cada proyecto de la raíz en `projects/<proyecto>/views/index.html` y el visor en `projects/views/index.html` | No escribe el modelo de lectura, no modifica ningún artefacto, no omite un proyecto por no poder proyectarlo y no enlaza nada fuera de la raíz de HACTORS. |

Ninguno de los dos ejecuta Git ni asume que existe un repositorio Git.

### El tablero

El tablero de un proyecto responde, sin recorrer sus archivos:

- Qué artefactos hay, de qué familia, y en qué estado está cada uno.
- Qué tiene asignado cada actor, y qué no tiene actor declarado.
- Cómo se ramifica la ejecución y qué instancia está bloqueada, con su motivo.
- Qué aristas declara el grafo del proyecto.
- Qué inconsistencias denuncia `validate`, con su mismo texto.

Cada artefacto enlaza su archivo real con una ruta relativa al tablero. El estado se reproduce tal como consta: el tablero no lo reinterpreta, no deduce uno nuevo y no agrupa bajo una categoría que el artefacto no declare.

### El visor

El visor enumera los proyectos de la raíz y enlaza el tablero de cada uno. De un proyecto proyecta su nombre, su descripción, el recuento de sus artefactos por familia, el de sus instancias y el de sus inconsistencias; y marca cuál es el proyecto activo leyendo `projects/.state.yaml`, que es la única fuente del contexto activo.

Un directorio de `projects/` que no satisface los requisitos de un proyecto se lista con la razón por la que no se puede proyectar, en lugar de omitirse en silencio: ocultarlo sería una segunda forma de desmentir lo que hay en la raíz.

## El visor servido

`tools/viewer/` produce una vista sin escribir ningún archivo derivado: sirve la proyección por HTTP. Resuelve el modelo de lectura en memoria en cada petición con el mismo cálculo que `export` —`root_models` de `hactors_cli.core.model`, el que `write_model` vuelca a `project.json`— y lo dibuja en una página. No es el visor de `projects/views/index.html`, que es un archivo derivado que `render` reemplaza: este no deja vistas detrás, así que apagarlo no le quita nada a la raíz y encenderlo no le añade nada.

Tres rasgos suyos que la disposición de archivos de arriba no contempla quedan fijados aquí:

- **No cachea entre peticiones.** Una vista de archivo se queda atrás hasta que alguien la regenera; esta se resuelve entera cada vez, y lo que muestra es lo que hay en el instante de pedirla.
- **Vive en `tools/`, no en `projects/`.** Es herramienta como la CLI y no artefacto de un proyecto: ningún barrido de `projects/` la recorre, no se cuenta al enumerar la raíz y no resuelve como destino de una relación.
- **Su selección no es el contexto activo.** El proyecto consultado viaja en la consulta, `?proyecto=<nombre>`, y no en `projects/.state.yaml`: mirar un proyecto no es ponerlo en curso. Un nombre que no existe en la raíz se denuncia en la página en lugar de resolverse en silencio al proyecto activo. Ponerlo en curso es otra cosa: la operación de la columna derecha, que sí escribe el estado activo.

Consume la CLI como biblioteca, para calcular y para su única escritura: importa el cálculo del modelo y `set_active_project` de `hactors_cli.core.state`, la misma función que ejecuta `hactors use-project`. No invoca ningún otro comando ni escribe nada más: ni artefactos, ni contadores, ni relaciones, ni vistas.

### El panel de wildcards y las tres columnas

La página se dispone en dos zonas bajo la cabecera: una banda a todo el ancho que lleva las cifras del ámbito consultado, y debajo las tres columnas, cada una con su propia pregunta.

**El panel de wildcards.** Las cifras del ámbito consultado no viven en ninguna columna sino en una banda a todo el ancho entre la cabecera y las tres columnas, porque son el resumen de la página entera y no el contenido de una de sus vistas: las ocho familias, las ejecuciones y las inconsistencias del proyecto elegido, o los totales de la raíz cuando no lo hay. La banda declara su ámbito en el encabezado —el nombre del proyecto consultado, o la raíz— y denuncia en ella misma el nombre consultado que no existe en la raíz, porque ese nombre explica por qué las cifras que muestra son las de la raíz y no las de un proyecto. No reinterpreta ni rellena: un contador a cero se dibuja como cero, y con el ámbito de un proyecto las ocho familias se muestran todas, a cero las que el proyecto no declara, mientras que con el ámbito de la raíz solo se dibujan las familias presentes.

| Columna | Responde | No hace |
|---|---|---|
| Izquierda, los proyectos | Qué proyectos hay en la raíz, cuál es el activo, cuál no se puede proyectar y con qué razón, y cuál se está consultando, con sus recuentos de artefactos, de ejecuciones y de inconsistencias. | No cambia el proyecto activo: seleccionar es seguir un enlace, no enviar la operación. |
| Central, la vista | El texto de cada inconsistencia tal como `validate` lo denuncia, los artefactos documentales del proyecto elegido agrupados por familia en el orden del corpus —con su identificador, su estado tal como consta, su título, su ruta relativa y su actor cuando su familia lo declara, y las acciones derivadas de una RFC y las versiones de un HRN anidadas bajo la fila de su archivo— y los `workflow_run` del proyecto con su identificador, su estado, su ruta relativa y su motivo de bloqueo cuando lo tienen. | No reinterpreta estados ni rellena lo que un artefacto no declara: un estado vacío se muestra como ausencia y no se sustituye por uno deducido. Las vistas posteriores del proyecto se añaden a esta columna sin alterar las otras dos ni la banda de cifras. |
| Derecha, operaciones y comandos | Qué operación escribe el visor sobre la raíz, y qué comando de la CLI produce cada una de las demás que interesan sobre lo consultado, con el texto y el alcance exactos de ese comando. | No ejecuta los comandos que solo muestra: quien quiera lanzarlos los copia y los ejecuta fuera de la página. Y no escribe sin envío expreso: elegir qué proyecto se ve no activa nada. |

La columna derecha separa lo que el visor hace de lo que solo enseña a hacer, en lugar de esconder el límite: lo que la página no puede hacer aparece con el comando que sí lo hace, y cuando el proyecto consultado no es el activo, con el aviso de que la CLI opera sobre el activo y de dónde se activa.

### La operación de activar

El visor ejecuta una sola operación: fijar el proyecto activo, que es lo único que escribe. Su contrato:

- **Se envía, no se elige.** Cada proyecto de la raíz es un botón de envío de un formulario `POST`; no hay activación por selección ni por enlace, y sin JavaScript nada puede enviar el formulario sin un clic.
- **Lleva la marca de la página.** El formulario porta una marca derivada del secreto de la aplicación, así que un formulario servido por otro origen no la reproduce y su envío se rechaza.
- **El destino lo guarda la CLI.** El nombre enviado se comprueba contra los proyectos de la raíz y la escritura la hace `set_active_project`, cuya guarda es la de `use-project`: un nombre que la CLI no acepta se rechaza con su mismo motivo, sin que el visor decida por su cuenta qué nombre es activable.
- **Redirige tras escribir.** La respuesta es un `303` al tablero con el proyecto ya activo, así que recargar la página no vuelve a enviar la operación. Un rechazo se dibuja en el propio tablero con su motivo y un estado `400`, y no cambia nada.

### Lo que el visor servido no hace

No autentica a quien lo abre ni registra quién consultó u operó qué: ninguna vista acredita operadores, y esta tampoco. No ejecuta Git ni asume que existe un repositorio. No carga recursos de la red ni ejecuta JavaScript: la página es HTML y CSS autocontenidos, y todo lo que interpola del proyecto lo escapa como texto. Fuera de la operación de activar no escribe nada: ni artefactos, ni contadores, ni relaciones, ni vistas derivadas.

## Lo que una vista no hace

El HTML es autocontenido: no carga hojas de estilo ni scripts de la red, no hace peticiones y no ejecuta código del proyecto que muestra. Todo lo que se interpola del proyecto se escapa como texto, así que un título no puede convertir una vista en un ejecutor.

Una vista no escribe de vuelta sobre los artefactos, no consume contadores, no registra relaciones, no cambia estados y no repara lo que denuncia. No es un sustituto de `validate`: reproduce sus inconsistencias, no las reevalúa con otro criterio. Y no es un mecanismo de reconstrucción: borrar `views/` entero no le quita nada al proyecto, y regenerarlo no le añade nada. La única escritura de una vista servida no es de la vista sino de su operación: fijar el contexto activo, conforme a [«El visor servido»](#el-visor-servido); ni esa toca un artefacto.
