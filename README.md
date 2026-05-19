# GDELT Headline Dataset

> **Bachelor Thesis** | Bachelor of Science in Digital Business & AI  
> Bern University of Applied Sciences (BFH) — Business School  
> Author: Carlos Gomez

## Part of a Three-Repository Project
 
This repository is one part of three interconnected repositories that together form the
complete research project. It provides the **data foundation**: a GDELT-based ETL
pipeline and a dataset of 7,187 political news headlines from 77 US outlets, balanced
across five bias categories (LEFT to RIGHT) according to the AllSides Media Bias Chart.
 
For the thesis analyses, a random subsample of 50 headlines was drawn from this dataset
using the included `sample_random_news.py` script and manually annotated to create a
ground truth for Analysis 2.1 in the evaluation app. The full dataset and pipeline are
published here for anyone who wants to collect their own GDELT data or work with the
broader headline corpus.
 
| Repository | What it contains |
|---|---|
| 📦 **[headline-debiasing-dataset](https://github.com/gomec1/headline-debiasing-dataset)** ← *you are here* | GDELT data pipeline + 7,187 headline dataset |
| 🔬 **[headline-debiasing-evaluation](https://github.com/gomec1/headline-debiasing-evalaluation)** | LLM evaluation app — bias detection and rewriting experiments across multiple models (research-grade, exploratory) |
| 🛠️ **[headline-debiasing-editor](https://github.com/gomec1/headline-debiasing-editor)** | The finished KI-Redakteur prototype — clean, user-facing tool for scoring and neutralizing headlines |
 
---

## Overview

This repository contains the data collection scripts and dataset developed as part of the bachelor thesis *"KI-gestützte Entbiasierung von Headlines — Design, Implementation und Evaluation"* (AI-Assisted Debiasing of News Headlines — Design, Implementation and Evaluation).

The thesis investigates how political bias in news headlines can be automatically detected and neutralized using Large Language Models (LLMs). The dataset compiled here forms the empirical foundation for the analyses conducted in the thesis.

---

## Repository Contents

| File | Description |
|------|-------------|
| `export_gdelt_headlines_usa_dataset.py` | ETL pipeline to export political news headlines from GDELT via Google BigQuery. Covers 77 US news outlets across 5 bias categories (LEFT, LEAN LEFT, CENTER, LEAN RIGHT, RIGHT) based on the AllSides Media Bias Chart. |
| `sample_random_news.py` | Utility script to draw random subsamples from the compiled dataset for analysis. Outputs results with full metadata and as a plain headline list. |
| `gdelt_us_media_headlines_by_outlet_100_each.json` | The compiled dataset: **7,187 political news headlines** from 77 US news outlets (up to 100 per outlet), covering the period January 2019 – December 2025. |

---

## Dataset Description

The dataset was built using the [GDELT Project](https://www.gdeltproject.org/) via Google BigQuery. Outlet selection follows the **AllSides Media Bias Chart**, covering all five political bias categories:

| Bias Category | Outlets |
|---------------|---------|
| LEFT | 16 outlets (e.g. HuffPost, The Guardian, Vox, Jacobin) |
| LEAN LEFT | 17 outlets (e.g. CNN, NPR, The Washington Post, The New York Times) |
| CENTER | 14 outlets (e.g. Reuters, BBC News, The Hill, Forbes) |
| LEAN RIGHT | 14 outlets (e.g. Fox Business, Washington Examiner, The Washington Times) |
| RIGHT | 16 outlets (e.g. Fox News, Breitbart, Daily Wire, The Federalist) |

### Filtering Criteria

Headlines were included only if they met all of the following conditions:

- URL is non-null and starts with `http`
- Headline is non-null, non-empty, and contains at least 5 words
- Language is English (`lang = 'en'`)
- Publication date falls between 1 January 2019 and 31 December 2025
- The article is classified as politically relevant via GDELT's `V2Themes` field **or** contains political keywords in the headline itself

### Sampling Strategy

To ensure temporal balance, articles were first shuffled randomly within each calendar year, then merged across years before selecting the top 100 per outlet. This prevents any single period (e.g. election cycles) from dominating the sample. Deduplication was applied at the URL level.

### Dataset Fields

Each record in `gdelt_us_media_headlines_by_outlet_100_each.json` contains:

| Field | Description |
|-------|-------------|
| `id` | Unique record ID (e.g. `msg_000001`) |
| `bias_category` | Political bias label (LEFT / LEAN LEFT / CENTER / LEAN RIGHT / RIGHT) |
| `outlet` | Name of the news outlet |
| `article_date` | Publication date (YYYY-MM-DD) |
| `article_year` | Publication year |
| `url` | Original article URL |
| `headline` | News headline |
| `source` | Source name as recorded in GDELT |
| `lang` | Language code (always `en`) |
| `V2Tone` | GDELT tone score |
| `V2Themes` | GDELT theme tags used for political filtering |

---

## Usage

### Prerequisites

- Python 3.8+
- Google Cloud account with BigQuery access (for `export_gdelt_headlines_usa_dataset.py`)
- `google-cloud-bigquery` and `pandas` packages

```bash
pip install google-cloud-bigquery pandas
```

### Re-running the Export

```bash
python export_gdelt_headlines_usa_dataset.py
```

> **Note:** Because the export uses `RAND()` for sampling within BigQuery, re-running the pipeline will produce a different random sample. The dataset committed to this repository represents the fixed snapshot used in the thesis.

### Drawing a Random Subsample

```bash
python sample_random_news.py
```

You will be prompted to enter how many headlines to sample. Results are printed with full metadata and as a plain headline list for direct use in analysis tools.

---

## Limitations

- GDELT indexing coverage varies by outlet. Large, internationally distributed portals typically reach the maximum of 100 headlines, while smaller or less-indexed outlets may contribute fewer articles.
- Paywalled content is underrepresented in GDELT.
- Where news and opinion sections share a domain (e.g. NYT, WSJ, National Review, New York Post), URL-based inclusion/exclusion rules were applied to separate them — this separation may not be perfectly consistent across all outlets.

---

## Related Work

This dataset was developed in the context of the following thesis and builds on the following key references:

- Lyu et al. (2024). *Computational Assessment of Hyperpartisanship in News Titles.* ICWSM. https://doi.org/10.1609/icwsm.v18i1.31368
- AllSides Media Bias Chart: https://www.allsides.com/media-bias/media-bias-chart
- GDELT Project: https://www.gdeltproject.org/

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Academic Context

This repository accompanies the bachelor thesis:

> **KI-gestützte Entbiasierung von Headlines — Design, Implementation und Evaluation**
> Carlos Gomez  
> Bachelor of Science in Digital Business & AI  
> Bern University of Applied Sciences (BFH), Business School  
> Supervised by: Prof. Ulrich Matter (IADSF, Departement W)
