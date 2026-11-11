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

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessAppValidationError ( Exception ) :
  """
  Exception raised when application validation fails.

  Used to indicate errors in the structure or configuration
  of a Success application during the validation process.
  """
  pass


class SuccessAppValidator ( SuccessClass ) :
  """
  Validator for Success application structure.

  Verifies that an application has the required directory structure and
  files for the Success framework.

  Purpose:
  ----------
  SuccessAppValidator is responsible for validating:
  - Existence of application base directory
  - Presence of .env file
  - Existence of blueprints.json and endpoints.json
  - Presence of modules/ and services/ directories
  - Python content in modules/ and services/

  Required structure:
  ---------------------
  apps/
  └── myapp/
      ├── .env              # Required
      ├── blueprints.json   # Required
      ├── endpoints.json    # Required
      ├── modules/          # Required with .py content
      └── services/         # Required with .py content

  Usage:
  ------
  validator = SuccessAppValidator('myapp', '/apps/myapp')
  validator.validate()  # Raises SuccessAppValidationError if fails

  Attributes:
      __appName (str): Name of the application to validate.
      __appPath (str): Absolute path to application directory.

  Raises:
      SuccessAppValidationError: If any validation fails.

  Note:
    - All validations are mandatory
    - Executed in order: basePath, env, modules, services
  """

  __appName : str = None
  __appPath : str = None


  def __init__ ( self, appName : str, appPath : str ) -> None :
    """
    Initialize the application validator.

    Args:
        appName: Name of the application to validate.
        appPath: Absolute path to the application directory.
    """
    super ().__init__ ()
    self.__appName = appName
    self.__appPath = appPath


  def validate ( self ) -> None :
    """
    Execute all application validations.

    Validates in order: basePath, env, modules, services.
    If all pass, logs a success message.

    Raises:
        SuccessAppValidationError: If any validation fails.
    """
    self._logger.log ( f"Iniciando validación de la aplicación '{self.__appName}'...", "INFO" )

    self._validateBasePath ()
    self._validateEnv ()
    self._validateModules ()
    self._validateServices ()

    self._logger.log ( f"Aplicación '{self.__appName}' validada correctamente.", "INFO" )


  # ---------- validations ----------

  def _validateBasePath ( self ) -> None :
    """
    Validate that the application base directory exists.

    Raises:
        SuccessAppValidationError: If the directory does not exist.
    """
    if not os.path.isdir ( self.__appPath ) :
      raise SuccessAppValidationError ( f"La ruta de la aplicación '{self.__appName}' no existe." )


  def _validateBlueprints ( self ) -> None :
    """
    Validate the existence of the blueprints.json file.

    Raises:
        SuccessAppValidationError: If the file does not exist.
    """
    self.__validateFile ( "blueprints.json" )


  def _validateEndpoints ( self ) -> None :
    """
    Validate the existence of the endpoints.json file.

    Raises:
        SuccessAppValidationError: If the file does not exist.
    """
    self.__validateFile ( "endpoints.json" )


  def _validateEnv ( self ) -> None :
    """
    Validate the existence of the .env configuration file.

    Raises:
        SuccessAppValidationError: If the file does not exist.
    """
    self.__validateFile ( ".env" )


  def _validateExtensions ( self ) -> None :
    """
    Validate the existence of the extensions.json file.

    Raises:
        SuccessAppValidationError: If the file does not exist.
    """
    self.__validateFile ( "extensions.json" )


  def _validateHooks ( self ) -> None :
    """
    Validate the existence of the hooks.json file.

    Raises:
        SuccessAppValidationError: If the file does not exist.
    """
    self.__validateFile ( "hooks.json" )


  def __validateFile ( self, fileName : str ) -> None :
    """
    Validate the existence of a specific file in the application directory.

    Args:
        fileName: Name of the file to validate.

    Raises:
        SuccessAppValidationError: If the file does not exist.
    """
    filePath = os.path.join ( self.__appPath, fileName )
    if not os.path.isfile ( filePath ) :
      raise SuccessAppValidationError ( f"La aplicación '{self.__appName}' no contiene archivo '{fileName}'")


  def _validateModules ( self ) -> None :
    """
    Validate the existence and content of the modules/ directory.

    Verifies that the modules/ directory exists and contains at least
    one Python file (excluding __init__.py).

    Raises:
        SuccessAppValidationError: If the directory does not exist or is empty.
    """
    modulesPath = os.path.join ( self.__appPath, "modules" )
    if not os.path.isdir ( modulesPath ) :
      raise SuccessAppValidationError ( f"La aplicación '{self.__appName}' no define el directorio 'modules'" )

    if not self._hasPythonContent ( modulesPath ) :
      raise SuccessAppValidationError ( f"El directorio 'modules' de '{self.__appName}' está vacío" )


  def _validateServices ( self ) -> None :
    """
    Validate the existence and content of the services/ directory.

    Verifies that the services/ directory exists and contains at least
    one Python file (excluding __init__.py).

    Raises:
        SuccessAppValidationError: If the directory does not exist or is empty.
    """
    servicesPath = os.path.join ( self.__appPath, "services" )
    if not os.path.isdir ( servicesPath ) :
      raise SuccessAppValidationError ( f"La aplicación '{self.__appName}' no define el directorio 'services'" )

    if not self._hasPythonContent ( servicesPath ) :
      raise SuccessAppValidationError ( f"La aplicación '{self.__appName}' no expone ningún servicio" )


  # ---------- helpers ----------

  def _hasPythonContent ( self, path : str ) -> bool :
    """
    Check if a directory contains Python files.

    Recursively traverses the directory looking for .py files
    (excluding __init__.py).

    Args:
        path: Directory path to check.

    Returns:
        bool: True if at least one .py file is found, False otherwise.
    """
    for root, _, files in os.walk ( path ) :
      for file in files :
        if file.endswith ( ".py") and file != "__init__.py" :
          return True
    return False


  # ---------- static utility methods ----------

  @staticmethod
  def isValidAppDir ( appPath : str ) -> bool :
    """
    Check if a directory contains a valid Success application.

    Validates the basic required structure without raising exceptions:
    - Directory exists
    - Contains .env
    - Contains modules/ with Python content
    - Contains services/ with Python content

    Args:
        appPath: Absolute path to the application directory.

    Returns:
        bool: True if the directory is a valid Success app, False otherwise.

    Usage:
        if SuccessAppValidator.isValidAppDir('/apps/myapp'):
            # It's a valid app
    """
    if not os.path.isdir ( appPath ) :
      return False

    # Verificar archivos requeridos
    requiredFiles = [ ".env" ]
    for fileName in requiredFiles :
      if not os.path.isfile ( os.path.join ( appPath, fileName ) ) :
        return False

    # Verificar directorio modules/ con contenido Python
    modulesPath = os.path.join ( appPath, "modules" )
    if not os.path.isdir ( modulesPath ) :
      return False

    if not SuccessAppValidator._checkPythonContent ( modulesPath ) :
      return False

    # Verificar directorio services/ con contenido Python
    servicesPath = os.path.join ( appPath, "services" )
    if not os.path.isdir ( servicesPath ) :
      return False

    if not SuccessAppValidator._checkPythonContent ( servicesPath ) :
      return False

    return True


  @staticmethod
  def hasFactoryOrInstance ( appPath : str ) -> bool :
    """
    Check if an application has a Flask factory or instance.

    Searches the application directory for:
    - create.py file with createApp() or create() function
    - app.py file with 'app' or 'application' instance
    - __init__.py file with 'app' or 'application' instance

    Args:
        appPath: Absolute path to the application directory.

    Returns:
        bool: True if a factory or instance is found, False otherwise.

    Note:
        This validation is optional and used for compatibility with
        legacy applications that do not follow the standard structure.
    """
    if not os.path.isdir ( appPath ) :
      return False

    # Buscar create.py con función factory
    createPath = os.path.join ( appPath, "create.py" )
    if os.path.isfile ( createPath ) :
      try :
        with open ( createPath, 'r', encoding = 'utf-8' ) as f :
          content = f.read ()
          if 'def createApp' in content or 'def create (' in content :
            return True
      except Exception :
        pass

    # Buscar app.py con instancia
    appPathFile = os.path.join ( appPath, "app.py" )
    if os.path.isfile ( appPathFile ) :
      try :
        with open ( appPathFile, 'r', encoding = 'utf-8' ) as f :
          content = f.read ()
          if 'app =' in content or 'application =' in content :
            return True
      except Exception :
        pass

    # Buscar __init__.py con instancia
    initPath = os.path.join ( appPath, "__init__.py" )
    if os.path.isfile ( initPath ) :
      try :
        with open ( initPath, 'r', encoding = 'utf-8' ) as f :
          content = f.read ()
          if 'app =' in content or 'application =' in content :
            return True
      except Exception :
        pass

    return False


  @staticmethod
  def _checkPythonContent ( path : str ) -> bool :
    """
    Check if a directory contains Python files.

    Internal static method that recursively traverses the directory
    looking for .py files (excluding __init__.py).

    Args:
        path: Directory path to check.

    Returns:
        bool: True if at least one .py file is found, False otherwise.
    """
    for root, _, files in os.walk ( path ) :
      for file in files :
        if file.endswith ( ".py") and file != "__init__.py" :
          return True
    return False
