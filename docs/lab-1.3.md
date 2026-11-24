# Lab 1.3 — Company and generative AI integration

**Selected company — Wikimedia, LLC, operator of Wikimedia Enterprise.** Wikimedia Enterprise provides structured, read-only access to Wikipedia and other Wikimedia projects. Its Structured Contents initiative already extracts published structures such as sections, references, and infoboxes. The thesis prototype could complement this service by proposing missing structures from the prose before an editor reviews them. A plausible integration begins with English Wikipedia biographies and country articles where relevant facts are present but metadata is incomplete. This is a proposed use case for the company. [Wikimedia Enterprise about page](https://enterprise.wikimedia.com/about/) · [Structured Contents initiative](https://enterprise.wikimedia.com/api/structured-contents/) · [API reference](https://enterprise.wikimedia.com/docs/api/)

The component diagram shows where Google Gemini sits in the service and how the Lab 1.6 extension supplies examples from Chroma. The sequence diagram follows an editor's request, including an invalid model result. Article text and any examples go to Gemini, and the service checks the resulting JSON before presenting it for editorial review. The Wikimedia data API serves as a potential upstream source. The lab demonstration uses prepared text instead.

| Diagram | Source | Rendered |
| --- | --- | --- |
| Component diagram | [PlantUML](../diagrams/components.puml) | [SVG](../diagrams/components.svg) |
| Sequence diagram | [PlantUML](../diagrams/sequence.puml) | [SVG](../diagrams/sequence.svg) |

The diagrams were drafted with Codex and rendered using PlantUML. You can paste each `.puml` file into the [PlantUML editor](https://www.plantuml.com/plantuml/uml/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000).
