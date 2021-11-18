from collections import defaultdict
from itertools import combinations

dataset_path = "simple_test_abc.dat"

def first_count():
    # Key start with 0 count
    all_items = defaultdict(lambda: 0)
    with open(dataset_path, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            items = line.split()
            for i in items:
                all_items[i] += 1
    f.close()
    return all_items


def count_itemsets(itemsets):
    pass


def generate_candidate_itemsets(items, k):
    if k == 2:
        candidates = combinations(items, k)
        return candidates
    else:
        #TODO: need to check that every subset of the combinations also are frequent
        pass


def prune_non_frequent(itemset, s):
    to_delete = []
    for i in itemset:
        if itemset[i] <= s:
            to_delete.append(i)
    for j in to_delete:
        del itemset[j]
    print("\n To delete: ")
    print(to_delete)
    return itemset


def count_support_and_prune(C, k, s):
    itemsets = defaultdict(lambda: 0)
    with open(dataset_path, "r") as f:
        counter = 0
        while True:
            line = f.readline()
            if not line:
                break
            items = sorted(set(line.split()))
            bucket_combinations = generate_candidate_itemsets(items, k)
            for comb in bucket_combinations:
                if comb in C:
                    # TODO: varför blir det fel här?
                    #  Den hittar inte alla plus att det blir typ olika varje gång man kör koden?
                    print("this combination was in C! ")
                    print(comb)
                    itemsets[comb] += 1

            counter +=1
    print(f"\n Number of processed lines: {counter}")

    f.close()
    # Prune the itemset
    print("found this: ")
    print(itemsets)
    itemsets = prune_non_frequent(itemsets, s)
    return itemsets




def main():
    all_items = first_count()
    # find support threshold
    # s = round(len(all_items)*0.01)
    # NOTE: we set it to 1 for our very simple test! Change back for real data
    s = 1
    print(f"Support threshhold is: {s}")
    L1 = prune_non_frequent(all_items, s)
    L1 = sorted(set(L1))
    C2 = generate_candidate_itemsets(L1, 2)
    C2 = list(C2)
    assert list(C2) == [('A', 'B'), ('A', 'C'), ('A', 'E'), ('B', 'C'), ('B', 'E'), ('C', 'E')]
    # TODO: blir snyggare sen, men bara för test nu för olika k 
    k = 2
    L2 = count_support_and_prune(C2, k, s)
    print(L2)


main()
