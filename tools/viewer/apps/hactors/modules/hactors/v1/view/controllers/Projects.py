import os
from pathlib import Path

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

    return {
      "status"   : 200,
      "root"     : str ( root ),
      "active"   : active,
      "projects" : rows,
      "cards"    : self._cards ( rows, totals )
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
      "problems"    : len ( model.get ( "problems", [] ) ),
      "counts"      : counts,
      "chips"       : [
        { "label" : FAMILY_LABELS.get ( kind, kind ), "count" : count }
        for kind, count in sorted ( counts.items (), key = lambda item : ( -item [ 1 ], item [ 0 ] ) )
      ],
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
      "count" : sum ( row [ "problems" ] for row in rows ),
      "kind"  : "problem"
    } )

    return cards
