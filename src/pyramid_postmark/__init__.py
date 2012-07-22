# -*- coding: utf-8 -*-

"""Allow developers to configure using ``config.include('pyramid_postmark')``."""

from .hooks import get_mailer, get_send_email

def includeme(config):
    """Pyramid configuration for this package.
      
          >>> from mock import Mock
          >>> mock_config = Mock()
          >>> includeme(mock_config)
          >>> mock_config.set_request_property.assert_any_call(
          ...         get_mailer, 'mailer', reify=True)
          >>> mock_config.set_request_property.assert_any_call(
          ...         get_send_email, 'send_email', reify=True)
      
    """
    
    # Set request properties.
    config.set_request_property(get_mailer, 'mailer', reify=True)
    config.set_request_property(get_send_email, 'send_email', reify=True)

