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
from pathlib import Path
import json
import importlib
import inspect
import os

# Application Libraries / Librerías de la Aplicación
from success.common.base.SuccessClass                 import SuccessClass
from success.common.reflection.SuccessModuleLoader    import SuccessModuleLoader
from success.common.tools.SuccessFile                 import SuccessFile
from success.core.SuccessContext                      import SuccessContext
from success.engine.infrastructure.HookAction         import HookAction
from success.engine.infrastructure.HookDeclaration    import HookDeclaration
from success.engine.infrastructure.HookMatcher        import HookMatcher
from success.engine.infrastructure.SuccessHookCatalog import SuccessHookCatalog
from success.engine.infrastructure.SuccessHook        import SuccessHook

# Preconditions / Precondiciones


class SuccessHookManager ( SuccessClass ) :
  """
  Manager for hook registration and execution.

  Handles loading hooks from hooks.json, registering them,
  and executing them at appropriate points in the application lifecycle.

  Attributes:
    __appPath (str): Application path.
    __data (dict): Hook data from hooks.json.
    __hooks (list): List of registered hooks.
  """

  __appPath : str  = None
  __data    : dict = None
  __hooks   : list = []


  def __init__ ( self, appPath : str ) -> None :
    """
    Initialize the hook manager.

    Args:
      appPath: Path to the application directory.
    """
    super ().__init__ ()
    self.__appPath = appPath
    self.__hooks   = []
    self.__data    = SuccessFile.loadAppJson ( os.path.join ( self.__appPath, "hooks.json" ) )


  def execute ( self, when : str, action : str, **kwargs ) -> None :
    """
    Execute hooks matching the given criteria.

    Args:
      when: Execution timing ('before' or 'after').
      action: Hook action string.
      **kwargs: Additional context arguments.
    """
    self._logger.log ( f"Executing hooks (when={when}, action={action})...", "INFO" )

    try :
      emittedAction = HookMatcher.parse ( action )

    except Exception as e :
      self._logger.log ( f"Invalid hook action '{action}': {e}", "ERROR" )
      return

    executed = False

    for hook in self.__hooks :
      if hook [ "when" ] == when and HookMatcher.matches ( hook [ "action" ], emittedAction ) :
        callback     = hook [ "callback" ]
        hookInstance = hook [ "hook" ]
        context      = {
          "hook"             : hookInstance,
          "declaration"      : hookInstance.declaration,
          "payload"          : hookInstance.payload,
          "when"             : when,
          "action"           : str ( emittedAction ),
          "action_hierarchy" : HookMatcher.hierarchyStrings ( emittedAction ),
          "kwargs"           : kwargs
        }

        try :
          sig = inspect.signature ( callback )
          if len ( sig.parameters ) == 0 :
            callback ()

          elif len ( sig.parameters ) == 1 :
            callback ( context )

          else :
            callback ( context, **kwargs )

          executed = True

          self._logger.log (
            f"Hook executed successfully (name={hook [ 'name' ]}, "
            f"declared_action={hook [ 'action' ]}, emitted_action={emittedAction}).",
            "INFO"
          )

        except Exception as e :
          self._logger.log ( f"Error executing hook (name={hook [ 'name' ]}): {e}", "ERROR" )

    if not executed :
      self._logger.log ( f"No matching hooks found (when={when}, action={action}).", "WARNING" )


  @staticmethod
  def null () -> "SuccessHookManager" :
    """
    Create a null hook manager (no-op implementation).

    Returns:
      SuccessHookManager: Null hook manager instance.
    """
    return _NullHookManager ()


  def register ( self ) -> None :
    """
    Register hooks from hooks.json.

    Loads hook declarations, validates them, resolves callbacks,
    and registers them for execution.
    """
    if not self.__data :
      self._logger.log ( f"No hooks registered for application {SuccessContext ().getCurrentAppName ()}.", "WARNING" )
      return

    if not isinstance ( self.__data, list ) :
      self._logger.log ( "hooks.json must contain a list of hooks.", "ERROR" )
      return

    for idx, hook in enumerate ( self.__data ) :
      defaultName = f"unnamed_hook_{idx}"
      try :
        declaration = HookDeclaration.fromDict ( hook, defaultName = defaultName )
      except Exception as e :
        self._logger.log ( f"[{defaultName}] Invalid declaration: {e}", "ERROR" )
        continue

      if not declaration.enabled :
        self._logger.log ( f"Hook omitted due to enabled=false (name={declaration.name}).", "DEBUG" )
        continue

      if not SuccessHookCatalog.isDefined ( declaration.action ) :
        self._logger.log ( f"[{declaration.name}] Action not defined in catalog: '{declaration.action}'.", "ERROR" )
        continue

      try :
        hookInstance, method = self.resolveCallback ( declaration.callback )

      except Exception as e :
        self._logger.log ( f"[{declaration.name}] Error resolving callback '{declaration.callback}': {e}", "ERROR" )
        continue

      try :
        hookInstance.bind ( declaration )
      except Exception as e :
        self._logger.log ( f"[{declaration.name}] Error binding hook declaration: {e}", "ERROR" )
        continue

      self.__hooks.append (
        {
          "name"     : declaration.name,
          "hook"     : hookInstance,
          "callback" : method,
          "when"     : declaration.when,
          "action"   : declaration.action,
          "priority" : declaration.priority
        }
      )

      self._logger.log (
        f"Hook registered successfully (name={declaration.name}, when={declaration.when}, "
        f"action={declaration.action}, priority={declaration.priority}).",
        "INFO"
      )

    self.__hooks.sort ( key = lambda item: item [ "priority" ] )


  def resolveCallback ( self, callback : str ) -> tuple [ SuccessHook, callable ] :
    """
    Resolve a callback from a string path.

    Args:
      callback: Callback path (module.Class.method).

    Returns:
      tuple[SuccessHook, callable]: Hook instance and method.

    Raises:
      RuntimeError: If callback resolution fails.
    """
    try :
      parts = callback.split ( "." )
      if len ( parts ) < 3 :
        raise ValueError ( f"Callback '{callback}' must have full format: module.Class.method" )

      *moduleParts, className, methodName = parts

      # New implementation with SuccessModuleLoader
      module_path = ".".join ( moduleParts + [ className ] )
      _class      = SuccessModuleLoader.loadClassFromString ( module_path )

      if not issubclass ( _class, SuccessHook ) :
        raise TypeError ( f"Class '{className}' does not inherit from SuccessHook." )

      hookInstance = _class ()
      method       = getattr ( hookInstance, methodName )

      if not callable ( method ) :
        raise TypeError ( f"Method '{methodName}' is not callable." )

      return hookInstance, method

    except Exception as e :
      raise RuntimeError ( f"Error resolving callback '{callback}': {e}" )



class _NullHookManager ( SuccessHookManager ) :
  """
  Null object implementation of SuccessHookManager.

  Provides no-op implementations for all methods.
  """

  def __init__ ( self ) -> None :
    """
    Initialize the null hook manager.
    """
    self._SuccessHookManager__appPath = ""
    self._SuccessHookManager__hooks = []
    self._SuccessHookManager__data = []

  def execute ( self, *args, **kwargs ) -> None :
    """
    No-op execute method.
    """
    pass
