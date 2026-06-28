def describe_word(word):
    tags = []
    if word.isupper():
        tags.append("shouting")
    if word.islower():
        tags.append("quiet")
    if word.isdigit():
        tags.append("number")
    if word.endswith("ing"):
        tags.append("verb-ish")
    if word.endswith("ly"):
        tags.append("adverb-ish")
    if len(word) > 12:
        tags.append("long")
    elif len(word) < 3:
        tags.append("short")
    if word and word[0] in "aeiou":
        tags.append("vowel-start")
    return tags
