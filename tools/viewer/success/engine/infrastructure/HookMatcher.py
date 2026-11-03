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
from typing import Iterable
from typing import List
from typing import Tuple

# Application Libraries / Librerías de la Aplicación
from success.engine.infrastructure.HookAction import HookAction


class HookMatcher () :
  """
  Matching utilities for hook actions.

  Main strategy:
    - Emitted action -> ancestor chain (from most specific to most general)
    - Declared hook matches if it coincides with any of those ancestors
  """


  @staticmethod
  def parse ( action : HookAction | str ) -> HookAction :
    """
    Parse an action from HookAction or string.

    Args:
      action: HookAction or string to parse.

    Returns:
      HookAction: Parsed action.
    """
    return action if isinstance ( action, HookAction ) else HookAction.fromString ( action )


  @staticmethod
  def hierarchy ( emittedAction : HookAction | str ) -> Tuple [ HookAction, ... ] :
    """
    Get the hierarchy of an emitted action.

    Args:
      emittedAction: Action to get hierarchy for.

    Returns:
      Tuple[HookAction, ...]: Tuple of ancestor actions.
    """
    emitted = HookMatcher.parse ( emittedAction )

    return emitted.ancestors ( includeSelf = True, minDepth = 1 )


  @staticmethod
  def hierarchyStrings ( emittedAction : HookAction | str ) -> Tuple [ str, ... ] :
    """
    Get the hierarchy as strings.

    Args:
      emittedAction: Action to get hierarchy for.

    Returns:
      Tuple[str, ...]: Tuple of ancestor action strings.
    """
    return tuple ( item.asString () for item in HookMatcher.hierarchy ( emittedAction ) )


  @staticmethod
  def matches ( declaredAction : HookAction | str, emittedAction : HookAction | str ) -> bool :
    """
    Check if a declared action matches an emitted action.

    Args:
      declaredAction: Declared hook action.
      emittedAction: Emitted action to match against.

    Returns:
      bool: True if actions match.
    """
    declared         = HookMatcher.parse ( declaredAction )
    emittedHierarchy = HookMatcher.hierarchy ( emittedAction )

    return any ( declared == candidate for candidate in emittedHierarchy )


  @staticmethod
  def filterMatches ( declaredActions : Iterable [ HookAction | str ], emittedAction : HookAction | str ) -> List [ HookAction ] :
    """
    Filter declared actions that match an emitted action.

    Args:
      declaredActions: Iterable of declared actions.
      emittedAction: Emitted action to match against.

    Returns:
      List[HookAction]: List of matching actions, sorted by specificity.
    """
    declared         = [ HookMatcher.parse ( action ) for action in declaredActions ]
    emittedHierarchy = HookMatcher.hierarchy ( emittedAction )
    emittedSet       = set ( emittedHierarchy )
    matches          = [ action for action in declared if action in emittedSet ]
    # More specific first
    matches.sort ( key = lambda item: item.depth, reverse = True )

    return matches

