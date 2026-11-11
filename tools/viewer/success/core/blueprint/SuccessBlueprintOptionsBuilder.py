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
from typing import Any

# Success Libraries / Librerías Success
from success.common.base.SuccessClass             import SuccessClass
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
BLUEPRINT_ALLOWED_ARGS = {
  "name",
  "import_name",
  "url_prefix",
      "subdomain",
  "url_defaults",
  "cli_group",
}


class SuccessBlueprintOptionsBuilder ( SuccessClass ) :
  """
  Builder for Flask blueprint options.

  Constructs the dictionary of parameters needed to create a
  Flask blueprint based on the application's JSON configuration.

  Purpose:
  ----------
  SuccessBlueprintOptionsBuilder is responsible for:
  - Building unique blueprint name
  - Generating import_name for the module
  - Configuring url_prefix, subdomain, cli_group as appropriate
  - Handling url_defaults for versioning

  Expected options structure:
  --------------------------------
  {
    "id": "main",
    "module": {
      "name": "chromadb",
      "path": {
        "protocol": "view",
        "service": "api",
        "version": "v1"
      }
    },
    "url_prefix": "/api",  # Optional
    "cli_group": "api"     # Optional
  }

  Usage:
  ------
  builder = SuccessBlueprintOptionsBuilder('myapp', blueprint_def)
  kwargs = builder.build()
  blueprint = Flask.Blueprint(**kwargs)

  Attributes:
      __appName (str): Application name.
      __module (str): Module name.
      __options (str): Blueprint configuration.
      __path (dict): Module path (protocol, service, version).

  Note:
    - Blueprint name follows pattern: apps_{app}_services_{protocol}_{service}_{version}_{module}_{id}
    - subdomain is only included in SUCCESS_APP_MODE=subdomain mode
  """

  __appName : str  = None
  __module  : str  = None
  __options : str  = None
  __path    : dict = None


  def __init__ ( self, appName : str, options : dict ) -> None :
    """
    Initialize the blueprint options builder.

    Args:
        appName: Name of the application owning the blueprint.
        options: Dictionary with blueprint configuration.
    """
    super ().__init__ ()
    self.__appName = appName
    self.__options = options
    self.__module  = self.__options [ "module" ]
    self.__path    = self.__module [ "path" ]


  def build ( self ) -> dict :
    """
    Build and return the Flask.Blueprint options dictionary.

    Returns:
        dict: Dictionary with name, import_name, and optionally
             url_prefix, subdomain, cli_group.

    Note:
        - subdomain is only included in subdomain mode
        - url_prefix and cli_group only if defined
    """

    options : dict = {
      "name"        : self._name (),
      "import_name" : self._import_name (),
    }

    if self._has_url_prefix () :
      options [ "url_prefix" ] = self._url_prefix ()

    if SuccessSystemEnv.get ( "SUCCESS_APP_MODE" ) == "subdomain" :
      options [ "subdomain" ] = self._subdomain ()

    if self._has_cli_group () :
      options [ "cli_group" ] = self._cli_group ()

    return options


  def _has_cli_group ( self ) -> bool :
    """
    Determine if the blueprint declares a cli_group in its definition.

    Returns:
        bool: True if the blueprint has 'cli_group' defined and is not None.
    """
    return bool ( self.__options.get ( "cli_group" ) )


  def _has_url_defaults ( self ) -> bool :
    """
    Determine if the blueprint declares url_defaults in its definition.

    Returns:
        bool: True if the blueprint has 'url_defaults' defined or has version.
    """
    # default derivado automáticamente
    version  = self.__path.get ( "version" )
    explicit = self.__options.get ( "url_defaults" )

    return bool ( version ) or bool ( explicit )


  def _has_url_prefix ( self ) -> bool :
    """
    Determine if the blueprint declares a url_prefix in its definition.

    Returns:
        bool: True if the blueprint has 'url_prefix' defined and is not None.
    """
    return bool ( self.__options.get ( "url_prefix" ) )


  def _name ( self ) -> str :
    """
    Build the unique blueprint name.

    Returns:
        str: Name in format apps_{app}_services_{protocol}_{service}_{version}_{module}_{id}.
    """
    return f"apps_{self.__appName}_services_{self.__path [ 'protocol' ]}_{self.__path [ 'service' ]}_{self.__path [ 'version' ]}_{self.__module [ 'name' ]}_{self.__options [ 'id' ]}"


  def _import_name ( self ) -> str :
    """
    Build the import_name for the blueprint module.

    Returns:
        str: Import path in Python module format.
    """
    return f"apps.{self.__appName}.services.{self.__path [ 'protocol' ]}.{self.__path [ 'service' ]}.{self.__path [ 'version' ]}.{self.__module [ 'name' ]}.{self.__options [ 'id' ]}"


  def _url_prefix ( self ) -> str :
    """
    Get the configured url_prefix for the blueprint.

    Returns:
        str: The url_prefix defined in the options.
    """
    return self.__options.get ( "url_prefix" )


  def _subdomain ( self ) -> str :
    """
    Determine the subdomain for the blueprint in subdomain mode.

    Returns:
        str: Subdomain name (app name by default).
        None: If not in subdomain mode.

    Note:
        Only used when SUCCESS_APP_MODE=subdomain.
    """
    if SuccessSystemEnv.get ( "SUCCESS_APP_MODE" ) != "subdomain" :
      return None

    return self.__options.get ( "subdomain" ) or self.__appName


  def _url_defaults ( self ) -> dict [ str, Any ] :
    """
    Build the url_defaults dictionary for the blueprint.

    Returns:
        dict[str, Any]: Dictionary with version and additional defaults,
            or None if no defaults exist.

    Note:
        Automatically includes version if defined.
    """
    defaults = {}

    version = self.__path.get ( "version" )
    if version :
      defaults [ "version" ] = version

    extra_defaults = self.__options.get ( "url_defaults", {} )
    if extra_defaults :
      defaults.update ( extra_defaults )

    return defaults or None


  def _cli_group ( self ) -> str :
    """
    Get the configured cli_group for the blueprint.

    Returns:
        str: The cli_group defined in the options.
    """
    return self.__options.get ( "cli_group" )
