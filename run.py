#!/usr/bin/env python

# Written by Gem Newman. This work is licensed under a Creative Commons         
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.                    


from werkzeug.serving import run_simple
from argparse import ArgumentParser

from app import app


if __name__ == '__main__':
    description = "Runs the Flask server for the Magic tournament program."
    parser = ArgumentParser(description=description)
    parser.add_argument("-t", "--test", help="Changes host information to "
                        "allow access via localhost.", action="store_true")
    parser.add_argument("-d", "--debug", help="Turns server debug mode on. "
                        "(Not recommended for world-accesible servers!)",
                        action="store_true")
    parser.add_argument("-r", "--reload", help="Turns the automatic realoder "
                        "on. This setting restarts the server whenever a "
                        "change in the source is detected.",
                        action="store_true")
    args = parser.parse_args()

    if args.test:
        app.config["SERVER_NAME"] = app.config["TEST_SERVER_NAME"]
        app.config["HOST"] = app.config["TEST_HOST"]

    app.run(app.config["HOST"], app.config["PORT"], use_debugger=args.debug,
            use_reloader=args.reload)

