"""Rebuild the synthetic retrieval corpus and the hand-written lab examples."""

import json
from pathlib import Path
from random import Random


HERE = Path(__file__).resolve().parent
TEMPLATES = {"person": "Infobox person", "country": "Infobox country", "other": None}


def pair(item_id, category, title, lead, paragraphs=(), fields=(), entities=()):
    return {
        "id": item_id,
        "source": "synthetic",
        "X": {"title": title, "text": "\n\n".join([lead, *(text for _, text in paragraphs)])},
        "y": {
            "category": category,
            "template": TEMPLATES[category],
            "fields": [
                {"key": key, "value": value, "evidence": evidence}
                for key, value, evidence in ([("name", title, title)] + list(fields)
                                             if category != "other" else [])
            ],
            "entities": [{"text": text, "type": kind} for text, kind in entities],
            "sections": [{"heading": "Lead", "paragraphs": [1]}] + [
                {"heading": heading, "paragraphs": [number]}
                for number, (heading, _) in enumerate(paragraphs, 2)
            ],
        },
    }


def corpus():
    rng = Random(20261124)
    starts = "Alen Bell Corv Darel Elen Fael Garv Halv Iren Jorv Kest Larn Mav Neral Orel Pel Quen Rel Sav Terv".split()
    ends = "aris aven beck cairn dell evar fell gard hame isen jora keld lenn mar neth oren pell quar rath sel".split()
    names = [start + end for start in starts for end in ends]
    roles = [
        ("botanist", "catalogued coastal plants"),
        ("historian", "documented trade routes"),
        ("sculptor", "carved public monuments"),
        ("composer", "wrote chamber music"),
        ("architect", "designed public libraries"),
        ("cartographer", "surveyed mountain passes"),
        ("journalist", "reported on regional elections"),
        ("engineer", "designed tidal bridges"),
        ("novelist", "published historical fiction"),
        ("linguist", "compiled a regional dictionary"),
    ]
    environments = ["river valleys", "wooded hills", "coastal plains", "mountain plateaus"]
    for index, stem in enumerate(names):
        number = index + 1
        title = "Mira " + stem
        town = rng.choice(names) + " Bay"
        year = str(rng.randrange(1840, 1980))
        role, work = rng.choice(roles)
        lead = [
            f"{title} was a {role} who {work}.",
            f"{title}, a {role}, {work} during a long public career.",
            f"The {role} {title} {work}.",
            f"As a {role}, {title} {work}.",
        ][index % 4]
        childhood = [
            f"{title} was born in {town} in {year}.",
            f"The birthplace of {title} was {town}, in {year}.",
            f"In {year}, {title} was born in {town}.",
            f"{town} was where {title} was born in {year}.",
        ][index % 4]
        person_fields = [("occupation", role, lead), ("birth_place", town, childhood)]
        person_entities = [(title, "PERSON"), (town, "LOCATION")]
        if index % 5:
            person_fields.append(("birth_date", year, childhood))
            person_entities.append((year, "DATE"))
        else:
            childhood = f"{title} was born in {town}."
            person_fields[1] = ("birth_place", town, childhood)
        yield pair(
            f"person-{number:03d}", "person", title, lead,
            [("Early life", childhood), ("Career", f"Later, {title} taught workshops.")],
            person_fields, person_entities,
        )

        title = "Republic of " + stem
        capital = rng.choice(names) + " City"
        language = stem + "ic"
        currency = stem.lower() + " mark"
        terrain = rng.choice(environments)
        country_lead = [
            f"The {title} is a sovereign country. Its capital is {capital}.",
            f"{capital} is the capital of the independent {title}.",
            f"The independent country known as the {title} has its capital in {capital}.",
            f"The {title}, a sovereign state, has {capital} as its capital.",
        ][index % 4]
        economy = f"The {currency} is the national currency."
        country_fields = [("capital", capital, country_lead), ("currency", currency, economy)]
        country_body = [("Geography", f"Its geography includes extensive {terrain}.")]
        if index % 5:
            culture = f"{language} is the official language and is used in schools."
            country_fields.append(("official_language", language, culture))
            country_body.append(("Culture", culture))
        country_body.append(("Economy", economy))
        yield pair(
            f"country-{number:03d}", "country", title, country_lead, country_body,
            country_fields, [(title, "LOCATION"), (capital, "LOCATION")],
        )

        if index < 200:
            if index % 2:
                title = stem + " Historical Society"
                lead = f"The {title} is a volunteer organization that maintains a local archive."
                body = ("History", "The organization began by preserving donated photographs.")
                category = "ORGANIZATION"
            else:
                title = "Lake " + stem
                lead = f"{title} is a freshwater lake surrounded by {terrain}."
                body = ("Geography", "Several small streams feed the lake from the north.")
                category = "LOCATION"
            yield pair(f"other-{number:03d}", "other", title, lead, [body],
                       entities=[(title, category)])


def demos():
    return [
        pair(
            "demo-person", "person", "Leona Darvick", "Leona Darvick is a marine biologist.",
            [("Early life", "Leona Darvick was born in Dalenport in 1982."),
             ("Career", "She later joined the Argent Marine Institute.")],
            [("occupation", "marine biologist", "Leona Darvick is a marine biologist."),
             ("birth_place", "Dalenport", "Leona Darvick was born in Dalenport in 1982."),
             ("birth_date", "1982", "Leona Darvick was born in Dalenport in 1982.")],
            [("Leona Darvick", "PERSON"), ("Dalenport", "LOCATION"), ("1982", "DATE"),
             ("Argent Marine Institute", "ORGANIZATION")],
        ),
        pair(
            "demo-country", "country", "Velmora", "Velmora is a sovereign country. Its capital is Sondrel.",
            [("Geography", "Forested valleys stretch across the north."),
             ("Economy", "The vel is the national currency.")],
            [("capital", "Sondrel", "Its capital is Sondrel."),
             ("currency", "vel", "The vel is the national currency.")],
            [("Velmora", "LOCATION"), ("Sondrel", "LOCATION")],
        ),
        pair(
            "demo-other", "other", "Lake Windmere", "Lake Windmere is a freshwater lake.",
            [("Geography", "The lake occupies a glacial basin beside the Tovik Ridge.")],
            entities=[("Lake Windmere", "LOCATION"), ("Tovik Ridge", "LOCATION")],
        ),
    ]


def holdout():
    return [
        pair(
            "test-country-1", "country", "Nemeris",
            "Nemeris is an independent island country. Its government moved the capital from Karda to Oltan in 1998.",
            [("Culture", "The constitution recognizes Nemeri as the official language."),
             ("Economy", "Nemeris uses the island crown as its national currency.")],
            [("capital", "Oltan", "Its government moved the capital from Karda to Oltan in 1998."),
             ("official_language", "Nemeri", "The constitution recognizes Nemeri as the official language."),
             ("currency", "island crown", "Nemeris uses the island crown as its national currency.")],
            [("Nemeris", "LOCATION"), ("Karda", "LOCATION"), ("Oltan", "LOCATION"), ("1998", "DATE")],
        ),
        pair(
            "test-person-1", "person", "Isolde Varn", "Isolde Varn worked as a conservator.",
            [("Early life", "She was born on 4 May 1961 in Pellaro and spent her childhood in Tivren."),
             ("Career", "The Merwick Museum invited her to restore its textile collection.")],
            [("occupation", "conservator", "Isolde Varn worked as a conservator."),
             ("birth_date", "4 May 1961", "She was born on 4 May 1961 in Pellaro and spent her childhood in Tivren."),
             ("birth_place", "Pellaro", "She was born on 4 May 1961 in Pellaro and spent her childhood in Tivren.")],
            [("Isolde Varn", "PERSON"), ("4 May 1961", "DATE"), ("Pellaro", "LOCATION"),
             ("Tivren", "LOCATION"), ("Merwick Museum", "ORGANIZATION")],
        ),
        pair(
            "test-other-1", "other", "Duskfen Island",
            "Duskfen Island is an island administered by the neighboring country of Ferond.",
            [("Geography", "The northern shore is bounded by the Marn Strait.")],
            entities=[("Duskfen Island", "LOCATION"), ("Ferond", "LOCATION"), ("Marn Strait", "LOCATION")],
        ),
        pair(
            "test-person-2", "person", "Tal Orvane",
            "Tal Orvane was a ceramicist who specialized in glazed vessels.",
            [("Career", "Orvane opened a workshop in Ulder in 2001.")],
            [("occupation", "ceramicist", "Tal Orvane was a ceramicist who specialized in glazed vessels.")],
            [("Tal Orvane", "PERSON"), ("Orvane", "PERSON"), ("Ulder", "LOCATION"), ("2001", "DATE")],
        ),
        pair(
            "test-country-2", "country", "Asterin", "Asterin is a sovereign state on a river delta.",
            [("Geography", "Most settlements lie on the higher banks of the River Savael."),
             ("Economy", "Cross-border trade is important, and the national currency is the ast.")],
            [("currency", "ast", "Cross-border trade is important, and the national currency is the ast.")],
            [("Asterin", "LOCATION"), ("River Savael", "LOCATION")],
        ),
        pair(
            "test-other-2", "other", "Candlewick Press", "Candlewick Press is a fictional publishing house.",
            [("History", "It began operating in Nelst in 1959.")],
            entities=[("Candlewick Press", "ORGANIZATION"), ("Nelst", "LOCATION"), ("1959", "DATE")],
        ),
    ]


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    write_jsonl(HERE / "examples.jsonl", demos())
    write_jsonl(HERE / "retrieval_examples.jsonl", corpus())
    write_jsonl(HERE / "holdout.jsonl", holdout())
