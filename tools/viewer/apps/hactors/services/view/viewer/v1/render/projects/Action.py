from flask import Response as FlaskResponse

from success.engine.io.SuccessViewAction import SuccessViewAction
from success.engine.io.SuccessOutput     import SuccessOutput

from apps.hactors.services.view.viewer.v1.render.projects.Input    import Input
from apps.hactors.services.view.viewer.v1.render.projects.Response import Response as ActionResponse
from apps.hactors.modules.hactors.v1.view.controllers.Projects     import Projects


class Action ( SuccessViewAction ) :

  def __init__ ( self ) -> None :
    super ().__init__ ( Input (), SuccessOutput (), ActionResponse (), Projects () )
    self._controllerMethod    = "load"
    self._outputSpec.template = "projects.html"

  def get ( self ) -> FlaskResponse :
    return self.execute ( self._controllerMethod )
