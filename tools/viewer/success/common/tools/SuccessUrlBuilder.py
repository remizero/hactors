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

# Preconditions / Precondiciones


class SuccessUrlBuilder () :
  """
  URL builder for constructing hostnames with subdomain and port.

  Provides a fluent interface for building URLs with subdomain,
  domain, and port components.
  """

  __domain    : str | None       = None
  __port      : str | int | None = None
  __subdomain : str | None       = None


  def __init__ ( self ) -> None :
    """
    Initialize the URL builder with default values.
    """
    self.__subdomain = None
    self.__domain    = None
    self.__port      = None


  def subdomain ( self, value : str | None ) -> "SuccessUrlBuilder" :
    """
    Set the subdomain.

    Args:
      value: Subdomain value or None.

    Returns:
      SuccessUrlBuilder: Self for method chaining.
    """
    self.__subdomain = self._clean_label ( value )
    return self


  def domain ( self, value : str | None ) -> "SuccessUrlBuilder" :
    """
    Set the domain.

    Args:
      value: Domain value or None.

    Returns:
      SuccessUrlBuilder: Self for method chaining.
    """
    self.__domain = self._clean_label ( value )
    return self


  def port ( self, value : str | int | None ) -> "SuccessUrlBuilder" :
    """
    Set the port.

    Args:
      value: Port value as string or int, or None.

    Returns:
      SuccessUrlBuilder: Self for method chaining.
    """
    text        = str ( value ).strip () if value is not None else ""
    self.__port = text if text else None
    return self


  def build ( self ) -> str | None :
    """
    Build the final hostname string.

    Returns:
      str | None: Complete hostname with subdomain and port, or None if no domain is set.
    """
    if not self.__domain :
      return None

    host = self.__domain
    if self.__subdomain :
      host = f"{self.__subdomain}.{host}"

    if self.__port :
      host = f"{host}:{self.__port}"

    return host


  def _clean_label ( self, value : str | None ) -> str | None :
    """
    Clean a label value by stripping whitespace and dots.

    Args:
      value: Label value to clean.

    Returns:
      str | None: Cleaned label or None if empty.
    """
    text = str ( value ).strip () if value is not None else ""
    if not text :
      return None
      
    return text.strip ( "." )
