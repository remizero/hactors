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
from Cryptodome.Cipher import AES
from datetime          import datetime
from hashlib           import sha256
from hashlib           import sha512
import base64

# Success Libraries / Librerías Success

# Preconditions / Precondiciones


class SuccessEncryption () :
  """
  Encryption and encoding utilities for the Success framework.

  Provides static methods for base64 encoding/decoding, AES encryption,
  and password hashing.
  """


  @staticmethod
  def base64Encode ( string : str ) -> str :
    """
    Encode a string to base64.

    Args:
      string: String to encode.

    Returns:
      str: Base64 encoded string.
    """
    stringToHashing = string
    stringBytes     = stringToHashing.encode ( 'utf-8' )
    base64Bytes     = base64.b64encode ( stringBytes )
    stringBase64    = base64Bytes.decode ( 'utf-8' )

    return stringBase64


  @staticmethod
  def base64Decode ( string : str ) -> str :
    """
    Decode a base64 string.

    Args:
      string: Base64 encoded string to decode.

    Returns:
      str: Decoded string.
    """
    stringToHashing = string
    stringBytes     = stringToHashing.encode ( 'utf-8' )
    base64Bytes     = base64.b64decode ( stringBytes )
    stringBase64    = base64Bytes.decode ( 'utf-8' )

    return stringBase64


  @staticmethod
  def decrypt ( key, str_byte ) -> bytes :
    """
    Decrypt data using AES encryption.

    Args:
      key: Encryption key.
      str_byte: Encrypted data as base64 string.

    Returns:
      bytes: Decrypted data.
    """
    data       = base64.b64decode ( str_byte.encode () )
    nonce      = data [ 0 : 8 ] + data [ 16 : 24 ]
    tag        = data [ 8 : 16 ] + data [ 24 : 32 ]
    ciphertext = data [ AES.block_size * 2 : ]
    cipher     = AES.new ( key, AES.MODE_EAX, nonce )

    return cipher.decrypt_and_verify ( ciphertext, tag )


  @staticmethod
  def encrypt ( key, data ) -> str :
    """
    Encrypt data using AES encryption.

    Args:
      key: Encryption key.
      data: Data to encrypt.

    Returns:
      str: Encrypted data as base64 string.
    """
    cipher          = AES.new ( key, AES.MODE_EAX )
    ciphertext, tag = cipher.encrypt_and_digest ( data )
    str_byte        = cipher.nonce [ 0 : 8 ] + tag [ 0 : 8 ] + cipher.nonce [ 8 : 16 ] + tag [ 8 : 16 ] + ciphertext
    
    return base64.b64encode ( str_byte ).decode ()


  @staticmethod
  def generateHash ( emailToHashing ) -> str :
    """
    Generate a hash from an email address.

    Args:
      emailToHashing: Email address to hash.

    Returns:
      str: SHA256 hash of the salted email.
    """
    salt              = 'QweRt1!2"3#4$5%AsDF'
    dateNow           = datetime.now ()
    formatDate        = dateNow.strftime ( '%d%m%Y%H' )
    emailBase64Encode = SuccessEncryption.base64Encode ( emailToHashing )
    saltedInputString = salt + emailBase64Encode + formatDate
    valueHash         = sha256 ( saltedInputString.encode () ).hexdigest ()

    return valueHash


  @staticmethod
  def password ( password : str ) -> str :
    """
    Hash a password using SHA512 with salt.

    Args:
      password: Password string to hash.

    Returns:
      str: SHA512 hash of the salted password.
    """
    salt      = SuccessSystemEnv.get ( 'SECRET_KEY' )
    loginHash = ''
    inputData = salt + password
    loginHash = sha512 ( inputData.encode () ).hexdigest ()
    return loginHash
