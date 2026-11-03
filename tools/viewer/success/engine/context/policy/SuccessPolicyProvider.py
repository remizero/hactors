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

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessPolicyProvider ( SuccessClass ) :
  """
  Abstract base class for policy providers.

  Defines the interface for all policy providers that evaluate
  authorization and security policies in the Success framework.
  """


  def __init__ ( self ) -> None :
    """
    Initialize the policy provider.
    """
    super ().__init__ ()


  def supports ( self, spec : dict, context : dict ) -> bool :
    """
    Check if this provider supports the given policy specification.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      bool: True if this provider can evaluate the specification.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError ()


  def evaluate ( self, spec : dict, context : dict ) -> dict :
    """
    Evaluate the policy specification against the context.

    Args:
      spec: Policy specification dictionary.
      context: Evaluation context dictionary.

    Returns:
      dict: Evaluation result with 'allowed', 'status', 'message', etc.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError ()


  def allow ( self ) -> dict :
    """
    Return an allow result.

    Returns:
      dict: Dictionary indicating access is allowed.
    """
    return {
      "allowed" : True,
      "status"  : 200,
      "message" : "OK",
      "error"   : None,
      "code"    : None,
      "type"    : None
    }


  def deny ( self, status : int, message : str, code : str, _type : str = "authorization", error = None ) -> dict :
    """
    Return a deny result.

    Args:
      status: HTTP status code for the denial.
      message: Human-readable denial message.
      code: Machine-readable error code.
      _type: Type of denial (default: 'authorization').
      error: Additional error details (optional).

    Returns:
      dict: Dictionary indicating access is denied.
    """
    return {
      "allowed" : False,
      "status"  : status,
      "message" : message,
      "error"   : error or message,
      "code"    : code,
      "type"    : _type
    }
