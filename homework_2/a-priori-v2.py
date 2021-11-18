from collections import defaultdict
from itertools import combinations
from pprint import pprint


class APriori:
    dataset_path: str
    itemset: dict = defaultdict(lambda: 0)

    def __init__(self, dataset_path, constant_support=None):
        self.dataset_path = dataset_path
        self.constant_support = constant_support

    def get_line(self):
        """Get a line from our datafile one at a time"""
        with open(self.dataset_path, "r") as f:
            for line in f:
                yield line

    def find_support_threshhold(self):
        """Either use the constant support provided on init, or calculate one
        depending on number of unique items in our itemset"""
        return self.constant_support or round(len(self.itemset) * 0.01)

    def prune_non_frequent(self):
        """Prune the unnecessary items from our itemset, i.e. the items that have
        a lower count than a certain threshhold"""
        support = self.find_support_threshhold()
        to_delete = [key for key in self.itemset if self.itemset[key] <= support]
        for key in to_delete:
            del self.itemset[key]

    def count_support(self, k):
        """Count the number of item combinations for k per line in datafile"""
        next_itemset = defaultdict(lambda: 0)
        for line in self.get_line():
            items = sorted(set(line.split()))
            possible_combinations = combinations(items, k)
            for combination in possible_combinations:
                next_itemset[combination] += 1
        self.itemset = next_itemset

    def get_candidates(self, k):
        """Build candidate itemset for a provided k"""
        for current_k in range(1, k + 1):
            self.count_support(current_k)
            self.prune_non_frequent()
        return self.itemset


def simple_test():
    a_priori = APriori("simple_test_abc.dat", 1)
    candidates = a_priori.get_candidates(3)
    pprint(candidates)
    assert len(candidates.keys()) == 1, "should only have one set of keys"
    assert candidates[("B", "C", "E")] == 2, "support should be 2"


if __name__ == "__main__":
    simple_test()
