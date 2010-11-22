
from django.db import transaction

class Transaction(object):
    def __init__(self, db=None):
        self.db = db

    def __enter__(self):
        print "Entering a transaction"
        transaction.enter_transaction_management(using=self.db)
        transaction.managed(True, using=self.db)

    def __exit__(self, a,b,c):
        if a is None:
            print "Commiting transaction"
            transaction.commit(using=self.db)
        else:
            # TODO: Might be nice to log all DB rollbacks...

            print "Rolling back transaction"
            transaction.rollback(using=self.db)

