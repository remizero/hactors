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
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from flask                import Flask
from flask                import render_template
from logging              import LogRecord
from logging.handlers     import SMTPHandler
from smtplib              import SMTP
from smtplib              import SMTP_SSL
from smtplib              import SMTPAuthenticationError
from smtplib              import SMTPDataError
from smtplib              import SMTPException
from smtplib              import SMTPHeloError
from smtplib              import SMTPNotSupportedError
from smtplib              import SMTPRecipientsRefused
from smtplib              import SMTPSenderRefused
import os
import ssl

# Success Libraries / Librerías Success
from success.common.SuccessDebug         import SuccessDebug
from success.common.tools.SuccessParsers import SuccessParsers

# Application Libraries / Librerías de la Aplicación

# Preconditions / Precondiciones


class SuccessLoggerMailer ( SMTPHandler ) :
  """
  Custom SMTP handler for sending log records via email.

  Extends SMTPHandler to provide email notification capabilities for log
  records, particularly for errors and critical events. Supports SSL/TLS
  connections, retry logic, and HTML-formatted email templates.

  Attributes:
    __app (Flask): Flask application instance for context.
    __stmp (SMTP or SMTP_SSL): SMTP connection instance.
    __useSsl (bool): Whether SSL is enabled for the SMTP connection.
    _max_retries (int): Maximum number of retry attempts for sending email.
  """

  __app        : Flask            = None
  __stmp       : SMTP or SMTP_SSL = None
  __useSsl     : bool             = False
  _max_retries : int              = 0


  def __init__( self ) -> None :
    """
    Initialize the SuccessLoggerMailer with SMTP configuration from environment.

    Configures the mailer using environment variables:
      - LOGGER_MAIL_SERVER: SMTP server hostname
      - LOGGER_MAIL_USERNAME: SMTP username (from/to address)
      - LOGGER_MAIL_PASSWORD: SMTP password
      - LOGGER_MESSAGE_SUBJECT: Default email subject
      - LOGGER_MAIL_PORT: SMTP port
      - LOGGER_MAIL_SSL: Whether to use SSL
      - LOGGER_MAX_RETRIES: Maximum retry attempts
    """
    config = {
      'mailhost'    : os.environ.get ( 'LOGGER_MAIL_SERVER' ),
      'fromaddr'    : os.environ.get ( 'LOGGER_MAIL_USERNAME' ),
      'toaddrs'     : os.environ.get ( 'LOGGER_MAIL_USERNAME' ),
      'subject'     : os.environ.get ( 'LOGGER_MESSAGE_SUBJECT' ),
      'credentials' : (
        os.environ.get ( 'LOGGER_MAIL_USERNAME' ),
        os.environ.get ( 'LOGGER_MAIL_PASSWORD' )
      )
    }
    self._max_retries = int ( os.environ.get ( 'LOGGER_MAX_RETRIES', 3 ) )
    super ().__init__ ( **config )
    self.mailport = SuccessSystemEnv.toInt ( 'LOGGER_MAIL_PORT' )
    # self.__useSsl = os.environ.get ( 'LOGGER_MAIL_SSL' ).lower () == 'true'
    self.__useSsl = SuccessSystemEnv.isTrue ( 'LOGGER_MAIL_SSL' )
    self.__smtp   = SMTP_SSL ( host = self.mailhost, port = self.mailport ) if self.__useSsl else SMTP ( host = self.mailhost, port = self.mailport )


  def customInit ( self, app : Flask = None, *args, **kwargs ) -> None :
    """
    Perform custom initialization with a Flask application.

    Args:
      app (Flask): Flask application instance required for rendering templates.

    Raises:
      ValueError: If no Flask app is provided.
    """
    if not app :
      raise ValueError ( "SuccessLoggerMailer requires a Flask apps to initialize." )
    
    self.__app = app


  def emit ( self, record : LogRecord ) -> None :
    """
    Emit a log record by sending it via email.

    Attempts to send the log record as an HTML email with retry logic.
    Connects to the SMTP server, authenticates, renders the email template
    with the log record context, and sends the email. Handles various
    SMTP exceptions and retries up to the maximum configured attempts.

    Args:
      record (LogRecord): The log record to emit via email.

    Note:
      Uses retry logic with _max_retries attempts. On failure, calls
      handleError() for each failed attempt. Always closes the SMTP
      connection in the finally block.
    """

    retries = 0
    while retries < self._max_retries:
      try :
        self.__smtp.connect ( host = self.mailhost, port = self.mailport )
        if ( not self.__useSsl ) :
          self.__smtp.ehlo ()
          context = self._secure_context ()
          response = self.__smtp.starttls ( context = context )
          if response [ 0 ] != 220 :
            return
          self.__smtp.ehlo ()

        self.__smtp.login ( user = self.fromaddr, password = self.password )
        email = MIMEMultipart ( 'alternative' )
        email.set_charset ( 'utf-8' )
        email [ 'Subject' ] = os.environ.get ( 'LOGGER_MESSAGE_SUBJECT' )
        email [ 'From' ]    = self.fromaddr
        email [ 'To' ]      = os.environ.get ( 'LOGGER_ADMIN' )
        # TODO Falta procesar el objeto exc_info del objeto record para resaltar
        # la informacion mas importante.
        # https://docs.python.org/3/library/logging.html#logrecord-objects
        # context, template = SuccessParsers.parse_exc_info ( record.exc_info )
        # template            = ''
        # if ( isinstance ( record.exc_info, Exception ) ) :
        #   template = os.environ.get ( 'LOGGER_TEMPLATE_HTML_EXCEPTION' )

        # else :
        #   template = os.environ.get ( 'LOGGER_TEMPLATE_HTML_ERROR' )

        # Procesar exc_info si existe
        # if record.exc_info :
        #   context, template = SuccessParsers.exc_info ( record.exc_info )
        #   SuccessDebug.log ( 'SuccessLoggerMailer: Captured exception for email.' )

        # else :
        #   context, template = SuccessParsers.record ( record )
        #   SuccessDebug.log ( 'SuccessLoggerMailer: No exception info; sending plain error message.' )
        context, template = SuccessParsers.record ( record )
        if record.exc_info :
          SuccessDebug.log ( 'SuccessLoggerMailer: Captured exception for email.' )

        else :
          SuccessDebug.log ( 'SuccessLoggerMailer: No exception info; sending plain error message.' )


        SuccessDebug.log ( record.exc_info )
        with self.__app.app_context () :
          payload = MIMEText ( render_template ( template, **context ), 'html', _charset="utf-8" )
          
        email.attach ( payload )
        self.__smtp.sendmail ( msg = email.as_string (), from_addr = self.fromaddr, to_addrs = os.environ.get ( 'LOGGER_ADMIN' ) )

        break

      except (
        RuntimeError,
        SMTPAuthenticationError,
        SMTPDataError,
        SMTPException,
        SMTPHeloError,
        SMTPNotSupportedError,
        SMTPRecipientsRefused,
        SMTPSenderRefused
      ) as exception :
        # TODO como procesar estas excepciones
        retries += 1
        self.handleError ( record )
      
      except :
        retries += 1
        self.handleError ( record )

      finally :
        try :
          self.__smtp.quit ()

        except Exception :
          pass

    # else :
    #   if self.debug_mode :
    #     print ( "[SuccessLoggerMailer] Todos los intentos fallaron, imprimiendo en consola como fallback:" )
    #     print ( self.format ( record ) )

  def _secure_context ( self ) -> ssl.SSLContext :
    """
    Create a secure SSL context for SMTP connections.

    Configures an SSL context with secure defaults including:
      - TLS client protocol
      - Strong cipher suites
      - No SSLv2 or SSLv3 support
      - Certificate verification required

    Returns:
      ssl.SSLContext: Configured SSL context for secure SMTP connections.
    """
    _DEFAULT_CIPHERS = (
      'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:'
      'ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:'
      'RSA+3DES:!aNULL:!eNULL:!MD5'
    )
    context = ssl.SSLContext ( ssl.PROTOCOL_TLS_CLIENT )  # Usa TLS client explícito
    context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
    context.set_ciphers ( _DEFAULT_CIPHERS )
    context.set_default_verify_paths ()
    context.verify_mode = ssl.CERT_REQUIRED
    return context
