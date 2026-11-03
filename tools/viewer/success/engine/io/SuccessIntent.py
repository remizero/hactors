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
from abc   import ABC
from abc   import abstractmethod
from flask import Response

# Success Libraries / Librerías Success
from success.engine.context.SuccessResponsePolicy import SuccessResponsePolicy

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessIntent ( ABC ) :
  """
  Abstract base class for output intent executors.

  Defines the interface for executing different types of output
  such as default JSON, redirect, or template render.
  """


  @abstractmethod
  def execute ( self, builtOutput : dict, responsePolicy : SuccessResponsePolicy ) -> Response :
    """
    Execute the intent and return a Flask response.

    Args:
      builtOutput: Built output dictionary.
      responsePolicy: Response policy for configuration.

    Returns:
      Response: Flask response object.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError ()
