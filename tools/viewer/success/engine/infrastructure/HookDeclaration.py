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

from dataclasses import dataclass
from types import MappingProxyType

from success.engine.infrastructure.HookAction import HookAction


@dataclass ( frozen = True )
class HookDeclaration :
  """
  Typed and immutable hook declaration.

  Attributes:
    name (str): Hook name.
    callback (str): Callback path (module.Class.method).
    when (str): Execution timing ('before' or 'after').
    action (HookAction): Hook action to match.
    payload (MappingProxyType): Hook payload data.
    enabled (bool): Whether the hook is enabled.
    priority (int): Hook priority (lower = higher priority).
  """

  name     : str
  callback : str
  when     : str
  action   : HookAction
  payload  : MappingProxyType
  enabled  : bool = True
  priority : int  = 100


  @staticmethod
  def fromDict ( data : dict, defaultName : str = "unnamed_hook" ) -> "HookDeclaration" :
    """
    Create a HookDeclaration from a dictionary.

    Args:
      data: Dictionary with hook declaration data.
      defaultName: Default name if not provided.

    Returns:
      HookDeclaration: Created declaration.

    Raises:
      TypeError: If data is not a dict or payload is invalid.
      ValueError: If when is invalid or callback is missing.
    """
    if not isinstance ( data, dict ) :
      raise TypeError ( "Hook declaration must be dict." )

    name = str ( data.get ( "name", defaultName ) ).strip () or defaultName
    callback = str ( data.get ( "callback", "" ) ).strip ()
    when = str ( data.get ( "when", "" ) ).strip ().lower ()
    actionRaw = str ( data.get ( "action", "" ) ).strip ()
    enabled = bool ( data.get ( "enabled", True ) )
    priority = int ( data.get ( "priority", 100 ) )

    payload = data.get ( "payload", {} )
    if payload is None :
      payload = {}
    if not isinstance ( payload, dict ) :
      raise TypeError ( f"[{name}] Payload must be dict." )

    if when not in [ "before", "after" ] :
      raise ValueError ( f"[{name}] Invalid when '{when}'. Must be 'before' or 'after'." )

    if not callback :
      raise ValueError ( f"[{name}] Callback is required." )

    action = HookAction.fromString ( actionRaw )

    return HookDeclaration (
      name     = name,
      callback = callback,
      when     = when,
      action   = action,
      payload  = MappingProxyType ( dict ( payload ) ),
      enabled  = enabled,
      priority = priority
    )


  def asDict ( self ) -> dict :
    """
    Convert the declaration to a dictionary.

    Returns:
      dict: Dictionary representation of the declaration.
    """
    return {
      "name"     : self.name,
      "callback" : self.callback,
      "when"     : self.when,
      "action"   : self.action.asString (),
      "payload"  : self.payload,
      "enabled"  : self.enabled,
      "priority" : self.priority
    }

