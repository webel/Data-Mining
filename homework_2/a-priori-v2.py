from collections import defaultdict, Counter
from itertools import chain, combinations
from pprint import pprint
from utils import printProgressBar, test


def dprint(ddict):
    """Print a defaultdict without the type
    Slightly faster than casting to dict
    """
    print(dict.__repr__(ddict))


def iprint(name, itemset):
    """Print an itemset"""
    print(name, end=": "), dprint(itemset)


def flatten(list_of_lists):
    return chain.from_iterable(list_of_lists)


class Transaction:
    pass


class APriori:
    dataset_path: str
    
    itemset: dict = defaultdict(lambda: 0)
    total_lines: int = 0

    def __init__(self, dataset_path, constant_support=None):
        self.dataset_path = dataset_path
        self.support = constant_support

    def get_line(self):
        """Get a line from our datafile one at a time"""
        with open(self.dataset_path, "r") as f:
            for line in f:
                yield set(map(int, line.split()))

    def set_support_threshhold(self):
        """Calculate depending on number of unique items in our itemset"""
        self.support = round(len(self.itemset) * 0.01)

    def prune_non_frequent(self):
        """Prune the unnecessary items from our itemset, i.e. the items that have
        a lower count than a certain threshhold"""
        to_delete = [key for key in self.itemset if self.itemset[key] <= self.support]
        for key in to_delete:
            del self.itemset[key]

    def check_subcandidates(self, candidate, k):
        """Check that subcombinations of a candidate are indeed in our previous itemset"""
        return all(
            subcandidate in self.itemset
            for subcandidate in combinations(candidate, k - 1)
        )

    def get_next_candidates(self, k):
        """Get the next candidates from the previous large itemset

        We get the keys from itemset with list(), flatten the list of keys and create a set.
        Itemset:   {('A', 'C'): 2, ('B', 'C'): 2, ('B', 'E'): 3, ('C', 'E'): 2}
        Keys:   -> [('A', 'C'), ('B', 'C'), ('B', 'E'), ('C', 'E')]
        Set:    -> ('A', 'B', 'E', 'C')
        Sorted: -> ('A', 'B', 'C', 'E')

        Given the sorted single items we create combinations, and check for each combination
        that it's subcombinations exist in our previous large itemset.
        """
        keys = list(self.itemset)
        if k == 2:
            # If k is 2, we don't need to check subsets
            return combinations(sorted(keys), k)
        else:
            items = sorted(set(flatten(keys)))
            # print(keys)
            potential_candidates = combinations(items, k)
            # Now we need to check all the subsets of a possible candidate
            candidates = [
                candidate
                for candidate in potential_candidates
                if self.check_subcandidates(candidate, k)
            ]
            return candidates

    def initial_single_count(self):
        for line in self.get_line():
            self.total_lines += 1
            for item in line:
                self.itemset[item] += 1


    def get_candidates_for_k(self, k, verbose=True):
        """Count the number of item combinations for k per line in datafile"""
        count = 0
        verbose and printProgressBar(
            0, self.total_lines, prefix=f"Progress for current k={k}:"
        )

        candidates = self.get_next_candidates(k)
        # NOTE: This looks crazy but it works
        next_itemset = Counter(candidates)
        next_itemset.subtract(next_itemset)
        for candidate in candidates:
            next_itemset[candidate] = 0
        for index, line in enumerate(self.get_line()):
            if count != 0 and count % 100 == 0:
                verbose and printProgressBar(
                    index, self.total_lines, prefix=f"Progress for current k={k}:"
                )
            # NOTE: Yes, we're getting all the combinations and incrementing 
            # but this version takes 0.41 seconds for 100
            # For the full dataset it takes about 75s on my M1 for a constant treshhold of 50
            line_combinations = combinations(sorted(line), k)
            for combination in line_combinations:
                if combination in next_itemset:
                    next_itemset[combination] += 1

            # NOTE: For 100 items takes 5s
            # to_increment = [
            #     candidate for candidate in candidates if line.issuperset(candidate)
            # ]
            # for candidate in to_increment:
            #     next_itemset[candidate] += 1

            # NOTE: For 100 items takes 17s
            # line_combinations = combinations(line, k)
            # for combination in line_combinations:
            #     if combination in candidates:
            #         next_itemset[combination] +=1

            # increment_dict = self._check_candidates_in_line(line, candidates, k)
            # next_itemset = dict(Counter(next_itemset) + Counter(increment_dict))
            count += 1

        verbose and printProgressBar(
            index + 1, self.total_lines, prefix=f"Progress for current k={k}:"
        )
        self.itemset = next_itemset

    def get_candidates(self, k, verbose=True):
        """Build large itemset for a provided k"""
        verbose and print("Initial count...")
        self.itemset = defaultdict(lambda: 0)
        self.initial_single_count()

        if not self.support:
            verbose and print("Setting threshhold...")
            self.set_support_threshhold()

        verbose and print("Pruning singletones...")
        verbose and print(
            f"Singletons before pruning. Currently {len(self.itemset)} keys"
        )
        self.prune_non_frequent()
        verbose and print(
            f"Singletons after pruning. Currently {len(self.itemset)} keys"
        )

        for current_k in range(2, k + 1):
            if not self.itemset:
                break
            verbose and print(f"Get itemsets for k={current_k}...")
            self.get_candidates_for_k(current_k)

            verbose and print(
                f"k={current_k} - before pruning. Currently {len(self.itemset)} keys"
            )
            self.prune_non_frequent()
            verbose and print(
                f"k={current_k} - after pruning. Currently {len(self.itemset)} keys"
            )
        return self.itemset


@test
def test_get_next_candidates():
    """Check that the next candidates are expected given a known current large set"""
    large_itemset = {("A", "C"): 2, ("B", "C"): 2, ("B", "E"): 3, ("C", "E"): 2}
    print("Large itemset:")
    pprint(large_itemset)
    a_priori = APriori("", 1)
    a_priori.itemset = large_itemset
    candidates = a_priori.get_next_candidates(k=3)
    print("Candidates:")
    pprint(candidates)
    # Happens to be same as the final L
    assert [("B", "C", "E")] == candidates


@test
def test_toy_dataset_large_itemsets():
    """Check that the large itemsets are as expected for k's 1 through 4 for our toy dataset"""
    a_priori = APriori("simple_test.dat", 1)
    candidates = a_priori.get_candidates(3)
    L1 = a_priori.get_candidates(1)
    iprint("L1", L1)
    candidates = {1: 2, 3: 3, 2: 3, 5: 3}
    assert len(L1) == len(candidates)
    assert candidates == L1

    L2 = a_priori.get_candidates(2)
    iprint("L2", L2)
    candidates = {(1, 3): 2, (2, 3): 2, (2, 5): 3, (3, 5): 2}
    assert candidates == L2

    L3 = a_priori.get_candidates(3)
    iprint("L3", L3)
    candidates = {(2, 3, 5): 2}
    assert candidates == L3

    L4 = a_priori.get_candidates(4)
    iprint("L4", L4)
    candidates = {}
    assert candidates == L4


@test
def test_real_transactions():
    a_priori = APriori("T10I4D100K.dat")
    candidates = a_priori.get_candidates(3, verbose=True)
    iprint("L3", candidates)


if __name__ == "__main__":
    test_real_transactions()
    # test_get_next_candidates()
    #test_toy_dataset_large_itemsets()
