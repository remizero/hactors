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
from abc import abstractmethod

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass
from success.core.SuccessBuildContext import SuccessBuildContext

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
ENDPOINT_ALLOWED_ARGS = {
  "rule",
  "endpoint",
  "view_func",
  "provide_automatic__options",
  "options",
}


class SuccessEndpointOptionsBuilder ( SuccessClass ) :
  """
  Abstract base class for endpoint options builders.

  Defines the interface for building endpoint configuration
  dictionaries for different protocol types.
  """

  _buildContext : SuccessBuildContext = None
  _options      : dict                = None


  def __init__ ( self, buildContext : SuccessBuildContext, options : dict ) -> None :
    """
    Initialize the endpoint options builder.

    Args:
      buildContext: Build context with application configuration.
      options: Dictionary with endpoint configuration.
    """
    super ().__init__ ()
    self._buildContext = buildContext
    self._options      = options


  @abstractmethod
  def build ( self ) -> dict :
    """
    Build and return the endpoint configuration dictionary.

    Returns:
      dict: Configuration dictionary for the endpoint.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError ()
