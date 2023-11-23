from time import time

def timer_func(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        if 'debug' in kwargs and kwargs['debug']:
          print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func

def getIntFromBits(bit_array):
  '''
  Convert an array of 1s and 0s to its integer representation
  '''
  out_num = 0
  for bit in bit_array:
    out_num = (out_num << 1) | bit
  return out_num