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
  "resource",
  "urls",
  "endpoint",
}


class SuccessRestfulOptionsBuilder ( SuccessEndpointOptionsBuilder ) :
  """
  Options builder for RESTful type endpoints.

  Builds the configuration needed to register an endpoint
  that exposes REST resources (protocol 'restful').

  Attributes:
    _buildContext (SuccessBuildContext): Build context.
    _options (dict): Specific endpoint configuration.

  Usage:
    builder = SuccessRestfulOptionsBuilder(ctx, endpoint_def)
    kwargs = builder.build()  # {'resource': ..., 'urls': ..., 'endpoint': ...}
  """


  def __init__ ( self, buildContext : SuccessBuildContext, options : dict ) -> None :
    """
    Initialize the options builder for REST resources.

    Args:
      buildContext: Build context with application configuration.
      options: Dictionary with endpoint configuration (resource, urls).
    """
    super ().__init__ ( buildContext, options )


  def build ( self ) -> dict :
    kwargs = {
      "resource" : self.getResource (),
      "urls"     : self._options.get ( "urls" ),
      "endpoint" : self._options.get ( "endpoint" ),
    }
    host = self.getHost ()
    if host :
      kwargs [ "host" ] = host

    return kwargs


  def getResource ( self ) :
    return SuccessSemanticResolver.resolveRestResource (
      self._buildContext._appPath,
      self._options [ "resource" ]
    )


  def getHost ( self ) -> str | None :
    appMode = SuccessSystemEnv.get (
      "SUCCESS_APP_MODE",
      SuccessSystemEnv.get ( "SUCCESS_APP_DOMAIN", "standard" )
    ).strip ().lower ()

    if appMode != "subdomain" :
      return None

    # Opción A (override explícito por endpoint)
    host = self._options.get ( "host" )
    if host :
      return host

    # Opción B (default automático por app en modo subdomain)
    appConfig = self._buildContext._app.config
    if not isinstance ( appConfig, dict ) :
      appConfig = {}

    serverName = appConfig.get ( "SERVER_NAME", SuccessSystemEnv.get ( "SERVER_NAME" ) )
    appPort    = appConfig.get ( "APP_PORT", SuccessSystemEnv.get ( "APP_PORT" ) )
    appName    = os.path.basename ( self._buildContext._app.name )
    return SuccessUrlBuilder ().subdomain ( appName ).domain ( serverName ).port ( appPort ).build ()
