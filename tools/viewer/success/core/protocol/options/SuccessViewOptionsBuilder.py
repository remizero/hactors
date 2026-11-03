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
import os

# Success Libraries / Librerías Success
from success.core.protocol.options.SuccessEndpointOptionsBuilder import SuccessEndpointOptionsBuilder
from success.common.infra.config.SuccessSystemEnv                import SuccessSystemEnv
from success.core.discovery.SuccessSemanticResolver              import SuccessSemanticResolver
from success.common.tools.SuccessUrlBuilder                      import SuccessUrlBuilder
from success.core.SuccessBuildContext                            import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
ENDPOINT_ALLOWED_ARGS = {
  "rule",
  "endpoint",
  "view_func",
  "provide_automatic_options",
  "options",
}


class SuccessViewOptionsBuilder ( SuccessEndpointOptionsBuilder ) :
  """
  Options builder for View type endpoints.

  Builds the configuration needed to register an endpoint
  that renders views (protocol 'view').

  Attributes:
    _buildContext (SuccessBuildContext): Build context.
    _options (dict): Specific endpoint configuration.

  Usage:
    builder = SuccessViewOptionsBuilder(ctx, endpoint_def)
    kwargs = builder.build()  # {'rule': ..., 'view_func': ..., 'methods': ...}
  """


  def __init__ ( self, buildContext : SuccessBuildContext, options : dict ) -> None :
    """
    Initialize the options builder for views.

    Args:
      buildContext: Build context with application configuration.
      options: Dictionary with endpoint configuration (rule, action, methods).
    """
    super ().__init__ ( buildContext, options )


  def build ( self ) -> dict :
    host   = self.getHost ()
    _viewFunc = self.getViewFunc ()
    kwargs = {
      "rule"      : self._options.get ( "rule" ),
      "view_func" : self.getViewFunc (),
      "methods"   : self._options.get ( "methods", [ "GET" ] ),
    }
    if host :
      kwargs [ "host" ] = host

    return kwargs


  def getHost ( self ) -> str | None :
    appMode = SuccessSystemEnv.get (
      "SUCCESS_APP_MODE",
      SuccessSystemEnv.get ( "SUCCESS_APP_DOMAIN", "standard" )
    ).strip ().lower ()

    if appMode != "subdomain" :
      return None

    host = self._options.get ( "host" )
    if host :
      return host

    appConfig = self._buildContext._app.config
    if not isinstance ( appConfig, dict ) :
      appConfig = {}

    serverName = appConfig.get ( "SERVER_NAME", SuccessSystemEnv.get ( "SERVER_NAME" ) )
    appPort    = appConfig.get ( "APP_PORT", SuccessSystemEnv.get ( "APP_PORT" ) )
    appName    = os.path.basename ( self._buildContext._app.name )

    return SuccessUrlBuilder ().subdomain ( appName ).domain ( serverName ).port ( appPort ).build ()


  def getViewFunc ( self ) :
    return SuccessSemanticResolver.resolveViewFunc (
      self._buildContext._appPath,
      self._options [ "action" ],
      self._options.get ( "action_name" )
    )
