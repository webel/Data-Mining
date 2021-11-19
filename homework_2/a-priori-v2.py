from collections import defaultdict
from itertools import chain, combinations
from functools import lru_cache
from pprint import pprint


def flatten(list_of_lists):
    return chain.from_iterable(list_of_lists)


class APriori:
    dataset_path: str
    itemset: dict = defaultdict(lambda: 0)

    def __init__(self, dataset_path, constant_support=None):
        self.dataset_path = dataset_path
        self.support = constant_support

    def get_line(self):
        """Get a line from our datafile one at a time"""
        with open(self.dataset_path, "r") as f:
            for line in f:
                yield sorted(map(int, line.split()))

    def set_support_threshhold(self):
        """Calculate depending on number of unique items in our itemset"""
        self.support = round(len(self.itemset) * 0.01)

    def prune_non_frequent(self):
        """Prune the unnecessary items from our itemset, i.e. the items that have
        a lower count than a certain threshhold"""
        to_delete = [key for key in self.itemset if self.itemset[key] <= self.support]
        for key in to_delete:
            del self.itemset[key]

    def get_possible_combinations(self, k):
        keys = list(self.itemset)
        if k == 2:
            return combinations(keys, 2)
        # Join self.itemset with itself
        key_sets = list(map(set, sorted(keys)))
        combos = set()
        for i_item in key_sets:
            for j_item in key_sets[1:]:
                union = sorted(i_item.union(j_item))
                if len(union) == k:
                    combos.add(tuple(union))
        return combos

    def get_possible_combinations2(self, k):
        keys = sorted(list(self.itemset))
        if k == 2:
            return combinations(keys, 2)
        combos = set()
        for item in combinations(keys, k - 1):
            # TODO check necessary sort
            combo = sorted(set(flatten(item)))
            if len(combo) == k:
                combos.add(tuple(combo))
        return combos

    def get_possible_combinations3(self, k):
        keys = sorted(list(self.itemset))
        if k == 2:
            return combinations(keys, 2)
        keys = set(flatten(keys))
        # TODO check sub-combinations indeed in self.itemset
        return combinations(keys, k)

    def initial_single_count(self):
        for line in self.get_line():
            for item in line:
                self.itemset[item] += 1

    def check_combination_in_line(self, line, combination):
        # PROBLEM-BARNET
        for value in combination:
            if value not in line:
                return False
        return True
    
    # @lru_cache(maxsize=10)
    # def get_line_combination(self, line, k):
    #     return combinations(line, k)

    def count_support(self, k):
        """Count the number of item combinations for k per line in datafile"""
        next_itemset = defaultdict(lambda: 0)
        count = 0

        # ~~We need to cast to list as otherwise the generator is consumed on first run through~~
        # We do not cast possible_combinations to list here as it is cheaper to create a new generator
        # for each line. Like 50x cheaper timewise.
    
        for line in self.get_line():
            possible_combinations = self.get_possible_combinations3(k)
            # ~~TODO> beat 60 seconds for 500~~
            # TODO> beat 2.5 seconds for 500
            if count != 0 and count % 1000 == 0:
                print(f"processed {count} lines")
            # NOTE: Break early for testing purposes
            # if count != 0 and count % 5000 == 0:
            #     break
            # NOTE: This is sorted, I've tested, although could do one assert on one item
            line_combinations = combinations(line, k)
            for combination in line_combinations:
                if combination in possible_combinations:
                    next_itemset[combination] += 1

            # NOTE: tested switching and this takes double the time
            # for combination in possible_combinations:
            #     if combination in line_combinations:
            #         next_itemset[combination] += 1

            # for combination in possible_combinations:
            # NOTE This check stands for 95% of the time and takes an ungodly amount of time
            # You can see this by running python -m cProfile filename.py
            #     exists = self.check_combination_in_line(line, combination)
            #     if exists:
            #         next_itemset[combination] += 1
            count += 1

        self.itemset = next_itemset

    def get_candidates(self, k):
        """Build candidate itemset for a provided k"""
        print("Initial count...")
        self.initial_single_count()

        if not self.support:
            print("Setting threshhold...")
            self.set_support_threshhold()

        print("Pruning singletones...")
        self.prune_non_frequent()

        for current_k in range(2, k + 1):
            print("Count support...")
            self.count_support(current_k)

            print(f"k={current_k} - before pruning. Currently {len(self.itemset)} keys")
            #print(self.itemset)
            self.prune_non_frequent()
            print(f"k={current_k} - after pruning. Currently {len(self.itemset)} keys")
            #print(self.itemset)
        return self.itemset

    def naive_count_support(self, k):
        """Count the number of item combinations for k per line in datafile"""
        next_itemset = defaultdict(lambda: 0)
        for line in self.get_line():
            possible_combinations = combinations(line, k)
            for combination in possible_combinations:
                next_itemset[combination] += 1
        self.itemset = next_itemset

    def naive_get_candidates(self, k):
        """Build candidate itemset for a provided k"""
        for current_k in range(1, k + 1):
            self.naive_count_support(current_k)
            if not self.support:
                self.set_support_threshhold()
            self.prune_non_frequent()
        return self.itemset


def simple_test():
    a_priori = APriori("simple_test.dat", 1)
    candidates = a_priori.get_candidates(3)
    assert len(candidates.keys()) == 1, "should only have one set of keys"
    assert candidates[(2, 3, 5)] == 2, "should be 2"
    print(candidates)


def real_test():
    a_priori = APriori("T10I4D100K.dat")
    candidates = a_priori.get_candidates(3)
    pprint(candidates)


if __name__ == "__main__":
    #simple_test()
    real_test()
