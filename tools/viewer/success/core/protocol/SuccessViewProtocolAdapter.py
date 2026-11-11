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
from flask import Blueprint

# Success Libraries / Librerías Success
from success.core.protocol.SuccessProtocolAdapter            import SuccessProtocolAdapter
from success.core.protocol.options.SuccessViewOptionsBuilder import SuccessViewOptionsBuilder
from success.core.SuccessBuildContext                        import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessViewProtocolAdapter ( SuccessProtocolAdapter ) :
  """
  Protocol adapter for View type endpoints.

  Registers endpoints that render HTML views using the 'view' protocol.
  Each endpoint is registered as a URL rule in the blueprint with
  a view function that renders templates.

  Usage:
    adapter = SuccessViewProtocolAdapter()
    adapter.register(ctx, blueprint, options)
  """


  def __init__ ( self ) -> None :
    """
    Initialize the View protocol adapter.
    """
    super ().__init__ ()


  def register ( self, buildContext : SuccessBuildContext, blueprint : Blueprint, options : dict ) -> None :
    """
    Register a View type endpoint in the blueprint.

    Builds the endpoint options using SuccessViewOptionsBuilder
    and registers the URL rule in the blueprint.

    Args:
      buildContext: Build context with application configuration.
      blueprint: Flask blueprint where the endpoint will be registered.
      options: Dictionary with endpoint configuration
              (endpoint_id, rule, action, methods, etc.).

    Example:
      options = {
        "endpoint_id": "home",
        "rule": "/",
        "action": "services/view/HomeAction",
        "methods": ["GET"]
      }
      adapter.register(ctx, blueprint, options)
    """
    self._logger.log ( f"Creando endpoint {options.get ( "endpoint_id" )}", "INFO" )

    optionsBuilder = SuccessViewOptionsBuilder ( buildContext, options )
    kwargs         = optionsBuilder.build ()

    blueprint.add_url_rule ( **kwargs )

    self._logger.log ( f"Creado endpoint {options.get ( "endpoint_id" )}", "INFO" )