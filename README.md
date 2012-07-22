[pyramid_postmark][] is a package that integrates the [Postmark][] email sending
service with a [Pyramid][] web application.  It's a very thin layer around the
[python-postmark][] library that provides:

* `request.mailer`, a configured `postmark.PMBatchMail` instance
* `request.send_email` a function to send one or more email messages

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

You can then send an email like this:

    # E.g.: in a view callable / anywhere where you're handling a `request`.
    from postmark import PMMail
    email = PMMail(sender='a@b.com', to='b@c.com', subject='Subject', 
            html_body='<p>Body</p>', text_body='Body')
    request.send_email(email)

Or send multiple emails:

    request.send_email([email, email])

Or use the batch mailer directly:

    request.mailer.messages = [email]
    request.mailer.send()

Note that your sender email will need to match your [Postmark sender signature][].

By default, `request.send_email` sends the email iff the current transaction
succeeds.  You can override this using the `postmark.should_join_tx` flag in
your `.ini` settings:

    postmark.should_join_tx = false

Or when calling `request.send_email`:

    request.send_email(email, should_join_tx=False)

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
