from typing import Callable
from pprint import pprint
from utils import primes
import math
import random
import os
import string
import pickle


class TestDocuments:
    A = "The dog which chased the cat"
    B = "The dog that chased the cat"
    C = "Chased the cat, the dog did"
    D = "Like a cat on a hot tin roof"
    E = "Football is a ball"
    F = "The yanks call footie soccer"
    G = "The dog likes football, but not the cat"
    H = "Soccer is all but a delight"
    I = "The cat plots giving the dog a chocolate delight"
    J = "What a fright, this spite, at midnight"


class Shingling:
    ### Instance attributes
    k: int
    document: str
    document_name: str
    hashed: set

    ### Class attributes
    all_hashed_shingles: set[int] = set()
    email2hashed: dict = {}
    path = "shingling.pickle"

    def __init__(self, k, document, document_name):
        self.k = k
        self.document = document
        self.document_name = document_name
        self.hashed = set()

    def prepare_document(self):
        # The simplest of replacements, newlines and . become a space
        self.document = self.document.replace("\n", " ").replace(".", " ")

    def populate_hashed(self):
        self.prepare_document()

        number_of_shingles = len(self.document) + 1 - self.k

        for index in range(number_of_shingles):
            shingle = self.document[index : index + self.k]
            hashed_shingle = hash(shingle)
            Shingling.all_hashed_shingles.add(hashed_shingle)
            self.hashed.add(hashed_shingle)
        Shingling.email2hashed[self.document_name] = self.hashed

    @classmethod
    def save_to_file(cls):
        with open(cls.path, "wb") as f:
            data_dict = {
                "all_hashed_shingles": cls.all_hashed_shingles,
                "email2hashed": cls.email2hashed,
            }
            pickle.dump(data_dict, f)

    @classmethod
    def load_from_file(cls):
        if not os.path.isfile(cls.path):
            raise Exception("Previous runs have not been saved to file.")
        with open(cls.path, "rb") as f:
            data_dict = pickle.load(f)
            return data_dict["all_hashed_shingles"], data_dict["email2hashed"]


class CompareSets:
    def jaccard_similarity(A: set, B: set) -> float:
        intersection = len(A.intersection(B))
        union = len(A.union(B))
        return intersection / union


def linear_hash(a, b, prime):
    print(f"{a}x + {b} mod {prime}")

    def func(x):
        return (a * x + b) % prime

    return func


class MinHashing:
    hash_functions: list[Callable] = []
    n_functions: int

    def __init__(self, n_functions=100):
        self.n_functions = n_functions
        self.generate_hash_functions(n_functions)

    def generate_hash_functions(self, n=100):
        if n > 100:
            raise Exception("Not enough prestored primes!")
        for prime in primes[:n]:
            a = random.randint(1, prime - 1)
            b = random.randint(1, prime - 1)
            func = linear_hash(a, b, prime)
            self.hash_functions.append(func)

    def build_minhash_signatures(self, items: set, doc2items: dict[str, set]):
        minhashed = {
            doc_identifier: [math.inf] * self.n_functions
            for doc_identifier in doc2items.keys()
        }
        for index, item in enumerate(items):
            row_values = [func(index) for func in self.hash_functions]
            for doc_identifier, item_set in doc2items.items():
                if item in item_set:
                    for index, value in enumerate(minhashed[doc_identifier]):
                        if row_values[index] < value:
                            # print(
                            #     f"Changing minhash_{index} value for {doc_identifier} from {minhashed[doc_identifier][index]} to {row_values[index]}"
                            # )
                            minhashed[doc_identifier][index] = row_values[index]
        return minhashed


def simple_test():
    """Trivial test with very similar sentences"""
    A = Shingling(3, TestDocuments.sentenceA).populate_hashed()
    B = Shingling(3, TestDocuments.sentenceB).populate_hashed()

    print(CompareSets.jaccard_similarity(A.hashed, B.hashed))


def fradulent_email_jaccard_test():
    directory = "./emails"

    for filename in os.listdir(directory):
        content = ""
        with open(f"{directory}/{filename}", "r") as f:
            content = f.read()
        shingler = Shingling(k=7, document=content, document_name=filename)
        shingler.populate_hashed()

    Shingling.save_to_file()
    email2hashed = Shingling.email2hashed

    similar_n = 5
    disimilar_n = 5
    similar_threshhold = 0.65
    disimilar_threshhold = 0.0
    for email1 in email2hashed.keys():
        if similar_n == 0 and disimilar_n == 0:
            break
        for email2 in email2hashed.keys():
            if email1 == email2:
                continue
            jacc = CompareSets.jaccard_similarity(
                email2hashed[email1], email2hashed[email2]
            )
            if jacc > similar_threshhold and similar_n > 0:
                print(f"{email1} and {email2} have jaccard similarity value {jacc} \n")
                similar_n -= 1
            if jacc <= disimilar_threshhold and disimilar_n > 0:
                print(f"{email1} and {email2} have jaccard similarity value {jacc} \n")
                disimilar_n -= 1
            if similar_n == 0 and disimilar_n == 0:
                break


def test_build_minhash_signatures():
    letters = string.ascii_uppercase[:10]
    for letter in letters:
        document = getattr(TestDocuments, letter)
        Shingling(k=3, document=document, document_name=letter).populate_hashed()
    Shingling.path = "test_documents.pickle"
    Shingling.save_to_file()

    all_hashed, email2hashed = Shingling.all_hashed_shingles, Shingling.email2hashed
    signatures = MinHashing(n_functions=20).build_minhash_signatures(
        all_hashed, email2hashed
    )
    pprint(signatures)


if __name__ == "__main__":
    # fradulent_email_jaccard_test()
    test_build_minhash_signatures()
