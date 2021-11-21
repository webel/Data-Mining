import logging
from collections import Counter, defaultdict
from itertools import combinations

from utils import flatten, iprint, progress, test, setup_logging


class APriori:
    dataset_path: str
    itemsets: defaultdict(Counter)
    n_transactions: int
    support = int

    def __init__(self, dataset_path, constant_support=None):
        self.dataset_path = dataset_path
        self.itemsets = defaultdict(Counter)
        self.n_transactions = 0
        self.support = constant_support

        self.first_pass()

    def get_line(self):
        """Get a line from our datafile one at a time"""
        with open(self.dataset_path, "r") as f:
            for line in f:
                yield map(int, line.split())

    def set_support_threshhold(self):
        """Calculate depending on number of transactions in our dataset"""
        self.support = self.n_transactions * 0.01
        logging.debug(f"Set threshhold to {self.support}")

    def first_pass(self):
        logging.debug("=== FIRST PASS ===")
        logging.debug("Initial count...")
        for line in self.get_line():
            self.n_transactions += 1
            for item in line:
                self.itemsets[1][item] += 1
        if not self.support:
            logging.debug("Setting threshhold...")
            self.set_support_threshhold()
        self.prune_non_frequent(k=1)

    def prune_non_frequent(self, k):
        """Prune the unnecessary items from our itemset, i.e. the items that have
        a lower count than a certain threshhold"""
        logging.debug(f"Before pruning: {len(self.itemsets[k])} items")
        self.itemsets[k] = Counter(
            {
                item: count
                for item, count in self.itemsets[k].items()
                if count > self.support
            }
        )
        logging.debug(f"After pruning: {len(self.itemsets[k])} items")

    def check_subcandidates(self, candidate, k):
        """Check that subcombinations of a candidate are indeed in our previous itemset
        Make all sub-combinations of the candidate, e.g.
        ('A', 'B', 'C') -> ('A', 'B'), ('A', 'C'), ('B', 'C')
        And check if all these exist in itemset[k-1]
        """
        return all(
            subcandidate in self.itemsets[k - 1]
            for subcandidate in combinations(candidate, k - 1)
        )

    def get_next_candidates(self, k):
        """Get the next candidates from the previous large itemset
        Known as the 'apriori-gen' step in the paper.

        We get the keys from itemset with list(), flatten the list of keys and create a set.
        Itemset:   {('A', 'C'): 2, ('B', 'C'): 2, ('B', 'E'): 3, ('C', 'E'): 2}
        Keys:   -> [('A', 'C'), ('B', 'C'), ('B', 'E'), ('C', 'E')]
        Set:    -> ('A', 'B', 'E', 'C')
        Sorted: -> ('A', 'B', 'C', 'E')

        Given the sorted single items we create combinations, and check for each combination
        that it's subcombinations exist in our previous large itemset.
        """
        keys = list(self.itemsets[k - 1])
        if k == 2:
            # If k is 2, we don't need to check subsets
            yield from combinations(sorted(keys), k)
        else:
            items = sorted(set(flatten(keys)))
            potential_candidates = combinations(items, k)
            # Now we need to check all the subsets of a possible candidate
            candidates = (
                candidate
                for candidate in potential_candidates
                if self.check_subcandidates(candidate, k)
            )
            yield from candidates

    def get_itemset_for_k(self, k):
        """Count the number of item combinations for k per line in datafile"""
        info_log = logging.INFO >= logging.root.level
        info_log and progress(0, self.n_transactions, prefix=f"Progress for k={k}:")

        candidates = self.get_next_candidates(k)
        # NOTE: This looks crazy but it works
        next_itemset = Counter(candidates)
        next_itemset.subtract(next_itemset)
        for index, line in enumerate(self.get_line()):
            if index != 0 and index % 5000 == 0:
                info_log and progress(
                    index, self.n_transactions, prefix=f"Progress for k={k}:"
                )
            # NOTE: Yes, we're getting all the combinations and incrementing
            # For the full dataset it takes about 2.3s on my M1 for a treshhold of 1000
            line_combinations = combinations(sorted(line), k)
            for combination in line_combinations:
                if combination in next_itemset:
                    next_itemset[combination] += 1

        info_log and progress(
            index + 1, self.n_transactions, prefix=f"Progress for k={k}:", printEnd="\n"
        )
        self.itemsets[k] = next_itemset

    def get_large_itemset(self, k):
        """Build large itemset for a provided k"""
        for current_k in range(2, k + 1):
            logging.debug(f"\n === PASS k={current_k} ===")
            logging.debug(f"Get itemsets for k={current_k}...")
            self.get_itemset_for_k(current_k)

            if not self.itemsets[current_k]:
                logging.debug("No itemsets for, breaking.")
                break

            self.prune_non_frequent(k=current_k)
        return self.itemsets


@test
def test_get_next_candidates():
    """Check that the next candidates are expected given a known current large set"""
    large_itemset = {(1, 3): 2, (2, 3): 2, (2, 5): 3, (3, 5): 2}
    iprint("Large itemset (L2)", large_itemset, True)
    a_priori = APriori("simple_test.dat", 1)
    a_priori.itemsets[2] = large_itemset
    candidates = list(a_priori.get_next_candidates(k=3))
    print("Candidates:", candidates)
    # Happens to be same as the final L
    assert [(2, 3, 5)] == candidates


@test
def test_toy_dataset_large_itemsets():
    """Check that the large itemsets are as expected for k's 1 through 4 for our toy dataset"""
    a_priori = APriori("simple_test.dat", constant_support=1)
    itemsets = a_priori.get_large_itemset(4)
    large_itemsets = [
        {1: 2, 3: 3, 2: 3, 5: 3},
        {(1, 3): 2, (2, 3): 2, (2, 5): 3, (3, 5): 2},
        {(2, 3, 5): 2},
        {},
    ]

    for index, itemset in itemsets.items():
        name = f"L{index}"
        iprint(name, itemset)
        assert large_itemsets[index - 1] == itemset

    print("No assertion error, they are as expected!")


@test
def test_large_dataset():
    """Test itemset generation for the provided dataset of the homework."""
    a_priori = APriori("T10I4D100K.dat")
    candidates = a_priori.get_large_itemset(3)
    iprint("L3", candidates[3], True)


if __name__ == "__main__":
    setup_logging()
    test_get_next_candidates()
    test_toy_dataset_large_itemsets()
    test_large_dataset()
