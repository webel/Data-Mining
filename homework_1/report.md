HW1

# Homework 1

**Authors**

## Summary

As a summary we include the complete output from `tests.py`:

```sh
```

## Files

Our submission consists of three files, `text_similarity.py`, `tests.py` and `utils.py`. The first is our implementation and the second the proof of work. The third merely contains a decorator and prestored primes. 

The only requirement is `python3.7>`, all imports are from the basic python module library.

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

### MinHashing 

We chose to implement the multiple hash-functions as opposed to the multiple permutations. Seeing as the "point" of the homework is not to generate primes (we hope) we chose to prestore 152 primes in our `utils.py` file.

### Fraction similarity

Given two signatures, compute the fraction of overlapping elements by comparing the signature parts one by one and seeing if they are equal.

### LSH

Provided documents of signatures, find the candidate pairs.