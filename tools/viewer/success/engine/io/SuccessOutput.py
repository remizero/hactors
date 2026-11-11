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
from success.common.base.SuccessClass             import SuccessClass
from success.common.tools.SuccessStructs          import SuccessStructs
from success.common.types.SuccessPayloadSource    import SuccessPayloadSource
from success.common.types.SuccessProtocol         import SuccessProtocol
from success.engine.io.DefaultIntent              import DefaultIntent
from success.engine.io.RedirectIntent             import RedirectIntent
from success.engine.io.RenderIntent               import RenderIntent
from success.engine.io.SuccessOutputModelFactory  import SuccessOutputModelFactory
from success.engine.io.SuccessOutputModelContract import SuccessOutputModelContract
from success.engine.io.SuccessIntent              import SuccessIntent
from success.engine.io.SuccessActionOutputSpec    import SuccessActionOutputSpec

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessOutput ( SuccessClass ) :
  """
  Output handler for presenting and normalizing response data.

  Coordinates output model selection, canonical normalization,
  and output building for different response types.

  Attributes:
    _canonical (dict): Canonical output format.
    _intent (SuccessIntent): Intent executor.
    _outputModel (SuccessOutputModelContract): Output model.
  """

  _canonical   : dict                       = None
  _intent      : SuccessIntent              = None
  _outputModel : SuccessOutputModelContract = None


  def __init__ ( self ) -> None :
    """
    Initialize the output handler.
    """
    super ().__init__ ()


  def getIntent ( self ) -> SuccessIntent :
    """
    Get the intent executor.

    Returns:
      SuccessIntent: Intent executor.
    """
    return self._intent


  def presenter ( self, payload, source : SuccessPayloadSource, outputSpec : SuccessActionOutputSpec ) -> "SuccessOutput" :
    """
    Set up the presenter with payload and source.

    Args:
      payload: Raw payload data.
      source: Payload source (INPUT or CONTROLLER).

    Returns:
      SuccessOutput: Self for chaining.

    Raises:
      TypeError: If output model is invalid.
    """
    self._canonical = self.normalize ( payload, source = source )

    if not self._outputModel :
      self._outputModel = SuccessOutputModelFactory.create ( self._canonical.get ( "kind", "success" ), outputSpec.protocol )

    if self._outputModel and not isinstance ( self._outputModel, SuccessOutputModelContract ) :
      raise TypeError ( "Invalid output model: must inherit from SuccessOutputModelContract" )

    self._resolve_intent ( outputSpec )

    return self


  def _resolve_intent ( self, outputSpec : SuccessActionOutputSpec ) -> "SuccessOutput" :
    """
    Resolve and assign an intent lazily using canonical payload and protocol.

    Resolution order:
      1) Keep existing explicit intent if already set.
      2) Use payload explicit intent ('render' | 'redirect' | 'default').
      3) Apply protocol defaults.

    Args:
      protocol: Current action protocol.

    Returns:
      SuccessOutput: Self for chaining.
    """
    if self._intent :
      if not isinstance ( self._intent, SuccessIntent ) :
        raise TypeError ( "Invalid intent: must inherit from SuccessIntent" )
      return self

    if outputSpec.protocol == SuccessProtocol.RESTFUL :
      self._intent = DefaultIntent ()
      return self

    if outputSpec.protocol == SuccessProtocol.VIEW :
      canonical       = self._canonical if isinstance ( self._canonical, dict ) else {}
      hasError        = canonical.get ( "success" ) is False or canonical.get ( "kind" ) in ( "input_error", "controller_error" )
      redirectTarget  = outputSpec.redirect_to or outputSpec.fallback_redirect or outputSpec.redirect
      template        = outputSpec.template

      if hasError and redirectTarget :
        self._intent = RedirectIntent ( str ( redirectTarget ) )
      elif template :
        self._intent = RenderIntent ( str ( template ) )
      elif redirectTarget :
        self._intent = RedirectIntent ( str ( redirectTarget ) )
      else :
        self._intent = DefaultIntent ()
      return self

    self._intent = DefaultIntent ()
    return self


  def normalize ( self, raw, *, source : SuccessPayloadSource ) -> dict :
    """
    Convert any raw payload to CanonicalOutput format.

    Args:
      raw: Raw payload data.
      source: Payload source ("input" or "controller").

    Returns:
      dict: Normalized canonical output.
    """
    canonical = SuccessStructs.successCanonicalOutput ()

    # 1) Input error (e.g., Input object with _errors)
    if source == SuccessPayloadSource.INPUT :
      errors = getattr ( raw, "_errors", None ) or []
      if errors :
        canonical [ "kind" ]    = "input_error"
        canonical [ "success" ] = False
        canonical [ "status" ]  = 400
        canonical [ "message" ] = "Validation error"
        canonical [ "error" ]   = {
            "type"   : "input",
            "code"   : "INPUT_VALIDATION_ERROR",
            "detail" : "; ".join ( errors ),
        }
        return canonical

      # Valid input
      canonical [ "data" ] = getattr ( raw, "_validatedData", {} )
      return canonical

    # 2) Controller response
    if source == SuccessPayloadSource.CONTROLLER :
        # Explicit error case in raw controller dict
        if isinstance ( raw, dict ) and ( "error" in raw or raw.get ( "success" ) is False ) :
            canonical [ "kind" ]    = "controller_error"
            canonical [ "success" ] = False
            canonical [ "status" ]  = raw.get("status", 500)
            canonical [ "message" ] = raw.get("message", "Controller error")
            canonical [ "intent" ]  = raw.get ( "intent", None )
            canonical [ "view" ]    = raw.get ( "view", None )
            canonical [ "redirect_to" ] = raw.get ( "redirect_to", None )
            canonical [ "error" ]   = {
              "type"   : raw.get ( "type", "controller" ),
              "code"   : raw.get ( "code", "CONTROLLER_ERROR" ),
              "detail" : raw.get ( "error", raw.get ( "detail", "Unspecified error" ) ),
            }
            return canonical

        # Controller success case (resultset, dict, list, etc.)
        canonical [ "status" ]  = raw.get ( "status", 200 ) if isinstance ( raw, dict ) else 200
        canonical [ "message" ] = raw.get ( "message", "Operation successful" ) if isinstance ( raw, dict ) else "Operation successful"

        if isinstance ( raw, dict ) :
          canonical [ "intent" ]      = raw.get ( "intent", None )
          canonical [ "view" ]        = raw.get ( "view", None )
          canonical [ "redirect_to" ] = raw.get ( "redirect_to", None )
          # Convention: prioritize body/data, otherwise entire dict
          canonical [ "data" ] = raw.get ( "body", raw.get ( "data", raw ) )
        else :
          canonical [ "data" ] = raw

        return canonical

    # 3) Unknown source
    canonical [ "kind" ]    = "controller_error"
    canonical [ "success" ] = False
    canonical [ "status" ]  = 500
    canonical [ "message" ] = "Unknown payload source"
    canonical [ "error" ]   = {
      "type"   : "unexpected",
      "code"   : "UNKNOWN_SOURCE",
      "detail" : f"source='{source}' not supported",
    }
    return canonical
