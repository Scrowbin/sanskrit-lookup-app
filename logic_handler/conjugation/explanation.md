├── lexicon.py # Root database with class, voice, irregularities

├── stem_rules.py # Class 1-9 stem formation functions

├── endings.py # P/Ā thematic/athematic ending tables

├── sandhi.py # Internal and external sandhi rules

├── guṇa.py # Guṇa/vṛddhi functions

├── conjugate.py # Main pipeline orchestrator

└── test.py # Unit tests for each class

Overall Pipeline (High-Level)

Input (root + features)

↓

[1] Lexicon Lookup

↓

[2] Stem Formation (per class + strong/weak)

↓

[3] Ending Addition

↓

[4] Guṇa/Vṛddhi Application (if not already applied)

↓

[5] Internal Sandhi (within stem + ending)

↓

[6] External Sandhi (word boundaries - optional)

↓

Output (conjugated form)