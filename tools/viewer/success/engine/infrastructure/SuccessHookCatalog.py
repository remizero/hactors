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
from typing import Dict
from typing import Tuple

# Application Libraries / Librerías de la Aplicación
from success.engine.infrastructure.HookAction      import HookAction
from success.engine.infrastructure.HookActionChain import HookActionChain

# Preconditions / Precondiciones


class SuccessHookCatalog () :
  """
  Official catalog of supported hook actions for the framework.

  Defines all valid hook action paths that can be used when
  registering hooks in the Success framework.
  """

  BUILD_APP                           = HookActionChain.start ( "build", "app" ).build ()
  BUILD_APP_CONFIG_LOAD               = HookActionChain.fromAction ( BUILD_APP ).component ( "config" ).stage ( "load" ).build ()
  BUILD_APP_EXTENSIONS_CORE_LOAD      = HookActionChain.fromAction ( BUILD_APP ).component ( "extensions" ).stage ( "core_load" ).build ()
  BUILD_APP_EXTENSIONS_CUSTOM_LOAD    = HookActionChain.fromAction ( BUILD_APP ).component ( "extensions" ).stage ( "custom_load" ).build ()
  BUILD_APP_BLUEPRINTS_LOAD           = HookActionChain.fromAction ( BUILD_APP ).component ( "blueprints" ).stage ( "load" ).build ()

  BUILD_EXTENSION                     = HookActionChain.start ( "build", "extension" ).build ()
  BUILD_EXTENSION_CORE_REGISTER       = HookActionChain.fromAction ( BUILD_EXTENSION ).component ( "core" ).stage ( "register" ).build ()
  BUILD_EXTENSION_CUSTOM_REGISTER     = HookActionChain.fromAction ( BUILD_EXTENSION ).component ( "custom" ).stage ( "register" ).build ()

  BUILD_BLUEPRINT                     = HookActionChain.start ( "build", "blueprint" ).build ()
  BUILD_BLUEPRINT_LOADER_LOAD         = HookActionChain.fromAction ( BUILD_BLUEPRINT ).component ( "loader" ).stage ( "load" ).build ()
  BUILD_BLUEPRINT_BUILDER_CREATE      = HookActionChain.fromAction ( BUILD_BLUEPRINT ).component ( "builder" ).stage ( "create" ).build ()

  BUILD_ENDPOINT                      = HookActionChain.start ( "build", "endpoint" ).build ()
  BUILD_ENDPOINT_LOADER_LOAD          = HookActionChain.fromAction ( BUILD_ENDPOINT ).component ( "loader" ).stage ( "load" ).build ()
  BUILD_ENDPOINT_BUILDER_CREATE       = HookActionChain.fromAction ( BUILD_ENDPOINT ).component ( "builder" ).stage ( "create" ).build ()
  BUILD_ENDPOINT_ADAPTER_REGISTER     = HookActionChain.fromAction ( BUILD_ENDPOINT ).component ( "adapter" ).stage ( "register" ).build ()

  _ACTIONS : Dict [ str, HookAction ] = {
    "BUILD_APP"                        : BUILD_APP,
    "BUILD_APP_CONFIG_LOAD"            : BUILD_APP_CONFIG_LOAD,
    "BUILD_APP_EXTENSIONS_CORE_LOAD"   : BUILD_APP_EXTENSIONS_CORE_LOAD,
    "BUILD_APP_EXTENSIONS_CUSTOM_LOAD" : BUILD_APP_EXTENSIONS_CUSTOM_LOAD,
    "BUILD_APP_BLUEPRINTS_LOAD"        : BUILD_APP_BLUEPRINTS_LOAD,
    "BUILD_EXTENSION"                  : BUILD_EXTENSION,
    "BUILD_EXTENSION_CORE_REGISTER"    : BUILD_EXTENSION_CORE_REGISTER,
    "BUILD_EXTENSION_CUSTOM_REGISTER"  : BUILD_EXTENSION_CUSTOM_REGISTER,
    "BUILD_BLUEPRINT"                  : BUILD_BLUEPRINT,
    "BUILD_BLUEPRINT_LOADER_LOAD"      : BUILD_BLUEPRINT_LOADER_LOAD,
    "BUILD_BLUEPRINT_BUILDER_CREATE"   : BUILD_BLUEPRINT_BUILDER_CREATE,
    "BUILD_ENDPOINT"                   : BUILD_ENDPOINT,
    "BUILD_ENDPOINT_LOADER_LOAD"       : BUILD_ENDPOINT_LOADER_LOAD,
    "BUILD_ENDPOINT_BUILDER_CREATE"    : BUILD_ENDPOINT_BUILDER_CREATE,
    "BUILD_ENDPOINT_ADAPTER_REGISTER"  : BUILD_ENDPOINT_ADAPTER_REGISTER
  }


  @classmethod
  def all ( cls ) -> Tuple [ HookAction, ... ] :
    """
    Get all catalog actions.

    Returns:
      Tuple[HookAction, ...]: Tuple of all hook actions.
    """
    return tuple ( cls._ACTIONS.values () )


  @classmethod
  def names ( cls ) -> Tuple [ str, ... ] :
    """
    Get all catalog action names.

    Returns:
      Tuple[str, ...]: Tuple of action names.
    """
    return tuple ( cls._ACTIONS.keys () )


  @classmethod
  def asDict ( cls ) -> Dict [ str, str ] :
    """
    Get catalog as a dictionary.

    Returns:
      Dict[str, str]: Dictionary mapping names to action strings.
    """
    return { name : action.asString () for name, action in cls._ACTIONS.items () }


  @classmethod
  def get ( cls, name : str ) -> HookAction :
    """
    Get a catalog action by name.

    Args:
      name: Action name.

    Returns:
      HookAction: The requested action.

    Raises:
      KeyError: If action is not defined in catalog.
    """
    try :
      return cls._ACTIONS [ str ( name ).strip ().upper () ]
    except KeyError as e :
      raise KeyError ( f"Hook action not defined in catalog: {name}" ) from e


  @classmethod
  def isDefined ( cls, action : HookAction | str ) -> bool :
    """
    Check if an action is defined in the catalog.

    Args:
      action: HookAction or string to check.

    Returns:
      bool: True if action is defined.
    """
    target = action if isinstance ( action, HookAction ) else HookAction.fromString ( action )
    return any ( catalogAction == target for catalogAction in cls._ACTIONS.values () )

