from marshmallow.exceptions import ValidationError

from success.engine.io.SuccessInput import SuccessInput

from apps.hactors.services.view.viewer.v1.render.projects.Schema import Schema


class Input ( SuccessInput ) :

  def __init__ ( self ) -> None :
    super ().__init__ ()
    self._schema = Schema ()

  def parse ( self ) :
    try :
      self._parseInput ()
    except Exception as e :
      self._logger.log ( f"Error al procesar el request data: {e}", "EXCEPTION" )
    return self

  def validate ( self ) :
    try :
      self._validatedData = self._schema.load ( self._rawData )
    except ValidationError as e :
      self._logger.log ( f"Error al procesar el request data: {e}", "EXCEPTION" )
      self._errors.extend ( [ f"{k}: {', '.join ( v )}" for k, v in e.messages.items () ] )
    return self
