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
from flask import request

# Success Libraries / Librerías Success
from success.common.base.SuccessClass    import SuccessClass
from success.common.base.SuccessClass    import abstractmethod
from success.engine.models.SuccessSchema import SuccessSchema
from success.common.tools.SuccessHttp    import SuccessHttp

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessInput ( SuccessClass ) :
  """
  Base input handler for parsing and validating HTTP request data.

  Provides abstract methods for parsing request data based on
  HTTP method and validating against schemas.

  Attributes:
    _errors (list): List of validation errors.
    _method: HTTP method.
    _rawData (dict): Raw request data.
    _schema (SuccessSchema): Validation schema.
    _validatedData (dict): Validated data.
  """

  _errors        : list          = None
  _method                        = None
  _rawData       : dict          = None
  _schema        : SuccessSchema = None
  _validatedData : dict          = None


  def __init__ ( self ) -> None :
    """
    Initialize the input handler.
    """
    super ().__init__ ()
    self._errors        = []
    self._rawData       = {}
    self._validatedData = {}


  def _parseInput ( self ) -> None :
    """
    Parse input data based on HTTP method.

    Extracts data from query params, JSON body, or form data
    depending on the request method.
    """
    if SuccessHttp.isGet () :
      self._rawData = request.args.to_dict ()

    elif SuccessHttp.isPost () or SuccessHttp.isPut () or SuccessHttp.isPatch () :
      if request.is_json :
        self._rawData = request.get_json ( silent = True ) or {}

      else :
        self._rawData = request.form.to_dict ()

    elif SuccessHttp.isDelete () :
      self._rawData = request.args.to_dict ()
      if request.is_json :
        self._rawData.update ( request.get_json ( silent = True ) or {} )

    else :
      self._rawData = {}


  def get ( self, key, default = None ) :
    """
    Get a value from raw data.

    Args:
      key: Data key.
      default: Default value if key not found.

    Returns:
      The value or default.
    """
    return self._rawData.get ( key, default )


  @abstractmethod
  def parse ( self ) :
    """
    Parse the input data.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    pass


  @abstractmethod
  def validate ( self ) :
    """
    Validate the parsed data.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    pass
