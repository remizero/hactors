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
from flask import Flask

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessAppPlaceholderFactory () :
  """
  Factory for creating placeholder Flask applications.

  Provides a default Flask application with a placeholder route
  when no main application is defined.
  """

  @classmethod
  def build ( cls ) -> Flask :
    """
    Build a placeholder Flask application.

    Returns:
      Flask: A Flask application instance with a default root route.
    """
    app = Flask ( "success_placeholder_root" )

    @app.route ( "/" )
    def root () :
      return (
        "<h1>🚧 App principal no definida</h1>"
        "<p>Estás viendo la app placeholder de Success.</p>"
        "<p>Define <code>SUCCESS_MAIN_APP</code> para cambiar esta vista.</p>",
        200,
      )

    return app