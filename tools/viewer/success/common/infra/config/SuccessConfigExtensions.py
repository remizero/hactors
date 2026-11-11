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
from datetime import timedelta

# Application Libraries / Librerías de la Aplicación
from success.common.infra.config.SuccessAppEnv import SuccessAppEnv

# Preconditions / Precondiciones


class SuccessConfigExtensions () :
  """
  Configuration factory for Success framework extensions.

  Provides static methods to load specific configurations for each
  supported extension (ACL, Blueprint, CORS, JWT, Logger, Email,
  Marshmallow, Redis, Restful, Session, SqlAlchemy).

  Each method checks if the extension is enabled and returns the
  corresponding configuration dictionary or an empty dictionary.

  Usage:
    env = SuccessAppEnv('/apps/myapp')
    cors_config = SuccessConfigExtensions.loadCors(env)
    jwt_config = SuccessConfigExtensions.loadJwt(env)
    logger_config = SuccessConfigExtensions.loadLogger(env)
  """


  @staticmethod
  def loadAcl ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the ACL (Access Control List) extension.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with ACL configuration if enabled, empty dictionary
        otherwise.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_ACL' ) ) :
      return {

      }
    return {}


  @staticmethod
  def loadBlueprint ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the Blueprint extension.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with Blueprint configuration if enabled, empty
        dictionary otherwise.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_BLUEPRINT' ) ) :
      return {

      }
    return {}


  @staticmethod
  def loadCors ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the CORS (Cross-Origin Resource Sharing) extension.

    Configures cross-origin access policies for different domains, including
    allowed origins, HTTP methods, headers, and other CORS options.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with CORS configuration if enabled, empty dictionary
        otherwise.

    Note:
      Includes configuration for multiple domains via CORS_RESOURCES_APP_*
      variables that allow custom policies per domain.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_CORS' ) ) :
      return {
        "CORS_ALLOW_HEADERS"                : env.toList ( 'CORS_ALLOW_HEADERS' ),
        "CORS_ALWAYS_SEND"                  : env.isTrue ( 'CORS_ALWAYS_SEND' ),
        "CORS_AUTOMATIC_OPTIONS"            : env.isTrue ( 'CORS_AUTOMATIC_OPTIONS' ),
        "CORS_EXPOSE_HEADERS"               : env.toList ( 'CORS_EXPOSE_HEADERS' ),
        "CORS_INTERCEPT_EXCEPTIONS"         : env.isTrue ( 'CORS_INTERCEPT_EXCEPTIONS' ),
        "CORS_MAX_AGE"                      : env.get    ( 'CORS_MAX_AGE' ),
        "CORS_METHODS"                      : env.toList ( 'CORS_METHODS' ),
        "CORS_ORIGINS"                      : env.get    ( 'CORS_ORIGINS' ),
        "CORS_RESOURCES"                    : env.get    ( 'CORS_RESOURCES' ),
        "CORS_SEND_WILDCARD"                : env.isTrue ( 'CORS_SEND_WILDCARD' ),
        "CORS_SUPPORTS_CREDENTIALS"         : env.isTrue ( 'CORS_SUPPORTS_CREDENTIALS' ),
        "CORS_VARY_HEADER"                  : env.isTrue ( 'CORS_VARY_HEADER' ),
        # ---------------------------------------------------------
        # Cors Optional Configuration
        # These macros are special and customized for proper handling of Cors policies in flask for different domains in a personalized way.
        # ---------------------------------------------------------
        "CORS_RESOURCES_APP_RESOURCES"      : env.toList ( 'CORS_RESOURCES_APP_RESOURCES' ),
        "CORS_RESOURCES_APP_ORIGINS"        : env.toList ( 'CORS_RESOURCES_APP_ORIGINS' ),
        "CORS_RESOURCES_APP_METHODS"        : env.toList ( 'CORS_RESOURCES_APP_METHODS' ),
        "CORS_RESOURCES_APP_ALLOW_HEADERS"  : env.toList ( 'CORS_RESOURCES_APP_ALLOW_HEADERS' ),
        "CORS_RESOURCES_APP_EXPOSE_HEADERS" : env.toList ( 'CORS_RESOURCES_APP_EXPOSE_HEADERS' )
      }
    return {}


  @staticmethod
  def loadJwt ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the JWT (JSON Web Tokens) extension.

    Configures all JWT authentication options including access and refresh
    tokens, cookies, CSRF, encryption algorithms, and more.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with JWT configuration if enabled, empty dictionary
        otherwise.

    Note:
      Includes configuration for access and refresh tokens, secure cookies,
      CSRF protection, and encryption/decryption options.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_JWT' ) ) :
      return {
        # Set a new name to token cookies
        "JWT_ACCESS_COOKIE_NAME"        : env.get ( 'JWT_ACCESS_COOKIE_NAME' ),
        # Set the cookie paths
        "JWT_ACCESS_COOKIE_PATH"        : env.get ( 'JWT_ACCESS_COOKIE_PATH' ),
        # "JWT_ACCESS_CSRF_COOKIE_NAME"   : env.get ( 'JWT_ACCESS_CSRF_COOKIE_NAME' ),
        # "JWT_ACCESS_CSRF_COOKIE_PATH"   : env.get ( 'JWT_ACCESS_CSRF_COOKIE_PATH' ),
        # "JWT_ACCESS_CSRF_FIELD_NAME"    : env.get ( 'JWT_ACCESS_CSRF_FIELD_NAME' ),
        # Set header access name for csrf
        "JWT_ACCESS_CSRF_HEADER_NAME"   : env.get ( 'JWT_ACCESS_CSRF_HEADER_NAME' ),
        # Se define el tiempo de duración del token de acceso
        "JWT_ACCESS_TOKEN_EXPIRES"      : env.toInt ( 'JWT_ACCESS_TOKEN_EXPIRES' ),
        # "JWT_ALGORITHM"                 : env.get ( 'JWT_ALGORITHM' ),
        "JWT_BLOCKLIST_ENABLED"         : env.isTrue ( 'JWT_BLOCKLIST_ENABLED' ),
        "JWT_BLOCKLIST_TOKEN_CHECKS"    : env.toList ( 'JWT_BLOCKLIST_TOKEN_CHECKS' ),
        # Enable csrf double submit protection.
        "JWT_COOKIE_CSRF_PROTECT"       : env.isTrue ( 'JWT_COOKIE_CSRF_PROTECT' ),
        # Se define el dominio sobre el cual se crearan las cookies
        # HABILITAR SOLO PARA MODO DE DESARROLLO EN LOCAL
        # HABILITAR PARA MODO SUCCESS_STAGING Y/O PRODUCCION
        # "JWT_COOKIE_DOMAIN"             : env.get ( 'JWT_COOKIE_DOMAIN' ),
        # "JWT_COOKIE_SAMESITE"           : env.get ( 'JWT_COOKIE_SAMESITE' ),
        # Only allow JWT cookies to be sent over https. In production, this should likely be True
        "JWT_COOKIE_SECURE"             : env.isTrue ( 'JWT_COOKIE_SECURE' ),
        # Set csrf check form
        "JWT_CSRF_CHECK_FORM"           : env.isTrue ( 'JWT_CSRF_CHECK_FORM' ),
        # "JWT_CSRF_IN_COOKIES"           : env.isTrue ( 'JWT_CSRF_IN_COOKIES' ),
        # Set allowed methods for csrf
        "JWT_CSRF_METHODS"              : env.toList ( 'JWT_CSRF_METHODS' ),
        # "JWT_DECODE_ALGORITHMS"         : env.get ( 'JWT_DECODE_ALGORITHMS' ),
        # "JWT_DECODE_AUDIENCE"           : env.get ( 'JWT_DECODE_AUDIENCE' ),
        # "JWT_DECODE_ISSUER"             : env.get ( 'JWT_DECODE_ISSUER' ),
        # "JWT_DECODE_LEEWAY"             : env.toInt ( 'JWT_DECODE_LEEWAY' ),
        # "JWT_ENCODE_AUDIENCE"           : env.get ( 'JWT_ENCODE_AUDIENCE' ),
        # "JWT_ENCODE_ISSUER"             : env.get ( 'JWT_ENCODE_ISSUER' ),
        # Se define el índice que devolverá los errores generados para la sesión
        "JWT_ERROR_MESSAGE_KEY"         : env.get ( 'JWT_ERROR_MESSAGE_KEY' ),
        # "JWT_HEADER_NAME"               : env.get ( 'JWT_HEADER_NAME' ),
        # "JWT_HEADER_TYPE"               : env.get ( 'JWT_HEADER_TYPE' ),
        # "JWT_IDENTITY_CLAIM"            : env.get ( 'JWT_IDENTITY_CLAIM' ),
        # "JWT_JSON_KEY"                  : env.get ( 'JWT_JSON_KEY' ),
        # "JWT_PRIVATE_KEY"               : env.get ( 'JWT_PRIVATE_KEY' ),
        # "JWT_PUBLIC_KEY"                : env.get ( 'JWT_PUBLIC_KEY' ),
        # "JWT_QUERY_STRING_NAME"         : env.get ( 'JWT_QUERY_STRING_NAME' ),
        # "JWT_QUERY_STRING_VALUE_PREFIX" : env.get ( 'JWT_QUERY_STRING_VALUE_PREFIX' ),
        # Set a new name to token cookies
        "JWT_REFRESH_COOKIE_NAME"       : env.get ( 'JWT_REFRESH_COOKIE_NAME' ),
        # Set the cookie paths
        "JWT_REFRESH_COOKIE_PATH"       : env.get ( 'JWT_REFRESH_COOKIE_PATH' ),
        # "JWT_REFRESH_CSRF_COOKIE_NAME"  : env.get ( 'JWT_REFRESH_CSRF_COOKIE_NAME' ),
        # "JWT_REFRESH_CSRF_COOKIE_PATH"  : env.get ( 'JWT_REFRESH_CSRF_COOKIE_PATH' ),
        # "JWT_REFRESH_CSRF_FIELD_NAME"   : env.get ( 'JWT_REFRESH_CSRF_FIELD_NAME' ),
        # Set header refresh name for csrf
        "JWT_REFRESH_CSRF_HEADER_NAME"  : env.get ( 'JWT_REFRESH_CSRF_HEADER_NAME' ),
        # "JWT_REFRESH_JSON_KEY"          : env.get ( 'JWT_REFRESH_JSON_KEY' ),
        # Se define el tiempo de duración del token de reingreso o relogin
        "JWT_REFRESH_TOKEN_EXPIRES"     : env.toInt ( 'JWT_REFRESH_TOKEN_EXPIRES' ),
        # Set the secret key to sign the JWTs with
        "JWT_SECRET_KEY"                : env.get ( 'JWT_SECRET_KEY' ),
        # JWT_SESSION_COOKIE            : env.isTrue ( 'JWT_SESSION_COOKIE' ),
        # Configure application to store JWTs in cookies
        "JWT_TOKEN_LOCATION"            : env.get ( 'JWT_TOKEN_LOCATION' )
        # "JWT_ENCODE_NBF"                : env.isTrue ( 'JWT_ENCODE_NBF' )
      }
    return {}


  @staticmethod
  def loadLogger ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the Logger extension.

    Configures the logging system including console output, file output,
    and email logging for critical errors.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with Logger configuration if enabled, empty dictionary
        otherwise.

    Note:
      Supports multiple handlers (console, file, email) with file rotation
      and custom formatting.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_LOGGER' ) ) :
      return {
        "LOGGER_ADMIN"                   : env.get    ( 'LOGGER_ADMIN' ),
        "LOGGER_BACKUP_COUNT"            : env.toInt  ( 'LOGGER_BACKUP_COUNT' ),
        "LOGGER_CONSOLE"                 : env.isTrue ( 'LOGGER_CONSOLE' ),
        "LOGGER_DIR"                     : env.get    ( 'LOGGER_DIR' ),
        "LOGGER_ENCODING"                : env.get    ( 'LOGGER_ENCODING' ),
        "LOGGER_FILE"                    : env.isTrue ( 'LOGGER_FILE' ),
        "LOGGER_FORMAT"                  : env.get    ( 'LOGGER_FORMAT' ),
        "LOGGER_FORMATER"                : env.get    ( 'LOGGER_FORMATER' ),
        "LOGGER_LEVEL"                   : env.get    ( 'LOGGER_LEVEL' ),
        "LOGGER_MAIL_ENABLED"            : env.isTrue ( 'LOGGER_MAIL_ENABLED' ),
        "LOGGER_MAIL_PASSWORD"           : env.get    ( 'LOGGER_MAIL_PASSWORD' ),
        "LOGGER_MAIL_PORT"               : env.toInt  ( 'LOGGER_MAIL_PORT' ),
        "LOGGER_MAIL_SERVER"             : env.get    ( 'LOGGER_MAIL_SERVER' ),
        "LOGGER_MAIL_SSL"                : env.isTrue ( 'LOGGER_MAIL_SSL' ),
        "LOGGER_MAIL_TLS"                : env.isTrue ( 'LOGGER_MAIL_TLS' ),
        "LOGGER_MAIL_USERNAME"           : env.get    ( 'LOGGER_MAIL_USERNAME' ),
        "LOGGER_MAX_BYTES"               : env.toInt  ( 'LOGGER_MAX_BYTES' ),
        "LOGGER_MAX_RETRIES"             : env.toInt  ( 'LOGGER_MAX_RETRIES' ),
        "LOGGER_MESSAGE_SUBJECT"         : env.get    ( 'LOGGER_MESSAGE_SUBJECT' ),
        "LOGGER_ROTATE_INTERVAL"         : env.get    ( 'LOGGER_ROTATE_INTERVAL' ),
        "LOGGER_TEMPLATE_FORMAT_MESSAGE" : env.get    ( 'LOGGER_TEMPLATE_FORMAT_MESSAGE' ),
        "LOGGER_TEMPLATE_HTML_ERROR"     : env.get    ( 'LOGGER_TEMPLATE_HTML_ERROR' ),
        "LOGGER_TEMPLATE_HTML_EXCEPTION" : env.get    ( 'LOGGER_TEMPLATE_HTML_EXCEPTION' ),
        "LOGGER_ROTATE_WHEN"             : env.get    ( 'LOGGER_ROTATE_WHEN' )
      }
    return {}


  @staticmethod
  def loadEmail ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the Email extension.

    Configures the email sending service including SMTP server,
    authentication, security (TLS/SSL), and attachment options.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with Email configuration if enabled, empty dictionary
        otherwise.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_EMAIL' ) ) :
      return {
        "MAIL_SERVER"                : env.get    ( 'MAIL_SERVER' ),
        "MAIL_PORT"                  : env.toInt  ( 'MAIL_PORT' ),
        "MAIL_USE_TLS"               : env.isTrue ( 'MAIL_USE_TLS' ),
        "MAIL_USE_SSL"               : env.isTrue ( 'MAIL_USE_SSL' ),
        "MAIL_DEBUG"                 : env.toInt  ( 'MAIL_DEBUG' ),
        "MAIL_USERNAME"              : env.get    ( 'MAIL_USERNAME' ),
        "MAIL_PASSWORD"              : env.get    ( 'MAIL_PASSWORD' ),
        "MAIL_DEFAULT_SENDER"        : env.toList ( 'MAIL_DEFAULT_SENDER' ),
        "MAIL_MAX_EMAILS"            : env.toInt  ( 'MAIL_MAX_EMAILS' ),
        # "MAIL_SUPPRESS_SEND"         : env.get    ( 'MAIL_SUPPRESS_SEND' ),
        "MAIL_ASCII_ATTACHMENTS"     : env.isTrue ( 'MAIL_ASCII_ATTACHMENTS' ),
        # ---------------------------------------------------------
        # Mail Optional Configuration
        # ---------------------------------------------------------
        "MAIL_DONT_REPLY_FROM_EMAIL" : env.get    ( 'MAIL_DONT_REPLY_FROM_EMAIL' )
      }
    return {}


  @staticmethod
  def loadMarshmallow ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the Marshmallow extension.

    Configures data serialization and validation using Marshmallow.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with Marshmallow configuration if enabled, empty
        dictionary otherwise.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_MARSHMALLOW' ) ) :
      return {

      }
    return {}


  @staticmethod
  def loadRedis ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the Redis extension.

    Configures the Redis connection for caching, sessions, or in-memory
    data storage.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with Redis configuration if enabled, empty dictionary
        otherwise.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_REDIS' ) ) :
      return {
        "REDIS_CHARSET"          : env.get    ( 'REDIS_CHARSET' ),
        "REDIS_CONNECTION_POOL"  : env.get    ( 'REDIS_CONNECTION_POOL' ),
        "REDIS_DB"               : env.get    ( 'REDIS_DB' ),
        "REDIS_DECODE_RESPONSES" : env.isTrue ( 'REDIS_DECODE_RESPONSES' ),
        "REDIS_ERRORS"           : env.get    ( 'REDIS_ERRORS' ),
        "REDIS_HOST"             : env.get    ( 'REDIS_HOST' ),
        "REDIS_PASSWORD"         : env.get    ( 'REDIS_PASSWORD' ),
        "REDIS_PORT"             : env.toInt  ( 'REDIS_PORT' ),
        "REDIS_SOCKET_TIMEOUT"   : env.get    ( 'REDIS_SOCKET_TIMEOUT' ),
        "REDIS_UNIX_SOCKET_PATH" : env.get    ( 'REDIS_UNIX_SOCKET_PATH' )
      }
    return {}


  @staticmethod
  def loadRestful ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the RESTful (Flask-RESTful) extension.

    Configures REST API creation using Flask-RESTful.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with RESTful configuration if enabled, empty
        dictionary otherwise.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_RESTFUL' ) ) :
      return {
        "RESTFUL_CATCH_ALL_404S" : env.isTrue ( 'RESTFUL_CATCH_ALL_404S' )
      }
    return {}


  @staticmethod
  def loadSession ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the Session extension.

    Configures user session handling including storage type (filesystem,
    redis, sqlalchemy, etc.), cookies, and session lifetime.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with Session configuration if enabled, empty
        dictionary otherwise.
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_SESSION' ) ) :
      return {
        "SESSION_COOKIE_NAME"        : env.get    ( 'SESSION_COOKIE_NAME' ),
        "SESSION_COOKIE_DOMAIN"      : env.get    ( 'SESSION_COOKIE_DOMAIN' ),
        "SESSION_COOKIE_PATH"        : env.get    ( 'SESSION_COOKIE_PATH' ),
        "SESSION_COOKIE_HTTPONLY"    : env.isTrue ( 'SESSION_COOKIE_HTTPONLY' ),
        "SESSION_COOKIE_SECURE"      : env.isTrue ( 'SESSION_COOKIE_SECURE' ),
        "PERMANENT_SESSION_LIFETIME" : timedelta     ( seconds = env.toInt  ( 'PERMANENT_SESSION_LIFETIME' ) ),
        "SESSION_TYPE"               : env.get    ( 'SESSION_TYPE' ),
        "SESSION_PERMANENT"          : env.isTrue ( 'SESSION_PERMANENT' ),
        "SESSION_USE_SIGNER"         : env.isTrue ( 'SESSION_USE_SIGNER' ),
        "SESSION_KEY_PREFIX"         : env.get    ( 'SESSION_KEY_PREFIX' ),
        # "SESSION_REDIS"              : env.get    ( 'SESSION_REDIS' ),
        # "SESSION_MEMCACHED"          : env.get    ( 'SESSION_MEMCACHED' ),
        # "SESSION_FILE_DIR"           : env.get    ( 'SESSION_FILE_DIR' ),
        # "SESSION_FILE_THRESHOLD"     : env.get    ( 'SESSION_FILE_THRESHOLD' ),
        # "SESSION_FILE_MODE"          : env.get    ( 'SESSION_FILE_MODE' ),
        # "SESSION_MONGODB"            : env.get    ( 'SESSION_MONGODB' ),
        # "SESSION_MONGODB_DB"         : env.get    ( 'SESSION_MONGODB_DB' ),
        # "SESSION_MONGODB_COLLECT"    : env.get    ( 'SESSION_MONGODB_COLLECT' ),
        # "SESSION_SQLALCHEMY"         : env.get    ( 'SESSION_SQLALCHEMY' ),
        # "SESSION_SQLALCHEMY_TABLE"   : env.get    ( 'SESSION_SQLALCHEMY_TABLE' )
      }
    return {}


  @staticmethod
  def loadSqlalchemy ( env : SuccessAppEnv ) -> dict :
    """
    Load configuration for the SqlAlchemy extension.

    Configures database connection using SqlAlchemy including connection
    URI, multiple binds, query echo, modification tracking, and engine
    options.

    Args:
      env (SuccessAppEnv): Environment provider with configuration variables.

    Returns:
      dict: Dictionary with SqlAlchemy configuration if enabled, empty
        dictionary otherwise.

    Note:
      Automatically builds DATABASE_URI from SQLALCHEMY_DB_* variables
      (driver, user, pw, host, port, db).
    """
    if ( env.isTrue ( 'SUCCESS_EXTENSION_SQLALCHEMY' ) ) :
      return {
        "SQLALCHEMY_DATABASE_URI" : '{driver}://{user}:{pw}@{host}:{port}/{db}'.format (
          driver = env.get ( 'SQLALCHEMY_DB_DRIVER' ),
          user   = env.get ( 'SQLALCHEMY_DB_USER' ),
          pw     = env.get ( 'SQLALCHEMY_DB_PASSWORD' ),
          host   = env.get ( 'SQLALCHEMY_DB_HOST' ),
          port   = env.get ( 'SQLALCHEMY_DB_PORT' ),
          db     = env.get ( 'SQLALCHEMY_DB_NAME' )
        ),
        "SQLALCHEMY_BINDS"                    : env.getJson ( 'SQLALCHEMY_BINDS' ),
        # "SQLALCHEMY_BINDS"                    : env.getJson ( 'SQLALCHEMY_BINDS' ) ) or env.toResource ( 'SQLALCHEMY_BINDS' ),
        "SQLALCHEMY_ECHO"                     : env.isTrue  ( 'SQLALCHEMY_ECHO' ),
        "SQLALCHEMY_RECORD_QUERIES"           : env.isTrue  ( 'SQLALCHEMY_RECORD_QUERIES' ),
        "SQLALCHEMY_COMMIT_ON_TEARDOWN"       : env.isTrue  ( 'SQLALCHEMY_COMMIT_ON_TEARDOWN' ),
        "SQLALCHEMY_TRACK_MODIFICATIONS"      : env.isTrue  ( 'SQLALCHEMY_TRACK_MODIFICATIONS' ),
        "SQLALCHEMY_ENGINE_OPTIONS"           : env.get     ( 'SQLALCHEMY_ENGINE_OPTIONS' ),
        # ------------------------------------------------------------------------------------------------------------------------------------
        # Additional sqlalchemy configuration for database connection
        # ------------------------------------------------------------------------------------------------------------------------------------
        "SQLALCHEMY_DB_DRIVER"                : env.get     ( 'SQLALCHEMY_DB_DRIVER' ),
        "SQLALCHEMY_DB_HOST"                  : env.get     ( 'SQLALCHEMY_DB_HOST' ),
        "SQLALCHEMY_DB_PORT"                  : env.get     ( 'SQLALCHEMY_DB_PORT' ),
        "SQLALCHEMY_DB_NAME"                  : env.get     ( 'SQLALCHEMY_DB_NAME' ),
        "SQLALCHEMY_DB_USER"                  : env.get     ( 'SQLALCHEMY_DB_USER' ),
        "SQLALCHEMY_DB_PASSWORD"              : env.get     ( 'SQLALCHEMY_DB_PASSWORD' ),
        "SQLALCHEMY_TABLENAME_SUCCESS_MODEL"  : env.get     ( 'SQLALCHEMY_TABLENAME_SUCCESS_MODEL' )
      }
    return {}
