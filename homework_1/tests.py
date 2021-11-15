import string
from pprint import pprint

from text_similarity import LSH, CompareSets, CompareSignatures, MinHashing, Shingling
from utils import test


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

    @staticmethod
    def generator():
        letters = string.ascii_uppercase[:10]
        for letter in letters:
            yield letter, getattr(TestDocuments, letter)


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
def test_simple_compare_jaccard_and_minhash_signatures():
    """Compare two very similar sentences aswell as two disimilar
    for the jaccard similarity and the minhash approximation.
    """
    shingling = Shingling(k=3)
    shingling.add_documents(
        {"A": TestDocuments.A, "B": TestDocuments.B, "H": TestDocuments.H}
    )
    print(f"A: {TestDocuments.A}")
    print(f"B: {TestDocuments.B}")
    print(f"H: {TestDocuments.H} \n")

    all_hashed = shingling.get_all_hashed_shingles()
    doc2hashed = shingling.get_doc2hashed()

    n_functions = 100
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
    print(f"Disimilar Jaccard similarity {jaccard_similarity_disimilar}")
    print(
        f"Disimilar Approximate similarity {approx_similarity_disimilar} with {n_functions} hash functions"
    )


@test
def test_simple_lsh():
    """Get the candidate pairs for our simple documents"""
    n_functions = 24

    shingler = Shingling(4)
    for letter, sentence in TestDocuments.generator():
        shingler.add_document(document=sentence, document_name=letter)
    shingles = sorted(shingler.get_all_hashed_shingles())
    signatures = MinHashing(n_functions=n_functions).build_minhash_signatures(
        shingles, shingler.doc2hashed
    )

    bands = 8
    rows = 3
    lsh = LSH(n=n_functions, r=rows, b=bands)
    print(
        f"Approx threshhold is: {lsh.approx_threshold:0.2f}, with n = {n_functions}, b = {bands} and r = {rows} \n"
    )
    found_candidate_pairs = lsh.get_candidate_pairs_for_signatures(signatures)
    print(f"Found candidate pairs: {found_candidate_pairs} \n")
    for id, candidate_pairs in found_candidate_pairs.items():
        document = getattr(TestDocuments, id)
        print(f"{id}: {document}")
        for candidate_id in candidate_pairs:
            candidate_document = getattr(TestDocuments, candidate_id)
            print(f"\t{candidate_id}: {candidate_document}")


if __name__ == "__main__":
    test_simple()
    test_simple_build_minhash_signatures()
    test_simple_compare_jaccard_and_minhash_signatures()
    test_simple_lsh()
