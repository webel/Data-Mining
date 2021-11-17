from itertools import combinations

def first_count():
    all_items = {}
    with open("T10I4D100K.dat", "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            items = line.split()
            for i in items:
                if i in all_items:
                    all_items[i] += 1
                else:
                    all_items[i] = 1
    f.close()
    print(all_items)
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
        if itemset[i] < s:
            to_delete.append(i)
    for j in to_delete:
        del itemset[j]
    print("to delete: ")
    print(to_delete)
    return itemset


def count_support_and_prune(C, k, s):
    itemsets = {}
    with open("T10I4D100K.dat", "r") as f:
        counter = 0
        while True:
            line = f.readline()
            if not line:
                break
            items = line.split()

            bucket_combinations = generate_candidate_itemsets(set(items), k)
            for comb in bucket_combinations:
                #print(comb)
                if comb in C:
                    # TODO: varför blir det fel här?
                    #  Den hittar inte alla plus att det blir typ olika varje gång man kör koden?
                    print("this combination was in C! ")
                    print(comb)
                    if comb in itemsets:
                        itemsets[comb] += 1
                    else:
                        itemsets[comb] = 1

            counter +=1

    f.close()
    print("counter: " + str(counter))
    # Prune the itemset
    print("found this: ")
    print(itemsets)
    itemsets = prune_non_frequent(itemsets, s)
    return itemsets




def main():
    all_items = first_count()
    # find support threshold
    s = round(len(all_items)*0.01)
    print(s)
    L1 = prune_non_frequent(all_items, s)
    C2 = generate_candidate_itemsets(L1, 2)
    k = 2
    L2 = count_support_and_prune(C2, k, s)
    print(L2)


main()
