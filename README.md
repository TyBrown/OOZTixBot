## Synopsis

The OneOrZero TixBot is a Robot Libary written in Python designed to perform automated processing and updates to tickets in the OneOrZero 1.8 Help Desk Application. (http://www.oneorzero.com)

Note: This is for v1.8 of the OneOrZero Helpdesk System, and is not designed for, nor is it tested with the newer OneOrZero AIMS system.

## Code Example

```
#!/usr/bin/python

import logging
import os
import time

from tixbot import TixBot

if __name__ == '__main__':
    # Setup constants
    DB_HOST = 'database.example.com'
    DB_USER = 'username'
    DB_PASS = 'password'
    DB_DB = 'database_name'
    DB_TABLE = 'helpdesk_tickets'

    # Setup logging
    logfile = os.path.splitext(os.path.abspath(__file__))[0] + '.log'
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(name)-30s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', filename=logfile,
        level=logging.WARNING
        )

    # Setup Password Bot
    passwordbot = TixBot(botname='PasswordsBot',
                         host=DB_HOST,
                         user=DB_USER,
                         passwd=DB_PASS,
                         db=DB_DB,
                         table=DB_TABLE)
    passwordbot.set_query('status="Unassigned" '
                          'AND short LIKE "%password%"')
    passwordbot.set_values({'priority': 'Low',
                            'severity': '4 - Low',
                            'status': 'Open',
                            'category': 'Password Reset',
                            'platform': 'Windows',
                            'project': 'Not Applicable'})

    # Setup loop to run robots every minute
    while True:
        passwordbot.run_robot()
        time.sleep(60)
```

## Motivation

This project was motivated by a sheer volume of tedious tickets that our HelpDesk would receive, and enabled staff to reduce time doing paperwork and instead focus on helping customers.

The TixBot is also useful for handling repetitive tickets that might get emailed to the OneOrZero Helpdesk software from monitoring or alerting applications.

## Installation

git clone this project and import as shown in the example above.

## API Reference

See Docstrings

## License

Copyright (C) 2015  Ty Brown
Licensed under the GNU General Public License Version 3

See the file "LICENSE" for information on the terms & conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.
