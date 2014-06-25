Overview
========

A web program (with a Flask and SQLite back-end) that facilitates a Magic: The Gathering limited tournament (sealed or draft). Players are randomized, seated, and paired. Match results are recorded, standings may be displayed, etc. Any given user can run (and suspend) multiple tournaments.

Installation
============

Instructions
------------

The config.py file contains values for HOST and SERVER_NAME for local testing and for running deployed on your own server. Comment out the appropriate line (and, if deploying, edit the SERVER_NAME appropriately). Make note of the PORT number specified, as this is also required to connect. Before running for the first time, run db_create.py. Then simply execute run.py.

Requirements
------------

* flask
* flask-login
* sqlalchemy
* python-ldap

Bugs and Feature Requests
=========================

Feature Requests
----------------

The current version is a "minimally viable product" that is missing some important features. The following features will be supported in future releases:

* Editing player pairings (the existing algorithm for pairing isn't perfect).
* Displaying detailed player stats.
* Dropping players from the tournament.
* Closing the tournament from the main menu.

Additionally, the following features may be implemented in the future:

* An "undo" fuction would be fairly trivial (and useful!) to implement! Just keep a deep copy of the players set!
* Add verification for some of the bad stuff you can do accidentally. (Dropping players, etc.)
* Add logging, including the IP address of whomever connects (to satisfy my curiosity as to where people are connecting from).

The old (non-web) version of the program can be found in the old/ directory.

Known Bugs
----------

* Pairings can result in multiple byes if bottom-ranked players have already played each other.
* Players can hypothetically achieve multiple byes (if the tournament goes long and they are once again the bottom-ranked player).

Tournament Rules
================

More information about byes, tiebreakers, etc. can be found here:
http://www.wizards.com/ContentResources/Wizards/WPN/Main/Documents/Magic_The_Gathering_Tournament_Rules_PDF2.pdf

License Information
===================

Written by Gem Newman.
http://www.startleddisbelief.com

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
