# -*- coding: utf-8 -*-

"""Allow developers to configure using ``config.include('pyramid_postmark')``."""

from .hooks import *

def includeme(config):
    """Pyramid configuration for this package.
      
          >>> from mock import Mock
          >>> mock_config = Mock()
          >>> includeme(mock_config)
          >>> mock_config.add_request_method.assert_any_call(
          ...         email_factory, 'email_factory')
          >>> mock_config.add_request_method.assert_any_call(
          ...         get_mailer, 'mailer', reify=True)
          >>> mock_config.add_request_method.assert_any_call(
          ...         render_email, 'render_email')
          >>> mock_config.add_request_method.assert_any_call(
          ...         send_email, 'send_email')
      
    """
    
    # Extend the request.
    config.add_request_method(email_factory, 'email_factory')
    config.add_request_method(get_mailer, 'mailer', reify=True)
    config.add_request_method(render_email, 'render_email')
    config.add_request_method(send_email, 'send_email', reify=True)

