Tournament
==========

A web program (with a Flask and SQLite back-end) that facilitates a Magic: The Gathering limited tournament (sealed or draft). Players are randomized, seated, and paired. Match results are recorded, standings may be displayed, etc. Any given user can run (and suspend) multiple tournaments.

Installation
============

Instructions
------------

Edit `config.py` and specify the desired hostname and port. Before running for the first time, run `db_create.py`. Then simply execute `run.py`. (By default, it will be externally accessible. For testing on localhost, use the `--test` flag.)

Requirements
------------

* flask
* flask-login
* flask-wtf
* flask-sqlalchemy
* sqlalchemy
* python-ldap

Bugs and Feature Requests
=========================

Feature Requests
----------------

The following features may be implemented in the future:

* An "undo" fuction would be fairly useful. A single-level undo probably wouldn't be too hard to implement.
* Verification ("Are you sure?") for some of the more disastrous stuff you can do accidentally. (Dropping players, closing tournaments, etc.)
* Logging, including the IP address of whomever connects (to satisfy my curiosity as to where people are connecting from).

An older, command-line version of the program can be found in the cli/ directory. It has most of the same features, but will probably not be updated in the future.

Known Bugs
----------

* Pairings can result in multiple byes if bottom-ranked players have already played each other.
* Players can hypothetically achieve multiple byes (if the tournament goes long and they are once again the bottom-ranked player).

Both of these bugs can be mitigated by manually re-pairing players using the "Edit Pairings" function.

Tournament Rules
================

More information about byes, tiebreakers, etc. can be found in the [Magic: The Gathering Tournament Rules](http://www.wizards.com/ContentResources/Wizards/WPN/Main/Documents/Magic_The_Gathering_Tournament_Rules_PDF2.pdf).

License Information
===================

Written by Gem Newman. [GitHub](https://github.com/spurll/) | [Blog](http://www.startleddisbelief.com) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).
