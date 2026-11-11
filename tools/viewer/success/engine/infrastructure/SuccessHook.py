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
from abc   import abstractmethod
from types import MappingProxyType

# Success Libraries / Librerías Success
from success.common.base.SuccessClass import SuccessClass
from success.engine.infrastructure.HookDeclaration import HookDeclaration

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessHook ( SuccessClass ) :
  """
  Base class for hook implementations.

  Attributes:
    _bound (bool): Whether the hook has been bound.
    _declaration (MappingProxyType): Hook declaration data.
  """

  _bound       : bool             = False
  _declaration : MappingProxyType = None


  def __init__ ( self, declaration : HookDeclaration | dict = None ) :
    """
    Initialize the hook with an optional declaration.

    Args:
      declaration: HookDeclaration or dict with hook data.
    """
    super ().__init__ ()
    if declaration is not None :
      self.bind ( declaration )


  def bind ( self, declaration : HookDeclaration | dict ) -> "SuccessHook" :
    """
    Inject the hook declaration once.
    After bind, the state becomes immutable.

    Args:
      declaration: HookDeclaration or dict to bind.

    Returns:
      SuccessHook: Self for chaining.

    Raises:
      RuntimeError: If hook is already bound.
      TypeError: If declaration is invalid.
    """
    if self._bound :
      raise RuntimeError ( f"Hook {self.__class__.__name__} is already bound." )

    if isinstance ( declaration, HookDeclaration ) :
      normalized = declaration.asDict ()
    elif isinstance ( declaration, dict ) :
      payload = declaration.get ( "payload", {} )
      if payload is None :
        payload = {}
      if not isinstance ( payload, dict ) :
        raise TypeError ( "Hook declaration payload must be dict." )
      normalized = dict ( declaration )
      normalized [ "payload" ] = MappingProxyType ( dict ( payload ) )
    else :
      raise TypeError ( "Hook declaration must be HookDeclaration or dict." )

    self._declaration = MappingProxyType ( normalized )
    self._bound       = True

    self.onBind ()

    return self


  def onBind ( self ) -> None :
    """
    Optional hook for post-bind internal initialization.
    """
    return


  @property
  def declaration ( self ) -> MappingProxyType :
    """
    Get the hook declaration.

    Returns:
      MappingProxyType: Hook declaration.

    Raises:
      RuntimeError: If hook is not bound.
    """
    if not self._bound or self._declaration is None :
      raise RuntimeError ( f"Hook {self.__class__.__name__} is not bound." )

    return self._declaration


  @property
  def payload ( self ) -> MappingProxyType :
    """
    Get the hook payload.

    Returns:
      MappingProxyType: Hook payload.
    """
    return self.declaration.get ( "payload", MappingProxyType ( {} ) )


  @property
  def action ( self ) -> str :
    """
    Get the hook action string.

    Returns:
      str: Hook action string.
    """
    return str ( self.declaration.get ( "action", "" ) )


  @property
  def when ( self ) -> str :
    """
    Get the hook timing (before/after).

    Returns:
      str: Hook timing.
    """
    return str ( self.declaration.get ( "when", "" ) )


  @abstractmethod
  def execute ( self, context : dict ) -> None :
    """
    Required method that defines hook execution.

    Args:
      context: Execution context dictionary.

    Raises:
      NotImplementedError: Must be implemented by subclasses.
    """
    raise NotImplementedError ( "You must implement the `execute()` method" )
