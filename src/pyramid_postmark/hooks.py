# -*- coding: utf-8 -*-

"""Provide ``get_batch_mailer`` and ``get_send_email_function`` functions."""

import logging
logger = logging.getLogger(__name__)

from pyramid.settings import asbool

from postmark import PMBatchMail
from pyramid_weblayer import tx

def get_mailer(request, mailer_factory=None):
    """Return a configured ``PMBatchMail`` instance.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_request.registry.settings = {'postmark.api_key': '...'}
          >>> mock_mailer_cls = Mock()
          >>> mock_mailer_cls.return_value = '<mailer>'
      
      Test::
      
          >>> get_mailer(mock_request, mailer_factory=mock_mailer_cls)
          '<mailer>'
          >>> mock_mailer_cls.assert_called_with(api_key='...')
      
    """
    
    # Test jig.
    if mailer_factory is None: # pragma: no cover
        mailer_factory = PMBatchMail
    
    # Get the api key to use from the settings.
    settings = request.registry.settings
    api_key = settings.get('postmark.api_key')
    
    return mailer_factory(api_key=api_key)

def get_send_email(request, get_batch_mailer=None, join_to_transaction=None):
    """Provides a function to send one or more emails.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_request.registry.settings = {}
          >>> mock_get_mailer = Mock()
          >>> mock_mailer = Mock()
          >>> mock_mailer.send.return_value = None
          >>> mock_get_mailer.return_value = mock_mailer
          >>> mock_join = Mock()
          >>> mock_join.return_value = None
      
      Returns ``send_email`` function that instantiates and populates a mailer::
      
          >>> send_email = get_send_email(mock_request, get_batch_mailer=mock_get_mailer,
          ...         join_to_transaction=mock_join)
          >>> send_email('msg')
          >>> mock_get_mailer.assert_called_with(mock_request)
          >>> mock_mailer.messages = ['msg']
      
      Unless told otherwise, sends the email iff the current transactions succeeds::
      
          >>> mock_join.assert_called_with(mock_mailer.send)
          >>> mock_mailer.send.called
          False
          >>> send_email('msg', should_join_tx=False)
          >>> mock_mailer.send.called
          True
          >>> mock_request.registry.settings = {'postmark.should_join_tx': 'false'}
          >>> send_email = get_send_email(mock_request, get_batch_mailer=mock_get_mailer,
          ...         join_to_transaction=mock_join)
          >>> send_email('msg')
          >>> mock_mailer.send.called
          True
      
    """
    
    # Test jig.
    if get_batch_mailer is None: # pragma: no cover
        get_batch_mailer = get_mailer
    if join_to_transaction is None: # pragma: no cover
        join_to_transaction = tx.join_to_transaction
    
    # Unpack settings.
    settings = request.registry.settings
    default_join_tx = asbool(settings.get('postmark.should_join_tx', True))
    
    # Create the send email function.
    def send_email(messages, should_join_tx=None):
        """Send ``messages``, either immediately, or using an after commit hook."""
        
        # Default to the .ini setting if ``should_join_tx`` isn't provided.
        if should_join_tx is None:
            should_join_tx = default_join_tx
        
        # If passed a single message, turn it into a list.
        if not bool(isinstance(messages, list) or isinstance(messages, tuple)):
            messages = [messages]
        
        # Set the batch mailer's messages.
        mailer = get_batch_mailer(request)
        mailer.messages = messages
        
        # Send immediately, or use an after commit hook.
        return join_to_transaction(mailer.send) if should_join_tx else mailer.send()
    
    # Return the function.
    return send_email

