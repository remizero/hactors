import os
from pathlib import Path
from typing import Optional

from success.engine.infrastructure.SuccessController import SuccessController

from hactors_cli.core.model import root_models
from hactors_cli.core.paths import find_hactors_root
from hactors_cli.core.state import StateError, load_state

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


class Projects ( SuccessController ) :
  """
  Proyecta los proyectos gestionados por HACTORS.

  Solo lectura: resuelve en vivo desde la raíz de HACTORS en cada petición y no
  escribe artefactos, vistas ni estado activo.
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
      "actions"  : self._actions ( selected, active )
    }


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

    return {
      "name"        : entry [ "name" ],
      "description" : model.get ( "description", "" ),
      "active"      : entry [ "name" ] == active,
      "artifacts"   : len ( model.get ( "artifacts", [] ) ),
      "runs"        : len ( model.get ( "runs", [] ) ),
      "problems"    : model.get ( "problems", [] ),
      "counts"      : counts,
      "error"       : entry [ "error" ]
    }


  def _cards ( self, rows : list, totals : dict ) -> list :
    cards = [ { "label" : "proyectos", "count" : len ( rows ), "kind" : "project" } ]

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
    """Las tarjetas del proyecto seleccionado, con sus ocho familias incluso vacías."""
    cards = [
      { "label" : FAMILY_LABELS [ kind ], "count" : row [ "counts" ].get ( kind, 0 ), "kind" : kind }
      for kind in FAMILY_LABELS
    ]

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
        "ejecuta el primer comando antes que los demás."
      )
      actions.append ( {
        "label"   : "Establecer como proyecto activo",
        "command" : f"hactors use-project {selected [ 'name' ]}",
        "detail"  : "Fija el proyecto activo y limpia la selección de ejecución."
      } )

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
