from dataclasses import dataclass, field
from typing import Iterable, List, Set

test_document = "abcab"

class TestDocuments:
    short = "abcab"
    sentenceA = "The dog which chased the cat"
    sentenceB = "The dog that chased the cat"

# @dataclass
# class Shingle:
#     string: str

#     def __hash__(self) -> int:
#         # I don't think we need to implement our own hash?!
#         return hash(self.string)

@dataclass
class Shingling:
    k: int
    # TODO make this document file path
    document: str
    hashed: set = field(default_factory=set)

    def get_hashed_shingles(self):
        if not self.hashed:
            self.load_shingles()
        return self.hashed

    def load_shingles(self):
        """Load from disc
        Maybe too overkill to implement for this assignment, 
        depends on the dataset we show I guess.
        """
        pass

    def read_document(self):
        """Read document contents
        :returns: document as str
        """
        pass

    def populate_hashed(self):
        number_of_shingles = len(self.document) + 1 - self.k
        
        for index in range(number_of_shingles):
            shingle = self.document[index:index+self.k]
            hashed_shingle = hash(shingle)
            self.hashed.add(hashed_shingle)
        

shingling = Shingling(2, TestDocuments.short)
shingling.populate_hashed()
print(shingling.hashed)

A = Shingling(3, TestDocuments.sentenceA)
B = Shingling(3, TestDocuments.sentenceB)

for item in [A, B]:
    item.populate_hashed()

class CompareSets:
    def jaccard_similarity(A: set, B: set) -> float:
        #import ipdb; ipdb.set_trace()
        intersection = len(A.intersection(B))
        union = len(A.union(B))
        return intersection/union

print(CompareSets.jaccard_similarity(A.hashed, B.hashed))




