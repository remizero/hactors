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
from copy import deepcopy

# Success Libraries / Librerías Success

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessStructs () :
  """
  Data structure utilities for the Success framework.

  Provides static methods for creating standard data structures,
  schemas, and response formats.
  """

  @staticmethod
  def session () -> dict :
    """
    Create a session data structure.

    Returns:
      dict: Session structure with id, username, group_id, role_id, and token.
    """
    struct = {
      'id'       : '',
      'username' : '',
      'group_id' : '',
      'role_id'  : '',
      'token'    : ''
    }
    return struct.copy ()
  
  @staticmethod
  def signin () -> dict :
    """
    Create a signin data structure.

    Returns:
      dict: Signin structure with username, fullname, token, loggedin, type, and status.
    """
    struct = {
      'username' : '',
      'fullname' : '',
      'token'    : '',
      'loggedin' : '',
      'type'     : '',
      'status'   : ''
    }
    return struct.copy ()
  
  @staticmethod
  def signout () -> dict :
    """
    Create a signout data structure.

    Returns:
      dict: Signout structure with msg, loggedin, type, and status.
    """
    struct = {
      'msg'      : '',
      'loggedin' : '',
      'type'     : '',
      'status'   : ''
    }
    return struct.copy ()

  @staticmethod
  def booleanOptions () :
    """
    Create a boolean options list.

    Returns:
      list: List containing True and False option dictionaries.
    """
    return [
      {
        'True'  : True
      },
      {
        'False' : False
      }
    ]

  @staticmethod
  def successRichSchema () -> dict :
    """
    Create a rich schema structure.

    Returns:
      dict: Rich schema with action, data, and uimodel keys.
    """
    richSchema = {
      'action'   : '',
      'data'     : list (),
      'uimodel'  : list ()
    }
    return richSchema.copy ()


  @staticmethod
  def successCanonicalOutput () -> dict :
    """
    Create a canonical output structure.

    Returns:
      dict: Canonical output with kind, success, status, message, data, and error keys.
    """
    canonicalOutput = {
      "kind": "success",          # success | input_error | controller_error
      "success": True,
      "status": 200,
      "message": "Operación exitosa",
      "data": None,
      "error": None,
    }
    return canonicalOutput.copy ()


  @staticmethod
  def successBaseOutput () -> dict :
    """
    Create a base output schema structure.

    Returns:
      dict: Base output schema with action, data, and model keys.
    """
    schemaList = list ()
    schemaList.append ( SuccessStructs.jsonInputSchema ( 'id', 'ID', '', 'input', '', 'False', 1 ) )
    schemaList.append ( SuccessStructs.jsonSelectBooleanSchema ( 'enabled', 'Habilitado', '', 'False', 2 ) )
    schemaList.append ( SuccessStructs.jsonInputSchema ( 'created_at', 'Creado en', '', 'input', 'True', 'datetime-local', 3 ) )
    schemaList.append ( SuccessStructs.jsonInputSchema ( 'updated_at', 'Actualizado en', '', 'input', 'False', 'datetime-local', 4 ) )
    schemaList.append ( SuccessStructs.jsonSelectBooleanSchema ( 'deleted', 'Eliminado', '', 'False', 5 ) )
    fullSchema = {
      'action' : '',
      'data'   : [],
      'model'  : [
        {
          'name'      : 'id',
          'label'     : 'ID',
          'action'    : '',
          'htmlType'  : 'input',
          'maxLength' : '0',
          'required'  : 'False',
          'type'      : 'number'
        },
        {
          'name'      : 'enabled',
          'label'     : 'Habilitado',
          'action'    : '',
          'htmlType'  : 'select',
          'maxLength' : 'None',
          'required'  : 'False',
          'type'      : 'boolean',
          'options'   : [
            {
              'True'  : 'True'
            },
            {
              'False' : 'False'
            }
          ]
        },
        {
          'name'      : 'created_at',
          'label'     : 'Creado en',
          'action'    : '',
          'htmlType'  : 'input',
          'maxLength' : 'None',
          'required'  : 'True',
          'type'      : 'datetime-local'
        },
        {
          'name'      : 'updated_at',
          'label'     : 'Actualizado en',
          'action'    : '',
          'htmlType'  : 'input',
          'maxLength' : 'None',
          'required'  : 'True',
          'type'      : 'datetime-local'
        },
        {
          'name'      : 'deleted',
          'label'     : 'Eliminado',
          'action'    : '',
          'htmlType'  : 'select',
          'maxLength' : 'None',
          'required'  : 'False',
          'type'      : 'boolean',
          'options'   : [
            {
              'True'  : 'True'
            },
            {
              'False' : 'False'
            }
          ]
        }
      ]
    }
    return schemaList.copy ()
  
  @staticmethod
  def getJsonKeys ( jsonData ) :
    """
    Get keys from a JSON object.

    Args:
      jsonData: JSON object to extract keys from.

    Returns:
      The keys of the JSON object.
    """
    return jsonData.keys ()
  
  @staticmethod
  def getJsonValues ( jsonData ) :
    """
    Get values from a JSON object.

    Args:
      jsonData: JSON object to extract values from.

    Returns:
      The values of the JSON object.
    """
    return jsonData.values ()
  
  @staticmethod
  def jsonModelMsgResponse ( msg : str, type : str, status : int ) -> dict :
    """
    Create a JSON model message response.

    Args:
      msg: Message string.
      type: Message type (warning, fatal, error, normal).
      status: HTTP status code.

    Returns:
      dict: Response dictionary with msg, type, and status.
    """
    return {
      'msg'    : msg,
      'type'   : type, # warning, fatal, error, normal
      'status' : status #200, 401, ...
    }

  @staticmethod
  def jsonInputSchema ( name, label, action, maxLength, required, type, order ) -> dict :
    """
    Create a JSON input schema.

    Args:
      name: Field name.
      label: Field label.
      action: Field action.
      maxLength: Maximum length.
      required: Whether the field is required.
      type: Field type.
      order: Field order.

    Returns:
      dict: Input schema dictionary.
    """
    return {
      'name'      : name,
      'label'     : label,
      'action'    : action,
      'htmlType'  : 'input',
      'maxLength' : maxLength,
      'required'  : required,
      'type'      : type,
      'order'     : order
    }

  @staticmethod
  def jsonInputRangeSchema ( name, label, action, maxLength, required, type, min, max, step, order ) -> dict :
    """
    Create a JSON input range schema.

    Args:
      name: Field name.
      label: Field label.
      action: Field action.
      maxLength: Maximum length.
      required: Whether the field is required.
      type: Field type.
      min: Minimum value.
      max: Maximum value.
      step: Step value.
      order: Field order.

    Returns:
      dict: Input range schema dictionary.
    """
    return {
      'name'      : name,
      'label'     : label,
      'action'    : action,
      'htmlType'  : 'input',
      'maxLength' : maxLength,
      'required'  : required,
      'type'      : type,
      'order'     : order,
      'min'       : min,
      'max'       : max,
      'step'      : step
    }

  @staticmethod
  def jsonSelectSchema ( name, label, action, maxLength, required, type, order ) -> dict :
    """
    Create a JSON select schema.

    Args:
      name: Field name.
      label: Field label.
      action: Field action.
      maxLength: Maximum length.
      required: Whether the field is required.
      type: Field type.
      order: Field order.

    Returns:
      dict: Select schema dictionary.
    """
    return {
      'name'      : name,
      'label'     : label,
      'action'    : action,
      'htmlType'  : 'select',
      'maxLength' : maxLength,
      'required'  : required,
      'type'      : type,
      'order'     : order,
      'options'   : []
    }

  @staticmethod
  def jsonSelectBooleanSchema ( name, label, action, required, order ) -> dict :
    """
    Create a JSON boolean select schema.

    Args:
      name: Field name.
      label: Field label.
      action: Field action.
      required: Whether the field is required.
      order: Field order.

    Returns:
      dict: Boolean select schema dictionary.
    """
    return {
      'name'      : name,
      'label'     : label,
      'action'    : action,
      'htmlType'  : 'select',
      'maxLength' : '',
      'required'  : required,
      'type'      : 'boolean',
      'order'     : order,
      'options'   : [
        {
          'True'  : 'True'
        },
        {
          'False' : 'False'
        }
      ]
    }

  @staticmethod
  def jsonTextareaSchema ( name, label, maxLength, required, order ) -> dict :
    """
    Create a JSON textarea schema.

    Args:
      name: Field name.
      label: Field label.
      maxLength: Maximum length.
      required: Whether the field is required.
      order: Field order.

    Returns:
      dict: Textarea schema dictionary.
    """
    return {
      'name'      : name,
      'label'     : label,
      'action'    : '',
      'htmlType'  : 'textarea',
      'maxLength' : maxLength,
      'required'  : required,
      'type'      : 'text',
      'order'     : order
    }


  @staticmethod
  def redirect ( enabled : bool, target : str, context : dict ) -> dict :
    """
    Create a redirect structure.

    Args:
      enabled: Whether redirect is enabled.
      target: Target URL.
      context: Context dictionary.

    Returns:
      dict: Redirect structure dictionary.
    """
    redirect = { "enabled" : enabled, "target" : target, "context" : context or {} }
    return deepcopy ( redirect )


  @staticmethod
  def render ( enabled : bool, template : str, context : dict ) -> dict :
    """
    Create a render structure.

    Args:
      enabled: Whether render is enabled.
      template: Template name.
      context: Context dictionary.

    Returns:
      dict: Render structure dictionary.
    """
    render = { "enabled" : enabled, "template" : template, "context" : { "context": context or {} } }
    return deepcopy ( render )


  @staticmethod
  def resulset ( status : str | int , data : dict, raw_response : dict ) -> dict :
    """
    Create a resultset structure.

    Args:
      status: Status code or string.
      data: Data dictionary.
      raw_response: Raw response dictionary.

    Returns:
      dict: Resultset structure dictionary.
    """
    resulset = { "status" : status, "data" : data, "raw_response" : raw_response }
    return deepcopy ( resulset )


  @staticmethod
  def error ( status : str | int , error : dict, raw_response ) -> dict :
    """
    Create an error structure.

    Args:
      status: Status code or string.
      error: Error dictionary.
      raw_response: Raw response object.

    Returns:
      dict: Error structure dictionary.
    """
    error = { "status" : status, "error" : error, "raw_response" : raw_response }
    return deepcopy ( error )


  @staticmethod
  def successContextApp ( appName : str ) -> dict :
    """
    Create a success context for an application.

    Args:
      appName: Application name.

    Returns:
      dict: Application context dictionary with config, instance, module, logger, extensions, and breadcrumb.
    """
    context = {
      appName : {
        "config"     : None,
        "instance"   : None,
        "module"     : None,
        "logger"     : None,
        "extensions" : {},
        "breadcrumb" : {
          "current" : "",
          "scope"   : ""
        }
      }
    }
    return deepcopy ( context )


  @staticmethod
  def successContextFramework () -> dict :
    """
    Create a success context for the framework.

    Returns:
      dict: Framework context dictionary with config and success apps.
    """
    context = {
      "config"  : None,
      "success" : {
        "apps" : {},
      }
    }
    return context.copy ()
