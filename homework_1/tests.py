import string
from pprint import pprint

from text_similarity import LSH, CompareSets, CompareSignatures, MinHashing, Shingling
from utils import test


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


def get_fradulent_email_shingling(force_new=False):
    directory = "./emails"
    pickle_path = "fradulent_emails_shingling.pickle"
    if not force_new and os.path.isfile("fradulent_emails_shingling.pickle"):
        shingling = Shingling.load_from_file(pickle_path)
    else:
        shingling = Shingling(k=6, path=pickle_path)
        for filename in os.listdir(directory):
            content = ""
            with open(f"{directory}/{filename}", "r") as f:
                content = f.read()
            shingling.add_document(document=content, document_name=filename)
        shingling.save_to_file()
    return shingling


@test
def test_fradulent_email_jaccard():
    """Get 5 very similar fradulent emails and 5 very disimilar emails"""
    shingling = get_fradulent_email_shingling()

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
def test_fradulent_email_minhash_signatures():
    """Create minhash signatures for fradulent emails
    print a subset of 10, test two known similarities
    """
    shingling = get_fradulent_email_shingling(force_new=True)
    sorted_hashed_shingles = sorted(shingling.all_hashed_shingles)
    n_functions = 100
    signatures = MinHashing(n_functions=n_functions).build_minhash_signatures(
        sorted_hashed_shingles, shingling.doc2hashed
    )

    email1 = signatures["email-3480.txt"]
    email2 = signatures["email-3374.txt"]

    approx_similarity = CompareSignatures.approximate_jaccard_similarity(email1, email2)
    print(
        f"Approx similarity for email-3480.txt and email-3374.txt: {approx_similarity}"
    )

    return signatures


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
    # TODO: The disimilar approx is still well over 0 when using less than 150 hash functions
    # is this normal?! Is there something off with our hash functions?
    print(f"Disimilar Jaccard similarity {jaccard_similarity_disimilar}")
    print(
        f"Disimilar Approximate similarity {approx_similarity_disimilar} with {n_functions} hash functions"
    )


@test
def test_simple_lsh():
    """Get the candidate pairs for our simple documents
    """
    n_functions = 100

    shingler = Shingling(3)
    for letter, sentence in TestDocuments.generator():
        shingler.add_document(document=sentence, document_name=letter)
    shingles = sorted(shingler.get_all_hashed_shingles())
    signatures = MinHashing(n_functions=n_functions).build_minhash_signatures(
        shingles, shingler.doc2hashed
    )

    bands = 20
    rows = 5
    lsh = LSH(n=n_functions, r=rows, b=bands)
    print(f"Approx threshhold is: {lsh.approx_threshold}, with n = {n_functions}, b = {bands} and r = {rows}")
    dup_buckets = {}
    for letter, signature in signatures.items():
        lsh_for_sig = lsh.get_lsh_for_signature(signature)
        buckets = lsh.insert_lsh_in_bucket(letter, lsh_for_sig)
        buckets = lsh.prepare_dup_buckets(buckets, letter)
        dup_buckets[letter] = buckets
    pprint(dup_buckets)


if __name__ == "__main__":
    test_simple()
    test_simple_build_minhash_signatures()
    test_simple_compare_jaccard_and_minhash_signatures()
    # test_fradulent_email_jaccard()
    # test_fradulent_email_minhash_signatures()
    test_simple_lsh()
