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
from flask       import Flask
from flask       import g
from threading   import Lock
from contextvars import ContextVar
import re

# Application Libraries / Librerías de la Aplicación
# from success.common.base.SuccessExtension      import SuccessExtension
from success.common.infra.logger.SuccessLogger import SuccessLogger

# Preconditions / Precondiciones
CURRENT_APP = ContextVar ( "CURRENT_APP" )


class SuccessContext () :
  """
  Singleton class that manages the application context for the Success framework.

  Provides a centralized context for managing Flask applications, extensions,
  loggers, and state within the Success ecosystem. Uses thread-safe singleton
  pattern with double-checked locking.

  Attributes:
    __apps (dict): Dictionary storing application entries with their instances, modules, loggers, extensions, and state.
    __framework (dict): Dictionary storing framework-level configuration and values.
    _instance: The singleton instance of the class.
    _lock (Lock): Thread lock for singleton creation.
  """

  __apps      : dict = {}
  __framework : dict = {}
  _instance          = None
  _lock       : Lock = Lock ()


  def __new__ ( cls ) -> 'SuccessContext' :
    """
    Creates or returns the singleton instance of SuccessContext.

    Uses double-checked locking pattern to ensure thread-safe singleton creation.
    Initializes the apps and framework dictionaries for new instances.

    Returns:
      SuccessContext: The singleton instance of the class.
    """
    if not cls._instance :
      with cls._lock :
        if not cls._instance :
          cls._instance = super ().__new__ ( cls )
          cls._instance.__apps      = {}
          cls._instance.__framework = {}

    return cls._instance


  def _normalizeAppName ( self, appName : str | None ) -> str | None :
    """
    Normalizes an application name to lowercase.

    Args:
      appName (str | None): The application name to normalize.

    Returns:
      str | None: The normalized application name in lowercase, or None if input is falsy.
    """
    if not appName :
      return None
    return appName.lower ()


  def _getOrCreateAppEntry ( self, appName : str | None, create : bool = False ) -> dict | None :
    """
    Retrieves or creates an application entry in the context.

    Args:
      appName (str | None): The name of the application.
      create (bool): Whether to create a new entry if one doesn't exist.

    Returns:
      dict | None: The application entry dictionary or None if appName is None.
    """
    key = self._normalizeAppName ( appName )
    if not key :
      return None

    if create and key not in self.__apps :
      self.__apps [ key ] = {
        "instance"   : None,
        "module"     : None,
        "logger"     : None,
        "extensions" : {},
        "state"      : {}
      }

    return self.__apps.get ( key )


  def setApp ( self, appInstance : Flask ) -> None :
    """
    Sets a Flask application instance in the context.

    Args:
      appInstance (Flask): The Flask application instance to store.
    """
    appName  = self.getCurrentAppName () or getattr ( appInstance, "name", None )
    appEntry = self._getOrCreateAppEntry ( appName, create = True )
    if appEntry is not None :
      appEntry [ "instance" ] = appInstance


  def getApp ( self ) -> Flask :
    """
    Retrieves the current Flask application instance from the context.

    Returns:
      Flask: The Flask application instance, or None if not found.
    """
    appEntry = self._getOrCreateAppEntry ( self.getCurrentAppName (), create = False )
    if appEntry is not None :
      return appEntry.get ( "instance" )
    return None


  def setAppModule ( self, module ) -> None :
    """
    Sets the module associated with the current application.

    Args:
      module: The module to associate with the current application.
    """
    appEntry = self._getOrCreateAppEntry ( self.getCurrentAppName (), create = True )
    if appEntry is not None :
      appEntry [ "module" ] = module


  def getAppModule ( self ) :
    """
    Retrieves the module associated with the current application.

    Returns:
      The module associated with the current application, or None if not found.
    """
    appEntry = self._getOrCreateAppEntry ( self.getCurrentAppName (), create = False )
    if appEntry is not None :
      return appEntry.get ( "module" )
    return None


  def getContext ( self ) -> dict :
    """
    Retrieves the complete context dictionary.

    Returns:
      dict: A dictionary containing framework settings and all application entries.
    """
    return {
      "success" : {
        **self.__framework,
        "apps" : self.__apps
      }
    }


  def setContext ( self, context : dict ) -> None :
    """
    Sets context data from a dictionary.

    Merges framework-level settings and application data from the provided context.

    Args:
      context (dict): The context dictionary containing 'success' key with framework and apps data.
    """
    if not context or not isinstance ( context, dict ) :
      return

    successContext = context.get ( "success", {} ) if isinstance ( context.get ( "success", {} ), dict ) else {}
    for key, value in successContext.items () :
      if key == "apps" and isinstance ( value, dict ) :
        for appName, appData in value.items () :
          appEntry = self._getOrCreateAppEntry ( appName, create = True )
          if isinstance ( appData, dict ) and appEntry is not None :
            appEntry.update ( appData )

      else :
        self.__framework [ key ] = value


  def getAppLogger ( self ) -> SuccessLogger | None :
    """
    Retrieves the logger for the current application.

    Returns:
      SuccessLogger | None: The SuccessLogger instance for the current app, or None if not found.
    """
    appEntry = self._getOrCreateAppEntry ( self.getCurrentAppName (), create = False )
    if appEntry is not None :
      return appEntry.get ( "logger" )

    return None


  def setAppLogger ( self, logger : SuccessLogger ) -> None :
    """
    Sets the logger for the current application.

    Args:
      logger (SuccessLogger): The SuccessLogger instance to associate with the current app.
    """
    appEntry = self._getOrCreateAppEntry ( self.getCurrentAppName (), create = True )
    if appEntry is not None :
      appEntry [ "logger" ] = logger


  def setState ( self, name : str, state ) :
    """
    Sets a state value for the current application.

    Args:
      name (str): The name of the state.
      state: The state value to store.
    """
    appEntry = self._getOrCreateAppEntry ( self.getCurrentAppName (), create = True )
    if appEntry is not None :
      appEntry [ "state" ] [ name.lower () ] = state


  def getState ( self, name : str ) :
    """
    Retrieves a state value for the current application.

    Args:
      name (str): The name of the state to retrieve.

    Returns:
      The state value, or None if not found.
    """
    appEntry = self._getOrCreateAppEntry ( self.getCurrentAppName (), create = False )
    if appEntry is not None :
      return appEntry [ "state" ].get ( name.lower () )
    return None


  @staticmethod
  def _ensure_scope ( scope ) :
    """
    Ensures a scope dictionary exists in the Flask g object.

    Args:
      scope: The scope name to ensure exists.

    Returns:
      dict: The scope dictionary.
    """
    if not hasattr ( g, '_success_context' ) :
      g._success_context = {}

    if scope not in g._success_context :
        g._success_context [ scope ] = {}

    return g._success_context [ scope ]


  @staticmethod
  def set ( scope, key, value, persist = False ) :
    """
    Sets a value in the specified scope.

    Args:
      scope: The scope to store the value in.
      key: The key for the value.
      value: The value to store.
      persist (bool): If True, persists the value using the session extension.
    """
    if persist :
      sessionExtension = SuccessContext ().getExtension ( "SuccessSessionExtension" )
      if sessionExtension and hasattr ( sessionExtension, "set" ) :
        sessionExtension.set ( f"{scope}:{key}", value )

    else :
      scope_data         = SuccessContext ()._ensure_scope ( scope )
      scope_data [ key ] = value


  @staticmethod
  def get ( scope, key, default = None, persist = False ) :
    """
    Retrieves a value from the specified scope.

    Args:
      scope: The scope to retrieve the value from.
      key: The key of the value to retrieve.
      default: The default value to return if key is not found.
      persist (bool): If True, retrieves from the session extension.

    Returns:
      The stored value, or the default if not found.
    """
    if persist :
      sessionExtension = SuccessContext ().getExtension ( "SuccessSessionExtension" )
      if sessionExtension and hasattr ( sessionExtension, "get" ) :
        return sessionExtension.get ( f"{scope}:{key}", default )
      return default

    else :
      scope_data = SuccessContext ()._ensure_scope ( scope )
      return scope_data.get ( key, default )


  @staticmethod
  def clear ( scope = None, persist = False ) :
    """
    Clears values from the specified scope or all scopes.

    Args:
      scope: The scope to clear. If None, clears all scopes.
      persist (bool): If True, clears using the session extension.
    """
    if persist :
      sessionExtension = SuccessContext ().getExtension ( "SuccessSessionExtension" )
      if sessionExtension and hasattr ( sessionExtension, "clear" ) :
        sessionExtension.clear ( scope )  # define en SuccessSessionExtension cómo limpiar por prefijo

    else :
      if hasattr ( g, '_success_context' ) :
        if scope :
          g._success_context.pop ( scope, None )

        else :
          g._success_context = {}


  def getCurrentAppName ( self ) :
    """
    Retrieves the current application name.

    Returns:
      The current application name from the context variable or framework settings.
    """
    return (
      CURRENT_APP.get ( None )
      or self.__framework.get ( "current_app" )
    )


  def setSuccessValue ( self, key : str, value ) -> None :
    """
    Sets a framework-level value in the context.

    Args:
      key (str): The key for the value.
      value: The value to store.
    """
    self.__framework [ key ] = value


  def getSuccessValue ( self, key : str ) :
    """
    Retrieves a framework-level value from the context.

    Args:
      key (str): The key of the value to retrieve.

    Returns:
      The stored value, or None if not found.
    """
    return self.__framework.get ( key )
