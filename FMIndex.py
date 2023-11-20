from WaveletTree import WaveletTree
from utils import timer_func
from SuffixArray import suffix_array_best

class FMIndex:
  '''
  Class to build an FM Index based on the BWT of the text
  Stores the Wavelet tree built over the BWT, 
  the "skip counts" for each character in the charcater set,
  and the mapping from each character to its index in the sorted order of characters
  Space: O(|WaveletTree| + 2Σ )
  '''
  @timer_func
  def __init__(self,text:str,character_set:str,debug:bool = False):
    self._text_size = len(text)
    # Stores the mapping: character -> character index in the lexicographically ordered set
    self._charToIdx = dict(zip(character_set,range(len(character_set))))

    # Stores a dictionary of where each character in the character set is first seen
    # among all the sorted suffixes
    self._skip_count = [0] * len(character_set)
    bwt = self._buildBWTandSkipCounts(text)
    self._waveletTree = WaveletTree(bwt,character_set)

  def _buildBWTandSkipCounts(self,text:str):
    '''
    Builds the BWT for the given text using its Suffix Array
    Also populates the skip counts in the process
    '''
    sa = suffix_array_best(text)
    seen = set()
    bwt = ['']*len(sa)
    for i in range(len(sa)):
      try:
        currCharIdx = self._charToIdx[text[sa[i]]]
      except:
        raise SyntaxError("pattern includes at least one character that's not in the character set of the FM Index")
      currBWTChar = text[sa[i]-1]
      bwt[i] = currBWTChar
      if currCharIdx not in seen:
        self._skip_count[currCharIdx] = i
        seen.add(currCharIdx)
    return "".join(bwt)

  @timer_func
  def findMatchCount(self,pattern:str):
    '''
    Use backward matching on the BWT to find the
    number of occurences of the given pattern on the static text
    '''
    m = len(pattern)
    sp = 0
    ep = self._text_size
    for i in range(m - 1,-1,-1):
      try:
        currCharIdx = self._charToIdx[pattern[i]]
      except:
        raise SyntaxError("pattern includes at least one character that's not in the character set of the FM Index")
      start_rank = self._waveletTree.getRank(currCharIdx,sp)
      end_rank = self._waveletTree.getRank(currCharIdx,ep)

      # If the current character in the pattern
      # has a rank of zero at the end of the current bwt interval being scanned
      # we can be sure that the pattern has no matches in the string
      if end_rank == 0:
        return 0

      skip = self._skip_count[currCharIdx]
      sp = start_rank + skip
      ep = end_rank + skip
    return ep - sp