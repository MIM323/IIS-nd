# Lab 1.2 — End-to-end project description

Wikipedia articles sometimes contain useful facts in prose but lack an infobox or helpful headings. The project helps an editor recover that structure. Given article text, it identifies the subject, recognizes entities, extracts template-specific facts, and groups source paragraphs under section headings. The output is a reviewable draft. A useful result represents the source accurately, leaves unsupported fields absent, and preserves the article's paragraph order.

The thesis methodology starts with reading articles from a Wikipedia XML dump and stripping MediaWiki markup. It proposes BERT-based classification and NER, followed by rule-based or model-based extraction and assembly. In the lab prototype, a user provides English text after cleaning, and one Gemini agent performs topic classification, entity recognition, fact extraction, and section assignment. The prototype supports person and country infoboxes. Other topics still receive a section plan and entity list.

| Stage | Operation | Result |
| --- | --- | --- |
| Receive article | Take the title and body of one English article. In the thesis pipeline these come from a dump. | Input `X`. |
| Prepare text | Normalize whitespace, split by blank lines, and number the paragraphs. | Title and ordered paragraphs. |
| Classify | Decide whether the main subject is a person, country, or another topic. | Category and applicable template. |
| Recognize and extract | Identify person, location, organization and date mentions. Connect the article subject to facts that have explicit evidence. | Entity spans and infobox fields with source quotations. |
| Assemble and validate | Assign section labels to the original paragraphs and check the output schema, field rules and paragraph coverage. | Structured JSON `y` and a readable preview. |
| Review | The editor checks the source evidence and accepts or edits the proposal. | A structure suitable for editorial use. |

The [data directory](../data/README.md) describes the lab's `(X,y)` examples. These examples show a person infobox, a country infobox with a missing field, and an article that falls outside the two templates.

## Preliminary process model

Open the [process diagram](../diagrams/preliminary-process.svg) or its [PlantUML source](../diagrams/preliminary-process.puml). To reproduce it by hand, start with a circle and stack three boxes for article text, whitespace cleanup, and topic classification. Draw a diamond labeled *Person or country?*. Route **Yes** through a box for selecting an infobox and **No** around it. Rejoin the arrows at a box for entities and supported facts, then add boxes for section assembly and validation. Draw a second diamond for valid output, leading to editor review on **Yes** and a correction request on **No**. End both paths at the same closing circle. Write `X` beside the first box and `y` beside the review box.

## Course reference notebooks

### Notebook 1 — Video data processing

KaggleHub downloads the `csanskriti/video-and-audio-samples` dataset, and the notebook copies it into `/content/video-data/` if the directory is absent. MoviePy iterates over the MP4 files, writes each audio track as MP3, and saves one JPEG per video at half its duration. Whisper's `medium` model transcribes the audio files and saves the returned text as separate TXT files. The notebook mounts Google Drive and writes `audio-data.zip`, `text-data.zip`, and `frame-data.zip` under `MyDrive/colab-output-tmp`. The notebook uses MoviePy's older `moviepy.editor` import. [Video data processing notebook](https://colab.research.google.com/drive/1P1oWHEfyRYKXRvroefokW6-71tSHC4Ng)

### Notebook 2 — Image description generation

This notebook loads the `GOOGLE_API_KEY` Colab Secret into the `GEMINI_API_KEY` environment variable and mounts Drive. It extracts the first notebook's `frame-data.zip` into `/content/frame-data/`. For each JPG, JPEG, or PNG, it sends the image bytes and a short description instruction through the Google Gen AI SDK. The active model in the notebook is `gemma-3-27b-it`. It combines the streamed chunks, writes a TXT file per successful image, and stores the files in `image-descriptions.zip`. The code marks every image as JPEG. The normal pipeline supplies JPEGs, and any added PNGs would need the correct MIME type. The second notebook consumes frames only. [Image description generation notebook](https://colab.research.google.com/drive/15r2XMoSW-xx3WPewuuZK3zUkfzGJBMF4)

The handoff illustrates two design choices used in this lab. Input preparation creates a predictable representation for inference, and the model response is saved in a form that can be inspected and reused. Here the input is an article and the representation is a list of numbered paragraphs. Gemini returns schema-validated article structure, including field evidence and paragraph references.
