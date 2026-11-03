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

# Success Libraries / Librerías Success
from success.engine.io.SuccessOutputModelContract import SuccessOutputModelContract

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessInputErrorOutputModel ( SuccessOutputModelContract ) :
  """
  Output model for input validation error responses.

  Formats input validation errors with appropriate structure
  including success flag, message, type, and status.
  """


  def __init__ ( self ) :
    """
    Initialize the input error output model.
    """
    super ().__init__ ()


  def build ( self, canonicalOutput : dict ) -> dict :
    """
    Build the output from canonical format for input errors.

    Args:
      canonicalOutput: Canonical output dictionary.

    Returns:
      dict: Built output with input error information.
    """
    error = canonicalOutput.get ( "error", {} ) or {}
    return {
      'success' : False,
      'msg'     : error.get ( "detail", canonicalOutput.get ( "message" ) ),
      'type'    : "input",
      'status'  : canonicalOutput.get ( "status", 400 )
    }
