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
import ast
import re

# Success Libraries / Librerías Success
from success.common.SuccessDebug import SuccessDebug

# Preconditions / Precondiciones


class SuccessStrings () :
  """
  String manipulation utilities for the Success framework.

  Provides static methods for string conversion, case transformation,
  and singular/plural conversion.
  """

  tab       = '  '
  lineBreak = '\n'


  @staticmethod
  def cleanStdout ( string : str ) -> str :
    """
    Clean a stdout string by removing the last character and decoding.

    Args:
      string: String to clean.

    Returns:
      str: Cleaned UTF-8 decoded string.
    """
    string = string [ 0:len ( string ) - 1:1 ]

    return string.decode ( "utf-8" )


  @staticmethod
  def sliceindex ( string : str ) -> str :
    """
    Find the index of the first alphabetic character in a string.

    Args:
      string: String to search.

    Returns:
      str: Index of the first alphabetic character.
    """
    i = 0
    for c in string :
      if c.isalpha () :
        i = i + 1
        return i
      i = i + 1


  @staticmethod
  def snakeCase ( string : str ) -> str :
    """
    Convert a string to snake_case.

    Args:
      string: String to convert.

    Returns:
      str: Snake case formatted string.
    """
    case = re.sub ( '(.)([A-Z][a-z]+)', r'\1_\2', string )

    return re.sub ( '([a-z0-9])([A-Z])', r'\1_\2', case ).lower ()


  @staticmethod
  def CamelCase ( string : str ) -> str :
    """
    Convert a string to CamelCase.

    Args:
      string: String to convert.

    Returns:
      str: CamelCase formatted string.
    """
    # split underscore using split
    temp = string.split ( '_' )
    # joining result
    res = temp [ 0 ] + ''.join ( ele.title () for ele in temp [ 1 : ] )

    return str ( res )


  @staticmethod
  def lowerFirst ( string : str ) -> str :
    """
    Convert the first character of a string to lowercase.

    Args:
      string: String to convert.

    Returns:
      str: String with first character lowercased.
    """
    i = SuccessStrings.sliceindex ( string )

    return string [ : i ].lower () + string [ i : ]


  @staticmethod
  def toPlural ( string : str ) -> str :
    """
    Get the plural form of a string.

    Args:
      string: Singular string to convert.

    Returns:
      str: Plural form of the string.
    """
    if string [ -1 ] == 'y' :
      return string [ 0:-1 ] + 'ies'

    if string [ -1 ] == 's' :
      return string [ 0:-1 ] + 'ses'

    if string [ -1 ] == 'x' :
      return string [ 0:-1 ] + 'xes'

    if string [ -1 ] == 'h' and string [ -2 ] == 'c' :
      return string [ 0:-1 ] + 'hes'

    return string + 's'


  @staticmethod
  def toSingular ( string : str ) -> str :
    """
    Get the singular form of a plural string.

    Args:
      string: Plural string to convert.

    Returns:
      str: Singular form of the string.
    """
    if string [ len ( string ) - 3 : ] == 'ies' :
      return string [ 0 : -3 ] + 'y'

    if string [ len ( string ) - 3 : ] == 'ses' :
      return string [ 0 : -3 ] + 's'

    if string [ len ( string ) - 3 : ] == 'xes' :
      return string [ 0 : -3 ] + 'x'

    if string [ len ( string ) - 3 : ] == 'hes' :
      return string [ 0 : -3 ] + 'ch'

    if string [ -1 ] == 's' and string [ -2 ] in [ 'e', 'g', 'k', 'l', 'm', 'n', 'p', 'r', 't' ] :
      return string [ 0 : -1 ]

    return string


  @staticmethod
  def toList ( string : str, token : str = '' ) -> list :
    """
    Convert a string to a list by stripping tokens.

    Args:
      string: String to convert.
      token: Token to strip (default: '').

    Returns:
      list: Stripped string as list.
    """

    return string.strip ( token )


  @staticmethod
  def upperFirst ( string : str ) -> str :
    """
    Convert the first character of a string to uppercase.

    Args:
      string: String to convert.

    Returns:
      str: String with first character uppercased.
    """
    i = SuccessStrings.sliceindex ( string )
    
    return string [ : i ].upper () + string [ i : ]
