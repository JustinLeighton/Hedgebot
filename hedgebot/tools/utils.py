import datetime
import re
from typing import Dict, Tuple, Any

from unidecode import unidecode
from nltk import ngrams  # type: ignore[reportMissingTypeStubs]
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def year():
    """Returns current year"""
    return str(datetime.datetime.now().year)


def sanitize_string(s: str) -> str:
    """
    Sanitize a string by converting to lowercase and removing punctuation.

    Parameters:
    s (str): The input string.

    Returns:
    str: The sanitized string.
    """
    s = s.lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = s.strip()
    s = unidecode(s)
    return s


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute the Levenshtein distance between two strings.

    Parameters:
    s1 (str): The first string.
    s2 (str): The second string.

    Returns:
    int: The Levenshtein distance between the two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def ngram_vectorize(s: str, n: int) -> Dict[Tuple[str, ...], int]:
    """
    Convert a string into a dictionary of n-gram frequencies.

    Args:
    - s (str): Input string.
    - n (int): Length of n-grams (e.g., 2 for bigrams, 3 for trigrams).

    Returns:
    - dict: Dictionary where keys are n-grams (tuples of n characters) and values are their frequencies in the string.
    """
    grams = ngrams(s, n)
    gram_freq = {}
    for gram in grams:
        gram_freq[gram] = gram_freq.get(gram, 0) + 1
    return gram_freq


def cosine_similarity_ngrams(s1: str, s2: str, n: int = 3) -> float:
    """
    Calculate cosine similarity between two strings based on n-gram vectorization.

    Args:
    - s1 (str): First input string.
    - s2 (str): Second input string.
    - n (int): Length of n-grams (e.g., 2 for bigrams, 3 for trigrams).

    Returns:
    - float: Cosine similarity between the two strings based on their n-gram vector representations.
    """
    vec1 = ngram_vectorize(s1, n)
    vec2 = ngram_vectorize(s2, n)

    all_ngrams = set(vec1.keys()).union(set(vec2.keys()))

    v1 = np.array([vec1.get(ngram, 0) for ngram in all_ngrams])
    v2 = np.array([vec2.get(ngram, 0) for ngram in all_ngrams])

    # Calculate cosine similarity
    similarity = cosine_similarity([v1], [v2])[0][0]  # type: ignore
    return similarity


def safe_cast_to_int(value: Any) -> int:
    """
    Tries to cast the given value to an integer.

    Args:
        value (any): The value to be cast to an integer.

    Returns:
        int: The integer value if casting is successful, otherwise -1.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return -1
