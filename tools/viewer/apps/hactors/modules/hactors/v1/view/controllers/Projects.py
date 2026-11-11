import hashlib
import hmac
import os
import secrets
from pathlib import Path

import mistune
from typing import Optional

from flask import current_app

from success.engine.infrastructure.SuccessController import SuccessController

from hactors_cli.core.model import root_models
from hactors_cli.core.paths import find_hactors_root
from hactors_cli.core.scan import ScanError, load_mapping
from hactors_cli.core.state import StateError, load_state, set_active_project

# Las etiquetas son las familias del corpus, no nombres inventados: las mismas
# que usa la tabla de VIEWS.md#artefactos.
FAMILY_LABELS : dict = {
  "task"     : "TASK",
  "rfc"      : "RFC",
  "plan"     : "PLAN",
  "test"     : "TEST",
  "adr"      : "ADR",
  "summary"  : "SUMMARY",
  "evidence" : "EVD",
  "finding"  : "FND",
  "harness"  : "HRN"
}

# La marca se deriva del secreto de la aplicación, así que solo esta página puede
# emitirla: un formulario servido por otro origen no la reproduce y su envío se
# rechaza.
MARK_SCOPE = b"hactors/viewer/use-project"

# El renderizador escapa el HTML crudo que un documento traiga: su marcado
# propio se dibuja como texto, y los esquemas de enlace que no son de contenido
# quedan neutralizados. Las tablas van como plugin porque el CommonMark puro no
# las conoce y las RFC del corpus sí las usan.
MARKDOWN = mistune.create_markdown ( escape = True, plugins = [ "table" ] )

# Lo que la vista de artefacto sabe dibujar: las familias cuyo archivo es
# markdown y las dos de registro. El catálogo de un HRN es la única familia
# proyectada que se queda fuera, así que su fila no enlaza.
MARKDOWN_KINDS = frozenset ( { "task", "rfc", "plan", "test", "adr", "summary" } )
RECORD_KINDS   = frozenset ( { "evidence", "finding" } )
SERVED_KINDS   = MARKDOWN_KINDS | RECORD_KINDS

# El verbo de cada relación es el de su especificación; un tipo que no está ahí
# se dibuja con el nombre declarado, no con una traducción inventada.
RELATION_LABELS = { "verifies" : "Verifica", "supports" : "Soporta", "affects" : "Afecta" }

# Los campos de procedencia y de fechas en el orden en que los lista el esquema
# de cada registro, que es el orden en que se dibujan.
EVIDENCE_SOURCE = (
  ( "rfc", "RFC" ), ( "harness", "Harness" ), ( "execution", "Ejecución" ),
  ( "artifact", "Artefacto" ), ( "commit", "Commit" )
)
EVIDENCE_DATES  = ( ( "recorded", "Registrado" ), )

FINDING_SOURCE  = (
  ( "execution", "Ejecución" ), ( "artifact", "Artefacto" ), ( "workflow", "Workflow" ),
  ( "task", "TASK" ), ( "rfc", "RFC" )
)
FINDING_DATES   = ( ( "opened", "Abierto" ), ( "updated", "Actualizado" ), ( "resolved", "Resuelto" ) )

# Las dos severidades que bloquean el cierre de la TASK de origen, conforme a
# FINDING.md: son las que la insignia marca.
BLOCKING_SEVERITIES = frozenset ( { "critical", "high" } )


def operation_mark () -> str :
  return hmac.new ( str ( current_app.secret_key ).encode (), MARK_SCOPE, hashlib.sha256 ).hexdigest ()


def _text ( value ) -> str :
  return value.strip () if isinstance ( value, str ) else ""


def _items ( value ) -> list :
  """Los elementos declarados de una lista, sin los vacíos."""
  if not isinstance ( value, list ) :
    return []
  return [ item for item in ( _text ( element ) for element in value ) if item ]


def _declared_fields ( block, fields : tuple ) -> list :
  """Los campos con valor, en el orden en que los lista el esquema."""
  block   = block if isinstance ( block, dict ) else { }
  drawn   = []
  for key, label in fields :
    value = _text ( block.get ( key ) )
    if value :
      drawn.append ( { "label" : label, "value" : value } )
  return drawn


def _badges ( declared : tuple ) -> list :
  """Las insignias del registro, en el orden dado y solo las que tienen valor."""
  return [ { "value" : value, "bad" : bad } for value, bad in declared if value ]


def _relation_groups ( declared ) -> list :
  """Las relaciones agrupadas por tipo, en el orden en que el registro las declara."""
  groups = []
  for entry in declared if isinstance ( declared, list ) else [] :
    if not isinstance ( entry, dict ) :
      continue
    target = _text ( entry.get ( "target" ) )
    if not target :
      continue
    kind  = _text ( entry.get ( "relation" ) )
    group = next ( ( item for item in groups if item [ "relation" ] == kind ), None )
    if group is None :
      groups.append ( {
        "relation" : kind,
        "label"    : RELATION_LABELS.get ( kind, kind ),
        "targets"  : [ target ]
      } )
    else :
      group [ "targets" ].append ( target )
  return groups


def _relations_section ( declared ) -> dict :
  return {
    "kind"   : "relations",
    "label"  : "Relaciones",
    "groups" : _relation_groups ( declared ),
    "empty"  : "Sin relaciones declaradas"
  }


def _source_section ( data : dict, fields : tuple ) -> dict :
  return {
    "kind"  : "fields",
    "label" : "Procedencia",
    "rows"  : _declared_fields ( data.get ( "source" ), fields ),
    "empty" : "Sin procedencia declarada"
  }


def _evidence_record ( data : dict ) -> dict :
  environment = data.get ( "environment" )
  environment = environment if isinstance ( environment, dict ) else { }
  observed    = {
    "platform" : _text ( environment.get ( "platform" ) ),
    "commands" : _items ( environment.get ( "commands" ) ),
    "outputs"  : _items ( environment.get ( "outputs" ) )
  }

  sections = [
    _relations_section ( data.get ( "relations" ) ),
    _source_section ( data, EVIDENCE_SOURCE )
  ]
  # El entorno solo abre una sección cuando algo de él consta: un título sobre un
  # bloque vacío dibujaría un apartado que el registro no declara.
  if observed [ "platform" ] or observed [ "commands" ] or observed [ "outputs" ] :
    sections.append ( {
      "kind"        : "environment",
      "label"       : "Entorno y resultados",
      "environment" : observed
    } )

  return {
    "family"   : "evidence",
    "title"    : _text ( data.get ( "title" ) ),
    "badges"   : _badges ( ( ( _text ( data.get ( "kind" ) ), False ), ) ),
    "sections" : sections,
    "dates"    : _declared_fields ( data, EVIDENCE_DATES )
  }


def _finding_record ( data : dict ) -> dict :
  severity = _text ( data.get ( "severity" ) )
  return {
    "family"   : "finding",
    "title"    : _text ( data.get ( "title" ) ),
    "badges"   : _badges ( (
      ( severity, severity in BLOCKING_SEVERITIES ),
      ( _text ( data.get ( "state" ) ), False ),
      ( _text ( data.get ( "kind" ) ), False )
    ) ),
    "sections" : [
      _source_section ( data, FINDING_SOURCE ),
      {
        "kind"    : "chips",
        "label"   : "Acciones",
        # `entries` y no `items`, por lo mismo que en `_family_groups`.
        "entries" : _items ( data.get ( "actions" ) ),
        "empty"   : "Sin acciones declaradas"
      },
      _relations_section ( data.get ( "relations" ) )
    ],
    "dates"    : _declared_fields ( data, FINDING_DATES )
  }


def _record ( project : Path, path : Path, kind : str ) -> dict :
  """
  Los campos que el registro declara, en el orden en que los lista su esquema.

  Se lee con el lector de la CLI y con su misma tolerancia: un registro que no se
  puede leer se dibuja con sus campos vacíos, como lo proyecta el modelo, y el
  defecto lo denuncia `validate`, no esta vista.
  """
  try :
    data = load_mapping ( project, path )
  except ScanError :
    data = { }
  return _evidence_record ( data ) if kind == "evidence" else _finding_record ( data )


class Projects ( SuccessController ) :
  """
  Proyecta los proyectos gestionados por HACTORS y permite activar uno.

  Resuelve en vivo desde la raíz de HACTORS en cada petición y no guarda nada
  entre una y otra. `load` solo lee; `useProject` es la única escritura del
  visor y reproduce lo que hace `hactors use-project`.
  """

  def load ( self, payload : dict ) -> dict :
    root = self._root ()

    try :
      active = load_state ( root ) [ "active_project" ]
    except StateError :
      active = ""

    rows   = [ self._row ( entry, active ) for entry in root_models ( root ) ]
    totals : dict = {}
    for row in rows :
      for kind, count in row [ "counts" ].items () :
        totals [ kind ] = totals.get ( kind, 0 ) + count

    # La selección vive en la consulta y no en el estado activo: elegir qué
    # proyecto se ve no es declarar cuál está en curso.
    wanted   = str ( payload.get ( "proyecto", "" ) ).strip ()
    selected = next ( ( row for row in rows if row [ "name" ] == wanted ), None )

    # La instancia elegida viaja con su proyecto: su raíz solo existe dentro de él.
    # La vista es el directorio de la instancia, no su profundidad: solo los
    # artefactos que viven directamente en él y las instancias que anida.
    wanted_run = str ( payload.get ( "ejecucion", "" ) ).strip ()
    run        = None
    if selected and not selected [ "error" ] and wanted_run :
      run = next ( ( entry for entry in selected [ "instances" ] if entry [ "id" ] == wanted_run ), None )

    if run :
      prefix   = run [ "path" ] + "/"
      direct   = [
        art for art in selected [ "documents" ]
        if art [ "path" ].startswith ( prefix ) and "/" not in art [ "path" ] [ len ( prefix ) : ]
      ]
      children = [ entry for entry in selected [ "instances" ] if entry [ "parent" ] == run [ "id" ] ]
      trail    = self._run_trail ( selected [ "instances" ], run )
    else :
      direct   = []
      children = []
      trail    = []

    # El origen de una instancia es el documento que la inicia: su propia
    # referencia, y en el `task_run` la del `workflow_run` del que desciende,
    # que es donde la norma la pone. Solo se enlaza el documento que el modelo
    # proyecta y el visor sabe dibujar: una referencia sin archivo no recibe un
    # enlace inventado.
    origin_ref = self._origin_reference ( selected [ "instances" ], run ) if run else ""
    origin_doc = (
      next (
        ( art for art in selected [ "documents" ] if art [ "id" ] == origin_ref and art [ "served" ] ),
        None
      )
      if selected and origin_ref else None
    )

    # El artefacto consultado viaja por su ruta relativa al proyecto, y solo se
    # sirve el que el modelo proyecta y cuya familia el visor sabe dibujar: un
    # nombre ajeno, o un camino fuera del proyecto, no abren ningún archivo y se
    # denuncian en la columna.
    wanted_doc = str ( payload.get ( "documento", "" ) ).strip ()
    doc        = None
    if selected and not selected [ "error" ] and wanted_doc :
      found = next (
        ( art for art in selected [ "documents" ]
          if art [ "path" ] == wanted_doc and art [ "served" ] ),
        None
      )
      if found :
        doc = self._rendered_artifact ( root, selected [ "name" ], found )

    return {
      "status"   : 200,
      "root"     : str ( root ),
      "active"   : active,
      "projects" : rows,
      "selected" : selected,
      "missing"  : wanted if wanted and selected is None else "",
      "run"          : run,
      "run_trail"    : trail,
      "run_direct"   : self._origin_group ( origin_ref, origin_doc ) + self._family_groups ( direct ),
      "run_children" : children,
      "run_missing"  : wanted_run if selected and not selected [ "error" ] and wanted_run and run is None else "",
      "doc"          : doc,
      "doc_missing"  : wanted_doc if selected and not selected [ "error" ] and wanted_doc and doc is None else "",
      "cards"    : self._project_cards ( selected ) if selected else self._cards ( rows, totals ),
      "actions"  : self._actions ( selected, active ),
      "marca"    : operation_mark ()
    }


  def _run_trail ( self, instances : list, run : dict ) -> list :
    """La cadena de identidades desde el `workflow_run` hasta la instancia elegida."""
    by_id  = { entry [ "id" ] : entry for entry in instances }
    trail  = [ run [ "id" ] ]
    parent = run [ "parent" ]
    while parent in by_id :
      trail.insert ( 0, parent )
      parent = by_id [ parent ] [ "parent" ]
    return trail


  def _origin_reference ( self, instances : list, run : dict ) -> str :
    """La identidad del documento que inicia la instancia elegida."""
    if run [ "reference" ] :
      return run [ "reference" ]
    if run [ "kind" ] != "task_run" :
      return ""
    by_id  = { entry [ "id" ] : entry for entry in instances }
    parent = run [ "parent" ]
    while parent in by_id :
      if by_id [ parent ] [ "reference" ] :
        return by_id [ parent ] [ "reference" ]
      parent = by_id [ parent ] [ "parent" ]
    return ""


  def _rendered_artifact ( self, root : Path, project : str, artifact : dict ) -> dict :
    """El artefacto proyectado con su contenido dibujado según su familia."""
    directory = root / "projects" / project
    path      = directory / artifact [ "path" ]
    if artifact [ "kind" ] in RECORD_KINDS :
      return { **artifact, "record" : _record ( directory, path, artifact [ "kind" ] ) }
    return { **artifact, "markdown" : MARKDOWN ( path.read_text ( encoding = "utf-8" ) ) }


  def useProject ( self, payload : dict ) -> dict :
    """
    Fija el proyecto activo, como `hactors use-project`.

    Devuelve el nombre activado para que la acción redirija, o el tablero de la
    raíz con el motivo del rechazo. La guarda del proyecto la pone la CLI: el
    visor no decide por su cuenta qué nombre es activable.
    """
    root = self._root ()
    name = str ( payload.get ( "proyecto", "" ) ).strip ()
    mark = str ( payload.get ( "marca", "" ) )

    if not secrets.compare_digest ( mark.encode (), operation_mark ().encode () ) :
      rejected = "La operación no lleva la marca de esta página: recarga el visor y vuelve a enviarla."
    elif name not in { entry [ "name" ] for entry in root_models ( root ) } :
      rejected = f"No hay ningún proyecto llamado «{name}» en la raíz."
    else :
      try :
        set_active_project ( root, name )
      except StateError as exc :
        rejected = str ( exc )
      else :
        return { "activated" : name }

    # El nombre enviado no pasa a la selección: el rechazo ya lo nombra, y la
    # página no lo denuncia dos veces.
    board              = self.load ( {} )
    board [ "rejected" ] = rejected
    return board


  def _root ( self ) -> Path :
    declared = os.environ.get ( "HACTORS_ROOT", "" ).strip ()
    if declared :
      return Path ( declared ).expanduser ().resolve ()

    return find_hactors_root ( Path.cwd () )


  def _row ( self, entry : dict, active : str ) -> dict :
    model  = entry [ "model" ]
    counts : dict = {}
    for artifact in model.get ( "artifacts", [] ) :
      kind           = artifact.get ( "kind", "" )
      counts [ kind ] = counts.get ( kind, 0 ) + 1

    # `served` dice si la vista de artefacto sabe dibujar esa familia: es lo que
    # distingue una fila que enlaza de una que se queda inerte.
    return {
      "name"        : entry [ "name" ],
      "description" : model.get ( "description", "" ),
      "active"      : entry [ "name" ] == active,
      "artifacts"   : len ( model.get ( "artifacts", [] ) ),
      "documents"   : [
        { **artifact, "served" : artifact.get ( "kind", "" ) in SERVED_KINDS }
        for artifact in model.get ( "artifacts", [] )
      ],
      "runs"        : len ( model.get ( "runs", [] ) ),
      "instances"   : model.get ( "runs", [] ),
      "workflows"   : [ run for run in model.get ( "runs", [] ) if run.get ( "kind" ) == "workflow_run" ],
      "problems"    : model.get ( "problems", [] ),
      "counts"      : counts,
      "error"       : entry [ "error" ]
    }


  def _family_groups ( self, artifacts : list ) -> list :
    """Los artefactos dados agrupados por familia, en el orden del corpus y solo las presentes."""
    # La clave no puede llamarse `items`: Jinja resuelve antes el atributo del
    # dict y devolvería el método `dict.items` en lugar de la lista.
    return [
      {
        "kind"    : kind,
        "label"   : label,
        "entries" : [ entry for entry in artifacts if entry.get ( "kind" ) == kind ]
      }
      for kind, label in FAMILY_LABELS.items ()
      if any ( entry.get ( "kind" ) == kind for entry in artifacts )
    ]


  def _origin_group ( self, reference : str, document : Optional [ dict ] ) -> list :
    """El artefacto que inicia la instancia, como primer grupo de los suyos."""
    # Vive fuera del directorio de la instancia, así que el barrido de sus
    # artefactos directos no lo aporta y se añade delante de los de familia.
    if not reference :
      return []
    entry = (
      { **document, "origin" : True } if document else
      { "id" : reference, "status" : "", "title" : "", "path" : "",
        "served" : False, "origin" : True, "declared" : True }
    )
    return [ { "kind" : "origin", "label" : "Origen de esta instancia", "entries" : [ entry ] } ]


  def _cards ( self, rows : list, totals : dict ) -> list :
    cards = [ { "label" : "proyectos", "count" : len ( rows ), "kind" : "project" } ]

    # WORKFLOW y workflow_run son un mismo contador: lo físico es la instancia, no el concepto.
    cards.append ( {
      "label" : "workflow",
      "count" : sum ( len ( row [ "workflows" ] ) for row in rows ),
      "kind"  : "workflow"
    } )

    cards.extend (
      { "label" : FAMILY_LABELS [ kind ], "count" : totals [ kind ], "kind" : kind }
      for kind in FAMILY_LABELS if totals.get ( kind )
    )

    cards.append ( {
      "label" : "ejecuciones",
      "count" : sum ( row [ "runs" ] for row in rows ),
      "kind"  : "run"
    } )
    cards.append ( {
      "label" : "inconsistencias",
      "count" : sum ( len ( row [ "problems" ] ) for row in rows ),
      "kind"  : "problem"
    } )

    return cards


  def _project_cards ( self, row : dict ) -> list :
    """Las tarjetas del proyecto seleccionado: el contador de workflows y sus ocho familias incluso vacías."""
    cards = [ { "label" : "workflow", "count" : len ( row [ "workflows" ] ), "kind" : "workflow" } ]

    cards.extend (
      { "label" : FAMILY_LABELS [ kind ], "count" : row [ "counts" ].get ( kind, 0 ), "kind" : kind }
      for kind in FAMILY_LABELS
    )

    cards.append ( { "label" : "ejecuciones", "count" : row [ "runs" ], "kind" : "run" } )
    cards.append ( { "label" : "inconsistencias", "count" : len ( row [ "problems" ] ), "kind" : "problem" } )

    return cards


  def _actions ( self, selected : Optional [ dict ], active : str ) -> list :
    """
    Las acciones con el comando de la CLI que las produce.

    El visor no los ejecuta: los muestra. Las descripciones reproducen el help
    de cada comando, y el aviso del grupo declara que la CLI solo opera sobre el
    proyecto activo, que no tiene por qué ser el seleccionado aquí.
    """
    groups = [ {
      "title"   : "Globales",
      "note"    : "",
      "actions" : [
        {
          "label"   : "Regenerar las vistas derivadas",
          "command" : "hactors render",
          "detail"  : "Dibuja el visor de projects/views/ y el tablero de cada proyecto, sin exigir proyecto activo."
        },
        {
          "label"   : "Listar los comandos",
          "command" : "hactors --help",
          "detail"  : "La enumeración de la CLI, de la que esta columna es un resumen."
        }
      ]
    } ]

    if selected is None :
      return groups

    actions : list = []
    note           = ""

    if selected [ "name" ] != active :
      note = (
        f"La CLI solo opera sobre el proyecto activo, que ahora es «{active or 'ninguno'}»: "
        f"activa «{selected [ 'name' ]}» en el bloque de operaciones antes de ejecutar estos comandos."
      )

    actions.extend ( [
      {
        "label"   : "Comprobar el proyecto",
        "command" : "hactors validate",
        "detail"  : "Referencias, grafo, hallazgos bloqueantes y actions: del proyecto activo, sin reparar nada."
      },
      {
        "label"   : "Proyectar el modelo de lectura",
        "command" : "hactors export",
        "detail"  : "Escribe views/project.json del proyecto activo."
      },
      {
        "label"   : "Crear una TASK",
        "command" : 'hactors create-task --task "<descripción>"',
        "detail"  : "TASK-nnnnn en tasks/ con su cabecera, sin validar su contenido."
      }
    ] )

    groups.append ( { "title" : f"Proyecto {selected [ 'name' ]}", "note" : note, "actions" : actions } )

    return groups
