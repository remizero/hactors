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

# Application Libraries / Librerías de la Aplicación
from success.common.base.SuccessException import SuccessException

# Preconditions / Precondiciones


class OutputException ( SuccessException ) :
  """
  Exception raised when no valid output type is defined.

  Indicates that a valid output type must be defined for the response to be sent.
  """

  def __init__ ( self ) :
    """
    Initialize the OutputException with a default message.

    Sets the message indicating that no valid output type has been defined for the response.
    """
    self.message = "No se ha definido un tipo de salida valida para la respuesta a ser enviada."
