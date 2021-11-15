HW1

# Homework 1

**Authors**: Evita Stenqvist (920524-1020) and 

## Summary

As a summary we include the complete output from `tests.py`:

```txt
class TestDocuments:
    A = "The dog which chased the cat"
    B = "The dog that chased the cat"
    C = "Chased the cat, the dog did"
    D = "Like a cat on a hot tin roof"
    E = "The brits call football..."
    F = "The yanks call football..."
    G = "The dog likes football, but not the cat"
    H = "Soccer is just football"
    I = "The cat plots giving the dog a chocolate delight"
    J = "What a fright, this spite, at midnight"

 => test_simple 
Trivial jaccard test with two very similar sentences
Similarity between A and B 0.6


 => test_simple_build_minhash_signatures 
Build signatures for our simple sentences
Signatures for 20 hash functions
A: [11, 3, 31, 39, 12, 4, 22, 12, 10, 13, 0, 6, 3, 1, 4, 5, 5, 12, 1, 3]
B: [21, 3, 28, 18, 10, 4, 22, 12, 10, 13, 0, 17, 3, 1, 17, 0, 5, 12, 1, 3]
C: [15, 3, 26, 24, 7, 4, 46, 6, 10, 4, 0, 1, 3, 1, 13, 4, 5, 1, 1, 15]
D: [5, 7, 17, 0, 1, 1, 3, 1, 2, 8, 10, 4, 0, 4, 24, 5, 2, 6, 11, 4]
E: [31, 8, 35, 2, 6, 27, 21, 11, 19, 2, 3, 2, 65, 8, 2, 1, 23, 8, 1, 3]
F: [31, 8, 16, 2, 6, 9, 22, 18, 19, 23, 3, 2, 2, 8, 2, 1, 14, 7, 1, 3]
G: [0, 3, 20, 3, 6, 6, 3, 5, 2, 13, 0, 18, 66, 8, 2, 1, 6, 13, 1, 3]
H: [2, 2, 27, 30, 5, 27, 5, 18, 12, 6, 23, 33, 1, 10, 2, 1, 4, 0, 2, 27]
I: [1, 3, 18, 6, 8, 1, 2, 10, 3, 9, 0, 3, 68, 0, 6, 2, 3, 2, 0, 0]
J: [8, 3, 24, 12, 7, 1, 6, 3, 0, 1, 0, 7, 79, 5, 0, 0, 0, 1, 41, 0]


 => test_simple_compare_jaccard_and_minhash_signatures 
Compare two very similar sentences aswell as two disimilar
    for the jaccard similarity and the minhash approximation.
    
A: The dog which chased the cat
B: The dog that chased the cat
H: Soccer is just football 

Similar Jaccard similarity 0.6
Similar Approximate similarity 0.62 with 100 hash functions
Disimilar Jaccard similarity 0.0
Disimilar Approximate similarity 0.0 with 100 hash functions


 => test_simple_lsh 
Get the candidate pairs for our simple documents
Approx threshhold is: 0.50, with n = 24, b = 8 and r = 3 

Found candidate pairs: {'B': {'A'}, 'C': {'A', 'B'}, 'F': {'E'}} 

B: The dog that chased the cat
        A: The dog which chased the cat
C: Chased the cat, the dog did
        A: The dog which chased the cat
        B: The dog that chased the cat
F: The yanks call football...
        E: The brits call football...
```

## Files

Our submission consists of three files, `text_similarity.py`, `tests.py` and `utils.py`. The first is our implementation and the second the proof of work. The third merely contains a decorator and prestored primes. 

The only requirement is `python3.9^`, all imports are from the basic python module library.

To see output from the implementation:

```sh
python tests.py
```

## Tasks

Below the tasks and the most relevant code snippets are provided. See `text_similarity.py` for the complete implementations.

### Shingling

Simply takes a document and creates a set of its hashed shingles given a length of shingle $k$. The class keeps track of all seen shingles which can be used in the next steps.

```py
class Shingling:
    def add_document(self, document: str, document_name: str) -> list[int]:
        document = self.prepare_document(document)

        number_of_shingles = len(document) + 1 - self.k

        hashed_document = set()
        for index in range(number_of_shingles):
            shingle = document[index : index + self.k]
            hashed_shingle = hash(shingle)
            self.all_hashed_shingles.add(hashed_shingle)
            hashed_document.add(hashed_shingle)
        self.doc2hashed[document_name] = hashed_document
    return hashed_document
```

### Jaccard similarity

Given two sets created from the shingling class, return the Jaccard similarity.

```py
class CompareSets:
    def jaccard_similarity(A: set, B: set) -> float:
        intersection = len(A.intersection(B))
        union = len(A.union(B))
        return intersection / union
```

### MinHashing 

We chose to implement the multiple hash-functions as opposed to the multiple permutations. Seeing as the "point" of the homework is not to generate primes (we hope) we chose to prestore 152 primes in our `utils.py` file.

```py
class MinHashing:
    def generate_hash_functions(self, n=100):
        if n > len(primes):
            raise Exception("Not enough prestored primes!")
        for prime in primes[:n]:
            a = random.randint(prime // 2, prime - 1)
            b = random.randint(prime // 2, prime - 1)
            func = self.linear_hash(a, b, prime)
            self.hash_functions.append(func)

    def build_minhash_signatures(
        self, items: set, doc2items: dict[str, set], print_updates: bool = False
    ) -> dict[str, list[int]]:
        signatures = {
            doc_identifier: [math.inf] * self.n_functions
            for doc_identifier in doc2items.keys()
        }
        for index, item in enumerate(items):
            row_values = [func(index) for func in self.hash_functions]
            if index != 0 and index % 100000 == 0:
                print(f"Done row {index} out of {len(items)}", flush=True)
            for doc_identifier, item_set in doc2items.items():
                if item in item_set:
                    for index, value in enumerate(signatures[doc_identifier]):
                        if row_values[index] < value:
                            signatures[doc_identifier][index] = row_values[index]
        return signatures
```

### Fraction similarity

Given two signatures, compute the fraction of overlapping elements by comparing the signature parts one by one and seeing if they are equal.

```py
class CompareSignatures:
    def approximate_jaccard_similarity(A: list, B: list):
        assert len(A) == len(B), "Length of signatures should be equal"
        # Naive way
        equal_count = 0
        length = len(A)
        for index in range(length):
            if A[index] == B[index]:
                equal_count += 1
        approx_similarity = equal_count / length
        return approx_similarity
```

### LSH

Provided documents of signatures, find the candidate pairs by using the banding and row method.

```py
class LSH:
    def get_lsh_for_signature(self, signature) -> list[int]:
        lsh = []
        for i in range(self.b):
            # We make it a tuple as list is unhashable
            band = tuple(signature[i * self.r : i * self.r + self.r])
            lsh.append(hash(band))
        return lsh

    def insert_lsh_in_bucket(self, doc_id, lsh):
        buckets = []
        for i, band in enumerate(lsh):
            if doc_id not in self.cache[i][band]:
                buckets.append(self.cache[i][band])
                self.cache[i][band].append(doc_id)
        return buckets

    def get_candidate_pairs_for_signatures(self, signatures: dict):
        all_candidate_pairs = {}
        for id, signature in signatures.items():
            lsh_for_signature = self.get_lsh_for_signature(signature)
            buckets = self.insert_lsh_in_bucket(id, lsh_for_signature)
            # Flatten the buckets
            candidate_pairs = self.get_candidate_pairs(buckets, id=id)
            all_candidate_pairs[id] = candidate_pairs
        # Only return the id's that actually have candidate pairs
        return {
            id: candidate_pairs
            for id, candidate_pairs in all_candidate_pairs.items()
            if candidate_pairs
        }
```