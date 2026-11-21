# 病毒图谱 / Virus Atlas

Bilingual educational atlas, updated 20 November 2026. The taxonomy snapshot contains all 17,554 species in ICTV MSL41.v1 (427 families, 10 realms, including related entities such as viroids). It does not represent every detected sequence, variant or undiscovered virus. Thirty-eight clinical profiles group selected human viruses; these are not 38 species.

## Version 2

- Interactive realm → kingdom → phylum → class → order → family → genus → species navigator below the overview statistics, with search, counts, breadcrumbs, pagination and accessible buttons. Sector sizes are counts, not phylogenetic distances.
- Bilingual research context, evidence, limitations and research priorities for the 38 clinical profiles, with traceable sources. Canonical receptor terminology distinguishes ACE2 from the host protease TMPRSS2.
- Every clinical and taxonomy record includes a publication/news tracker. Opening or refreshing queries same-origin server endpoints. Snapshots cover the selected clinical profiles. Name-associated matches are not a systematic literature review or evidence of clinical efficacy.
- Publication metadata comes from Europe PMC's PubMed index; original title, authors, journal, date, DOI/PMID, open-access links and RIS export are provided. NUS links lead to institutional authentication for eligible readers; no account credentials or subscription full text are stored.
- News comes from the Google News RSS index, with selected WHO, CDC, NIH, ECDC and Reuters source hosts, title association and a 90-day window. News is displayed separately from scientific evidence. Empty results and connection failures are distinguished.
- Follows are browser-local bookmarks, not server subscriptions. No email, notifications, account synchronization or closed-browser background monitoring. Server caches successful queries for up to 15 minutes; refresh may return that cache and shows its query timestamp.

## Run and build

Requires Node 22 or newer. No npm dependencies.

```sh
node scripts/build-worker.mjs
node scripts/preview.mjs
```

Preview: http://localhost:8765. The builder embeds public assets in a Cloudflare Worker ES module at `dist/server/index.js`. The `.openai/hosting.json` retains the existing Site identity and omits static hosting because the tracker uses server-side external requests. Worker endpoints accept only registered record IDs and never an arbitrary upstream URL.

```sh
python3 scripts/build-offline.py
```

Creates `../病毒图谱-离线版.html` with embedded taxonomy and selected profile snapshots. Offline copies explicitly disable live refresh.

## Data maintenance

- `sources/import_taxonomy.py`: pinned ICTV MSL/VMR import, including member names and abbreviations.
- `sources/research-enrichment.json`: curated bilingual research notes and field updates; copied to `dist/research.json` before build.
- `sources/fetch_literature.py`: reproducible clinical/public-health metadata snapshot; `sources/literature-audit.json` records searches and bibliographic checks.
- `sources/fetch_news.py`: selected-source headline/link snapshot; requires Python requests.

Dates are source/index metadata and can differ from indexing or review dates. Automated retrieval does not update curated clinical statements. Editorial research priorities are not established findings or official roadmaps. Taxonomy entries without curated clinical notes say so explicitly. The atlas supplies high-level educational context, not laboratory procedures or individual treatment advice.

## Version 3 — five-year observatory

Every record has a rolling five-calendar-year literature view (`/api/progress`). Each of five intervals queries up to 40 index records and keeps up to 12 title-matched clinical/public-health records. The year chart reports raw index hits, not discoveries; theme counts use only the displayed sample and may overlap. Category rules are transparent title patterns, not AI full-text appraisal or evidence of efficacy. Clicking a year or theme filters the linked papers; complete source queries remain available.

The panel refreshes on opening and every 15 minutes while visible, with a 15-minute server cache. It cancels work when closed. Failed refreshes retain snapshots; partial responses retain matching older interval snapshots and label them. It does not send background alerts or operate after the page is closed.

Thirty-eight selected clinical profiles have separately curated bilingual priority/difficulty/bottleneck/outlook notes and vaccine/antiviral cards. Conditional outlooks are editorial inferences. Approval, recommendations, passive prevention, investigational therapies and supportive care are distinct; geography and indications matter. New paper metadata does not automatically rewrite clinical claims. Taxonomy records without a curated review explicitly show the knowledge gap instead of inheriting drugs or vaccines from related taxa.

`python3 sources/fetch_progress.py` rebuilds the five-year metadata snapshot. `sources/care-a.json` and `care-b.json` merge into `dist/care.json`; `sources/research-gaps.json` supplies `dist/gaps.json`. These reviewed resources carry their own date and sources. No institutional credentials or paywalled full text are stored.
