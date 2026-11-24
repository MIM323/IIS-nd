# Lab 1.4 — Article structuring prompts

One agent owns the complete request. It prepares the article, assembles the task and contexts, calls Gemini once, checks the proposed structure, and assembles a preview from the original paragraphs. In that call, Gemini interprets the article, classifies the subject, chooses the applicable template, recognizes entities, extracts facts with evidence, and proposes section headings. The evidence quotations and paragraph mappings make the result inspectable.

- [Zero-shot prompt](zero-shot.txt) presents a single new article about Nemeris and asks for `y`. Its example list is empty.
- [Few-shot prompt](few-shot.txt) presents the same article after the three labeled examples from [Lab 1.2](../data/examples.jsonl). Each example shows a different subject category and includes its full expected output.
- [Shared instructions](instructions.txt) define the output contract. The notebooks assemble the prompts from these instructions and the shared data so the notebook demonstrations use the same examples as this directory.

The target label is available for evaluation in [holdout.jsonl](../data/holdout.jsonl), where it stays outside the prompts. The same input in both runs makes differences in the proposals easy to inspect.
