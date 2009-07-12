"""
Database persistent connection app.
It should decrease load of database server.
Usable with dev server as well, especialy when database server is accessed via slower internet line.
"""
from time import time

from django.db import models, connection, transaction, close_connection
from django.db.transaction import TransactionManagementError
from django.core import signals
from django.conf import settings

UNUSED_DB_CONNECTION_TIMEOUT = None 
DEFAULT_UNUSED_DB_CONNECTION_TIMEOUT = 120 # sec.

_conn_last_used = time()

def handle_unfinished_transactions(**kwargs):
    global _conn_last_used
    if connection._valid_connection:
        _conn_last_used = time()
    if transaction.is_dirty():
        raise TransactionManagementError('Please commit or rollback database transaction. (transaction.is_dirty() == True when HTTP request processing is finished)')


def check_db_connection(**kwargs):
    if time() > (_conn_last_used + UNUSED_DB_CONNECTION_TIMEOUT):
        connection.close()

UNUSED_DB_CONNECTION_TIMEOUT = getattr(settings, 'UNUSED_DB_CONNECTION_TIMEOUT', DEFAULT_UNUSED_DB_CONNECTION_TIMEOUT)

# disconnect closing connection when each HTTP request is finished
signals.request_finished.disconnect(close_connection)
# connect signal to check if no uncommitted transaction left there
signals.request_finished.connect(handle_unfinished_transactions)
# check valid-connection timeout when processing HTTP request
signals.request_started.connect(check_db_connection)
