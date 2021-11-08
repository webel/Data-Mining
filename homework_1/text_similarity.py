from dataclasses import dataclass, field
from typing import Callable
from utils import primes, test
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

    @staticmethod
    def generator():
        letters = string.ascii_uppercase[:10]
        for letter in letters:
            yield letter, getattr(TestDocuments, letter)

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
        self, items: set, doc2items: dict[str, set]
    ) -> dict[str, list[int]]:
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


@test
def test_simple():
    """Trivial jaccard test with two very similar sentences"""
    shingling = Shingling(k=3)
    shingling.add_documents(dict(A=TestDocuments.A, B=TestDocuments.B))
    A = shingling.doc2hashed["A"]
    B = shingling.doc2hashed["B"]

    similarity = CompareSets.jaccard_similarity(A, B)
    print(f"Similarity between A and B {similarity}")
    return similarity


@test
def test_fradulent_email_jaccard():
    """Get 5 very similar fradulent emails and 5 very disimilar emails"""
    directory = "./emails"
    pickle_path = "fradulent_emails_shingling.pickle"
    if os.path.isfile("fradulent_emails_shingling.pickle"):
        shingling = Shingling.load_from_file(pickle_path)
    else:
        shingling = Shingling(k=7, path=pickle_path)
        for filename in os.listdir(directory):
            content = ""
            with open(f"{directory}/{filename}", "r") as f:
                content = f.read()
            shingling.add_document(document=content, document_name=filename)
        shingling.save_to_file()

    doc2hashed = shingling.doc2hashed

    similar_n = 5
    disimilar_n = 5
    similar_threshhold = 0.65
    disimilar_threshhold = 0.05
    print("Jaccard similarity between pairs")
    for email1 in doc2hashed.keys():
        if similar_n == 0 and disimilar_n == 0:
            break
        for email2 in doc2hashed.keys():
            if email1 == email2:
                continue
            jacc = CompareSets.jaccard_similarity(
                doc2hashed[email1], doc2hashed[email2]
            )
            if jacc > similar_threshhold and similar_n > 0:
                print(f"({email1}, {email2}) = {jacc} \n")
                similar_n -= 1
            if jacc <= disimilar_threshhold and disimilar_n > 0:
                print(f"({email1}, {email2}) = {jacc} \n")
                disimilar_n -= 1
            if similar_n == 0 and disimilar_n == 0:
                break


@test
def test_simple_build_minhash_signatures():
    """Build signatures for our simple sentences"""
    shingling = Shingling(k=3)
    for letter, document in TestDocuments.generator():
        shingling.add_document(document=document, document_name=letter)

    n_functions = 20
    all_hashed, doc2hashed = shingling.all_hashed_shingles, shingling.doc2hashed
    signatures = MinHashing(n_functions=n_functions).build_minhash_signatures(
        all_hashed, doc2hashed
    )
    print(f"Signatures for {n_functions} hash functions")
    for key, value in signatures.items():
        print(f"{key}: {value}")
    return signatures


@test
def test_compare_jaccard_and_minhash_signatures():
    """Compare two very similar sentences aswell as two disimilar
    for the jaccard similarity and the minhash approximation.
    """
    shingling = Shingling(k=5)
    shingling.add_documents(
        {"A": TestDocuments.A, "B": TestDocuments.B, "H": TestDocuments.H}
    )
    print(f"A: {TestDocuments.A}")
    print(f"B: {TestDocuments.B}")
    print(f"H: {TestDocuments.H} \n")

    all_hashed = shingling.get_all_hashed_shingles()
    doc2hashed = shingling.get_doc2hashed()

    n_functions = 200
    signatures = MinHashing(n_functions=n_functions).build_minhash_signatures(
        all_hashed, doc2hashed
    )

    jaccard_similarity_similar = CompareSets.jaccard_similarity(
        doc2hashed["A"], doc2hashed["B"]
    )
    jaccard_similarity_disimilar = CompareSets.jaccard_similarity(
        doc2hashed["A"], doc2hashed["H"]
    )

    approx_similarity_similar = CompareSignatures.approximate_jaccard_similarity(
        signatures["A"], signatures["B"]
    )
    approx_similarity_disimilar = CompareSignatures.approximate_jaccard_similarity(
        signatures["A"], signatures["H"]
    )
    print(f"Similar Jaccard similarity {jaccard_similarity_similar}")
    print(
        f"Similar Approximate similarity {approx_similarity_similar} with {n_functions} hash functions"
    )
    # TODO: The disimilar approx is still well over 0 when using less than 150 hash functions
    # is this normal?! Is there something off with our hash functions?
    print(f"Disimilar Jaccard similarity {jaccard_similarity_disimilar}")
    print(
        f"Disimilar Approximate similarity {approx_similarity_disimilar} with {n_functions} hash functions"
    )


if __name__ == "__main__":
    # test_fradulent_email_jaccard()
    test_simple()
    test_simple_build_minhash_signatures()
    test_compare_jaccard_and_minhash_signatures()
