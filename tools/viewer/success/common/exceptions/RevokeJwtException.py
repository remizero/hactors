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


class RevokeJwtException ( SuccessException ) :
  """
  Exception raised when JWT revocation fails.

  Indicates that the JWT token could not be successfully revoked.
  """

  def __init__ ( self ) :
    """
    Initialize the RevokeJwtException with a default message.

    Sets the message indicating that the JWT token could not be revoked successfully.
    """
    self.message = "JWToken no ha podido ser revocado con éxito."
