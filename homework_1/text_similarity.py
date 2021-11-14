from dataclasses import dataclass, field
from typing import Callable
from functools import reduce
from collections import defaultdict
from utils import primes, test
import math
import random
import os
import pickle


@dataclass
class Shingling:
    k: int
    all_hashed_shingles: set[int] = field(default_factory=set)
    doc2hashed: dict = field(default_factory=dict)
    path: str = "shingling.pickle"

    @staticmethod
    def prepare_document(document):
        # The simplest of replacements, newlines and . become a space
        return document.replace("\n", " ").replace(".", " ")

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

    def add_documents(self, documents: dict[str, str]):
        for document_name, document in documents.items():
            self.add_document(document, document_name)

    def get_all_hashed_shingles(self) -> list[int]:
        assert len(self.all_hashed_shingles) != 0, "all_hashed_shingles shouldn't be 0!"

        return self.all_hashed_shingles

    def get_doc2hashed(self) -> dict[str, str]:
        assert len(self.doc2hashed.keys()) != 0, "doc2hashed shouldn't be 0!"
        return self.doc2hashed

    def save_to_file(self):
        with open(self.path, "wb") as f:
            data_dict = {
                "k": self.k,
                "all_hashed_shingles": self.all_hashed_shingles,
                "doc2hashed": self.doc2hashed,
            }
            pickle.dump(data_dict, f)

    @classmethod
    def load_from_file(cls, path) -> "Shingling":
        if not os.path.isfile(path):
            raise Exception("Previous runs have not been saved to file.")
        with open(path, "rb") as f:
            data_dict = pickle.load(f)
            shingling = Shingling(k=data_dict["k"])
            shingling.all_hashed_shingles = data_dict["all_hashed_shingles"]
            shingling.doc2hashed = data_dict["doc2hashed"]
            return shingling


class CompareSets:
    def jaccard_similarity(A: set, B: set) -> float:
        intersection = len(A.intersection(B))
        union = len(A.union(B))
        return intersection / union


class MinHashing:
    hash_functions: list[Callable] = []
    n_functions: int

    def __init__(self, n_functions=100):
        self.n_functions = n_functions
        self.generate_hash_functions(n_functions)

    @staticmethod
    def linear_hash(a, b, prime, print_func=False):
        print_func and print(f"{a}x + {b} mod {prime}")

        def func(x):
            return (a * x + b) % prime

        return func

    def generate_hash_functions(self, n=100):
        if n > len(primes):
            raise Exception("Not enough prestored primes!")
        for prime in primes[:n]:
            a = random.randint(1, prime - 1)
            b = random.randint(1, prime - 1)
            func = self.linear_hash(a, b, prime)
            self.hash_functions.append(func)

    def build_minhash_signatures(
        self, items: set, doc2items: dict[str, set], print_updates: bool = False
    ) -> dict[str, list[int]]:
        minhashed = {
            doc_identifier: [math.inf] * self.n_functions
            for doc_identifier in doc2items.keys()
        }
        for index, item in enumerate(items):
            row_values = [func(index) for func in self.hash_functions]
            if index != 0 and index % 100000 == 0:
                print(f"Done row {index} out of {len(items)}", flush=True)
            for doc_identifier, item_set in doc2items.items():
                if item in item_set:
                    for index, value in enumerate(minhashed[doc_identifier]):
                        if row_values[index] < value:
                            print_updates and print(
                                f"Changing minhash_{index} value for {doc_identifier} from {minhashed[doc_identifier][index]} to {row_values[index]}"
                            )
                            minhashed[doc_identifier][index] = row_values[index]
        return minhashed


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


@dataclass
class LSH:
    n: int = 100
    r: int = 5
    b: int = 20

    cache: list = field(default_factory=list)

    @property
    def approx_threshold(self):
        return (1 / self.b) ** (1 / self.r)

    def __post_init__(self):
        assert self.r * self.b == self.n, "r*b should be n!"
        self.cache = [defaultdict(list) for _ in range(self.b)]

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

    @staticmethod
    def prepare_dup_buckets(buckets, id=None):
        all = list(set(reduce(list.__add__, buckets, [])))
        if id:
            all.remove(id)
        return all
