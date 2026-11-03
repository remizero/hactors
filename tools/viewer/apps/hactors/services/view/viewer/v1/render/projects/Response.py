from success.engine.context.SuccessResponse       import SuccessResponse
from success.engine.context.SuccessResponsePolicy import SuccessResponsePolicy


class ProjectsResponsePolicy ( SuccessResponsePolicy ) :

  def definitions ( self ) -> None :
    self._default_mimetype = "text/html"
    self._default_status   = 200
    self._charset          = "utf-8"
    self._content_type     = "text/html; charset=utf-8"


class Response ( SuccessResponse ) :

  def __init__ ( self ) -> None :
    super ().__init__ ( ProjectsResponsePolicy () )
