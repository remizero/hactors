from marshmallow import INCLUDE
from marshmallow import Schema as MarshmallowSchema


class Schema ( MarshmallowSchema ) :

  class Meta :
    unknown = INCLUDE
