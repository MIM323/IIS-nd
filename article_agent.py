"""Shared article-structuring workflow for Labs 1.2–1.6."""

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


MODEL = "gemini-3.5-flash-lite"
TEMPLATES = {
    "person": ("Infobox person", {"name", "birth_date", "birth_place", "occupation"}),
    "country": ("Infobox country", {"name", "capital", "official_language", "currency"}),
    "other": (None, set()),
}


class Field(BaseModel):
    key: str
    value: str
    evidence: str


class Entity(BaseModel):
    text: str
    type: Literal["PERSON", "LOCATION", "ORGANIZATION", "DATE"]


class Section(BaseModel):
    heading: Literal[
        "Lead", "Early life", "Career", "Geography", "History",
        "Government", "Culture", "Economy", "Other",
    ]
    paragraphs: list[int]


class Structure(BaseModel):
    category: Literal["person", "country", "other"]
    template: Literal["Infobox person", "Infobox country"] | None
    fields: list[Field]
    entities: list[Entity]
    sections: list[Section]


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()]


def prepare(observation):
    """Normalize plain text and assign stable 1-based paragraph IDs."""
    title = " ".join(observation["title"].split())
    raw_text = observation["text"].replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [" ".join(part.split()) for part in re.split(r"\n\s*\n", raw_text)]
    paragraphs = [part for part in paragraphs if part]
    if not title or not paragraphs:
        raise ValueError("Provide a title and at least one article paragraph.")
    return {"title": title, "paragraphs": [
        {"id": index, "text": paragraph} for index, paragraph in enumerate(paragraphs, 1)
    ]}


def build_prompt(instructions, observation, examples=()):
    demonstrations = [{"X": prepare(row["X"]), "y": row["y"]} for row in examples]
    payload = {"examples": demonstrations, "target_X": prepare(observation)}
    return instructions.strip() + "\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def validate(observation, output):
    """Check schema, template, grounding and paragraph coverage."""
    canonical = Structure.model_validate(output)
    article = prepare(observation)
    paragraphs = [part["text"] for part in article["paragraphs"]]
    expected_template, allowed_fields = TEMPLATES[canonical.category]
    if canonical.template != expected_template:
        raise ValueError("Template does not match the article category.")
    keys = [field.key for field in canonical.fields]
    if len(keys) != len(set(keys)) or not set(keys) <= allowed_fields:
        raise ValueError("Infobox contains duplicate or unsupported fields.")
    source_texts = [article["title"], *paragraphs]
    for field in canonical.fields:
        if not field.value.strip() or field.value not in field.evidence:
            raise ValueError(f"Field value is missing from its evidence: {field.key}")
        if not any(field.evidence in text for text in source_texts):
            raise ValueError(f"Field evidence is missing from the article: {field.key}")
    entity_spans = {(entity.text, entity.type) for entity in canonical.entities}
    if len(entity_spans) != len(canonical.entities):
        raise ValueError("Entity list contains duplicate mentions.")
    for entity in canonical.entities:
        if not entity.text.strip() or not any(entity.text in text for text in source_texts):
            raise ValueError(f"Entity span is missing from the article: {entity.text}")
    ids = [number for section in canonical.sections for number in section.paragraphs]
    headings = [section.heading for section in canonical.sections]
    if (ids != list(range(1, len(paragraphs) + 1)) or not headings
            or headings[0] != "Lead" or headings.count("Lead") != 1
            or any(not section.paragraphs for section in canonical.sections)):
        raise ValueError("Sections must begin with Lead and cover each paragraph once in order.")
    return canonical.model_dump()


def run_agent(client, instructions, observation, examples=(), model=MODEL):
    """Use one Gemini call for classification, evidence selection and structuring."""
    from google.genai import types

    prompt = build_prompt(instructions, observation, examples)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=Structure.model_json_schema(),
        ),
    )
    if not response.text:
        raise ValueError("Gemini returned no article structure.")
    return validate(observation, json.loads(response.text))


def preview(observation, output):
    """Assemble a readable article using the original normalized paragraphs."""
    article = prepare(observation)
    paragraphs = {item["id"]: item["text"] for item in article["paragraphs"]}
    lines = [article["title"]]
    if output["template"]:
        lines.extend(["", output["template"]])
        lines.extend(f"  {field['key']}: {field['value']}" for field in output["fields"])
    for section in output["sections"]:
        lines.extend(["", section["heading"]])
        lines.extend(paragraphs[number] for number in section["paragraphs"])
    return "\n".join(lines)


def embedding_text(observation):
    article = prepare(observation)
    return "\n".join([article["title"], *(part["text"] for part in article["paragraphs"])])


def index_examples(path, rows):
    """Build or reuse a persistent index keyed by the corpus contents."""
    import hashlib

    import chromadb

    payload = json.dumps(rows, sort_keys=True, ensure_ascii=False).encode("utf-8")
    fingerprint = hashlib.sha256(payload).hexdigest()[:16]
    client = chromadb.PersistentClient(path=str(path))
    collection = client.get_or_create_collection(
        name=f"article-pairs-{fingerprint}",
        configuration={"hnsw": {"space": "cosine"}},
    )
    if collection.count() != len(rows):
        for start in range(0, len(rows), 100):
            batch = rows[start:start + 100]
            collection.upsert(
                ids=[row["id"] for row in batch],
                documents=[embedding_text(row["X"]) for row in batch],
                metadatas=[
                    {"pair": json.dumps({"X": row["X"], "y": row["y"]}, ensure_ascii=False)}
                    for row in batch
                ],
            )
    if collection.count() != len(rows):
        raise RuntimeError("Expected one Chroma record per input pair.")
    return collection


def retrieve_three(collection, observation):
    result = collection.query(
        query_texts=[embedding_text(observation)],
        n_results=3,
        include=["metadatas", "distances"],
    )
    if len(result["ids"][0]) != 3:
        raise RuntimeError("Expected three retrieved examples.")
    return [
        {"id": item_id, "distance": distance, **json.loads(metadata["pair"])}
        for item_id, distance, metadata in zip(
            result["ids"][0], result["distances"][0], result["metadatas"][0], strict=True
        )
    ]


def score_corpus(gold, predictions):
    """Return classification accuracy and micro-averaged extraction metrics."""
    def item_sets(output):
        return {
            "field": {(item["key"], item["value"].casefold()) for item in output["fields"]},
            "entity": {(item["type"], item["text"].casefold()) for item in output["entities"]},
            "section": {(number, item["heading"]) for item in output["sections"]
                        for number in item["paragraphs"]},
        }

    if not gold or len(gold) != len(predictions):
        raise ValueError("Scoring requires one prediction slot per gold example.")
    counts = {kind: [0, 0, 0] for kind in ("field", "entity", "section")}
    correct = valid = 0
    for expected, predicted in zip(gold, predictions, strict=True):
        expected_items = item_sets(expected)
        valid += predicted is not None
        correct += predicted is not None and predicted["category"] == expected["category"]
        predicted_items = item_sets(predicted) if predicted is not None else {}
        for kind, targets in expected_items.items():
            items = predicted_items.get(kind, set())
            counts[kind][0] += len(targets & items)
            counts[kind][1] += len(items - targets)
            counts[kind][2] += len(targets - items)
    scores = {"category_accuracy": correct / len(gold), "valid_output_rate": valid / len(gold)}
    for kind, (tp, fp, fn) in counts.items():
        scores[f"{kind}_precision"] = tp / (tp + fp) if tp + fp else 0.0
        scores[f"{kind}_recall"] = tp / (tp + fn) if tp + fn else 0.0
        scores[f"{kind}_f1"] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    return scores
