Tournament
==========

A Python 3/Flask web program that facilitates a Magic: The Gathering limited tournament (sealed or draft). Players are randomized, seated, and paired. Match results are recorded, standings may be displayed, etc. Any given user can run (and suspend) multiple tournaments. Requires LDAP for authentication.

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

Before starting the server for the first time, run `db_create.py`.

Starting the Server
-------------------

Start the server with `run.py`. By default it will be accessible at `localhost:9999`. To make the server world-accessible or for other options, see `run.py -h`.

Bugs and Feature Requests
=========================

Feature Requests
----------------

* I feel like most of the functions in `models.py` should have the `@property` decorator.

An older, command-line version of the program can be found in the `cli/` directory. It has most of the same features, but will not be updated in the future and may have undocumented bugs.

Known Bugs
----------

* Pairings can result in multiple byes if bottom-ranked players have already played each other.
* Players can hypothetically achieve multiple byes (if the tournament goes long and they are once again the bottom-ranked player).
* The "Remember Me" option on the login page doesn't seem to work anymore.

Both of these bugs can be mitigated by manually re-pairing players using the "Edit Pairings" function.

Tournament Rules
================

More information about byes, tiebreakers, etc. can be found in the [Magic: The Gathering Tournament Rules](http://www.wizards.com/ContentResources/Wizards/WPN/Main/Documents/Magic_The_Gathering_Tournament_Rules_PDF2.pdf).

License Information
===================

Written by Gem Newman. [GitHub](https://github.com/spurll/) | [Blog](http://www.startleddisbelief.com) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).
