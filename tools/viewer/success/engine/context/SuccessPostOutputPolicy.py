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
from success.common.base.SuccessClass import SuccessClass

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessPostOutputPolicy ( SuccessClass ) :
  """
  Post-output policy handler.

  Applies policies to the output after it has been built,
  including normalization, metadata, headers, and cookies.
  """


  def __init__ ( self ) -> None :
    """
    Initialize the post-output policy handler.
    """
    super ().__init__ ()


  def apply ( self, builtOutput, responsePolicy ) -> dict :
    """
    Apply post-output policies to the built output.

    This is the central point for post-output policies:
    - Final payload normalization
    - Response metadata (mimetype/content_type/etc)
    - Headers/cookies (if defined in output model)

    Args:
      builtOutput: The built output dictionary.
      responsePolicy: Response policy to apply.

    Returns:
      dict: Modified output with applied policies.
    """
    if not isinstance ( builtOutput, dict ) :
      builtOutput = { "data" : builtOutput }

    responseMeta = builtOutput.get ( "response", {} ) or {}
    if not isinstance ( responseMeta, dict ) :
      responseMeta = {}

    kwargs = responseMeta.get ( "kwargs", {} ) or {}
    if not isinstance ( kwargs, dict ) :
      kwargs = {}

    defaults = responsePolicy.response_kwargs ()
    merged = defaults.copy ()
    merged.update ( kwargs )
    responseMeta [ "kwargs" ] = merged

    headers = responseMeta.get ( "headers", {} ) or {}
    if not isinstance ( headers, dict ) :
      headers = {}
    responseMeta [ "headers" ] = headers

    cookies = responseMeta.get ( "cookies", [] ) or []
    if not isinstance ( cookies, list ) :
      cookies = []
    responseMeta [ "cookies" ] = cookies

    builtOutput [ "response" ] = responseMeta
    return builtOutput
