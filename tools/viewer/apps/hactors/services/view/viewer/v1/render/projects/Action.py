from flask import Response as FlaskResponse
from flask import redirect
from flask import request
from flask import url_for

from success.common.types.SuccessPayloadSource import SuccessPayloadSource
from success.engine.io.SuccessViewAction       import SuccessViewAction
from success.engine.io.SuccessOutput           import SuccessOutput

from apps.hactors.services.view.viewer.v1.render.projects.Input    import Input
from apps.hactors.services.view.viewer.v1.render.projects.Response import Response as ActionResponse
from apps.hactors.modules.hactors.v1.view.controllers.Projects     import Projects


class Action ( SuccessViewAction ) :

  def __init__ ( self ) -> None :
    super ().__init__ ( Input (), SuccessOutput (), ActionResponse (), Projects () )
    self._controllerMethod    = "load"
    self._outputSpec.template = "projects.html"

  def dispatch_request ( self ) -> FlaskResponse :
    # SuccessViewAction solo despacha GET; el envío del formulario de operaciones
    # llega por POST y se resuelve aquí, sin tocar la copia vendida del framework.
    if request.method == "POST" :
      return self.post ()

    return super ().dispatch_request ()

  def get ( self ) -> FlaskResponse :
    return self.execute ( self._controllerMethod )

  def post ( self ) -> FlaskResponse :
    payload = self._input.parse ().validate ()
    outcome = self._controller.execute ( "useProject", payload._validatedData )

    activated = outcome.get ( "activated", "" )
    if activated :
      # Redirigir tras la escritura: recargar la página no la vuelve a enviar.
      return redirect ( url_for ( request.endpoint, proyecto = activated ), code = 303 )

    output   = self._output.presenter ( outcome, SuccessPayloadSource.CONTROLLER, self._outputSpec )
    response = self._response.response ( output )
    response.status_code = 400
    return response
