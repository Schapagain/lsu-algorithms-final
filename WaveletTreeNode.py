from constants import MAX_VEC_PRINT_LENGTH, BIT_PACK_SIZE
import math

class Node:
    def __init__(self,chrlo:int,chrhi:int,bit_vector:list[int] = None,ranks: list[int] = [],size: int = 0,block_size:int = None,depth: int = 0) -> None:
        '''
        :param str A list of 0s and 1s [TODO] Change to accept a true bitvector
        '''
        self._bit_vector = bit_vector
        self._size = size
        self._chrlo = chrlo
        self._chrhi = chrhi
        self._is_leaf = chrhi - chrlo <= 1
        self._left = None
        self._right = None
        self._depth = depth
        self._block_size = block_size
        self._ranks = ranks

    def __repr__(self) -> str:
      sentinel = "--"* 15
      s = f'{sentinel}\nNode:\n  Type: {"leaf" if self._is_leaf else "internal"}\n  Char Range: {self._chrlo} -> {self._chrhi}\n'
      if not self._is_leaf:
        s+= f'  Bit Vector: {"-".join(map(str,self._bit_vector[:MAX_VEC_PRINT_LENGTH]))}{"..." if self._size > MAX_VEC_PRINT_LENGTH else ""}\n{sentinel}\n'
      return s

    @property
    def is_leaf(self):
      return self._is_leaf

    @property
    def left(self):
      return self._left

    @property
    def right(self):
      return self._right

    @property
    def depth(self):
      return self._depth

    @property
    def val(self):
      if self._is_leaf:
        return self._chrlo
      raise SyntaxError("Only leaf nodes have values")

    @left.setter
    def left(self,child):
      if not isinstance(child,Node):
        raise SyntaxError("Child has to a Node type")
      self._left = child

    @right.setter
    def right(self,child):
      if not isinstance(child,Node):
        raise SyntaxError("Child has to a Node type")
      self._right = child

    def _getBit(self,i):
      '''
      Extract bit at index i from the BitVector
      '''
      if (i >= self._size):
        raise (f'Cannot get bit at index {i}. Max index is {self._size - 1}')

      packedIndex = i // BIT_PACK_SIZE
      bitIndex = i % BIT_PACK_SIZE
      packedInt = self._bit_vector[packedIndex]
      return packedInt >> (BIT_PACK_SIZE - bitIndex - 1)

    def getRank(self,charIdx,idx):
      if self._is_leaf: return idx
      if idx > self._size + 1:
        raise ValueError(f"Cannot get rank at index {idx}. Idx can be at most {self._size + 1}")

      mid = self._chrlo + math.ceil((self._chrhi - self._chrlo) / 2)

      prevBoundaryIdxInText = -1
      prevBoundaryRank = 0

      if self._block_size is not None:
        prevBoundaryIdxInText = (idx - idx % self._block_size)
        prevBoundaryIdxInRanks = prevBoundaryIdxInText // self._block_size

        if (prevBoundaryIdxInRanks >= len(self._ranks)):
          prevBoundaryRank = 0
          prevBoundaryIdxInText = 0
        else:
          prevBoundaryRank = self._ranks[prevBoundaryIdxInRanks]

      walkingRank = self._getWalkingRank(prevBoundaryIdxInText+1,idx)

      if charIdx < mid:
        rank = (idx - walkingRank - prevBoundaryRank)
      else:
        rank = walkingRank + prevBoundaryRank
      node = self
      if charIdx < mid:
        rank = self.left.getRank(charIdx,rank)
      else:
        rank = self.right.getRank(charIdx,rank)
      return rank

    def _getWalkingRank(self,i,j):
      '''
      Walk from i -> j and get the rank of 1 from bit_vector[i:j]
      '''
      return sum([self._getBit(k) for k in range(i,j)])