
import copy

#Soporte para transacciones (de StackOverflow casi todo)-----------------------------------------
def Memento(obj, deep=False):
   state = (copy.copy, copy.deepcopy)[bool(deep)](obj.__dict__)
   def Restore():
      obj.__dict__.clear()
      obj.__dict__.update(state)
   return Restore

class Transaction:
   """A transaction guard. This is realy just 
      syntactic suggar arount a memento closure.
   """
   deep = False
   def __init__(self, *targets):
      self.targets = targets
      self.Commit()
   def Commit(self):
      self.states = [Memento(target, self.deep) for target in self.targets]
   def Rollback(self):
      for state in self.states:
         state()

class transactional(object):
   """Adds transactional semantics to methods. Methods decorated 
      with @transactional will rollback to entry state upon exceptions.
   """
   def __init__(self, method):
      self.method = method
   def __get__(self, obj, T):
      def transaction(*args, **kwargs):
         state = Memento(obj)
         try:
            return self.method(obj, *args, **kwargs)
         except:
            state()
            raise
      return transaction

def _transaction(*objs):
    return Transaction(*objs)
def _rollback(*transactions):
    for t in transactions:
        t.Rollback()
    return 1
#-----------------------------------------------------------------------------------------
