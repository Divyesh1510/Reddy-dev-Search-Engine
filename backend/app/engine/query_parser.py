import re
from typing import List, Dict, Tuple

COMMON_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

class QueryParser:
    def __init__(self):
        pass

    def parse(self, raw_query: str) -> Dict[str, any]:
        """
        Parses query, handles field boosts (e.g. title:term), domain filters,
        and returns cleaned terms for lexical and semantic engines.
        """
        cleaned = raw_query.strip()
        domain_filter = None

        # Check for domain: example.com
        domain_match = re.search(r"domain:(\S+)", cleaned, re.IGNORECASE)
        if domain_match:
            domain_filter = domain_match.group(1).lower()
            cleaned = re.sub(r"domain:\S+", "", cleaned, flags=re.IGNORECASE).strip()

        # Check for site: example.com
        site_match = re.search(r"site:(\S+)", cleaned, re.IGNORECASE)
        if site_match:
            domain_filter = site_match.group(1).lower()
            cleaned = re.sub(r"site:\S+", "", cleaned, flags=re.IGNORECASE).strip()

        # Tokenize
        tokens = re.findall(r"\w+", cleaned.lower())
        filtered_tokens = [t for t in tokens if t not in COMMON_STOPWORDS or len(tokens) <= 2]

        return {
            "original_query": raw_query,
            "normalized_query": cleaned,
            "lexical_query": " ".join(filtered_tokens) if filtered_tokens else cleaned,
            "semantic_query": cleaned,
            "domain_filter": domain_filter,
            "tokens": tokens
        }

query_parser = QueryParser()
