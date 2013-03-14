# -*- coding: utf-8 -*-

"""Provide ``get_mailer`` and ``send_email``, ``email_factory`` and
  ``render_email`` request methods.
"""

__all__ = [
    'email_factory',
    'render_email',
    'get_mailer',
    'send_email'
]

import logging
logger = logging.getLogger(__name__)

import threading

from html2text import html2text
from postmark import PMBatchMail
from postmark import PMMail

from pyramid.renderers import render as renderers_render_template
from pyramid.settings import asbool

from pyramid_weblayer import tx

def email_factory(request, from_address, to_address, subject, body,
        msg_cls=None, **kwargs):
    """Instatiate an instance of ``postmark.PMMail``, where the strings provided
      are encoded to utf-8 and stripped::
      
          >>> mock_request = None
          >>> subject = u'Subject Line'
          >>> body = u'<p>Boo</p>'
          >>> kwargs = {}
          >>> mail = email_factory(mock_request, u'from@domain.com',
          ...         u'to@domain.com', subject, body, **kwargs)
          >>> assert isinstance(mail, PMMail)
          >>> mail.html_body
          '<p>Boo</p>'
          >>> mail.text_body
          'Boo'
      
      Any ``kwargs`` passed to the function are passed to the PMMail constructor.
    """
    
    # Compose.
    if msg_cls is None:
        msg_cls = PMMail
    
    # Prepare.
    subject_str = subject.encode('utf-8').strip()
    body_str = body.encode('utf-8').strip()
    text_str = html2text(body).encode('utf8').strip()
    
    return msg_cls(sender=from_address, to=to_address, subject=subject_str,
            html_body=body_str, text_body=text_str, **kwargs)

def render_email(request, from_address, to_address, subject, template_spec,
        template_vars={}, factory=None, render_template=None, **kwargs):
    """Use ``render_email`` to render an email using a template::
      
          >>> from mock import Mock
          >>> mock_render = Mock()
          >>> mock_render.return_value = '<p>Boo</p>'
          >>> mock_request = None
          >>> subject = u'Subject Line'
          >>> template_spec = 'pyramid_postmark:fixtures/example.mako'
          >>> template_vars = {'msg': u'Boo'}
          >>> kwargs = {}
          >>> mail = render_email(mock_request, u'from@domain.com',
          ...         u'to@domain.com', subject, template_spec, template_vars,
          ...         render_template=mock_render, **kwargs)
          >>> mail.html_body
          '<p>Boo</p>'
          >>> mock_render.assert_called_with(template_spec, template_vars,
          ...         request=mock_request)
      
      Any ``kwargs`` passed to the function are passed to the PMMail constructor.
    """
    
    # Compose.
    if factory is None:
        factory = email_factory
    if render_template is None:
        render_template = renderers_render_template
    
    # Use the template to generate the email body.
    body = render_template(template_spec, template_vars, request=request)
    
    # Use the factory to return an email.
    return factory(request, from_address, to_address, subject, body, **kwargs)


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
    
    # Compose.
    if mailer_factory is None: # pragma: no cover
        mailer_factory = PMBatchMail
    
    # Get the api key to use from the settings.
    settings = request.registry.settings
    api_key = settings.get('postmark.api_key')
    
    return mailer_factory(api_key=api_key)

def send_email(request, get_batch_mailer=None, join_to_transaction=None,
          thread_cls=None):
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
          >>> mock_thread_cls = Mock()
      
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
      
      Using a background thread if told to::
      
          >>> mock_request.registry.settings = {}
          >>> send_email = get_send_email(mock_request, get_batch_mailer=mock_get_mailer,
          ...         join_to_transaction=mock_join, thread_cls=mock_thread_cls)
          >>> 
          >>> send_email('msg', in_background=True)
          >>> mock_join.assert_called_with(mock_thread_cls.return_value.start)
      
    """
    
    # Compose.
    if get_batch_mailer is None: # pragma: no cover
        get_batch_mailer = get_mailer
    if join_to_transaction is None: # pragma: no cover
        join_to_transaction = tx.join_to_transaction
    if thread_cls is None: # pragma: no cover
        thread_cls = threading.Thread
    
    # Unpack settings.
    settings = request.registry.settings
    default_join_tx = asbool(settings.get('postmark.should_join_tx', True))
    
    # Create the send email function.
    def send_email(messages, should_join_tx=None, in_background=False):
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
        
        # Call directly, or in a background thread.
        do_send = thread_cls(target=mailer.send).start if in_background else mailer.send
        
        # Send immediately, or use an after commit hook.
        return join_to_transaction(do_send) if should_join_tx else do_send()
    
    # Return the function.
    return send_email


# Backwards compatibility.
get_send_email = send_email