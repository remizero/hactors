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
from flask_restful import Resource

# Success Libraries / Librerías Success
from success.common.types.SuccessProtocol            import SuccessProtocol
from success.engine.io.SuccessAction                 import SuccessAction
from success.engine.infrastructure.SuccessController import SuccessController
from success.engine.io.SuccessInput                  import SuccessInput
from success.engine.io.SuccessOutput                 import SuccessOutput
from success.engine.context.SuccessResponse          import SuccessResponse

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessRestfulAction ( SuccessAction, Resource ) :
  """
  RESTful action handler for REST API endpoints.

  Combines SuccessAction with Flask-RESTful Resource for
  handling REST API requests.
  """


  def __init__( self, _input : SuccessInput, _output : SuccessOutput, _response : SuccessResponse, _controller : SuccessController ) -> None :
    """
    Initialize the RESTful action.

    Args:
      _input: Input handler instance.
      _output: Output handler instance.
      _response: Response handler instance.
      _controller: Controller instance.
    """
    super ().__init__ ( _input, _output, _response, _controller )
    self._outputSpec.protocol = SuccessProtocol.RESTFUL
