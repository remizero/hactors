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
from success.common.tools.SuccessUrl import SuccessUrl

# Preconditions / Precondiciones



class SuccessJinja () :
  """
  Jinja2 template utilities for the Success framework.

  Provides methods for registering custom Jinja2 globals and filters.
  """


  @staticmethod
  def registerMethods ( app : Flask ) :
    """
    Register custom Jinja2 methods in the Flask application.

    Registers SuccessUrl methods as global template functions.

    Args:
      app: Flask application instance.
    """
    app.jinja_env.globals [ 'successUrlFor' ]   = SuccessUrl.urlFor
    app.jinja_env.globals [ 'successRedirect' ] = SuccessUrl.redirect
