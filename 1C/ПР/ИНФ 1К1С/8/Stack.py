class Stack:
  def __init__(self):
    self.storage = []

  def isEmpty(self):
    return len(self.storage) == 0

  def push(self,p):
    self.storage.append(p)

  def pop(self):
    return self.storage.pop()