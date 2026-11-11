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
from flask  import json
from flask  import request
from flask  import Response
from typing import Any

# Success Libraries / Librerías Success
from success.common.exceptions.JsonRequestException   import JsonRequestException
from success.common.exceptions.RequestMethodException import RequestMethodException

# Preconditions / Precondiciones


class SuccessHttp () :
  """
  HTTP utilities for the Success framework.

  Provides static methods for working with HTTP requests, responses,
  and method checking.
  """


  @staticmethod
  def contentTypeHtml () -> dict :
    """
    Get Content-Type header for HTML responses.

    Returns:
      dict: Dictionary with Content-Type header set to text/html.
    """
    return { "Content-Type": "text/html" }


  @staticmethod
  def isDelete () -> bool :
    """
    Check if the current request method is DELETE.

    Returns:
      bool: True if the request method is DELETE.
    """
    return SuccessHttp.__isMethod ( 'DELETE' )


  @staticmethod
  def isGet () -> bool :
    """
    Check if the current request method is GET.

    Returns:
      bool: True if the request method is GET.
    """
    return SuccessHttp.__isMethod ( 'GET' )


  @staticmethod
  def isPatch () -> bool :
    """
    Check if the current request method is PATCH.

    Returns:
      bool: True if the request method is PATCH.
    """
    return SuccessHttp.__isMethod ( 'PATCH' )


  @staticmethod
  def isPost () -> bool :
    """
    Check if the current request method is POST.

    Returns:
      bool: True if the request method is POST.
    """
    return SuccessHttp.__isMethod ( 'POST' )


  @staticmethod
  def isPut () -> bool :
    """
    Check if the current request method is PUT.

    Returns:
      bool: True if the request method is PUT.
    """
    return SuccessHttp.__isMethod ( 'PUT' )


  @staticmethod
  def isMethod ( method : str ) -> bool :
    """
    Check if the current request method matches the specified method.

    Args:
      method: HTTP method to check (e.g., 'GET', 'POST').

    Returns:
      bool: True if the request method matches.
    """
    return request.method == method


  @staticmethod
  def __isMethod ( method : str ) -> bool :
    """
    Check if the current request method matches the specified method.

    Args:
      method: HTTP method to check.

    Returns:
      bool: True if the request method matches.
    """
    return request.method == method


  @staticmethod
  def requestIsJson () -> bool :
    """
    Check if the request content type is JSON.

    Returns:
      bool: True if the request is JSON.

    Raises:
      JsonRequestException: If the request is not JSON.
    """
    if request.is_json :
      return True

    raise JsonRequestException ()


  @staticmethod
  def response ( data : Any, status : int ) -> Response :
    """
    Create a JSON response.

    Args:
      data: Data to serialize as JSON.
      status: HTTP status code.

    Returns:
      Response: Flask Response object with JSON content.
    """
    return Response (
      response = json.dumps ( data ),
      status   = status,
      mimetype = 'application/json'
    )
