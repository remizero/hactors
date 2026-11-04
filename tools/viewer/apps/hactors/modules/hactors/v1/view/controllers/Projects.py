import hashlib
import hmac
import os
import secrets
from pathlib import Path
from typing import Optional

from flask import current_app

from success.engine.infrastructure.SuccessController import SuccessController

from hactors_cli.core.model import root_models
from hactors_cli.core.paths import find_hactors_root
from hactors_cli.core.state import StateError, load_state, set_active_project

# Las etiquetas son las familias del corpus, no nombres inventados: las mismas
# que usa la tabla de VIEWS.md#artefactos.
FAMILY_LABELS : dict = {
  "task"     : "TASK",
  "rfc"      : "RFC",
  "plan"     : "PLAN",
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


def operation_mark () -> str :
  return hmac.new ( str ( current_app.secret_key ).encode (), MARK_SCOPE, hashlib.sha256 ).hexdigest ()


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

    return {
      "status"   : 200,
      "root"     : str ( root ),
      "active"   : active,
      "projects" : rows,
      "selected" : selected,
      "missing"  : wanted if wanted and selected is None else "",
      "cards"    : self._project_cards ( selected ) if selected else self._cards ( rows, totals ),
      "actions"  : self._actions ( selected, active ),
      "marca"    : operation_mark ()
    }


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

    # `artifacts` es el recuento y `families` la lista agrupada: dos claves para
    # dos valores, porque la columna izquierda dibuja el número y la central los
    # grupos, y una clave repetida en el literal hace ganar al último valor.
    return {
      "name"        : entry [ "name" ],
      "description" : model.get ( "description", "" ),
      "active"      : entry [ "name" ] == active,
      "artifacts"   : len ( model.get ( "artifacts", [] ) ),
      "runs"        : len ( model.get ( "runs", [] ) ),
      "workflows"   : [ run for run in model.get ( "runs", [] ) if run.get ( "kind" ) == "workflow_run" ],
      "families"    : self._artifact_groups ( model ),
      "problems"    : model.get ( "problems", [] ),
      "counts"      : counts,
      "error"       : entry [ "error" ]
    }


  def _artifact_groups ( self, model : dict ) -> list :
    """Los artefactos del proyecto agrupados por familia, en el orden del corpus."""
    # La clave no puede llamarse `items`: Jinja resuelve antes el atributo del
    # dict y devolvería el método `dict.items` en lugar de la lista.
    return [
      {
        "kind"    : kind,
        "label"   : label,
        "entries" : [ entry for entry in model.get ( "artifacts", [] ) if entry.get ( "kind" ) == kind ]
      }
      for kind, label in FAMILY_LABELS.items ()
      if any ( entry.get ( "kind" ) == kind for entry in model.get ( "artifacts", [] ) )
    ]


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
