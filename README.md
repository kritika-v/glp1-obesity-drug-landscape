# GLP-1 / Obesity Drug Trial Landscape: Competitive Intelligence Analysis

An analysis of **1,454 interventional clinical trials** involving GLP-1-based obesity and diabetes drugs (semaglutide, tirzepatide, retatrutide, orforglipron, survodutide, cagrilintide, mazdutide, ecnoglutide, liraglutide), built from ClinicalTrials.gov data. It covers data cleaning, mechanism and indication classification, SQL analysis, and a strategy memo.

**Strategy memo:** [glp1_strategy_memo.pdf](glp1_strategy_memo.pdf)

## Business question

After Wegovy and Zepbound, who is building the next generation of obesity drugs, which indications are they expanding into, and how contestable is the market for a mid-size company?

## Key findings

- **Concentration is falling.** Novo Nordisk and Eli Lilly sponsored 58.6% of trial starts in 2019 and 22.3% in 2025. The Herfindahl-Hirschman Index (HHI) for industry-sponsored trials fell from about 4,500 to about 1,600, moving from "highly concentrated" to "moderately concentrated".
- **Challengers are emerging.** Boehringer Ingelheim and Chinese developers (Innovent, Sciwind, Huadong) lead non-Novo/Lilly activity on newer mechanisms.
- **Obesity is now the centre of gravity.** Obesity-related trial starts rose from 30 (2021) to 112 (2025) while type 2 diabetes was flat (31 to 33). Cardiovascular and kidney trials are growing from a small base.
- **Newer mechanisms are early.** Classic GLP-1 agonists account for 926 trials versus 49 oral small-molecule, 26 triple-agonist, 63 GLP-1/glucagon dual and 12 amylin trials. About half of oral and triple-agonist trials are already in Phase 3; amylin is mostly Phase 1.
- **Low stall rate.** 3.9% of trials are terminated, withdrawn or suspended.

## Method

1. **Collect:** ClinicalTrials.gov search by intervention (drug names, all conditions), interventional studies only, exported as CSV with full field set (`ctg_studies_raw.csv`).
2. **Clean:** deduplicate NCT IDs, normalise phases, parse start year, and map sponsor names to groups (big pharma, Chinese biotech, other industry, academic).
3. **Classify:**
   - *Mechanism* from intervention text using a dictionary of generic names, brand names and code names (for example LY3437943 = retatrutide).
   - *Indication* (multi-label) from condition and title text using regex rules.
   - *Country footprint* parsed from site locations.
4. **Analyse:** loaded into SQLite and queried for sponsor share, HHI, indication growth, mechanism mix by phase, phase maturity and status.

## Tech stack

Python (pandas, regex), SQL (SQLite).

## Repository structure

```
├── ctg_studies_raw.csv      # Raw export from ClinicalTrials.gov
├── clean_classify.py        # Cleaning, mechanism/indication/sponsor classification
├── load_and_analyze.py      # Loads SQLite and runs analysis queries
├── glp1_trials_clean.csv    # Cleaned and classified dataset
├── glp1_trials.db           # SQLite database
├── glp1_strategy_memo.pdf   # One-page strategy memo
└── README.md
```

## Limitations

- **Search by drug name.** Companies developing other compounds are not captured, so results describe trials involving these drugs, not the whole obesity pipeline.
- **Trial counts are not market share.** Part of the fall in Novo/Lilly's share comes from academic groups running studies with approved drugs.
- **7% of trials are unclassified by mechanism**, mostly code-named compounds with little public detail.
- **2026 starts include planned trials**, so trend charts stop at 2025.
- Sponsor grouping and indication rules are keyword-based and were checked by sampling, not exhaustively.
- Snapshot taken in November 2026.

## Author

Kritika Verma
