import pynini as pn
from rules import *
visarga_sigma = pn.closure(pn.union(ALPHA, "ḥ"))
visarga = "ḥ"
'''
If visarga comes after a / ā
'''
# aḥ + vowel
visarga_before_a_after_a = pn.cdrewrite(
  #If next to visarga = a
  pn.cross("ḥ", 'o'),
  pn.union("a", "ā"),
  pn.union("a"),
  visarga_sigma
)

visarga_before_a_after_not_a = pn.cdrewrite(
  #If next to visarga = other vowel
  pn.cross("ḥ", ""),
  pn.union("a", "ā"),
  pn.difference(vowels, pn.union("a")),
  visarga_sigma
)

# aḥ + voiced consonant
visarga_before_a_after_voiced_consonant = pn.cdrewrite(
    #If next to visarga = voiced consonant
  pn.cross("ḥ", "o"),
  pn.union("a", "ā"),
  voiced_consonants,
  visarga_sigma
)

'''
If visarga comes after i, u, ṛ, e, etc

'''
# Before vowel or voiced consonant
visarga_before_vowel_or_consonant = pn.cdrewrite(
    # Before vowel or voiced consonant
  pn.cross("ḥ", "r"),
  "",
  pn.difference(vowels, voiced_consonants),
  visarga_sigma
)

# Before hard consonants (k p etc)
# Might be context bassed.
visarga_before_hard_consonants = pn.cdrewrite(
    # Before vowel or voiced consonant
  pn.cross("ḥ", "r"),
  "",
  hard_consonants,
  visarga_sigma
)

'''
Before certain consonants.
'''

# before c, ch -> ś
visarga_before_c = pn.cdrewrite(
    pn.cross(visarga, "ś"),
    "",
    pn.union("c", "ch"),
    visarga_sigma
)

# before ṭ ṭh → ṣ
visarga_before_t_dot = pn.cdrewrite(
    pn.cross(visarga, "ṣ" ),
    "",
    pn.union("ch", "ṭ"),
    visarga_sigma   
)
# before t th → s
visarga_before_t_th = pn.cdrewrite(
    pn.cross(visarga, "s"),
    "",
    pn.union("ch", "t"),
    visarga_sigma
)


# s_to_visarga
s_to_visarga = pn.cdrewrite(
    pn.cross("s", visarga),
    "",
    "<EOS>",
    visarga_sigma
)

# r_to_visarga
'''
UNIMPLEMENTED STUFF

acient Jihvamuliya Upadhmaniya arent included lol

Notes:
 - External Sandhi = #Rule only applies to sentences, siince we're just declensing a single word, so
this should be removed for simplicity lol

'''

# visarga_voiced_consonant_or_vowel = pn.cdrewrite(
# EXTERNAL SANDHI
#     # āḥ loses visarga before vowels or voiced consonants
#   pn.cross("ḥ", "o"),
#   pn.union("a", "ā"),
#   voiced_consonants,
#   visarga_sigma
# )

