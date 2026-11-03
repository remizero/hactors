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
from flask             import Flask
from flask_marshmallow import Marshmallow

# Application Libraries / Librerías de la Aplicación
from success.common.base.SuccessExtension                      import SuccessExtension
from success.engine.extensions.proxies.SuccessProxyMarshmallow import mm

# Preconditions / Precondiciones


class SuccessMarshmallowExtension ( SuccessExtension ) :
  """
  Marshmallow extension for the Success framework.

  Integrates Flask-Marshmallow for data serialization
  and schema validation.
  """


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the Marshmallow extension.

    Args:
      app: Flask application instance.
    """
    super ().__init__ ( app )
    self._extension = mm


  def config ( self ) -> None :
    """
    Configure the Marshmallow extension.

    Note:
      Currently a placeholder for future configuration.
    """
    pass


  def policyDefaults ( self ) -> dict :
    """
    Get default policy settings for Marshmallow.

    Returns:
      dict: Dictionary with default Marshmallow policy settings.
    """
    return {
      "require_session"   : False,
      "session_keys_all"  : []
    }
