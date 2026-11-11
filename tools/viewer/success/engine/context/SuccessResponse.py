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
from flask import Response

# Success Libraries / Librerías Success
from success.common.base.SuccessClass             import SuccessClass
from success.engine.context.SuccessPolicies       import SuccessPolicies
from success.engine.context.SuccessResponsePolicy import SuccessResponsePolicy
from success.engine.io.SuccessOutput              import SuccessOutput

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
# https://blog.miguelgrinberg.com/post/customizing-the-flask-response-class
# https://www.youtube.com/watch?v=gh2HPmpFjn8
# https://github.com/pallets/flask/issues/3294
# https://tedboy.github.io/flask/generated/generated/flask.Response.html
# TODO AGREGAR UN METODO QUE GENERE UNA RESPUESTA ESTANDAR

class SuccessResponse ( SuccessClass ) :
  """
  Response handler for the Success framework.

  Processes output through policies and generates the final
  Flask response using the configured intent executor.

  Attributes:
    _policy (SuccessResponsePolicy): Response policy handler.
    _policies (SuccessPolicies): Policy manager.
  """

  _policy   : SuccessResponsePolicy = None
  _policies : SuccessPolicies       = None


  def __init__ ( self, policy : SuccessResponsePolicy = None, policies : SuccessPolicies = None ) :
    """
    Initialize the response handler.

    Args:
      policy: Response policy instance. Uses default if None.
      policies: Policy manager instance. Uses default if None.
    """
    super ().__init__ ()
    self._policy   = policy or SuccessResponsePolicy ()
    self._policies = policies or SuccessPolicies ()


  def response ( self, output : SuccessOutput ) -> Response :
    """
    Generate a Flask response from the output.

    Args:
      output: SuccessOutput instance to process.

    Returns:
      Response: Flask Response object.

    Raises:
      RuntimeError: If output model or intent is not defined.
    """
    if not output._outputModel :
      raise RuntimeError ( "No se ha definido un output model para la respuesta." )

    if not output._intent :
      raise RuntimeError ( "No se ha definido un intent para la respuesta." )

    builtOutput = output._outputModel.build ( output._canonical )
    builtOutput = self._policies.postOutput ( builtOutput, self._policy )
    return output._intent.execute ( builtOutput, self._policy )
