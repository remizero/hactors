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
from dataclasses import dataclass
from typing      import Iterable
from typing      import Tuple
import re

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones
_SEGMENT_PATTERN = re.compile ( r"^[a-z][a-z0-9_]*$" )


@dataclass ( frozen = True )
class HookAction () :
  """
  Immutable value object for representing hook actions.

  Semantic format:
    verb:domain[:component[:stage[:detail...]]]

  Attributes:
    _segments (Tuple[str, ...]): Tuple of action segments.
  """

  _segments : Tuple [ str, ... ]


  def __init__ ( self, *segments : str ) -> None :
    """
    Initialize HookAction with normalized segments.

    Args:
      *segments: Variable number of segment strings.
    """
    normalized = self._normalizeSegments ( segments, minSegments = 2 )
    object.__setattr__ ( self, "_segments", normalized )


  @staticmethod
  def fromString ( action : str ) -> "HookAction" :
    """
    Create a HookAction from a colon-separated string.

    Args:
      action: Colon-separated action string.

    Returns:
      HookAction: Parsed action object.

    Raises:
      TypeError: If action is not a string.
      ValueError: If action is empty.
    """
    if not isinstance ( action, str ) :
      raise TypeError ( "action must be str." )

    raw = action.strip ()
    if not raw :
      raise ValueError ( "action cannot be empty." )

    parts = tuple ( part.strip () for part in raw.split ( ":" ) )
    return HookAction ( *parts )


  @property
  def segments ( self ) -> Tuple [ str, ... ] :
    """
    Get the action segments.

    Returns:
      Tuple[str, ...]: Tuple of segment strings.
    """
    return self._segments


  @property
  def depth ( self ) -> int :
    """
    Get the depth (number of segments) of the action.

    Returns:
      int: Number of segments.
    """
    return len ( self._segments )


  @property
  def verb ( self ) -> str :
    """
    Get the verb segment (first segment).

    Returns:
      str: The verb segment.
    """
    return self._segments [ 0 ]


  @property
  def domain ( self ) -> str :
    """
    Get the domain segment (second segment).

    Returns:
      str: The domain segment.

    Raises:
      ValueError: If action has less than 2 segments.
    """
    if self.depth < 2 :
      raise ValueError ( "HookAction requires at least verb and domain." )
    return self._segments [ 1 ]


  def child ( self, *segments : str ) -> "HookAction" :
    """
    Create a child action by appending segments.

    Args:
      *segments: Segments to append.

    Returns:
      HookAction: New child action.
    """
    extra = self._normalizeSegments ( segments, minSegments = 1 )
    return HookAction ( *( self._segments + extra ) )


  def parent ( self ) -> "HookAction" :
    """
    Get the parent action (remove last segment).

    Returns:
      HookAction: Parent action or self if depth <= 1.
    """
    if self.depth <= 1 :
      return self
    return HookAction ( *self._segments [ : -1 ] )


  def ancestors ( self, includeSelf : bool = True, minDepth : int = 1 ) -> Tuple [ "HookAction", ... ] :
    """
    Return the hierarchical chain from most specific to most general.

    Args:
      includeSelf: Whether to include self in the chain.
      minDepth: Minimum depth to include.

    Returns:
      Tuple[HookAction, ...]: Tuple of ancestor actions.

    Raises:
      ValueError: If minDepth is less than 1.
    """
    if minDepth < 1 :
      raise ValueError ( "minDepth must be >= 1." )

    startDepth = self.depth if includeSelf else self.depth - 1
    chain = []
    for depth in range ( startDepth, minDepth - 1, -1 ) :
      chain.append ( HookAction ( *self._segments [ : depth ] ) )
    return tuple ( chain )


  def asString ( self ) -> str :
    """
    Convert the action to a colon-separated string.

    Returns:
      str: Colon-separated action string.
    """
    return ":".join ( self._segments )


  def startsWith ( self, other : "HookAction | str" ) -> bool :
    """
    Check if this action starts with another action.

    Args:
      other: Action or string to compare.

    Returns:
      bool: True if this action starts with the other.
    """
    target = other if isinstance ( other, HookAction ) else HookAction.fromString ( other )
    if target.depth > self.depth :
      return False
    return self._segments [ : target.depth ] == target.segments


  def __str__ ( self ) -> str :
    """
    Return string representation of the action.

    Returns:
      str: Colon-separated action string.
    """
    return self.asString ()


  def __repr__ ( self ) -> str :
    """
    Return repr representation of the action.

    Returns:
      str: Repr string.
    """
    return f"HookAction('{self.asString ()}')"


  @staticmethod
  def _normalizeSegments ( segments : Iterable [ str ], minSegments : int = 2 ) -> Tuple [ str, ... ] :
    """
    Normalize and validate segments.

    Args:
      segments: Iterable of segment strings.
      minSegments: Minimum number of segments required.

    Returns:
      Tuple[str, ...]: Normalized tuple of segments.

    Raises:
      TypeError: If a segment is not a string.
      ValueError: If a segment is empty or invalid.
    """
    normalized = []
    for idx, segment in enumerate ( segments ) :
      if not isinstance ( segment, str ) :
        raise TypeError ( f"Segment at position {idx} must be str." )

      value = segment.strip ().lower ()
      if not value :
        raise ValueError ( f"Segment at position {idx} cannot be empty." )

      if not _SEGMENT_PATTERN.match ( value ) :
        raise ValueError (
          f"Invalid segment '{segment}'. "
          "Use lowercase, numbers and underscore; must start with letter."
        )

      normalized.append ( value )

    if len ( normalized ) < minSegments :
      if minSegments == 2 :
        raise ValueError ( "HookAction requires at least two segments: verb:domain." )
      raise ValueError ( f"HookAction requires at least {minSegments} segment(s)." )

    return tuple ( normalized )
