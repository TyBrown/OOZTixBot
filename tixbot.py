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
import MySQLdb
import time


class RobotConfigError(Exception):
    '''
    Simple Exception Class to enable try/except statements in higher
    level applications.
    '''
    pass


class TixBot(object):
    '''
    Instantiate a new Ticket Robot for Automated Processing of Tickets

    Each instance of TixBot should be for a different type of task or
    processing requirement for different types of tickets.

    Public Methods:
        self.set_query()
        self.set_values()
        self.run_robot()

    Instance Variables:
        The instance variables used within this class are not
        designed to be accessed directly. Please use the public
        methods provided so that appropriate sanity checking is
        performed.
    '''

    def __init__(self, *args, **kwargs):
        '''
        Instantiate a new TixBot to process Tickets

        Keyword Arguments for Instantiation:
            botname:A name to call this bot, used for logging.
                    (Default = UNK)
            host:   The DataBase host machine. (Default = localhost)
            user:   The DataBase user name. (Default = root)
            passwd: The DataBase user password. (Default is empty str)
            db:     DataBase that contains the OneOrZero tables.
                    (Default = oneorzero)
            table:  DataBase table for OneOrZero tickets.
                    (Default = tickets)
        '''

        self.db_host = kwargs.get('host', 'localhost')
        self.db_user = kwargs.get('user', 'root')
        self.db_pass = kwargs.get('passwd', '')
        self.db_db = kwargs.get('db', 'oneorzero')
        self.db_tixtable = kwargs.get('table', 'tickets')
        self.log = logging.getLogger('TixBot_' + kwargs.get('botname', 'UNK'))
        self.db_keys = ['id', 'lastupdate', 'update_log']
        self.log.debug("Ticket Robot Initialized")

    def set_query(self, query):
        '''
        Set the SQL Query to be used for finding Tickets to Process

        Positional Arguments:
            query:  A string containing the <query> portion of the SQL
                    query for finding tickets in the example below:
                        SELECT * FROM tickets WHERE <query>;

                Example:
                    'user="helpdesk" AND category="Email Help"'
        '''

        self.query = query
        self.log.debug("Query set to: %s" % self.query)

    def set_values(self, values):
        '''
        Set the field values that will be updated during processing

        Positional Arguments:
            values: A dict object that contains key/value pairs of the
                    fields that are to be modified during processing.

                Example:
                    {'status': 'Closed', 'priority': 'Low'}

                Available keys for updating are the field names from
                the tickets table in the OneOrZero DataBase:
                    groupid
                    supporter
                    supporter_id
                    priority
                    status
                    user
                    email
                    office
                    phone
                    category
                    platform
                    short
                    survey
                    severity
                    project

                    Note: supporter and supporter_id need to be changed
                        together in the same operation, otherwise
                        you'll have problems.
        '''

        if not isinstance(values, dict):
            self.log.fatal('Values must be dict in set_values()')
            raise TypeError('Values must be dict')
        self.new_values = values
        self.log.debug("New values configured: %s" % self.new_values)
        for key in self.new_values:
            if key not in self.db_keys:
                self.db_keys.append(key)
                self.log.debug('Added %s key to query' % key)

    def run_robot(self):
        '''
        Run the robot to start processing tickets

        Takes no arguments.
        '''

        self._check_query()
        self._check_values()
        if not self._collect_tix():
            self.log.warning("No Records for the Robot to Process")
            return
        else:
            self._process_tix()
            self.log.debug('Processed %s records' % len(self.precords))
            self._update_tix()
            self.log.info('Updated %s records in DB' % self.updated_records)

    def _check_query(self):
        '''
        Checks that the query is defined and will logs/raises exception

        Private method - called by self.run_robot
        '''

        try:
            self.query
        except AttributeError:
            self.log.fatal('No Robot Query was defined by set_query()')
            raise RobotConfigError('No Robot Query was defined by set_query()')

    def _check_values(self):
        '''
        Checks that the new values are defined, logs/raises exception

        Private method - called by self.run_robot
        '''

        try:
            self.new_values
        except AttributeError:
            self.log.fatal('No Robot Config setup for new values.')
            raise RobotConfigError('No Robot Config setup for new values.')

    def _collect_tix(self):
        '''
        Collects the tickets from the DataBase to be processed

        Returns the self.records object to determine if there are
        records to actually be processed or not.

        Private method - called by self.run_robot
        '''

        c = self._get_cursor()
        self.log.debug("Querying records from DB")
        c.execute('SELECT ' + ', '.join(self.db_keys) + ' ' +
                  'FROM %s ' % self.db_tixtable +
                  'WHERE (%s)' % self.query)
        records = c.fetchall()
        self._disconnect_db()
        self.log.debug("Collected %s records from the DB." % len(records))
        self.records = []
        for rec in records:
            self.log.debug('Found Ticket# %s' % rec[0])
            tix = dict(zip(self.db_keys, rec))  # Turn 2 lists to dict
            tix['id'] = int(tix['id'])
            self.records.append(tix)
        return self.records

    def _process_tix(self):
        '''
        Process the updates to be applied to the tickets

        Private method - called by self.run_robot
        '''

        self.precords = []
        for tix in self.records:
            ptime = int(time.time())
            log = ''
            for key in self.new_values:
                tix[key] = self.new_values[key]
                log += '%s $lang_by TixBot --//--' % ptime
                log += '$lang_%s changed to %s--//--' % (
                        key, self.new_values[key]
                        )
            tix['lastupdate'] = ptime
            tix['update_log'] += log
            self.log.debug('Ticket# %s processed' % tix['id'])
            self.precords.append(tix)

    def _update_tix(self):
        '''
        Takes the processed tickets from self.precords and updates
        the DataBase with the new information.

        Private method - called by self.run_robot
        '''

        self.updated_records = 0
        for record in self.precords:
            tid = record['id']
            del record['id']

            updstr = ''
            for key in record:
                if updstr:
                    updstr += ', %s="%s"' % (key, record[key])
                else:
                    updstr += '%s="%s"' % (key, record[key])

            sqlcmd = 'UPDATE %s SET %s WHERE id="%s"' % (
                self.db_tixtable, updstr, tid
            )
            c = self._get_cursor()
            try:
                c.execute(sqlcmd)
                self.log.info('Ticket# %s updated in DB' % tid)
                self.updated_records += 1
            except:
                self.log.error('Ticket# %s not updated' % tid, exc_info=True)
        self._disconnect_db()

    def _get_cursor(self):
        '''
        Connects to DB and returns a DB cursor

        Determines if a cursor already exists for the class instance
        and handles reconnections.

        Private method - called by various methods
        '''

        try:
            self._db
            self.log.debug("DB connection already established.")
        except AttributeError:
            self.log.debug("No DB connection. Establishing now . . .")
            self._db = MySQLdb.connect(host=self.db_host,
                                       user=self.db_user,
                                       passwd=self.db_pass,
                                       db=self.db_db)
            self.log.debug("DB connection established.")
        return self._db.cursor()

    def _disconnect_db(self):
        '''
        Handles disconnections from the DB and removes the
        self._db object so that self._get_cursor will get a new DB
        connection the next time it is called.

        Private method - called by various methods
        '''
        try:
            self._db.close()
            self.log.debug("Disconnected from DB.")
        except (MySQLdb.ProgrammingError, AttributeError):
            self.log.debug("DB was already disconnected.")
        del self._db
