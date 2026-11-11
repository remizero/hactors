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
from flask      import Flask
from flask      import render_template
from flask_mail import Mail
from flask_mail import Message
from typing     import Any
import os

# Application Libraries / Librerías de la Aplicación
from success.common.base.SuccessExtension import SuccessExtension

# Preconditions / Precondiciones


class SuccessEmailExtension ( SuccessExtension ) :
  """
  Email extension for the Success framework.

  Integrates Flask-Mail for email sending functionality
  with support for templates and attachments.

  Attributes:
    __message (Message): Current email message instance.
  """

  __message = Message


  def __init__ ( self, app : Flask ) -> None :
    """
    Initialize the Email extension.

    Args:
      app: Flask application instance.
    """
    super ().__init__ ( app )
    self._extension = Mail ()


  def message ( self,
      _subject       : str         = '',
      _body          : str         = None,
      _html          : str         = None,
      _sender        : str         = None,
      _cc            : str or list = None,
      _bcc           : str or list = None,
      _attachments   : Any         = None,
      _reply_to      : Any         = None,
      _date          : Any         = None,
      _charset       : str         = 'utf-8',
      _extra_headers : Any         = None,
      _mail_options  : Any         = None,
      _rcpt_options  : Any         = None,
      _template      : str         = None,
      **context      : dict [ str, Any ]
    ) -> None :
    """
    Create an email message.

    Args:
      _subject: Email subject line.
      _body: Plain text email body.
      _html: HTML email body.
      _sender: Sender email address.
      _cc: CC recipients.
      _bcc: BCC recipients.
      _attachments: Email attachments.
      _reply_to: Reply-to address.
      _date: Email date.
      _charset: Character set (default: 'utf-8').
      _extra_headers: Additional headers.
      _mail_options: Mail options.
      _rcpt_options: Recipient options.
      _template: Template name for rendering.
      **context: Template context variables.
    """

    # TODO VALIDAR TODOS LOS PARAMETROS
    # TODO MANEJO DE ARCHIVOS ADJUNTOS
    if ( _sender is None ) :
      if ( os.environ.get ( 'MAIL_DEFAULT_SENDER' ) != '' ) :
        _sender = os.environ.get ( 'MAIL_DEFAULT_SENDER' )
      else :
        _sender = os.environ.get ( 'MAIL_DEFAULT_SENDER' )
    self.__message = Message (
      subject       = _subject,
      body          = _body,
      html          = _html,
      sender        = _sender,
      cc            = _cc,
      bcc           = _bcc,
      attachments   = _attachments,
      reply_to      = _reply_to,
      date          = _date,
      charset       = _charset,
      extra_headers = _extra_headers,
      mail_options  = _mail_options,
      rcpt_options  = _rcpt_options
    )
    if ( _body != None ) :
      self.__message.body = _body
    if ( _template != None ) :
      self.__message.html = render_template ( _template, **context )


  def send ( self, _receiver : str ) :
    """
    Send an email to a single recipient.

    Args:
      _receiver: Recipient email address.
    """
    self.__message.add_recipient ( _receiver )
    self._extension.send ( self.__message )


  def sendMultiple ( self, _receiver : list = None ) -> None :
    """
    Send an email to multiple recipients.

    Args:
      _receiver: List of recipient email addresses.
    """
    with self._extension.connect () as connection :
      for receiver in _receiver :
        self.__message.add_recipient ( receiver )
        connection.send ( self.__message )
