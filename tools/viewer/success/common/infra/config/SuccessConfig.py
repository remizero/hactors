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

# Application Libraries / Librerías de la Aplicación
from success.common.infra.config.SuccessAppEnv           import SuccessAppEnv
from success.common.infra.config.SuccessConfigExtensions import SuccessConfigExtensions

# Preconditions / Precondiciones


class SuccessConfig ( object ) :
  """
  Main configuration class for the Success framework.

  Loads and manages all system configurations from environment variables,
  including base Flask configuration and specific configurations for each
  extension (ACL, CORS, JWT, Logger, Email, etc.).

  Configuration is organized in three levels:
  1. Base Success/Flask configuration
  2. Enabled extension configurations
  3. Custom application configuration

  Attributes:
    APP_ENV (str): Runtime environment (development, production, etc.).
    APP_HOST (str): Host where the application will run.
    APP_PORT (int): Application listening port.
    BASE_URL (str): Base URL of the application.
    DEBUG (bool): True if debug mode is enabled.
    SERVER_NAME (str): Server name.
    SECRET_KEY (str): Secret key for sessions and security.
    API_KEY (str): API key for authentication.
    SUCCESS_DEBUG_CONSOLE (bool): True if console debug is enabled.

  Usage:
    env = SuccessAppEnv('/apps/myApp')
    config = SuccessConfig(env)
    app.config.from_object(config)
  """


  def __init__ ( self, env : SuccessAppEnv ) -> None :
    """
    Initialize SuccessConfig loading values from the environment provider.

    Loads all configurations from the provided SuccessAppEnv, including
    base Success/Flask configuration and extension configurations based
    on enablement flags.

    Args:
      env (SuccessAppEnv): Environment provider from which to load
        configuration variables.

    Example:
      env = SuccessAppEnv('/apps/myApp')
      config = SuccessConfig(env)
      # config.APP_PORT → 5001
      # config.DEBUG → True
      # config.SECRET_KEY → 'your-secret-key'
    """
    # ----------------------------------------------------------
    # Success Configuration / Configuración de Success
    # ----------------------------------------------------------
    self.APP_ENV                       = env.get ( 'APP_ENV' )
    self.APP_HOST                      = env.get ( 'APP_HOST' )
    self.APP_PORT                      = env.toInt ( 'APP_PORT' )
    self.BASE_URL                      = env.get ( 'BASE_URL' )
    self.DEBUG                         = env.isTrue ( 'DEBUG' )
    self.SERVER_NAME                   = env.get ( 'SERVER_NAME' )
    self.SECRET_KEY                    = env.get ( 'SECRET_KEY' )
    self.API_KEY                       = env.get ( 'API_KEY' )
    self.SUCCESS_DEBUG_CONSOLE         = env.isTrue ( 'SUCCESS_DEBUG_CONSOLE' )
    self.SUCCESS_STAGING               = env.isTrue ( 'SUCCESS_STAGING' )
    self.SUCCESS_TESTING               = env.isTrue ( 'SUCCESS_TESTING' )
    self.SUCCESS_STRICT_SLASHES        = env.isTrue ( 'SUCCESS_STRICT_SLASHES' )
    self.SUCCESS_EXTENSION_ACL         = env.isTrue ( 'SUCCESS_EXTENSION_ACL' )
    self.SUCCESS_EXTENSION_CORS        = env.isTrue ( 'SUCCESS_EXTENSION_CORS' )
    self.SUCCESS_EXTENSION_SQLALCHEMY  = env.isTrue ( 'SUCCESS_EXTENSION_SQLALCHEMY' )
    self.SUCCESS_EXTENSION_EMAIL       = env.isTrue ( 'SUCCESS_EXTENSION_EMAIL' )
    self.SUCCESS_EXTENSION_JWT         = env.isTrue ( 'SUCCESS_EXTENSION_JWT' )
    self.SUCCESS_EXTENSION_LOGGER      = env.isTrue ( 'SUCCESS_EXTENSION_LOGGER' )
    self.SUCCESS_EXTENSION_MARSHMALLOW = env.isTrue ( 'SUCCESS_EXTENSION_MARSHMALLOW' )
    self.SUCCESS_EXTENSION_REDIS       = env.isTrue ( 'SUCCESS_EXTENSION_REDIS' )
    self.SUCCESS_EXTENSION_RESTFUL     = env.isTrue ( 'SUCCESS_EXTENSION_RESTFUL' )
    self.SUCCESS_EXTENSION_SESSION     = env.isTrue ( 'SUCCESS_EXTENSION_SESSION' )
    self.SUCCESS_OUTPUT_MODEL          = env.isTrue ( 'SUCCESS_OUTPUT_MODEL' )
    self.SUCCESS_TABLENAME_MODEL       = env.isTrue ( 'SUCCESS_TABLENAME_MODEL' )
    # # Control del CLI interno
    self.SUCCESS_ENABLE_CLI            = env.isTrue ( 'SUCCESS_ENABLE_CLI' )
    self.SUCCESS_ENABLE_GRAPHQL        = env.isTrue ( 'SUCCESS_ENABLE_GRAPHQL' )
    self.SUCCESS_ENABLE_REST           = env.isTrue ( 'SUCCESS_ENABLE_REST' )
    self.SUCCESS_ENABLE_RPC            = env.isTrue ( 'SUCCESS_ENABLE_RPC' )
    self.SUCCESS_ENABLE_SSE            = env.isTrue ( 'SUCCESS_ENABLE_SSE' )
    self.SUCCESS_ENABLE_SOAP           = env.isTrue ( 'SUCCESS_ENABLE_SOAP' )
    self.SUCCESS_ENABLE_VIEW           = env.isTrue ( 'SUCCESS_ENABLE_VIEW' )
    self.SUCCESS_ENABLE_WEB_SOCKET     = env.isTrue ( 'SUCCESS_SUCCESS_ENABLE_WEB_SOCKETENABLE_CLI' )
    

    self.SUCCESS_CUSTOM_CONFIG_CLASS   = env.get ( 'SUCCESS_CUSTOM_CONFIG_CLASS' )

    # Control del entrypoint visual
    # self.SUCCESS_ENABLE_DASHBOARD      = env.isTrue ( 'SUCCESS_ENABLE_DASHBOARD' )
    # # Aplicación principal (enrutada en '/')
    # self.SUCCESS_DEFAULT_APP           = env.isTrue ( 'SUCCESS_DEFAULT_APP' )
    self.SUCCESS_HUMOR_ENABLED         = env.isTrue ( 'SUCCESS_HUMOR_ENABLED' )
    self.SUCCESS_MOOD_LANG             = env.get ( 'SUCCESS_MOOD_LANG' )
    self.SUCCESS_CUSTOM_CONFIG_CLASS   = env.get ( 'SUCCESS_CUSTOM_CONFIG_CLASS' )
    self.SUCCESS_APP_MAIN              = env.isTrue ( 'SUCCESS_APP_MAIN' )
    # self.SUCCESS_EXTENSION_ =
    # self.SUCCESS_EXTENSION_ =


    # -----------------------------------------
    # Flask Configuration / Configuración Flask
    # -----------------------------------------
    # - Project name.
    self.FLASK_APP             = env.get ( 'FLASK_APP' )
    # - Controls the environment.
    self.FLASK_ENV             = env.get ( 'FLASK_ENV' )
    #  - Enables debug mode.
    self.FLASK_DEBUG           = env.isTrue ( 'FLASK_DEBUG' )
    # - A list of files that will be watched by the reloader in addition to the Python modules.
    # self.FLASK_RUN_EXTRA_FILES = env.get ( 'FLASK_RUN_EXTRA_FILES' )
    # - The host you want to bind your apps to.
    # self.FLASK_RUN_HOST        = env.get ( 'FLASK_RUN_HOST' )
    # - The port you want to use.
    # self.FLASK_RUN_PORT        = env.toInt ( 'FLASK_RUN_PORT' )
    # - A certificate file for so your apps can be run with HTTPS.
    # self.FLASK_RUN_CERT        = env.get ( 'FLASK_RUN_CERT' )
    # - The key file for your cert.
    # self.FLASK_RUN_KEY         = env.get ( 'FLASK_RUN_KEY' )

    # -------------------------------------------------
    # ACL Configuration / Configuración ACL
    # -------------------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_ACL' ) ) :
      self.extend ( SuccessConfigExtensions.loadAcl ( env ) )


    # -------------------------------------------------
    # Blueprint Configuration / Configuración Blueprint
    # -------------------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_BLUEPRINT' ) ) :
      self.extend ( SuccessConfigExtensions.loadBlueprint ( env ) )


    # ---------------------------------------
    # Cors Configuration / Configuración Cors
    # ---------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_CORS' ) ) :
      self.extend ( SuccessConfigExtensions.loadCors ( env ) )


    # ---------------------------------------
    # JWT Configuration / Configuración JWT
    # ---------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_JWT' ) ) :
      self.extend ( SuccessConfigExtensions.loadJwt ( env ) )


    # ---------------------------------------
    # SuccessLogger Configuration / Configuración SuccessLogger
    # ---------------------------------------
    # ---------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_LOGGER' ) ) :
      self.extend ( SuccessConfigExtensions.loadLogger ( env ) )


    # ---------------------------------------
    # Mail Configuration / Configuración Mail
    # ---------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_EMAIL' ) ) :
      self.extend ( SuccessConfigExtensions.loadEmail ( env ) )


    # -------------------------------------------------
    # MARSHMALLOW Configuration / Configuración MARSHMALLOW
    # -------------------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_MARSHMALLOW' ) ) :
      self.extend ( SuccessConfigExtensions.loadMarshmallow ( env ) )


    # -----------------------------------------
    # Redis Configuration / Configuración Redis
    # -----------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_REDIS' ) ) :
      self.extend ( SuccessConfigExtensions.loadRedis ( env ) )


    # ---------------------------------------------
    # Restful Configuration / Configuración Restful
    # ---------------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_RESTFUL' ) ) :
      self.extend ( SuccessConfigExtensions.loadRestful ( env ) )


    # -----------------------------------------------
    # SuccessSessionExtension Configuration / Configuración de Sesión
    # -----------------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_SESSION' ) ) :
      self.extend ( SuccessConfigExtensions.loadSession ( env ) )


    # ---------------------------------------------------
    # SqlAlchemy Configuration / Configuración SqlAlchemy
    # ---------------------------------------------------
    if ( env.isTrue ( 'SUCCESS_EXTENSION_SQLALCHEMY' ) ) :
      self.extend ( SuccessConfigExtensions.loadSqlalchemy ( env ) )


  def extend ( self, config_dict : dict ) -> None :
    """
    Extend configuration with an additional dictionary.

    Receives a dictionary with additional configurations and assigns them
    as attributes of the current instance.

    Args:
      config_dict (dict): Dictionary with additional configurations
        that will be added as attributes.

    Example:
      config.extend({'CUSTOM_SETTING': 'value'})
      # config.CUSTOM_SETTING → 'value'
    """
    for key, value in config_dict.items () :
      setattr ( self, key, value )


  def get ( self, key : str, default = None ) -> str :
    """
    Get a configuration value by key.

    Args:
      key (str): Configuration key name.
      default: Default value if the key does not exist.

    Returns:
      str: The configuration value, or the default if not found.

    Example:
      config.get('APP_PORT', 5000)  # → 5001
      config.get('NON_EXISTENT', 'default')  # → 'default'
    """
    return getattr ( self, key, default )
