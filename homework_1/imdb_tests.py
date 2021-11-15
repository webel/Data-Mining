import json
import os
import string
from pprint import pprint

from numpy import sign

from text_similarity import (
    LSH,
    CompareSets,
    CompareSignatures,
    Config,
    MinHashing,
    Shingling,
)
from utils import test

config = Config(k=6, n_functions=100, b=20, r=5)


def get_imdb_plot_from_id(id: str) -> dict:
    with open("IMDB_plots.json", "r") as f:
        movies = json.load(f)
    movie = list(filter(lambda item: item["movie_id"] == id, movies)).pop()
    return movie["plot_summary"]


def get_imdb_plots_shingling(force_new=False):
    pickle_path = "imdb_plots.pickle"
    if not force_new and os.path.isfile(pickle_path):
        shingling = Shingling.load_from_file(pickle_path)
    else:
        shingling = Shingling(k=config.k, path=pickle_path)
        with open("IMDB_plots.json", "r") as f:
            movies = json.load(f)
        for movie in movies[:5]:
            shingling.add_document(
                document=movie["plot_summary"], document_name=movie["movie_id"]
            )
        shingling.save_to_file()
    return shingling


def get_imdb_signatures(force_new=False):
    pickle_path = "imdb_plots_minhashing.pickle"
    if not force_new and os.path.isfile(pickle_path):
        minhashing = MinHashing.load_from_file(pickle_path)
        signatures = minhashing.signatures
    else:
        shingling = get_imdb_plots_shingling(force_new=True)
        minhashing = MinHashing(n_functions=config.n_functions, path=pickle_path)
        signatures = minhashing.build_minhash_signatures(
            sorted(shingling.all_hashed_shingles), shingling.doc2hashed
        )
        print(signatures) # NOTE: There's something really wrong here
        minhashing.save_to_file()

    return signatures


@test
def test_imdb_plots_jaccard():
    """Get 5 very similar movie plots and 5 very disimilar plots"""
    shingling = get_imdb_plots_shingling()

    doc2hashed = shingling.doc2hashed

    similar_n = 5
    disimilar_n = 1
    similar_threshhold = 0.20
    disimilar_threshhold = 0.01
    print("Jaccard similarity between pairs")
    for movie1 in doc2hashed.keys():
        if similar_n == 0 and disimilar_n == 0:
            break
        for movie2 in doc2hashed.keys():
            if movie1 == movie2:
                continue
            jacc = CompareSets.jaccard_similarity(
                doc2hashed[movie1], doc2hashed[movie2]
            )
            if jacc > similar_threshhold and similar_n > 0:
                print(f"({movie1}, {movie2}) = {jacc} \n")
                print("Movie 1: \n")
                pprint(get_imdb_plot_from_id(movie1))
                print("\n Movie 2: \n")
                pprint(get_imdb_plot_from_id(movie2))
                similar_n -= 1
            if jacc <= disimilar_threshhold and disimilar_n > 0:
                print(f"({movie1}, {movie2}) = {jacc} \n")
                print("Movie 1: \n")
                pprint(get_imdb_plot_from_id(movie1))
                print("\n Movie 2: \n")
                pprint(get_imdb_plot_from_id(movie2))
                disimilar_n -= 1
            if similar_n == 0 and disimilar_n == 0:
                break


@test
def test_imdb_lsh():
    """LSH on imdb plots"""
    n_functions = config.n_functions
    signatures = get_imdb_signatures(force_new=True)

    lsh = LSH(n=n_functions, r=config.r, b=config.b)
    candidate_pairs = lsh.get_candidate_pairs_for_signatures(signatures)
    print(
        f"Approx threshhold is: {lsh.approx_threshold}, with n = {n_functions}, b = {config.b} and r = {config.r} \n"
    )
    # print("Candidate pairs for tt6294822 are:")
    # pprint(get_imdb_plot_from_id("tt6294822"))
    # "\n"
    # for movie_id in candidate_pairs["tt6294822"]:
    #     pprint(get_imdb_plot_from_id(movie_id))
    #     print("\n")

    # print("Candidate pairs for tt7608418 are: ")
    # pprint(candidate_pairs["tt7608418"])

if __name__ == "__main__":
    test_imdb_lsh()
