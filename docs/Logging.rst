
Logging in `managesieve`
========================

`managesieve` follows the  `Logging for a Library`__ guidelines.

The logger is named :code:`managesieve`.
The modules defines the following debug logging levels:

===================== ================================================
Level                 When it’s used
===================== ================================================
``INFO``              Confirmation that things are working as expected
``DEBUG0``            Commands and responses
``DEBUG1``, ``DEBUG`` Data send and read (except long literals)
``DEBUG2``            More details
``DEBUG3``            All debug messages (pattern matching, etc.)
===================== ================================================

``logging.DEBUG`` corresponds to ``managesieve.DEBUG1``,
thus application loggers with level set to DEBUG get a reasonable
level of details for debugging communication.


 __ https://docs.python.org/3/howto/
        logging.html#configuring-logging-for-a-library
