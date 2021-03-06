#! /usr/bin/env python

"""
Test only actually works on Python 2.7 with MySQLdb installed.

Author: Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import sys
import time
import unittest
import MySQLdb
import logging

from CrossSecDB import inserter
from CrossSecDB import reader_cmssw as reader

logger = logging.getLogger(__name__)

class TestInsertRead(unittest.TestCase):

    cnf = os.environ.get('XSECCONF', os.path.join(os.path.dirname(__file__), 'my.cnf'))

    def setUp(self):
        """
        At the beginning of each test, start with a fresh database
        """
        conn = MySQLdb.connect(read_default_file=self.cnf,
                               read_default_group='mysql-crosssec-writer',
                               db='cross_sections')

        curs = conn.cursor()

        # Quickly parse our .sql file to setup a database for tests
        with open(os.path.join(os.path.dirname(__file__), '../db/cross_sections.sql'),'r') as sql_file:
            for line in \
                    ''.join([line.strip() for line in sql_file if line[:2] != '--']).split(';'):
                if line:
                    logger.debug('About to execute line:\n%s', line)
                    curs.execute(line)

        conn.close()

    def test_defaults(self):
        """
        This is just a test to check that inserting
        and reading under normal operations behaves
        appropriately.
        """
        # We can put in cross sections one at a time
        inserter.put_xsec('TestDataset', 45.0, 'test', cnf=self.cnf)
        self.assertEqual(reader.get_xsec('TestDataset', cnf=self.cnf), 45.0)

        # We can also put in parallel lists
        inserter.put_xsec(['Test1', 'Test2'], [10.0, 20.0], 'test', cnf=self.cnf)
        self.assertEqual(reader.get_xsec('Test1', cnf=self.cnf), 10.0)
        self.assertEqual(reader.get_xsec('Test2', cnf=self.cnf), 20.0)

        self.assertEqual(reader.get_xsec(['TestDataset', 'Test1', 'Test2'], cnf=self.cnf),
                         [45.0, 10.0, 20.0])

    def test_other_energy(self):
        """
        This is a test to check that the non-default
        energy tables work as intended.
        """
        self.assertRaises(inserter.BadInput, inserter.put_xsec, 'TestBadEnergy', 1.0, 'test', energy=4, cnf=self.cnf)

        inserter.put_xsec('TestDataset', 45.0, 'test', energy=8, cnf=self.cnf)
        self.assertEqual(reader.get_xsec('TestDataset', energy=8, cnf=self.cnf), 45.0)

    def test_no_source(self):
        """
        When someone doesn't supply a source for their
        cross section the insertion should fail
        """
        self.assertRaises(inserter.BadInput, inserter.put_xsec, 'TestNoSourceDocumented', 1.0, '', cnf=self.cnf)

    def test_update_existing(self):
        """
        Make sure that updating existing entry works
        """
        inserter.put_xsec('TestDataset', 10.0, 'A guess I thought of', 'This needs to be updated!', cnf=self.cnf)
        self.assertEqual(reader.get_xsec('TestDataset', cnf=self.cnf), 10.0)

        time.sleep(2)

        inserter.put_xsec('TestDataset', 11.0, 'test', cnf=self.cnf)
        self.assertEqual(reader.get_xsec('TestDataset', cnf=self.cnf), 11.0)

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        logging.basicConfig(level=logging.DEBUG)

    if sys.version_info[1] != 6:
        unittest.main()
