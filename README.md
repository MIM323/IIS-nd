# Structuring Wikipedia articles with an AI agent

This repository contains Labs 1.2–1.6 based on *Structuring Articles Using Natural Language Processing Methods*. The agent takes an English article title and plain-text body, classifies the subject, and returns a section plan, named entities, and proposed infobox fields with supporting quotations. An editor can review the result before using it.

| Lab | Deliverable |
| --- | --- |
| 1.2 | [Project description, preliminary process, and hand-drawing guide](docs/lab-1.2.md) · [Examples in data/](data/README.md) |
| 1.3 | [Company rationale and PlantUML diagrams](docs/lab-1.3.md) |
| 1.4 | [Single-agent design and zero-shot/few-shot prompts](prompts/README.md) |
| 1.5 | [Gemini notebook](notebooks/lab-1.5-gemini.ipynb) |
| 1.6 | [ChromaDB RAG notebook and baseline comparison](notebooks/lab-1.6-rag.ipynb) |

## Run in Colab

Once the files are on GitHub, open [Lab 1.5 in Colab](https://colab.research.google.com/github/MIM323/IIS-nd/blob/main/notebooks/lab-1.5-gemini.ipynb) or [Lab 1.6 in Colab](https://colab.research.google.com/github/MIM323/IIS-nd/blob/main/notebooks/lab-1.6-rag.ipynb). Before publishing, upload the `.ipynb` file to Colab and upload a ZIP with `article_agent.py`, `data/`, and `prompts/` into the runtime's `/content` directory. The setup cell extracts the ZIP automatically when it is named `iis-colab-input.zip`. In Colab's **Secrets** panel, add `GEMINI_KEY` and grant the notebook access. Each notebook contains its own setup and reflection.

The lab prototype starts with plain English text. The thesis's proposed full implementation starts upstream with a Wikipedia XML dump, MediaWiki markup removal, and dedicated NLP models. The lab implementation uses Gemini for the same core NLP tasks on a smaller input and output contract. The checked-in examples are synthetic.
