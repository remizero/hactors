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
from flask                  import Flask
from werkzeug.routing.rules import Rule
import time
from typing import Any, Dict, List, Optional, Tuple

# Success Libraries / Librerías Success
from success.common.infra.config.SuccessSystemEnv import SuccessSystemEnv
from success.common.tools.SuccessColor            import SuccessColor
from success.common.tools.Manifest                import random_creed_line
from success.common.tools.MoodEngine              import MoodEngine
from success.core.SuccessContext                  import SuccessContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessSystemState () :
  """
  Manages and reports the system state for the Success framework.

  Tracks application startup timing, environment configuration, loaded applications,
  and generates detailed system reports including routing, extensions, policies,
  and health information.

  Attributes:
    _start_time: The system start time for timing calculations.
    _env (str): The current environment name.
    _logger_file (bool): Whether file logging is enabled.
    _apps_cargadas (list): List of loaded Flask applications.
    _apps_omitidas (dict): Dictionary of omitted applications with reasons.
  """

  _start_time    = None
  _env           = "unknown"
  _logger_file   = False
  _apps_cargadas = []
  _apps_omitidas = {}


  @staticmethod
  def startTimer () -> None :
    """
    Starts the system startup timer.

    Records the current time for calculating bootstrap duration.
    """
    SuccessSystemState._start_time = time.perf_counter ()


  @staticmethod
  def stopTimer () -> int :
    """
    Stops the system startup timer and returns elapsed time.

    Returns:
      int: Elapsed time in milliseconds since startTimer was called, or 0 if not started.
    """
    if SuccessSystemState._start_time is None :
      return 0
    return int ( ( time.perf_counter () - SuccessSystemState._start_time ) * 1000 )


  @staticmethod
  def setEnv ( env : str ) -> None :
    """
    Sets the current environment name.

    Args:
      env (str): The environment name (e.g., 'development', 'production').
    """
    SuccessSystemState._env = env


  @staticmethod
  def setLoggerFile ( enabled : bool ) -> None :
    """
    Sets whether file logging is enabled.

    Args:
      enabled (bool): True to enable file logging, False otherwise.
    """
    SuccessSystemState._logger_file = enabled


  @staticmethod
  def addAppCargada ( app : Flask ) -> None :
    """
    Adds a loaded Flask application to the tracking list.

    Prevents duplicate entries by checking import_name.

    Args:
      app (Flask): The Flask application to add.
    """
    if app is None :
      return

    appName = getattr ( app, "import_name", None )
    if appName and any ( getattr ( currentApp, "import_name", None ) == appName for currentApp in SuccessSystemState._apps_cargadas ) :
      return

    SuccessSystemState._apps_cargadas.append ( app )


  @staticmethod
  def addAppOmitida ( path : str, reason : str = "Desconocido" ) -> None :
    """
    Records an application that was omitted during loading.

    Args:
      path (str): The path of the omitted application.
      reason (str): The reason for omission.
    """
    SuccessSystemState._apps_omitidas [ path ] = reason


  @staticmethod
  def getAppStats () -> Tuple [ int, int, int ] :
    """
    Retrieves application statistics.

    Returns:
      Tuple[int, int, int]: A tuple containing (total_apps, active_apps, omitted_apps).
    """
    total    = len ( SuccessSystemState._apps_cargadas ) + len ( SuccessSystemState._apps_omitidas )
    activas  = len ( SuccessSystemState._apps_cargadas )
    omitidas = len ( SuccessSystemState._apps_omitidas )

    return total, activas, omitidas


  @staticmethod
  def report ( logger : Any = None ) -> None :
    """
    Generates and outputs a comprehensive system state report.

    Includes build information, routing details, extensions, policies, and health status.
    Optionally uses humor/mood engine if enabled.

    Args:
      logger (Any): Optional logger instance for output. If None, prints to console.
    """
    ms          = SuccessSystemState.stopTimer ()
    logger_type = "Sí (archivo/log externo)" if SuccessSystemState._logger_file else "No (solo consola)"
    apps        = SuccessSystemState._resolveActiveApps ()
    total       = len ( apps ) + len ( SuccessSystemState._apps_omitidas )
    activas     = len ( apps )
    omitidas    = len ( SuccessSystemState._apps_omitidas )
    session_id  = SuccessContext ().getSuccessValue ( "SESSION_ID" )
    appType     = str ( SuccessSystemEnv.get ( "SUCCESS_APP_TYPE", "singleApp" ) )
    appMode     = str (
      SuccessSystemEnv.get (
        "SUCCESS_APP_MODE",
        SuccessSystemEnv.get ( "SUCCESS_APP_DOMAIN", "flask" if appType.lower () == "singleapp" else "standard" )
      )
    )
    contextInfo = SuccessContext ().getContext ().get ( "success", {} ) if isinstance ( SuccessContext ().getContext (), dict ) else {}
    contextApps = contextInfo.get ( "apps", {} ) if isinstance ( contextInfo.get ( "apps", {} ), dict ) else {}
    lines       = [ f"\n🔥 Success System Summary ({SuccessSystemState._env.upper ()}):" ]

    lines.extend ( SuccessSystemState._buildSectionBuild ( ms, logger_type, session_id, appType, appMode, len ( contextApps ), total, activas, omitidas ) )
    lines.extend ( SuccessSystemState._buildSectionApps ( apps ) )

    if SuccessSystemEnv.isTrue ( "SUCCESS_HUMOR_ENABLED" ) :
      lines.append ( f"{SuccessColor.level ( '└──' )} {SuccessColor.tag ( 'Mood' )}:              {MoodEngine.get_today_mood ()}" )

    summary = "\n".join ( lines ) + "\n" + f"{SuccessColor.level ( '─' )}" * 150 + "\n🔧 Generated by Success Engine ⛓️"

    if logger :
      logger.log ( summary, "INFO" )
      for path, reason in SuccessSystemState._apps_omitidas.items () :
        logger.log ( f"[SKIP] {path} → {reason}", "INFO" )

    else :
      print ( summary )
      for path, reason in SuccessSystemState._apps_omitidas.items () :
        print ( f"[SKIP] {path} → {reason}" )


  @staticmethod
  def _resolveActiveApps () -> list :
    """
    Resolves the list of active applications from multiple sources.

    Combines apps from _apps_cargadas list and context data.

    Returns:
      list: List of active Flask application instances.
    """
    apps        = list ( SuccessSystemState._apps_cargadas )
    contextData = SuccessContext ().getContext ()
    successNode = contextData.get ( "success", {} ) if isinstance ( contextData, dict ) else {}
    appMap      = successNode.get ( "apps", {} ) if isinstance ( successNode.get ( "apps", {} ), dict ) else {}

    for appEntry in appMap.values () :
      if not isinstance ( appEntry, dict ) :
        continue

      instance = appEntry.get ( "instance" )

      if instance is None :
        continue

      if not any ( current is instance for current in apps ) :
        apps.append ( instance )

    return apps


  @staticmethod
  def _buildSectionBuild ( ms : int, logger_type : str, session_id, app_type : str, app_mode : str, context_apps : int, total : int, activas : int, omitidas : int ) -> list :
    """
    Builds the build information section of the report.

    Args:
      ms (int): Bootstrap time in milliseconds.
      logger_type (str): Logger type description.
      session_id: The session ID.
      app_type (str): Application type.
      app_mode (str): Application mode.
      context_apps (int): Number of context apps.
      total (int): Total number of applications.
      activas (int): Number of active applications.
      omitidas (int): Number of omitted applications.

    Returns:
      list: List of formatted lines for the build section.
    """
    fields = [
      ( "Entorno", SuccessSystemState._env ),
      ( "App Type", app_type ),
      ( "App Mode", app_mode ),
      ( "Tiempo de arranque", f"{ms}ms" ),
      ( "SuccessLogger", logger_type ),
      ( "SuccessSession ID", session_id ),
      ( "Manifest", random_creed_line () ),
      ( "Context Apps", context_apps ),
      ( "Total apps detectadas", total ),
      ( "Total apps omitidas", f"{omitidas} / {total}" ),
      ( "Total apps activas", f"{activas} / {total}" )
    ]
    maxLabel = max ( len ( label ) for label, _ in fields )
    lines    = [ f"{SuccessColor.level ( '├──' )} {SuccessColor.tag ( 'Build' )}:" ]

    for index, ( label, value ) in enumerate ( fields ) :
      prefix      = '│   └──' if index == len ( fields ) - 1 else '│   ├──'
      paddedLabel = f"{label + ':':<{maxLabel + 1}}"
      lines.append ( f"{SuccessColor.level ( prefix )} {SuccessColor.tag ( paddedLabel )} {value}" )

    return lines


  @staticmethod
  def _buildSectionRouting ( apps : list ) -> list :
    """
    Builds the routing section of the report showing URL rules for each app.

    Args:
      apps (list): List of Flask applications.

    Returns:
      list: List of formatted lines for the routing section.
    """
    lines = [ f"{SuccessColor.level ( '├──' )} {SuccessColor.tag ( 'Routing' )}:" ]

    if not apps :
      lines.append ( f"{SuccessColor.level ( '│   └──' )} {SuccessColor.tag ( 'Apps' )}: 0" )
      return lines

    for appIndex, app in enumerate ( apps ) :
      appName   = getattr ( app, "import_name", "unknown_app" )
      rules     = list ( app.url_map.iter_rules () )
      appPrefix = '│   └──' if appIndex == len ( apps ) - 1 else '│   ├──'

      lines.append ( f"{SuccessColor.level ( appPrefix )} {SuccessColor.tag ( 'App' )}: {appName} ({len ( rules )} rutas)" )

      max_method = max ( ( len ( list ( rule.methods - { 'HEAD', 'OPTIONS' } ) [ 0 ] ) for rule in rules if len ( list ( rule.methods - { 'HEAD', 'OPTIONS' } ) ) > 0 ), default = 0 )
      max_rule   = max ( ( len ( rule.rule ) for rule in rules ), default = 0 )
      max_host   = max ( ( len ( rule.host or "" ) for rule in rules ), default = 0 )
      max_subdom = max ( ( len ( SuccessSystemState._displaySubdomain ( rule ) ) for rule in rules ), default = 0 )
      max_ep     = max ( ( len ( rule.endpoint or "" ) for rule in rules ), default = 0 )

      for ruleIndex, rule in enumerate ( rules ) :
        methods          = list ( rule.methods - { 'HEAD', 'OPTIONS' } )
        method           = methods [ 0 ] if methods else "ANY"
        routePrefix      = '│       └──' if ruleIndex == len ( rules ) - 1 else '│       ├──'
        displaySubdomain = SuccessSystemState._displaySubdomain ( rule )
        lines.append (
          f"{SuccessColor.level ( routePrefix )} "
          f"{method:<{max_method}}  "
          f"{rule.rule:<{max_rule}} "
          f"{SuccessColor.tag ( 'host' )}={rule.host or '':<{max_host}}   "
          f"{SuccessColor.tag ( 'subdomain' )}={displaySubdomain:<{max_subdom}}   "
          f"{SuccessColor.tag ( 'Action' )}={rule.endpoint or '':<{max_ep}}"
        )

    return lines


  @staticmethod
  def _buildSectionExtensions ( apps : list ) -> list :
    """
    Builds the extensions section of the report showing blueprints and extensions for each app.

    Args:
      apps (list): List of Flask applications.

    Returns:
      list: List of formatted lines for the extensions section.
    """
    lines = [ f"{SuccessColor.level ( '├──' )} {SuccessColor.tag ( 'Extensions' )}:" ]

    if not apps :
      lines.append ( f"{SuccessColor.level ( '│   └──' )} {SuccessColor.tag ( 'Apps' )}: 0" )
      return lines

    for appIndex, app in enumerate ( apps ) :
      appName    = getattr ( app, "import_name", "unknown_app" )
      blueprints = list ( app.blueprints.keys () )
      extNames   = sorted ( list ( app.extensions.keys () ) )
      prefix     = '│   └──' if appIndex == len ( apps ) - 1 else '│   ├──'

      lines.append ( f"{SuccessColor.level ( prefix )} {SuccessColor.tag ( 'App' )}: {appName}" )
      lines.append ( f"{SuccessColor.level ( '│       ├──' )} {SuccessColor.tag ( 'Blueprints' )}:  {', '.join ( blueprints ) or '—'}" )
      lines.append ( f"{SuccessColor.level ( '│       └──' )} {SuccessColor.tag ( 'Extensiones' )}: {', '.join ( extNames ) or '—'}" )

    return lines


  @staticmethod
  def _buildSectionPolicies ( apps : list ) -> list :
    """
    Builds the policies section of the report showing hooks for each app.

    Args:
      apps (list): List of Flask applications.

    Returns:
      list: List of formatted lines for the policies section.
    """
    lines = [ f"{SuccessColor.level ( '├──' )} {SuccessColor.tag ( 'Policies' )}:" ]

    if not apps :
      lines.append ( f"{SuccessColor.level ( '│   └──' )} {SuccessColor.tag ( 'Apps' )}: 0" )
      return lines

    for appIndex, app in enumerate ( apps ) :
      appName  = getattr ( app, "import_name", "unknown_app" )
      hooks    = getattr ( app, "success_hooks", {} )
      hookKeys = list ( hooks.keys () ) if isinstance ( hooks, dict ) else []
      prefix   = '│   └──' if appIndex == len ( apps ) - 1 else '│   ├──'

      lines.append ( f"{SuccessColor.level ( prefix )} {SuccessColor.tag ( 'App' )}: {appName}" )
      lines.append ( f"{SuccessColor.level ( '│       └──' )} {SuccessColor.tag ( 'Hooks' )}: {len ( hookKeys )} ({', '.join ( hookKeys ) or '—'})" )

    return lines


  @staticmethod
  def _buildSectionHealth ( apps : list, total : int, activas : int, omitidas : int ) -> list :
    """
    Builds the health section of the report with status and warnings.

    Args:
      apps (list): List of Flask applications.
      total (int): Total number of applications.
      activas (int): Number of active applications.
      omitidas (int): Number of omitted applications.

    Returns:
      list: List of formatted lines for the health section.
    """
    warnings = []

    if activas == 0 :
      warnings.append ( "No hay aplicaciones activas." )

    for app in apps :
      appName = getattr ( app, "import_name", "unknown_app" )
      rules   = list ( app.url_map.iter_rules () )
      if len ( rules ) == 0 :
        warnings.append ( f"App sin rutas: {appName}" )

    status = "OK" if len ( warnings ) == 0 else "WARN"
    lines  = [
      f"{SuccessColor.level ( '└──' )} {SuccessColor.tag ( 'Health' )}:",
      f"{SuccessColor.level ( '    ├──' )} {SuccessColor.tag ( 'Status' )}: {status}",
      f"{SuccessColor.level ( '    ├──' )} {SuccessColor.tag ( 'Apps Totales' )}: {total}",
      f"{SuccessColor.level ( '    ├──' )} {SuccessColor.tag ( 'Apps Activas' )}: {activas}",
      f"{SuccessColor.level ( '    └──' )} {SuccessColor.tag ( 'Warnings' )}: {len ( warnings )}"
    ]

    for warning in warnings :
      lines.append ( f"{SuccessColor.level ( '        └──' )} {warning}" )

    return lines


  @staticmethod
  def _buildSectionApps ( apps : list ) -> list :
    """
    Builds the detailed applications section of the report.

    Includes routing, blueprints, extensions, policies, hooks, and health for each app.

    Args:
      apps (list): List of Flask applications.

    Returns:
      list: List of formatted lines for the applications section.
    """
    lines = [ f"{SuccessColor.level ( '└──' )} {SuccessColor.tag ( 'Aplicaciones' )}:" ]

    if not apps :
      lines.append ( f"{SuccessColor.level ( '    └──' )} {SuccessColor.tag ( 'Apps' )}: 0" )
      return lines

    for appIndex, app in enumerate ( apps ) :
      appName       = getattr ( app, "import_name", "unknown_app" )
      rules         = list ( app.url_map.iter_rules () )
      blueprints    = list ( app.blueprints.keys () )
      extNames      = sorted ( list ( app.extensions.keys () ) )
      hooks         = getattr ( app, "success_hooks", {} )
      hookKeys      = list ( hooks.keys () ) if isinstance ( hooks, dict ) else []
      warnings      = SuccessSystemState._buildAppWarnings ( app )
      appPrefix     = '    └──' if appIndex == len ( apps ) - 1 else '    ├──'
      childBase     = '        ' if appIndex == len ( apps ) - 1 else '    │   '
      childListBase = f"{childBase}│   "
      warningBase   = f"{childBase}    "

      lines.append ( f"{SuccessColor.level ( appPrefix )} {SuccessColor.tag ( 'App' )}: {appName}" )
      lines.append ( f"{SuccessColor.level ( f'{childBase}├──' )} {SuccessColor.tag ( 'Routing' )}: ({len ( rules )} rutas)" )

      max_method = max ( ( len ( list ( rule.methods - { 'HEAD', 'OPTIONS' } ) [ 0 ] ) for rule in rules if len ( list ( rule.methods - { 'HEAD', 'OPTIONS' } ) ) > 0 ), default = 0 )
      max_rule   = max ( ( len ( rule.rule ) for rule in rules ), default = 0 )
      max_host   = max ( ( len ( rule.host or "" ) for rule in rules ), default = 0 )
      max_subdom = max ( ( len ( SuccessSystemState._displaySubdomain ( rule ) ) for rule in rules ), default = 0 )
      max_ep     = max ( ( len ( rule.endpoint or "" ) for rule in rules ), default = 0 )

      if len ( rules ) == 0 :
        lines.append ( f"{SuccessColor.level ( f'{childListBase}└──' )} —" )

      else :
        for ruleIndex, rule in enumerate ( rules ) :
          methods          = list ( rule.methods - { 'HEAD', 'OPTIONS' } )
          method           = methods [ 0 ] if methods else "ANY"
          routePrefix      = f"{childListBase}└──" if ruleIndex == len ( rules ) - 1 else f"{childListBase}├──"
          displaySubdomain = SuccessSystemState._displaySubdomain ( rule )

          lines.append (
            f"{SuccessColor.level ( routePrefix )} "
            f"{method:<{max_method}}  "
            f"{rule.rule:<{max_rule}} "
            f"{SuccessColor.tag ( 'host' )}={rule.host or '':<{max_host}}   "
            f"{SuccessColor.tag ( 'subdomain' )}={displaySubdomain:<{max_subdom}}   "
            f"{SuccessColor.tag ( 'Action' )}={rule.endpoint or '':<{max_ep}}"
          )

      lines.append ( f"{SuccessColor.level ( f'{childBase}├──' )} {SuccessColor.tag ( 'Blueprints' )}: ({len ( blueprints )})" )

      if len ( blueprints ) == 0 :
        lines.append ( f"{SuccessColor.level ( f'{childListBase}└──' )} —" )

      else :
        for bpIndex, blueprint in enumerate ( blueprints ) :
          bpPrefix = f"{childListBase}└──" if bpIndex == len ( blueprints ) - 1 else f"{childListBase}├──"
          lines.append ( f"{SuccessColor.level ( bpPrefix )} {blueprint}" )

      lines.append ( f"{SuccessColor.level ( f'{childBase}├──' )} {SuccessColor.tag ( 'Extensions' )}: ({len ( extNames )})" )

      if len ( extNames ) == 0 :
        lines.append ( f"{SuccessColor.level ( f'{childListBase}└──' )} —" )

      else :
        for extIndex, extension in enumerate ( extNames ) :
          extPrefix = f"{childListBase}└──" if extIndex == len ( extNames ) - 1 else f"{childListBase}├──"
          lines.append ( f"{SuccessColor.level ( extPrefix )} {extension}" )

      lines.append ( f"{SuccessColor.level ( f'{childBase}├──' )} {SuccessColor.tag ( 'Policies' )}: ({len ( hookKeys )})" )
      lines.append ( f"{SuccessColor.level ( f'{childListBase}└──' )} {'—' if len ( hookKeys ) == 0 else 'active'}" )
      lines.append ( f"{SuccessColor.level ( f'{childBase}├──' )} {SuccessColor.tag ( 'Hooks' )}: ({len ( hookKeys )})" )

      if len ( hookKeys ) == 0 :
        lines.append ( f"{SuccessColor.level ( f'{childListBase}└──' )} —" )

      else :
        for hookIndex, hookKey in enumerate ( hookKeys ) :
          hookPrefix = f"{childListBase}└──" if hookIndex == len ( hookKeys ) - 1 else f"{childListBase}├──"
          lines.append ( f"{SuccessColor.level ( hookPrefix )} {hookKey}" )

      lines.append ( f"{SuccessColor.level ( f'{childBase}└──' )} {SuccessColor.tag ( 'Health' )}: ({len ( warnings )}) {'OK' if len ( warnings ) == 0 else 'WARN'}" )

      if len ( warnings ) == 0 :
        lines.append ( f"{SuccessColor.level ( f'{warningBase}└──' )} Sin warnings" )

      else :
        for warningIndex, warning in enumerate ( warnings ) :
          warningPrefix = f"{warningBase}└──" if warningIndex == len ( warnings ) - 1 else f"{warningBase}├──"
          lines.append ( f"{SuccessColor.level ( warningPrefix )} {warning}" )

    return lines


  @staticmethod
  def _buildAppWarnings ( app : Flask ) -> list :
    """
    Generates warnings for a specific application.

    Args:
      app (Flask): The Flask application to check.

    Returns:
      list: List of warning messages for the application.
    """
    warnings = []
    appName  = getattr ( app, "import_name", "unknown_app" )
    rules    = list ( app.url_map.iter_rules () )
    if len ( rules ) == 0 :
      warnings.append ( f"App sin rutas: {appName}" )
    return warnings


  @staticmethod
  def _displaySubdomain ( rule : Rule ) -> str :
    """
    Determines the display subdomain for a URL rule.

    Args:
      rule (Rule): The URL rule to analyze.

    Returns:
      str: The subdomain string to display, or empty string if not applicable.
    """
    if rule.subdomain :
      return str ( rule.subdomain )

    appMode = str ( SuccessSystemEnv.get ( "SUCCESS_APP_MODE", "standard" ) ).strip ().lower ()
    if appMode != "subdomain" :
      return ""

    host = str ( rule.host or "" ).split ( ":" ) [ 0 ].strip ().lower ()
    if not host :
      return ""

    domain = str ( SuccessSystemEnv.get ( "SERVER_NAME", "" ) ).strip ().lower ()
    if domain and host.endswith ( f".{domain}" ) :
      return host [ : -( len ( domain ) + 1 ) ]

    return ""
