from dataclasses import dataclass
from functools import total_ordering
import logging
from collections import Counter, defaultdict
from itertools import combinations

from utils import flatten, iprint, progress, test, setup_logging


class APriori:
    dataset_path: str
    itemsets: defaultdict[int, Counter]
    n_transactions: int
    support = int

    def __init__(self, dataset_path, support=0.01):
        self.dataset_path = dataset_path
        self.itemsets = defaultdict(Counter)
        self.n_transactions = 0

        assert support > 0 and support <= 1, "Support should be between 0 and 1"
        self.support = support

        self.first_pass()

    def get_line(self):
        """Get a line from our datafile one at a time"""
        with open(self.dataset_path, "r") as f:
            for line in f:
                yield map(int, line.split())

    def set_support_threshhold(self):
        """Calculate depending on number of transactions in our dataset"""
        self.support = self.n_transactions * self.support
        logging.debug(f"Set threshhold to {self.support}")

    def first_pass(self):
        logging.debug("=== FIRST PASS ===")
        logging.debug("Initial count...")
        for line in self.get_line():
            self.n_transactions += 1
            for item in line:
                self.itemsets[1][tuple([item])] += 1
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

    @staticmethod
    def check_subcandidates(itemset, candidate, k):
        """Check that subcombinations of a candidate are indeed in our previous itemset
        Make all sub-combinations of the candidate, e.g.
        ('A', 'B', 'C') -> ('A', 'B'), ('A', 'C'), ('B', 'C')
        And check if all these exist in itemset[k-1]
        """
        return all(
            subcandidate in itemset for subcandidate in combinations(candidate, k - 1)
        )

    @staticmethod
    def get_next_candidates(itemset):
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
        keys = list(itemset)
        # Get k from provided itemset
        k = len(keys[0]) + 1

        keys = flatten(keys)
        if k == 2:
            # If k is 2, we don't need to check subsets
            yield from combinations(sorted(keys), k)
        else:
            items = sorted(set(keys))
            potential_candidates = combinations(items, k)
            # Now we need to check all the subsets of a possible candidate
            candidates = (
                candidate
                for candidate in potential_candidates
                if APriori.check_subcandidates(itemset, candidate, k)
            )
            yield from candidates

    def get_itemset_for_k(self, k):
        """Count the number of item combinations for k per line in datafile"""
        info_log = logging.INFO >= logging.root.level
        info_log and progress(0, self.n_transactions, prefix=f"Progress for k={k}:")

        candidates = self.get_next_candidates(self.itemsets[k - 1])
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

            if not self.itemsets[current_k - 1]:
                logging.debug("No previous large itemset, breaking.")
                break
            self.get_itemset_for_k(current_k)

            self.prune_non_frequent(k=current_k)
        return self.itemsets


@dataclass
@total_ordering
class Rule:
    """Represent a rule of the form X -> Y where X and Y are itemsets from the first part of the Apriori algorithm.

    Arguments:
    left            -- the left part of the rule
    right           -- the right part of the rule
    confidence      -- The conditional probability of X -> Y, P(Y|X)
    left_count      -- The probability of the union of X and Y, P(X and Y)
    """

    left: tuple
    right: tuple
    confidence: float
    support: float

    def __str__(self):
        """How to stringify a rule"""
        return f"{set(self.left)} -> {set(self.right)} (Confidence: {self.confidence:0.2f}. Support: {self.support:0.2f})"

    def __eq__(self, other):
        """Two rules are equal if their left and right are equal"""
        return (self.left, self.right) == (other.left, other.right)

    def __lt__(self, other):
        """The rule is less than another rule if it's confidence is less than
        Secondly, sort on length of left
        """
        return (len(self), self.confidence, len(self.left)) < (
            len(self),
            other.confidence,
            len(other.left),
        )

    def __len__(self):
        """The length of a rule is the length of the left side plus the right side"""
        return len(self.left) + len(self.right)


class GenerateRules:
    confidence: float
    itemsets: dict[int, Counter]
    n_transactions: int

    def __init__(self, itemsets, n_transactions, confidence=0.5):
        self.itemsets = itemsets
        self.n_transactions = n_transactions
        self.confidence = confidence

    def _count(self, itemset):
        return self.itemsets[len(itemset)][itemset]

    def _check_right_with_itemset(self, itemset, right):
        left = tuple(sorted(set(itemset).difference(right)))
        joint_count = self._count(itemset)
        left_count = self._count(left)
        conf = joint_count / left_count
        if conf >= self.confidence:
            yield Rule(left, right, conf, joint_count / self.n_transactions)
        else:
            return False

    def ap_genrules(
        self,
        k: int,
        itemset: Counter,
        h_m: list,
    ):
        """Recursively generate rules as described in the paper."""
        if k <= (len(h_m[0]) + 1):
            # If the right handside is larger or equal to our k, we stop
            return
        h_m_next = list(APriori.get_next_candidates(h_m))
        for right in h_m_next:
            yielded = self._check_right_with_itemset(itemset, right)
            if not yielded:
                h_m_next.remove(right)
            else:
                yield from yielded
        if h_m_next:
            yield from self.ap_genrules(k, itemset, h_m_next)

    def get(self):
        """Given itemsets, generate rules of the form X -> Y provided a confidence value and threshhold.
        This is an implementation of the algorithm presented in the paper under section 3.1, i.e. "A Faster Algorithm".
        """
        logging.debug("Generating rules")
        for k, sets in self.itemsets.items():
            if k == 1:
                continue

            for itemset in sets:
                for right in combinations(itemset, 1):
                    yield from self._check_right_with_itemset(itemset, right)

                h_1 = list(combinations(itemset, 1))
                yield from self.ap_genrules(k, itemset, h_1)


@test
def test_get_next_candidates():
    """Check that the next candidates are expected given a known current large set"""
    large_itemset = {(1, 3): 2, (2, 3): 2, (2, 5): 3, (3, 5): 2}
    iprint("Large itemset (L2)", large_itemset)
    candidates = list(APriori.get_next_candidates(large_itemset))
    print("Candidates:", candidates)
    # Happens to be same as the final L
    assert [(2, 3, 5)] == candidates


@test
def test_toy_dataset_large_itemsets():
    """Check that the large itemsets are as expected for k's 1 through 4 for our toy dataset"""
    a_priori = APriori("simple_test.dat", support=0.4)
    itemsets = a_priori.get_large_itemset(4)
    large_itemsets = [
        {(1,): 2, (3,): 3, (2,): 3, (5,): 3},
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
def test_itemsets_for_large_dataset():
    """Test itemset generation for the provided dataset of the homework."""
    a_priori = APriori("T10I4D100K.dat")
    candidates = a_priori.get_large_itemset(3)
    iprint("L3", candidates[3])


@test
def test_simple_rule_generation():
    """Test a very simple dataset to verify the rule generation"""
    itemsets = {1: {("a",): 3, ("b",): 2, ("c",): 1}, 2: {("a", "b"): 2, ("a", "c"): 1}}
    rules = GenerateRules(confidence=1, itemsets=itemsets, n_transactions=3).get()
    iprint("L1", itemsets[1])
    iprint("L2", itemsets[2])
    for rule in sorted(rules):
        print(rule)


@test
def test_toy_dataset_itemset_and_rule_generation():
    """Tests our dataset from itemset to rule generation"""
    a_priori = APriori("simple_test.dat", support=0.4)
    itemsets = a_priori.get_large_itemset(3)

    for k, itemset in itemsets.items():
        iprint(k, itemset)

    rules = GenerateRules(
        confidence=0.5,
        itemsets=itemsets,
        n_transactions=a_priori.n_transactions,
    ).get()
    print("Rules: ")
    for rule in sorted(rules, reverse=True):
        print(rule)


@test
def test_large_dataset_itemset_and_rule_generation():
    """Tests the provided dataset from itemset to rule generation"""
    a_priori = APriori("T10I4D100K.dat", support=0.01)
    itemsets = a_priori.get_large_itemset(3)

    iprint("L3", itemsets[3])

    rules = GenerateRules(
        confidence=0.75,
        itemsets=itemsets,
        n_transactions=a_priori.n_transactions,
    ).get()
    for rule in sorted(rules, reverse=True):
        print(rule)


if __name__ == "__main__":
    setup_logging()
    test_get_next_candidates()
    test_toy_dataset_large_itemsets()
    test_itemsets_for_large_dataset()
    test_simple_rule_generation()
    test_toy_dataset_itemset_and_rule_generation()
    test_large_dataset_itemset_and_rule_generation()
