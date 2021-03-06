Overview
========

tournament.py
-------------

A Python program that facilitates a Magic: The Gathering limited tournament (sealed or draft). Players are randomized, seated, and paired. Match results are recorded, standings may be displayed, etc.

### Arguments

Positional:
 * A list of player names. (You probably don't want to use the default list, which is a list of people with whom the author frequently plays Magic.)

Bugs and Feature Requests
=========================

Feature Requests
----------------

* An "undo" fuction would be fairly trivial (and useful!) to implement! Just keep a deep copy of the players set!
* Add web.py support.
* Add logging, including the IP address of whomever connects (to satisfy my curiosity as to where people are connecting from).

Known Bugs
----------

* Pairings can result in multiple byes if bottom-rung players have already played each other.
* Players can hypothetically achieve multiple byes (only if they suck).

Tournament Rules
================

More information about byes, tiebreakers, etc. can be found here:
http://www.wizards.com/ContentResources/Wizards/WPN/Main/Documents/Magic_The_Gathering_Tournament_Rules_PDF2.pdf

License Information
===================

Written by Gem Newman.
http://www.startleddisbelief.com

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
