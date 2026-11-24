# Article input and reference output

`X` contains a title and a plain English article body. Blank lines mark paragraph boundaries. The agent normalizes whitespace and assigns paragraph IDs starting at 1. `y` contains a subject category, a proposed infobox template, exact field values with quotations from the source, named entity mentions, and ordered section headings mapped to those paragraph IDs. A section can contain multiple consecutive paragraphs. A markdown-like preview in the notebooks places the original paragraph text under the proposed headings.

| Example | Input X | Expected y |
| --- | --- | --- |
| `demo-person` | An article about marine biologist Leona Darvick. The body gives her birthplace and birth year and describes her work. | `person` and `Infobox person`. Name Leona Darvick, occupation marine biologist, birthplace Dalenport, and birth date 1982. The last two paragraphs map to Early life and Career. |
| `demo-country` | An article about the fictional country Velmora. It names the capital and currency and describes its terrain. | `country` and `Infobox country`. Capital Sondrel and currency vel. The official-language field is omitted because the article gives no language. |
| `demo-other` | An article about Lake Windmere and its geography. | `other` with a null template and empty fields. The lake and Tovik Ridge are tagged as locations. |

The full inputs and labels, including evidence and entities, are in [examples.jsonl](examples.jsonl). Lab 1.4 uses these three records as its few-shot examples. For the common target, Lab 1.4 uses the Nemeris article from [holdout.jsonl](holdout.jsonl). Its label resolves the former capital Karda and current capital Oltan.

## Retrieval and evaluation data

- [retrieval_examples.jsonl](retrieval_examples.jsonl) contains 1,000 unique synthetic inputs with deterministic labels. It contains 400 biographies, 400 country articles, and 200 articles about lakes or organizations. Templates vary the wording, and some omit the birth date or official language to exercise missing fields. Each embedding is computed from the title and body, while the corresponding full pair is stored as metadata.
- [holdout.jsonl](holdout.jsonl) contains six separately written synthetic cases, two for each class. They include a former capital, a non-sovereign island, a childhood residence distinct from the birthplace, and missing fields. These inputs are outside the Chroma corpus and the fixed few-shot examples.
- [build_examples.py](build_examples.py) recreates the three datasets with `python data/build_examples.py`. All datasets use UTF-8 JSON Lines. The labels are reference expectations for the prototype. The corpus is intentionally templated, so evaluation on it has limited relevance to real Wikipedia prose.
