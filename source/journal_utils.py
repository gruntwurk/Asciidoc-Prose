"""
Utility code for using AsciiDoc as a Journaling/Research tool.

This includes utilities for automatically determining keywords (hash-tags).
"""
from datetime import datetime


CONNECTIVE_WORDS = [
    "a", "an", "the",
    "and", "but", "or", "nor", "not", "true", "false",
    "of", "to", "from",
    "i", "you", "he", "she", "them", "they", "my", "our", "ours", "your", "yours", "mine",
    "if", "then", "else", "that", "otherwise",
    "yes", "no", "have"]
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


def standardize_keywords(keywords, dictionary):
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
            if candidate in dictionary[kwd]:
                if kwd:
                    results.append(kwd)
                break
        else:
            results.append(candidate)
    return results



def journal_entry(subject="") -> str:
    """
    If we are given a subject, then we can build the journal entry header
    directly. Otherwise, we'll invoke a snippet so that the user can type
    in the subject after the entry header has been inserted.
    """
    hashtag_synonyms = {"": CONNECTIVE_WORDS}
    entry_timestamp = datetime.now()
    full_date = format_long(entry_timestamp)
    slug = format_slug_with_time(entry_timestamp)
    if subject:
        hashtag_candidates = re.sub(r"[^-_a-z0-9 ]","",subject.casefold()).split()
        print(hashtag_candidates)
        hashtags = " ".join(["((("+tag+")))" for tag in standardize_keywords(hashtag_candidates,hashtag_synonyms)])
        entry = JOURNAL_TEMPLATE % (slug, full_date, subject, hashtags)
    else:
        entry = JOURNAL_SNIPPET % (slug, full_date)
    return entry
