
# 0.3.1

Bugfix.

# 0.3

Refactor slightly to use `config.add_request_method`.  Provide two new request hooks:

* `request.email_factory` to instantiate new PMMail instances
* `request.render_email` to instantiate new PMMail instances where the body is
  rendered using a template

# 0.2

Implement basic background sending.

# 0.1

Initial version.
