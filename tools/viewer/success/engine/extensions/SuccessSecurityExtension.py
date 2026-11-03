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
from flask          import Flask
from flask_security import Security
from flask_security import UserDatastore

# Success Libraries / Librerías Success
from success.common.base.SuccessExtension import SuccessExtension

# Preconditions / Precondiciones


class SuccessSecurityExtension ( SuccessExtension ) :
  """
  Security extension for the Success framework.

  Integrates Flask-Security for comprehensive security features
  including user authentication, roles, and permissions.
  """


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the Security extension.

    Args:
      app: Flask application instance.
    """
    super ().__init__ ( app )
    # self._extension = Security ()


  def register ( self ) -> None :
    """
    Register the Security extension with the Flask application.

    Note:
      Currently a placeholder for future implementation.
    """
    # if self._extension and hasattr ( self._extension, "init_app" ) :
    #   self._extension.init_app ( self._app, UserDatastore () )
    pass


  def policyDefaults ( self ) -> dict :
    """
    Get default policy settings for Security.

    Returns:
      dict: Dictionary with default Security policy settings.
    """
    return {
      "require_security" : False
    }
