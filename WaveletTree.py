from enum import Enum
import string
import warnings
import math
from collections import deque
from utils import timer_func,getIntFromBits
from WaveletTreeNode import Node
from constants import MAX_TREE_PRINT_DEPTH, BIT_PACK_SIZE

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
      bit_vector_size = math.ceil(len(node_indexes)/ BIT_PACK_SIZE)

      # Leaf node
      if chrlo == mid or chrhi == mid:
        return Node(chrlo,chrhi,bit_vector=[0]*bit_vector_size,size=len(node_indexes),depth=depth,block_size=block_size)

      bit_vector = []
      child_indexes = {
          "left": [],
          "right": []
      }
      ranks = []
      runningRank = 0
      runningBits = [0] * BIT_PACK_SIZE
      runningBitsCtr = 0
      for j,i in enumerate(node_indexes):
        in_right_child = text[i] >= character_set[mid]

        # Pre-compute ranks and store at block boundaries
        if block_size is not None:
          if not j % block_size:
            ranks.append(runningRank)
          runningRank += int(in_right_child)
        
        # Pack bits and store as ints of size INT_SIZE
        runningBits[runningBitsCtr] = int(in_right_child)
        runningBitsCtr += 1
        if runningBitsCtr == BIT_PACK_SIZE or i == node_indexes[-1]:
          bit_vector.append(getIntFromBits(runningBits))
          # print(f'adding bits:: {runningBits}')
          runningBits = [0] * BIT_PACK_SIZE
          runningBitsCtr = 0

        child_indexes["right" if in_right_child else "left"].append(i)

      # If the length of the text is a multiple of block_size
      # Add an extra rank at the end
      if not (j+1) % block_size:
        ranks.append(runningRank)
     
      node = Node(chrlo,chrhi,bit_vector=bit_vector,size=len(node_indexes),depth=depth,block_size=block_size,ranks=ranks)
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

          if node.depth > MAX_TREE_PRINT_DEPTH:
            break

          s+= f'  Level: {depth}'
          s+= lb

        s+= repr(node)
        if not node.is_leaf:
          queue.append(node.left)
          queue.append(node.right)

      return s