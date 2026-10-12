# AI use and recorded provenance

Generative AI assisted candidate screening, source localization, structured evidence extraction, exploratory literature-reference labeling, and targeted checking. The current paper and repository also benefited from AI-assisted writing, scientific-figure code and analysis/package code.

The recorded initial extraction history is **69 GPT-6 Luna and 11 retained GPT-6 Astra cases**. Independent AI contexts and GPT-6.1 Sol were used for targeted review. The AI-assisted D/I/A/U reference was generated in two separate GPT-6 Luna contexts; GPT-6.1 Sol handled disagreements and rubric-consistency issues. These are recorded platform service identifiers. Immutable backend snapshots and service-managed generation settings were not exposed and are not inferred.

Actual case-level initial extraction provenance is in S18. S3 may contain a later normalized `model_id`; it should not replace S18 as the initial-history record. The retained prompt, schema and profile are in `Methods/`. Pending-execution fields in the historical profile describe that original stage, not an unresolved gate for these already generated outputs.

C0/C1/C2/C4 and A1–A4 are deterministic code applied to identical finalized evidence inputs. The AI does not freely generate their outputs. The public reproduction operates on those supplied vectors and does not claim to recreate the original cloud extraction.

The human reference is one project-author review, blinded to case-level AI labels and rule outputs but conducted with prior knowledge of aggregate results. It remains separate from the AI reference; disagreements are retained. No completed external two-human independent reference validation is claimed.

The deposited figures are programmatically drawn literature/data diagrams, not synthetic experimental recordings or micrographs. Source papers remain separately identifiable. AI is not an author; final research interpretation and submission decisions belong to the human author. This record describes the project's actual uses and is not a statement that a journal has approved them or that a supervisor has signed off.
