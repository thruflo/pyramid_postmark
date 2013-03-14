[pyramid_postmark][] is a package that integrates the [Postmark][] email sending
service with a [Pyramid][] web application. For example, to send an email using
a template:

    spec = 'mypackage:templates/newsletter.tmpl'
    email = request.render_email('a@b.com', 'b@c.com', 'Subject', spec)
    request.send_email(email)

It's a very thin layer around the [python-postmark][] library that provides:

* `request.mailer`, a configured `postmark.PMBatchMail` instance
* `request.send_email` a function to send one or more email messages
* `request.email_factory` to instantiate an email message
* `request.render_email` to instantiate an email using a template

These are integrated by default with the [pyramid_tm][] transaction machinery, so
emails are only sent if the current request is successful.

# Install

Install using `pip` or `easy_install`, e.g.:

    pip install pyramid_postmark

# Configure

Provide `postmark.api_key` in your application's `.ini` settings:

    postmark.api_key = <your key>

Include the package in the configuration portion of your Pyramid app:

    config.include('pyramid_postmark')

# Use

Generate an email using the postmark library directly:

    from postmark import PMMail
    email = PMMail(sender='a@b.com', to='b@c.com', subject='Subject', 
            html_body='<p>Boo</p>', text_body='Boo')

Or use the factory provided:

    # E.g.: in a view callable / anywhere where you're handling a `request`.
    email = request.email_factory('a@b.com', 'b@c.com', 'Subject', '<p>Boo</p>')

Or use a template:

    spec = 'mypackage:templates/mytemplate.tmpl'
    data = {'msg': 'Boo'} # <-- passed as variables to the template
    email = request.render_email('a@b.com', 'b@c.com', 'Subject', spec, data)

Then send the email like this:

    request.send_email(email)

Send multiple emails:

    request.send_email([email, email])

Use the batch mailer directly:

    request.mailer.messages = [email]
    request.mailer.send()

Note that your sender email will need to match your [Postmark sender signature][].

By default, `request.send_email` sends the email iff the current transaction
succeeds.  You can override this using the `postmark.should_join_tx` flag in
your `.ini` settings:

    postmark.should_join_tx = false

Or when calling `request.send_email`:

    request.send_email(email, should_join_tx=False)

If you're feeling optimisic, you can send the email in the background:

    request.send_email(email, in_background=True)

Note that background sending works whether you send immediately or wait for the
current transaction to succeed.  i.e.: As and when the email is to be sent, it
is send in a background thread using the following code:

    do_send = thread_cls(target=mailer.send).start if in_background else mailer.send

# Tests

Tested on python2.7 only (as [python-postmark][] is not yet Python3 compatible).  
Install `mock`, `nose` and `coverage` then e.g.:

    $ nosetests --with-coverage --with-doctest --cover-package pyramid_postmark pyramid_postmark
    ...
    Name                     Stmts   Miss  Cover   Missing
    ------------------------------------------------------
    pyramid_postmark             5      0   100%   
    pyramid_postmark.hooks      22      0   100%   
    ------------------------------------------------------
    TOTAL                       27      0   100%   
    ----------------------------------------------------------------------
    Ran 3 tests in 0.017s
    
    OK

[postmark]: http://postmarkapp.com
[Postmark sender signature]: http://developer.postmarkapp.com
[pyramid]: http://pyramid.readthedocs.org
[pyramid_postmark]: https://github.com/thruflo/pyramid_postmark
[pyramid_tm]: http://pyramid_tm.readthedocs.org
[python-postmark]: https://github.com/themartorana/python-postmark
