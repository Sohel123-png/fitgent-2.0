#!/usr/bin/env python
"""
Startup script for the authentication system server.
This script can be used to run the server automatically on system startup.
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Get the port from command line arguments or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    
    # Run the Flask application
    with app.app_context():
        from db import db
        db.create_all()
    
    # Start the server
    app.run(host='0.0.0.0', port=port, debug=False)
