# Copyright [2026] [Filiberto Zaá Avila "remizero"]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Python Libraries / Librerías Python
from flask                 import json
from flask                 import request
from flask                 import Response
from http                  import HTTPStatus

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                 import SuccessClass
from success.engine.context.SuccessPolicies           import SuccessPolicies
from success.engine.io.SuccessOutput                  import SuccessOutput
from success.engine.infrastructure.SuccessController  import SuccessController
from success.engine.io.SuccessInput                   import SuccessInput
from success.common.types.SuccessPayloadSource        import SuccessPayloadSource
from success.common.types.SuccessProtocol             import SuccessProtocol
from success.engine.context.SuccessResponse           import SuccessResponse
from success.engine.io.SuccessActionOutputSpec        import SuccessActionOutputSpec

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessAction ( SuccessClass ) :
  """
  Base action class for handling HTTP requests.

  Coordinates input parsing, policy evaluation, controller execution,
  and output presentation for both RESTful and View actions.

  Attributes:
    _controller (SuccessController): Controller instance.
    _input (SuccessInput): Input handler.
    _output (SuccessOutput): Output handler.
    _policies (SuccessPolicies): Policy manager.
    _response (SuccessResponse): Response handler.
    _type (SuccessProtocol): Protocol type (RESTFUL or VIEW).
  """

  _controller        : SuccessController       = None
  _input             : SuccessInput            = None
  _output            : SuccessOutput           = None
  _policies          : SuccessPolicies         = None
  _response          : SuccessResponse         = None
  _controllerMethod  : str                     = None
  _outputSpec        : SuccessActionOutputSpec = None




  def __init__( self, _input : SuccessInput, _output : SuccessOutput, _response : SuccessResponse, _controller : SuccessController, _policies : SuccessPolicies = None ) -> None :
    """
    Initialize the action with dependencies.

    Args:
      _input: Input handler instance.
      _output: Output handler instance.
      _response: Response handler instance.
      _controller: Controller instance.
      _policies: Optional policy manager.
    """
    super ().__init__ ()
    self._input      = _input
    self._output     = _output
    self._controller = _controller
    self._response   = _response
    self._policies   = _policies or SuccessPolicies ()
    self._outputSpec = SuccessActionOutputSpec ()


  def execute ( self, method : str ) -> Response :
    """
    Execute the action with pre-input policy evaluation.

    Args:
      method: Controller method name to execute.

    Returns:
      Response: Flask response object.
    """
    preInput = self._policies.preInput ( self, method )
    if not preInput.get ( "allowed", True ) :
      deniedPayload = {
        "success" : False,
        "status"  : preInput.get ( "status", 403 ),
        "message" : preInput.get ( "message", "Access denied" ),
        "error"   : preInput.get ( "error", "Access denied" ),
        "code"    : preInput.get ( "code", "FORBIDDEN" ),
        "type"    : preInput.get ( "type", "authorization" )
      }
      output = self._output.presenter ( deniedPayload, SuccessPayloadSource.CONTROLLER, self._outputSpec )
      return self._response.response ( output )

    source    = SuccessPayloadSource.INPUT
    payload   = self._input.parse ().validate ()

    if not payload._errors :
      source  = SuccessPayloadSource.CONTROLLER
      payload = self._controller.execute ( method, payload._validatedData )

    output    = self._output.presenter ( payload, source, self._outputSpec )

    return self._response.response ( output )
