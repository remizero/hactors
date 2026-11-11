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


class RequestMethodException ( SuccessException ) :
  """
  Exception raised when there is an error in the request method.

  Indicates that the request method must be of a specific type.
  """

  def __init__ ( self, message : str ) :
    """
    Initialize the RequestMethodException with a custom message.

    Args:
      message (str): The expected request method type to include in the error message.
    """
    self.message = "Error en el metodo de la solicitud, el metodo debe ser de tipo $s."%message
