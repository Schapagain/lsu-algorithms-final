from enum import Enum
import string
import warnings
import math
from collections import deque
from utils import timer_func

class WaveletTree:
    '''
    Representation of a Wavelet Tree over the given text and character set
    Uses a Node object to store the bitvectors
    Public methods:
      getRank(charIdx,idx) -> rank of charIdx-th character in the set at idx position in text
    Public properties:
      root
    Example use:
    tree = WaveletTree('acacaac$',character_set="$ac")
    tree.getRank(1,3) <-> rank_a(3)
    tree.getRank(2,5) <-> rank_c(5)

    Stores n bits at every depth => O(nlgΣ) bits space

    [TODO] If we pre-compute and store ranks at block boundaries,
    additional space is used. Need to factor this in to find the total space used.
    '''
    maxPrintDepth = 3 # Only print the first few levels of the tree
    maxTextPrintLength = 15 # Only print the first few text characters
    @timer_func
    def __init__(self,text: str, character_set: str, block_size = None,debug:bool = False) -> None:
      '''
        Build a wavelet tree that supports efficient rank_i(j) queries
        :param str text: string to represent as a Wavelet Tree
        :param str character_set: an ordered string of all possible characters
        :param function block_size: size of the blocks. Rank values are pre-computed at block boundaries
      '''
      self._size = len(text)
      self._character_size = len(character_set)
      if not len(set(character_set)) == self._character_size:
        raise ValueError("Character set cannot have duplicate characters")
      if len(character_set) < 2:
        raise ValueError("Character set must have at least two unique characters")
      self._root = self._buildTree(text,character_set,block_size,0,self._character_size,range(self._size))

    @property
    def root(self):
      return self._root

    def _buildTree(self,text:str,character_set:str,block_size:int,chrlo: int,chrhi: int, node_indexes: list[int],depth: int = 0):
      '''
        Recursively build the tree by partitioning the character_set using chrlo and chrhi
      '''
      mid = chrlo + math.ceil((chrhi - chrlo) / 2)

      # Leaf node
      if chrlo == mid or chrhi == mid:
        return Node(chrlo,chrhi,bit_vector=[0]*len(node_indexes),depth=depth,block_size=block_size)

      bit_vector = []
      child_indexes = {
          "left": [],
          "right": []
      }
      ranks = []
      runningRank = 0
      for i in node_indexes:
        in_left_child = text[i] < character_set[mid]

        # Pre-compute ranks and store at block boundaries
        if block_size is not None:
          if not i % block_size:
            ranks.append(runningRank)
          runningRank += 0 if in_left_child else 1

        bit_vector.append(1-int(in_left_child))
        child_indexes["left" if in_left_child else "right"].append(i)
      ranks.append(runningRank)

      node = Node(chrlo,chrhi,bit_vector=bit_vector,depth=depth,block_size=block_size,ranks=ranks)
      node.left = self._buildTree(text,character_set,block_size,chrlo,mid,child_indexes["left"],depth=depth+1)
      node.right = self._buildTree(text,character_set,block_size,mid,chrhi,child_indexes["right"],depth=depth+1)
      return node

    @timer_func
    def getRank(self,charIdx,idx,debug: bool =False):
      return self._root.getRank(charIdx,idx)

    def __repr__(self) -> str:
      '''
      Print nodes with BFS, upto the configured max depth
      '''
      queue = deque([self._root])
      lb = '\n' * 2
      s = 'WaveletTree:\n'
      depth = 0
      while len(queue):
        node = queue.popleft()
        if node.depth > depth:
          depth = node.depth
          s+= lb

          if node.depth > WaveletTree.maxPrintDepth:
            break

          s+= f'  Level: {depth}'
          s+= lb

        s+= repr(node)
        if not node.is_leaf:
          queue.append(node.left)
          queue.append(node.right)

      return s

class Node:

    maxVecPrintLength = 15 # Only print the first few bits
    def __init__(self,chrlo:int,chrhi:int,bit_vector:list[int] = None,ranks: list[int] = [],block_size:int = None,depth: int = 0) -> None:
        '''
        :param str A list of 0s and 1s [TODO] Change to accept a true bitvector
        '''
        self._bit_vector = bit_vector
        self._size = len(bit_vector)
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
        s+= f'  Bit Vector: {"".join(map(str,self._bit_vector[:Node.maxVecPrintLength]))}{"..." if self._size > Node.maxVecPrintLength else ""}\n{sentinel}\n'
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
      return sum([self._bit_vector[k] for k in range(i,j)])