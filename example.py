#!/usr/bin/python

###############################################################################
#    Copyright (C) 2015  Ty Brown
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

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
