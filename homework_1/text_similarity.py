from dataclasses import dataclass, field
import os


class TestDocuments:
    short = "abcab"
    sentenceA = "The dog which chased the cat"
    sentenceB = "The dog that chased the cat"


@dataclass
class Shingling:
    k: int
    # TODO make this document_file_path
    document: str
    hashed: set = field(default_factory=set)

    def read_document(self):
        """Read document contents from document_file_path
        :returns: document as str
        """
        pass

    def prepare_document(self):
        # The simplest of replacements, newlines and . become a space
        self.document = self.document.replace("\n", " ").replace(".", " ")

    def populate_hashed(self):
        self.prepare_document()

        number_of_shingles = len(self.document) + 1 - self.k

        for index in range(number_of_shingles):
            shingle = self.document[index : index + self.k]
            hashed_shingle = hash(shingle)
            self.hashed.add(hashed_shingle)


class CompareSets:
    def jaccard_similarity(A: set, B: set) -> float:
        intersection = len(A.intersection(B))
        union = len(A.union(B))
        return intersection / union


def simple_test():
    """Trivial test with very similar sentences"""
    A = Shingling(3, TestDocuments.sentenceA)
    B = Shingling(3, TestDocuments.sentenceB)

    for item in [A, B]:
        item.populate_hashed()

    print(CompareSets.jaccard_similarity(A.hashed, B.hashed))


def fradulent_email_test():
    directory = "./emails"
    email2hashed = {}

    for filename in os.listdir(directory):
        content = ""
        with open(f"{directory}/{filename}", "r") as f:
            content = f.read()
        shingler = Shingling(k=7, document=content)
        shingler.populate_hashed()
        email2hashed[filename] = shingler.hashed

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


if __name__ == "__main__":
    fradulent_email_test()
