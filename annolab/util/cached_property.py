import functools

# https://stackoverflow.com/questions/20535342/lazy-evaluation-in-python
class cached_property(object):
  def __init__(self, function):
    self.function = function
    functools.update_wrapper(self, function)

  def __get__(self, obj, type_):
    if obj is None:
      return self
    val = self.function(obj)
    obj.__dict__[self.function.__name__] = val
    return val