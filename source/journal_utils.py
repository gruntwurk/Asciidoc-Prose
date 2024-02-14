"""
Utility code for using AsciiDoc as a Journaling/Research tool.

This includes utilities for automatically determining keywords (hash-tags).
"""
from datetime import datetime, timedelta
from typing import List, Dict, Union
import re


INSIGNIFICANT_WORDS = [
    "a", "an", "the",
    "and", "but", "or", "nor", "not", "true", "false",
    "of", "to", "from",
    "i", "you", "he", "she", "them", "they", "my", "our", "ours", "your", "yours", "mine",
    "if", "then", "else", "that", "otherwise", "than"
    "yes", "no", "have",
    "in", "on", "with", "about"]
JOURNAL_TEMPLATE = """


[[entry-%s]]
== %s: %s

%s

"""
JOURNAL_SNIPPET = """


[[${2:entry-%s}]]
== %s: ${1:title}

$0

"""
# ${1/(^|\s+[a-z]*\s+|\s+)(\w+)/\(\(\(\L$2\)\)\)/g}


def format_long(dt: datetime):
    """
    Format for how the date is represented as the prefix for the journal entry's title
    """
    return dt.strftime("%d %B %Y %A")


def format_slug(dt: datetime):
    """
    "Slug" meaning the anchor ID
    """
    return dt.strftime("%Y-%m-%d")


def format_slug_with_time(dt: datetime):
    return dt.strftime("%Y-%m-%d-%H%M")


def format_day_of_week(dt: datetime):
    return dt.strftime("%A")


def standardize_keywords(keywords: list, dictionary: Dict[str, List[str]]) -> List[str]:
    """
    Standardizes a list of strings (keywords, hashtags, index entries, etc.)
    by comparing each word in the `keywords` list with the given `dictionary`.

    :param keywords: The list to be standardized.

    :param dictionary: The dictionary keys are the preferred keywords. The
    corresponding values are each a list of the sub-optimal keyword variations.

    :returns: A copy of the `keywords` list, but with any matches replaced
    by their preferred versions. In the special case of the dictionary key
    being blank (an empty string), the original keyword is simply suppressed,
    as opposed being replaced by the empty string.
    """
    results = []
    for candidate in keywords:
        for kwd in dictionary:
            if candidate.lower() in dictionary[kwd]:
                if kwd:
                    results.append(kwd)
                break
        else:
            results.append(candidate.lower())
    return results


def journal_entry(subject="", offset=None, reference_date=None) -> str:
    """
    :param offset: None means no offeset at all, use the current date and time.
        An offset of 0 means use the current date but no time.
        An offset of 1 means use yesterday's date (and no time).
        An offset of 2 means use the day before's date (and no time).
        An offset of 5 means use the date from 5 days ago (and no time).

    :param subject: If we are given a subject, then we can build the journal entry header directly.
        Otherwise, we'll invoke a live snippet so that the user can type in the subject after the entry header has been inserted.

    If a subject is provided, then we also have the advantage of being able to provide candidate hashtags based on the subject.
    """
    hashtag_synonyms = {"": INSIGNIFICANT_WORDS}
    if reference_date is None:
        reference_date = datetime.now()

    if offset is None:
        entry_timestamp = reference_date
        slug = format_slug_with_time(entry_timestamp)
    else:
        entry_timestamp = reference_date - timedelta(days=offset)
        slug = format_slug(entry_timestamp)
    full_date = format_long(entry_timestamp)
    if subject:
        hashtag_candidates = re.sub(r"[^-_a-z0-9 ]", "", subject.casefold()).split()
        print(hashtag_candidates)
        hashtags = " ".join(
            [
                f"((({tag})))"
                for tag in standardize_keywords(
                    hashtag_candidates, hashtag_synonyms
                )
            ]
        )
        return JOURNAL_TEMPLATE % (slug, full_date, subject, hashtags)
    else:
        return JOURNAL_SNIPPET % (slug, full_date)
