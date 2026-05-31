# Sanskrit Lookup App

A desktop application for Sanskrit word lookup, declension generation, and verb conjugation generation, built with Electron, React, and a Python-based linguistic engine.

## About the Project

This project began as a student research experiment to investigate whether Sanskrit morphology could be generated entirely on-the-fly rather than relying on large precomputed databases. 

The core question was simple:
> **Can a Sanskrit grammar engine generate declensions and conjugations in real time directly from grammatical rules?**

The answer is largely yes. Noun declensions can be generated accurately and efficiently, while verb conjugations are also possible but considerably slower due to the complexity of Sanskrit verbal morphology and the large number of interacting grammatical processes. 

In hindsight, a lower-level implementation (such as C++ or Rust) or a dedicated linguistic formalism similar to that used by the INRIA Sanskrit systems would likely provide substantially better performance. Nevertheless, the project demonstrates that large portions of Sanskrit morphology can be generated dynamically using finite-state methods. 

This application serves both as a practical lookup tool and as a research project in computational linguistics.

## Architecture

The application consists of two major components:

### Desktop Client
* **Tech Stack:** Electron, React, JavaScript
* **Details:** The desktop interface provides a search functionality that returns declension tables and conjugation tables.

### Linguistic Engine
* **Tech Stack:** Python, Flask API, Pynini, Finite State Transducers (FSTs)
* **Details:** The React/Electron frontend communicates with a local Flask server responsible for all linguistic processing. When a user requests a declension or conjugation, the frontend sends the grammatical specifications to the Flask API, which invokes the underlying Pynini-based finite-state grammar engine and returns the generated forms as JSON.

This separation allows the linguistic engine and user interface to evolve independently while keeping the computationally intensive morphology generation logic isolated from the frontend.

## Data Sources

The project incorporates and cross-references information from a variety of publicly available Sanskrit resources. These include:

* Digital dictionaries and lexical databases
* Traditional grammatical references
* Public morphological datasets
* Open linguistic resources
* Manually curated corrections and additions

There is a feature to compare the generated forms are against existing resources whenever possible to improve coverage and identify implementation gaps but its turned off as a default since that defeats the point of the implementation.

## Testing
INRIA's data dump was used a golden benchmark for this project, we sincerely thank Mr. Huet for providing this data for free for the community. Obviously, this project doesn't hold a candle to INRIA's and is mostly a fun exercise for us. We compared our outputed forms to INRIA's as a guideline to see where the engine is wrong, and used it as a debugging measure. 

## Distribution

The released desktop application includes the complete Conda environment required by the linguistic engine. 

This approach was chosen because Pynini has substantial native dependencies and can be difficult to install through a standard Python environment on Windows systems. Bundling the required environment ensures that users can run the application without manually compiling or configuring the underlying finite-state toolkit.

## Research Focus

Areas explored by this project include:
* Computational Linguistics
* Sanskrit Morphology
* Finite-State Morphology
* Morphological Generation
* Natural Language Processing
* Rule-Based Language Modeling

## Open Source and Non-Profit

This project is open source and developed for educational and research purposes. The project is not intended for commercial use and is maintained as an independent effort to explore Sanskrit morphology, finite-state methods, and computational linguistics. 

Contributions, issue reports, and academic discussion are welcome.

## Disclaimer

Sanskrit grammar is exceptionally complex and often preserves multiple competing grammatical traditions. Generated forms may occasionally differ from forms accepted by specific grammars, dictionaries, or teaching materials. 

*This application should be viewed as a research and educational tool rather than an authoritative linguistic reference.*
