# Validates user input, handles messy user input

import re

MAX_QUERY_LEN = 200
MAX_ING_CNT = 20


def clean_query(query: str):
    """
    clean search query
    return cleaned query, or None if query can't be used
    """

    if not query:
        return None
    
    query = query.strip()

    # truncate query if too long
    if len(query) > MAX_QUERY_LEN: query = query[:MAX_QUERY_LEN]

    query = re.sub(r"[^\w\s\-']", " ", query)       # remove weird chars from query
    query = re.sub(r"\s+", " ", query).strip()

    if len(query) < 2: return None

    return query


def clean_ingredients(ings: str):
    """
    clean string containing comma-separated ingredients
    return cleaned string, or None if string can't be used
    """

    if not ings or not ings.strip(): return None

    ings_list = ings.split(",")
    cleaned_ings = []

    for ing in ings_list:
        ing = ing.strip()

        if not ing or ing.isdigit(): continue

        ing = re.sub(r"[^\w\s\-]", "", ing).strip()     #remove characters that aren't letters (except spaces, hyphens)

        if len(ing) >= 2: cleaned_ings.append(ing.lower())

    if not cleaned_ings: return None

    return cleaned_ings[:MAX_ING_CNT]