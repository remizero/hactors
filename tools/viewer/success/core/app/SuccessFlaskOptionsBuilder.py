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
from success.common.base.SuccessClass             import SuccessClass
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv
from success.common.tools.SuccessUrlBuilder       import SuccessUrlBuilder
from success.core.SuccessBuildContext             import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessFlaskOptionsBuilder ( SuccessClass ) :
  """
  Builder for Flask configuration options.

  Constructs the dictionary of parameters needed to initialize
  a specific Flask application instance.

  Attributes:
      __buildContext (SuccessBuildContext): Build context with
                                           application configuration.

  Usage:
      ctx = SuccessBuildContext.from_app('synthetos', '/apps/synthetos')
      builder = SuccessFlaskOptionsBuilder(ctx)
      flask_kwargs = builder.build()
      app = Flask(**flask_kwargs)
  """

  __buildContext : SuccessBuildContext = None


  def __init__ ( self, buildContext : SuccessBuildContext ) -> None :
    """
    Initialize the builder with the build context.

    Args:
        buildContext: Context with application configuration.
    """
    super ().__init__ ()
    self.__buildContext = buildContext


  def build ( self ) -> dict :
    """
    Build the Flask parameters dictionary.

    Returns:
        dict: Dictionary with parameters to initialize Flask.
    """
    self._logger.log ( f"Constuyendo opciones de Flask para la aplicación {self.__buildContext._appName}.", "INFO" )

    return {
      "import_name"        : self._importName (),
      "subdomain_matching" : self._subdomainMatching (),
      "host_matching"      : self._hostMatching (),
      "static_host"        : self._staticHost () if self._hostMatching () else None,
      "template_folder"    : self._templateFolder (),
      "static_folder"      : self._staticFolder (),
    }


  def _importName ( self ) -> str :
    """
    Get the import name for the Flask application.

    Returns:
        str: Application name used as import_name.
    """
    return self.__buildContext._appName


  def _subdomainMatching ( self ) -> bool :
    """
    Check if subdomain matching is enabled.

    Returns:
        bool: True if SUCCESS_SUBDOMAIN_MATCHING is 'true', False otherwise.
    """
    return self.__buildContext._appEnv.isTrue ( "SUCCESS_SUBDOMAIN_MATCHING" )


  def _hostMatching ( self ) -> bool :
    """
    Check if host matching is enabled.

    Returns:
        bool: True if SUCCESS_HOST_MATCHING is 'true', False otherwise.
    """
    return self.__buildContext._appEnv.isTrue ( "SUCCESS_HOST_MATCHING" )


  def _staticHost ( self ) -> str | None :
    """
    Build the static host for the application.

    Returns:
        str | None: Static host URL or None if not configured.
    """
    server = self.__buildContext._appEnv.get ( "SERVER_NAME", SuccessSystemEnv.get ( "SERVER_NAME" ) )
    port   = self.__buildContext._appEnv.toInt ( "APP_PORT", SuccessSystemEnv.get ( "APP_PORT" ) )

    return SuccessUrlBuilder ().subdomain ( self.__buildContext._appName ).domain ( server ).port ( port ).build ()


  def _templateFolder ( self ) -> str | None :
    """
    Get the templates folder path.

    Returns:
        str | None: Absolute path to the templates folder.
    """
    return self.__buildContext._pathResolver.templatesFolder ()


  def _staticFolder ( self ) -> str | None :
    """
    Get the static files folder path.

    Returns:
        str | None: Absolute path to the static files folder.
    """
    return self.__buildContext._pathResolver.staticFolder ()
