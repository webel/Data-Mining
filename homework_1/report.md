# Homework 1

**Authors**: Evita Stenqvist (920524-1020) and Linnea Fredriksson (930913-3008)

## Summary

As a summary we include the complete output from `tests.py`, please see the file for the 10 simple sentences named A through J:

```txt
 => test_simple_jaccard 
Trivial jaccard test with two very similar sentences
Similarity between A and B 0.59

Timed: 0.00 seconds 


 => test_simple_build_minhash_signatures 
Build signatures for our simple sentences
Signatures for 10 hash functions
A: [789, 479, 81, 48, 184, 314, 286, 346, 250, 88]
B: [379, 717, 81, 745, 380, 314, 1289, 346, 250, 408]
C: [470, 836, 81, 745, 478, 314, 180, 78, 191, 994]
D: [242, 211, 84, 1163, 355, 331, 75, 28, 432, 861]
E: [333, 92, 227, 141, 576, 280, 233, 832, 68, 1447]
F: [743, 92, 227, 141, 86, 280, 233, 832, 68, 1012]
G: [288, 330, 227, 257, 61, 280, 22, 137, 68, 106]
H: [151, 360, 227, 257, 159, 280, 1341, 723, 9, 559]
I: [379, 449, 376, 25, 380, 382, 497, 614, 373, 70]
J: [60, 3, 519, 466, 257, 263, 1130, 78, 491, 221]

Timed: 0.00 seconds 


 => test_simple_compare_jaccard_and_minhash_signatures 
Compare two very similar sentences aswell as two disimilar
    for the jaccard similarity and the minhash approximation.
    
A: The dog which chased the cat
B: The dog that chased the cat
H: Soccer is just football 

Similar Jaccard similarity 0.5862068965517241
Similar Approximate similarity 0.63 with 100 hash functions
Disimilar Jaccard similarity 0.0
Disimilar Approximate similarity 0.0 with 100 hash functions

Timed: 0.00 seconds 


 => test_simple_lsh 
Get the candidate pairs for our simple documents
Approx threshhold is: 0.50, with n = 24, b = 8 and r = 3 

Found candidate pairs: {'B': {'A'}, 'C': {'B', 'A'}, 'F': {'E'}} 

B: The dog that chased the cat
        A: The dog which chased the cat
C: Chased the cat, the dog did
        B: The dog that chased the cat
        A: The dog which chased the cat
F: The yanks call football...
        E: The brits call football...

Timed: 0.00 seconds 


 => test_fradulent_email_jaccard 
Get 5 very similar fradulent emails and 5 very disimilar emails
Jaccard similarity between pairs
(email-1283.txt, email-3480.txt) = 0.028584927947082447 

(email-1283.txt, email-3374.txt) = 0.027196149217809867 

(email-2952.txt, email-3480.txt) = 0.027426663486763654 

(email-2952.txt, email-2931.txt) = 0.6901117087298304 

(email-2952.txt, email-1395.txt) = 0.684931506849315 

(email-2952.txt, email-1396.txt) = 0.684931506849315 

(email-2952.txt, email-3374.txt) = 0.027750730282375853 

(email-3494.txt, email-3480.txt) = 0.023322775698243592 

(email-3494.txt, email-3493.txt) = 1.0 

(email-3480.txt, email-3374.txt) = 0.8402084237950499 


Timed: 0.02 seconds 


 => test_fradulent_email_minhash_signatures 
Create minhash signatures for fradulent emails
    test two known documents similarity
    
Approx similarity for email-3480.txt and email-3374.txt: 0.864

Timed: 0.61 seconds 


 => test_fradulent_email_lsh 
Get the candidate pairs for our fradulent emails
Approx threshhold is: 0.55, with n = 100, b = 20 and r = 5 

Found candidate pairs: 

{'email-1395.txt': {'email-2952.txt', 'email-2931.txt'},
 'email-1396.txt': {'email-2931.txt', 'email-2952.txt', 'email-1395.txt'},
 'email-2931.txt': {'email-2952.txt'},
 'email-3374.txt': {'email-3480.txt'},
 'email-3493.txt': {'email-3494.txt'}}

Timed: 0.58 seconds 
```

## Files

Our submission consists of three files, `text_similarity.py`, `tests.py` and `utils.py`. The first is our implementation and the second the proof of work. The third merely contains a decorator and prestored primes. We have included a subset of 10 emails from our email dataset consisting of over 4000 emails.

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

We chose to implement the multiple hash-functions as opposed to the multiple permutations. Seeing as the "point" of the homework is not to generate primes (we hope) we chose to prestore primes in our `utils.py` file.

```py
class MinHashing:
    def generate_hash_functions(self, n=100):
        if n > len(primes):
            raise Exception("Not enough prestored primes!")
        for prime in primes[::-1][:n]:
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