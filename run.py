#!/usr/bin/env python

# Written by Gem Newman. This work is licensed under a Creative Commons         
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.                    


from argparse import ArgumentParser

from app import app


if __name__ == '__main__':
    description = "Runs the Flask server for the Magic tournament program."
    parser = ArgumentParser(description=description)
    parser.add_argument("-t", "--test", help="Changes host information to "
                        "allow access via localhost.", action="store_true")
    parser.add_argument("-n", "--nodebug", help="Turns off server debug "
                        "settings, including the reloader.",
                        action="store_true")
    args = parser.parse_args()

    if args.test:
        app.config["SERVER_NAME"] = app.config["TEST_SERVER_NAME"]
        app.config["HOST"] = app.config["TEST_HOST"]

    app.run(app.config["HOST"], app.config["PORT"], debug=not args.nodebug)

