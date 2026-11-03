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
from flask  import Flask
from typing import Type

# Success Libraries / Librerías Success
from success.common.base.SuccessClass                 import SuccessClass
from success.common.base.SuccessExtension             import SuccessExtension
from success.common.infra.config.SuccessConfig        import SuccessConfig
from success.engine.infrastructure.SuccessHookCatalog import SuccessHookCatalog
from success.engine.infrastructure.SuccessHookManager import SuccessHookManager
from success.core.SuccessBuildContext                 import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessExtensionBuilder ( SuccessClass ) :
  """
  Extension builder for the Success framework.

  Builds and configures SuccessExtension instances,
  validating they are enabled and executing registration hooks.

  Purpose:
  ----------
  SuccessExtensionBuilder is responsible for:
  - Verifying if an extension is enabled in the environment
  - Validating that the class inherits from SuccessExtension
  - Creating extension instance
  - Executing before/after 'extension_register' hooks
  - Configuring and registering the extension in the app

  Usage:
  ------
  ctx = SuccessBuildContext.from_app('myapp', '/apps/myapp')
  builder = SuccessExtensionBuilder(ctx)

  # Check if enabled
  if builder.isEnabled('SUCCESS_EXTENSION_CORS'):
      ext = builder.build('SUCCESS_EXTENSION_CORS', SuccessCorsExtension)

  Attributes:
      __buildContext (SuccessBuildContext): Build context.

  Note:
    - Uses wrapper strategy: each concrete extension resolves its config
    - Executes hooks during registration
  """

  __buildContext : SuccessBuildContext = None


  def __init__ ( self, buildContext : SuccessBuildContext ) -> None :
    """
    Initialize the extension builder.

    Args:
        buildContext: Build context with application configuration.
    """
    super ().__init__ ()
    self.__buildContext = buildContext


  def isEnabled ( self, envVar : str ) -> bool :
    """
    Check if an extension is enabled in the configuration.

    Args:
        envVar: Environment variable name (e.g., 'SUCCESS_EXTENSION_CORS').

    Returns:
        bool: True if the extension is enabled, False otherwise.

    Note:
        Returns False if _appEnv is not available in the context.
    """
    if not self.__buildContext._appEnv :
      return False

    return self.__buildContext._appEnv.isTrue ( envVar )


  def build ( self, envVar : str, extensionClass : Type [ SuccessExtension ] ) -> SuccessExtension | None :
    """
    Build and register an extension if enabled.

    Validates that the class inherits from SuccessExtension, creates an instance,
    executes hooks, configures and registers the extension in the application.

    Args:
        envVar: Environment variable that controls the extension.
        extensionClass: Extension class to build.

    Returns:
        SuccessExtension | None: Extension instance if built,
            None if not enabled.

    Raises:
        TypeError: If extensionClass does not inherit from SuccessExtension.

    Note:
        - Executes 'before/after extension_register' hooks
        - Uses wrapper strategy: the extension resolves its own config
    """
    if not self.isEnabled ( envVar ) :
      return None

    if not issubclass ( extensionClass, SuccessExtension ) :
      raise TypeError ( f"La clase {extensionClass.__name__} debe heredar de SuccessExtension." )

    instance = extensionClass ( self.__buildContext.getApp () )

    if self.__buildContext._hooks :
      self.__buildContext._hooks.execute (
        when = "before",
        action = SuccessHookCatalog.BUILD_EXTENSION_CORE_REGISTER,
        payload = { "extension" : instance }
      )

    # Wrapper strategy: cada extensión concreta resuelve su config especializada.
    instance.config ()
    instance.register ()

    if self.__buildContext._hooks :
      self.__buildContext._hooks.execute (
        when = "after",
        action = SuccessHookCatalog.BUILD_EXTENSION_CORE_REGISTER,
        payload = { "extension" : instance }
      )

    return instance
