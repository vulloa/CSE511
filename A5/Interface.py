#!/usr/bin/python2.7
#
# Assignment3 Interface
#

import psycopg2
import os
import sys
import thread
import threading

# Donot close the connection inside this file i.e. do not perform openconnection.close()
def ParallelSort (InputTable, SortingColumnName, OutputTable, openconnection):
    print("---Parallel Sort")

    cur = openconnection.cursor()

    cmd = "SELECT MIN(%s) FROM %s" % (SortingColumnName, InputTable)
    cur.execute(cmd)
    min = cur.fetchone()[0]

    cmd = "SELECT MAX(%s) FROM %s" % (SortingColumnName, InputTable)
    cur.execute(cmd)
    max = cur.fetchone()[0]

    interval = (max - min)/5

    cmd = "DROP TABLE IF EXISTS %s" % OutputTable
    cur.execute(cmd)
    cmd = "CREATE TABLE IF NOT EXISTS %s (LIKE %s)" % (OutputTable, InputTable)
    cur.execute(cmd)

    for i in range(0, 5):
        s = min
        e = min + interval
        thread = threading.Thread(target=sortvalues(i, s, e, InputTable, OutputTable, SortingColumnName, openconnection))
        thread.start()
        thread.join()
        min = e

    openconnection.commit()


def sortvalues(i, min, max, table, output, col, con):
    print("--sort %i" % i)
    cur = con.cursor()

    if i == 0:
        cmd = "CREATE TABLE IF NOT EXISTS %s (LIKE %s)" % (output, table)
        cur.execute(cmd)
        cmd = "INSERT INTO %s SELECT * FROM %s WHERE %s >= %s AND %s <= %s ORDER BY %s" % (output, table, col, str(min), col, str(max), col)
    else:
        cmd = "INSERT INTO %s SELECT * FROM %s WHERE %s > %s AND %s <= %s ORDER BY %s" % (output, table, col, str(min), col, str(max), col)

    cur.execute(cmd)
    cur.close()


def ParallelJoin (InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, OutputTable, openconnection):
    print("--Parallel Join")

    cur = openconnection.cursor()

    cmd = "SELECT MIN(%s) FROM %s" % (Table1JoinColumn, InputTable1)
    cur.execute(cmd)
    min1 = cur.fetchone()[0]
    cmd = "SELECT MIN(%s) FROM %s" % (Table2JoinColumn, InputTable2)
    cur.execute(cmd)
    min2 = cur.fetchone()[0]
    min = min1 if min1 < min2 else min2

    cmd = "SELECT MAX(%s) FROM %s" % (Table1JoinColumn, InputTable1)
    cur.execute(cmd)
    max1 = cur.fetchone()[0]
    cmd = "SELECT MAX(%s) FROM %s" % (Table2JoinColumn, InputTable2)
    cur.execute(cmd)
    max2 = cur.fetchone()[0]
    max = max1 if max1 > max2 else max2

    interval = (max - min)/5

    for i in range(0, 5):
        s = min
        e = min + interval
        thread = threading.Thread(target=joinvalues(i, s, e, InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, OutputTable, openconnection))
        thread.start()
        thread.join()
        min = e

    openconnection.commit()


def joinvalues(i, min, max, table1, table2, col1, col2, output, con):
    print("--join %i" % i)
    cur = con.cursor()

    if i == 0:
        cmd = "CREATE TABLE %s AS SELECT * FROM %s INNER JOIN %s ON %s.%s = %s.%s WHERE %s.%s >= %s AND %s.%s <= %s" % (output, table1, table2, table1, col1, table2, col2, table1, col1, min,  table1, col1, max)
    else:
        cmd = "INSERT INTO %s SELECT * FROM %s INNER JOIN %s ON %s.%s = %s.%s WHERE %s.%s > %s AND %s.%s <= %s" % (output, table1, table2, table1, col1, table2, col2, table1, col1, min, table1, col1, max)
    cur.execute(cmd)
    cur.close()

################### DO NOT CHANGE ANYTHING BELOW THIS #############################


# Donot change this function
def getOpenConnection(user='postgres', password='1234', dbname='postgres'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")

# Donot change this function
def createDB(dbname='dds_assignment'):
    """
    We create a DB by connecting to the default user and database of Postgres
    The function first checks if an existing database exists for a given name, else creates it.
    :return:None
    """
    # Connect to the default database
    con = getOpenConnection(dbname='postgres')
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    # Check if an existing database with the same name exists
    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (dbname,))  # Create the database
    else:
        print 'A database named {0} already exists'.format(dbname)

    # Clean up
    cur.close()
    con.commit()
    con.close()
