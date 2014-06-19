#!/usr/bin/env python
from app import app
app.run(app.config.get('HOST'), app.config.get('PORT'), debug=app.config.get('DEBUG'))
