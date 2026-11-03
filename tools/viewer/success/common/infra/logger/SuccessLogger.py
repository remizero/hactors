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
from flask   import Flask
from logging import CRITICAL
from logging import currentframe
from logging import DEBUG
from logging import ERROR
from logging import FATAL
from logging import getLogger
from logging import INFO
from logging import Logger
from logging import raiseExceptions
from logging import WARNING
from logging import LogRecord
from types   import TracebackType
import os
import sys
import traceback

# Success Libraries / Librerías Success
from success.core.SuccessAppMode                                import SuccessAppMode
from success.engine.context.RequestContext                      import RequestContext
from success.common.infra.config.SuccessSystemEnv               import SuccessSystemEnv
from success.common.infra.logger.handlers.SuccessConsoleHandler import SuccessConsoleHandler
from success.common.infra.logger.handlers.SuccessEmailHandler   import SuccessEmailHandler
from success.common.infra.logger.handlers.SuccessFileHandler    import SuccessFileHandler

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
# TODO PARA COLOREAR EL OUTPUT POR CONSOLA
# https://stackoverflow.com/questions/32906686/friendly-query-logging-in-sqlalchemy

# https://docs.python.org/es/3/howto/logging-cookbook.html
# https://docs.python.org/es/3/howto/logging.html
# https://docs.python.org/es/3.9/library/logging.handlers.html
# https://docs.python.org/es/3/library/logging.config.html
# https://stackify.dev/231524-custom-logger-class-and-correct-line-number-function-name-in-log
# https://www.machinelearningplus.com/python/python-logging-guide/
# https://dock2learn.com/tech/create-a-reusable-logger-factory-for-python-projects/
# https://www.peterspython.com/es/blog/cree-sus-propias-clases-de-excepcion-python-personalizadas-y-adaptadas-a-su-aplicacion
# https://desktop.arcgis.com/es/arcmap/10.3/analyze/python/error-handling-with-python.htm
# https://www.ionos.es/digitalguide/paginas-web/desarrollo-web/logging-de-python/
# https://docs.python.org/3/library/logging.html

# TODO PARA EL MANEJO DEL TAMANO DEL ARCHIVO
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling

# TODO PARA UTILIZAR DOCKER EN EL MANEJO DE ARCHIVOS LOG CENTRALIZADOS
# https://www.loggly.com/ultimate-guide/centralizing-python-logs/

# TODO PARA FORMATEAR EL ARCHIVO LOG EN FORMATO JSON
# https://everythingtech.dev/2021/03/python-logging-with-json-formatter/
# https://www.datadoghq.com/blog/python-logging-best-practices/
# https://docs.python.org/3/howto/logging-cookbook.html#a-qt-gui-for-logging
if hasattr ( sys, 'frozen' ) : #support for py2exe
  _srcfile = "logging%s__init__%s" % ( os.sep, __file__ [ -4 : ] )

elif __file__ [ -4 : ].lower () in [ '.pyc', '.pyo' ] :
  _srcfile = __file__ [ : -4 ] + '.py'

else :
  _srcfile = __file__

_srcfile = os.path.normcase ( _srcfile )


class SuccessLogger () :
  """
  Custom logger class for the Success framework.
  
  Provides logging functionality with support for console, file, and email handlers.
  Implements singleton pattern per module/scope combination. Includes request context
  enrichment and exception handling capabilities.
  
  Attributes:
    __enableConsole (bool): Whether console logging is enabled.
    __enableFile (bool): Whether file logging is enabled.
    __logger (Logger): The underlying Python Logger instance.
    __mailEnabled (bool): Whether email logging is enabled.
    __toShow (str): Error message to display to the user.
    _instances (dict): Dictionary of logger instances by module/scope key.
    _initialized (bool): Whether this instance has been initialized.
    _module (str): The module name for this logger.
    _scope (str): The scope for this logger.
  """

  # Enables sending errors to the console / Habilita el envío de errores a la consola
  __enableConsole : bool   = False
  # Enables sending errors to the console / Habilita el envío de errores a la consola
  __enableFile    : bool   = False
  # SuccessLogger object instance. / Instancia del objeto logger.
  __logger        : Logger = None
  # Enable sending errors to email / Habilita el envío de errores al correo
  __mailEnabled   : bool   = False
  # Error to display to the user at the frontend level. / Error a mostrar al usuario a nivel de frontend.
  __toShow        : str    = ''
  _instances               = {}
  _initialized             = False
  _module         : str    = ''
  _scope          : str    = ''


  def __new__ ( cls, module : str, scope : str = "application" ) :
    """
    Creates or returns a singleton instance of SuccessLogger for the given module and scope.
    
    Args:
      module (str): The module name for the logger.
      scope (str, optional): The scope for the logger. Defaults to "application".
    
    Returns:
      SuccessLogger: The singleton instance for the module/scope combination.
    """
    key = ( module, scope )

    if key not in cls._instances :
      instance = super ().__new__ ( cls )
      cls._instances [ key ] = instance
      instance._initialized = False

    return cls._instances [ key ]


  def __init__ ( self, module : str, scope : str ) -> None :
    """
    Initializes the SuccessLogger instance.
    
    Sets up the logger with appropriate level and handlers (file, console, email).
    Skips reinitialization if already initialized (singleton pattern).
    
    Args:
      module (str): The module name for the logger.
      scope (str): The scope for the logger.
    """
    if self._initialized :
      return  # Evita reinicialización si ya existe

    self._module      = module
    self._scope       = scope
    self._initialized = True
    self.__logger     = getLogger ( module )
    self.__logger.setLevel ( self.__getLevel () )
    self.__logger.propagate = False

    if not self.__logger.handlers :
      self.__fileHandled ()
      self.__consoleHandled ()
      self.__emailHandled ()

    if ( SuccessAppMode.isStagingMode () or SuccessAppMode.isProductionMode () ) :
      raiseExceptions = False


  def __consoleHandled ( self ) :
    """
    Sets up the console handler if console logging is enabled.
    
    Adds a SuccessConsoleHandler to the logger if LOGGER_CONSOLE is enabled.
    """
    if ( SuccessSystemEnv.isTrue ( "LOGGER_CONSOLE" ) ) :
      consoleHandled = SuccessConsoleHandler ()
      self.__logger.addHandler ( consoleHandled.getDescriptor () )


  def __emailHandled ( self ) :
    """
    Sets up the email handler if email logging is enabled.
    
    Adds a SuccessEmailHandler to the logger if LOGGER_MAIL_ENABLED is enabled.
    """
    self.__mailEnabled = SuccessSystemEnv.isTrue ( "LOGGER_MAIL_ENABLED" )
    if ( self.__mailEnabled ) :
      emailHandled = SuccessEmailHandler ()
      self.__loggerMailer = emailHandled.getDescriptor ()
      self.__logger.addHandler ( self.__loggerMailer )


  def __fileHandled ( self ) :
    """
    Sets up the file handler if file logging is enabled.
    
    Adds a SuccessFileHandler to the logger if LOGGER_FILE is enabled.
    """
    if ( SuccessSystemEnv.isTrue ( "LOGGER_FILE" ) ) :
      fileHandled = SuccessFileHandler ()
      self.__logger.addHandler ( fileHandled.getDescriptor () )


  def __getLevel ( self, level : str = None ) :
    """
    Determines the logging level from environment configuration.
    
    Args:
      level (str, optional): Explicit level to use. If None, reads from LOGGER_LEVEL env var.
    
    Returns:
      The logging level constant (DEBUG, INFO, WARNING, ERROR, or CRITICAL).
        Defaults to INFO if level is not recognized.
    """
    import os
    # level_str = ( level or SuccessSystemEnv.get ( "LOGGER_LEVEL", "INFO" ) ).upper ()
    level_str = ( level or os.environ.get ( "LOGGER_LEVEL", "INFO" ) ).upper ()
    levels = {
      "DEBUG"    : DEBUG,
      "INFO"     : INFO,
      "WARNING"  : WARNING,
      "ERROR"    : ERROR,
      "CRITICAL" : CRITICAL,
    }
    return levels.get ( level_str, INFO )


  def _log ( self, level, msg, args, exc_info = None, extra = None ) -> None :
    """
    Low-level logging routine which creates a LogRecord and then calls
    all the handlers of this logger to handle the record.
    
    Args:
      level: The logging level.
      msg: The log message.
      args: Arguments for the log message.
      exc_info: Exception information for logging exceptions.
      extra: Additional context to add to the log record.
    """
    # Add wrapping functionality here.
    if _srcfile :
      #IronPython doesn't track Python frames, so findCaller throws an
      #exception on some versions of IronPython. We trap it here so that
      #IronPython can use logging.
      try :
        fn, lno, func = self.findCaller ()

      except ValueError :
        fn, lno, func = "(unknown file)", 0, "(unknown function)"

    else :
      fn, lno, func = "(unknown file)", 0, "(unknown function)"

    if exc_info:
      if not isinstance ( exc_info, tuple ) :
        exc_info = sys.exc_info ()

    enriched = {
      "request_id" : RequestContext.getRequestId (),
      "app_id"     : RequestContext.getAppId (),
      "env"        : SuccessSystemEnv.get ( "APP_ENV", "unknown" )
    }

    if extra :
      enriched.update ( extra )

    record = self.__logger.makeRecord ( self.__logger.name, level, fn, lno, msg, args, exc_info, func, extra = enriched )
    self.__logger.handle ( record )


  def customInit ( self, app : Flask = None, *args, **kwargs ) -> None :
    """
    Performs custom initialization for handlers.
    
    Args:
      apps (Flask, optional): Flask application instances.
      *args: Additional positional arguments.
      **kwargs: Additional keyword arguments.
    """
    if apps :
      if self.__mailEnabled :
        self.__loggerMailer.customInit ( apps, *args, **kwargs )


  def findCaller ( self ) :
    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.
    
    Returns:
      tuple: A tuple containing (filename, line_number, function_name).
    """
    f = currentframe ()
    #On some versions of IronPython, currentframe() returns None if
    #IronPython isn't run with -X:Frames.
    if f is not None :
      f = f.f_back

    rv = "(unknown file)", 0, "(unknown function)"
    while hasattr ( f, "f_code" ) :
      co = f.f_code
      filename = os.path.normcase ( co.co_filename )
      if filename == _srcfile :
        f = f.f_back
        continue

      rv = ( co.co_filename, f.f_lineno, co.co_name )
      break

    return rv


  def log ( self, errorMessage, levelError : str = None ) -> None :
    """
    Logs an error message at the appropriate level.
    
    Handles various error object types including strings, objects with getMessage(),
    orig, and message attributes. Automatically elevates to CRITICAL level when needed.
    
    Args:
      errorMessage: The error message or error object to log.
      levelError (str, optional): Explicit log level. If None, determined automatically.
    """
    try :
      level    = self.__getLevel ( levelError )
      msg      = ""
      exc_info = None

      if isinstance ( errorMessage, str ) :
        msg = errorMessage

      elif hasattr ( errorMessage, 'getMessage' ) :
        msg = str ( errorMessage.getMessage () )
        exc_info = errorMessage

      elif hasattr ( errorMessage, 'orig' ) :
        msg = str ( errorMessage.orig )
        exc_info = errorMessage

      elif hasattr ( errorMessage, 'message' ) :
        msg = str ( errorMessage.message )
        exc_info = errorMessage

      else :
        msg = str ( errorMessage )
        exc_info = errorMessage

        if self.__logger.isEnabledFor ( CRITICAL ) :
          level = CRITICAL
          self.sendException ( "Critical exception", level, errorMessage )

      self.__toShow = msg
      self._log ( level, msg, args = (), exc_info = exc_info )

    except Exception as internal_error :
      self._log ( CRITICAL, f"[SuccessLogger] Error handling log message: {internal_error}", args = (), exc_info = True )


  def sendException ( self, _name : str, _level : int, _exc_info : BaseException or TracebackType ) :
    """
    Sends an exception record via email handler.
    
    Args:
      _name (str): The name/description of the exception.
      _level (int): The logging level.
      _exc_info (BaseException or TracebackType): The exception information.
    """
    if not self.__mailEnabled :
      return

    try :
      fn, lno, func = self.findCaller ()
      enriched = {
        "request_id" : RequestContext.getRequestId (),
        "app_id"     : RequestContext.getAppId (),
        "env"        : SuccessSystemEnv.get ( "APP_ENV", "unknown" )
      }
      record = self.__logger.makeRecord (
        name = self.__logger.name,
        level = level,
        fn = fn,
        lno = lno,
        msg = f"{name}: {exc_info}",
        args = (),
        exc_info = exc_info,
        func = func,
        extra = enriched
      )
      self.__loggerMailer.emit ( record )

    except Exception as e :
      self._log ( CRITICAL, f"[SuccessLogger] Error en sendException: {e}", args = (), exc_info = True )


  def toShow ( self ) -> str :
    """
    Retrieves the error message to display to the user.
    
    Returns:
      str: The error message for user display.
    """
    return self.__toShow


  def uncatchErrorException ( self ) -> None :
    """
    Handles uncaught errors by logging and preparing a user message.
    
    Sets a generic error message for user display and logs the full exception
    details via email if enabled.
    """
    self.__toShow = "Error no identificado, comunicarse inmediatamente con el administrador del sistema."
    try :
      self.sendException ( "uncaught exception", CRITICAL, sys.exc_info () )

    except Exception :
      pass

    self._log ( CRITICAL, self.__toShow, args = (), exc_info = True )
