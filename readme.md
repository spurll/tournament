Tournament
==========

A web application that facilitates a Magic: The Gathering limited tournament (sealed or
draft). Players are randomized, seated, and paired. Match results are recorded, standings
may be displayed, etc. Any given user can run (and suspend) multiple tournaments.
Requires LDAP for authentication.

Usage
=====

Requirements
------------

* flask
* flask-login
* flask-wtf
* flask-sqlalchemy
* sqlalchemy
* ldap3

Configuration
-------------

You'll need to create a `config.py` file, which specifies details such as which LDAP
server to use. A sample configuration file can be found at `sample_config.py`.

Starting the Server
-------------------

Start the server with `run.py`. By default it will be accessible at `localhost:9999`. To
make the server world-accessible or for other options, see `run.py -h`.

If you're having trouble configuring your sever, I wrote a
[blog post](http://blog.spurll.com/2015/02/configuring-flask-uwsgi-and-nginx.html)
explaining how you can get Flask, uWSGI, and Nginx working together.

Bugs and Feature Requests
=========================

Feature Requests
----------------

* I feel like most of the functions in `models.py` should have the `@property` decorator.

An older, command-line version of the program can be found in the `cli/` directory. It has
most of the same features, but will not be updated in the future and may have undocumented
bugs.

Known Bugs
----------

* Pairings can result in multiple byes if bottom-ranked players have already played each
  other.
* Players can hypothetically achieve multiple byes (if the tournament goes long and they
  are once again the bottom-ranked player).

Both of these bugs can be mitigated by manually re-pairing players using the "Edit
Pairings" function.

Tournament Rules
================

More information about byes, tiebreakers, etc. can be found in the
[Magic: The Gathering Tournament Rules](http://www.wizards.com/ContentResources/Wizards/WPN/Main/Documents/Magic_The_Gathering_Tournament_Rules_PDF2.pdf).

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

Remember: [GitHub is not my CV.](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/)
