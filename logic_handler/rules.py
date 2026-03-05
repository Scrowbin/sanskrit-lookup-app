import pynini as pn


ALPHA = pn.union(*"abcdefghijklmnopqrstuvwxyzāīūṛṝḷḹeaiouḥṃṅñṇnṃśṣs") # UNFINISHED, DIS DA ALPHABET
'''
VOWELS
'''
short_vowels = pn.union(*"aiuṛḷ")
long_vowels = pn.union('ā', 'ī', 'ū', 'ṝ', 'ḹ')
diph_thongs =  pn.union("e", "ai", "o", "au")
vowels = pn.union(short_vowels, long_vowels, diph_thongs)

vowel_endings = pn.union('a', 'ā', 'i', 'ī', 'u', 'ū', 'ṛ')
consonant_endings = pn.union('t', 'n', 's')

'''
CONSONANTS
'''
guttural = pn.union('k', 'kh', 'g', 'gh', 'ṅ')
palatal = pn.union('c', 'ch', 'j', 'jh', 'ñ')
retroflex = pn.union('ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ')
dental = pn.union('t', 'th', 'd', 'dh', 'n')
labial = pn.union('p', 'ph', 'b', 'bh', 'm')

semivowels = pn.union('y', 'r', 'l', 'v')
sibilants = pn.union('ś', 'ṣ', 's')
aspirate = pn.union('h')

'''
VOICED CONSONANTS
'''
voiced_stops = pn.union('g', 'gh', 'j', 'jh', 'ḍ', 'ḍh', 'd', 'dh', 'b', 'bh')
nasals = pn.union('ṅ', 'ñ', 'ṇ', 'n', 'm')

voiced_consonants = pn.union(
    voiced_stops,
    nasals,
    semivowels,
    aspirate
)
'''HARD CONSONANTS'''
# Unvoiced unaspirated and aspirated stops
unvoiced_stops = pn.union(
    "k", "kh", 
    "c", "ch", 
    "ṭ", "ṭh", 
    "t", "th", 
    "p", "ph"
)
# Sibilants (fricatives)
sibilants = pn.union(
    "ś", "ṣ", "s"
)
hard_consonants = pn.union(
    unvoiced_stops,
    sibilants
)

'''
MASTER SETS 
'''

voiced_sounds = pn.union(vowels, voiced_consonants)
all_consonants = pn.union(
    guttural, palatal, retroflex, dental, labial,
    semivowels, sibilants, aspirate
)
all_sounds = pn.union(vowels, all_consonants)
