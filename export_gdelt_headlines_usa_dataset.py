from google.cloud import bigquery
import pandas as pd
import json

# ------------------------------------------------------------
# Exportiert GDELT-Headlines fuer ausgewaehlte US-Medienhaeuser.
#
# Ziel:
# - 100 Nachrichten pro Medienhaus, sofern in GDELT vorhanden
# - Bias-Kategorie aus der vorgegebenen Liste mitspeichern
# - JSON-Export wie bisher
#
# Wichtig:
# - Der Titel steht in "headline"
# - Es werden nur politische News exportiert
# - Matching laeuft ueber Domains in der URL
# - Standardmaessig werden englische Artikel von 2019 bis 2025 genutzt
# ------------------------------------------------------------

ARTICLES_PER_OUTLET = 100
START_DATE = "2019-01-01"
END_DATE = "2025-12-31"
MIN_HEADLINE_WORDS = 5
OUTPUT_FILE = "gdelt_us_media_headlines_by_outlet_100_each.json"

OUTLETS = [
    # LEFT
    {"bias": "LEFT", "outlet": "AlterNet", "domains": ["alternet.org"]},
    {"bias": "LEFT", "outlet": "AP", "domains": ["apnews.com"]},
    {"bias": "LEFT", "outlet": "The Atlantic", "domains": ["theatlantic.com"]},
    {"bias": "LEFT", "outlet": "Daily Beast", "domains": ["thedailybeast.com"]},
    {"bias": "LEFT", "outlet": "Democracy Now!", "domains": ["democracynow.org"]},
    {"bias": "LEFT", "outlet": "The Guardian", "domains": ["theguardian.com"]},
    {"bias": "LEFT", "outlet": "HuffPost", "domains": ["huffpost.com"]},
    {"bias": "LEFT", "outlet": "The Intercept", "domains": ["theintercept.com"]},
    {"bias": "LEFT", "outlet": "Jacobin", "domains": ["jacobin.com"]},
    {"bias": "LEFT", "outlet": "Mother Jones", "domains": ["motherjones.com"]},
    {"bias": "LEFT", "outlet": "MSNOW", "domains": ["msnbc.com", "ms.now"]},
    {"bias": "LEFT", "outlet": "The Nation", "domains": ["thenation.com"]},
    {"bias": "LEFT", "outlet": "The New York Times (opinion)", "domains": ["nytimes.com"], "url_hint": "opinion"},
    {"bias": "LEFT", "outlet": "The New Yorker", "domains": ["newyorker.com"]},
    {"bias": "LEFT", "outlet": "Slate", "domains": ["slate.com"]},
    {"bias": "LEFT", "outlet": "Vox", "domains": ["vox.com"]},

    # LEAN LEFT
    {"bias": "LEAN LEFT", "outlet": "ABC News", "domains": ["abcnews.go.com"]},
    {"bias": "LEAN LEFT", "outlet": "Axios", "domains": ["axios.com"]},
    {"bias": "LEAN LEFT", "outlet": "Bloomberg", "domains": ["bloomberg.com"]},
    {"bias": "LEAN LEFT", "outlet": "CBS News", "domains": ["cbsnews.com"]},
    {"bias": "LEAN LEFT", "outlet": "CNBC", "domains": ["cnbc.com"]},
    {"bias": "LEAN LEFT", "outlet": "CNN", "domains": ["cnn.com"]},
    {"bias": "LEAN LEFT", "outlet": "Insider", "domains": ["businessinsider.com", "insider.com"]},
    {"bias": "LEAN LEFT", "outlet": "NBC News", "domains": ["nbcnews.com"]},
    {"bias": "LEAN LEFT", "outlet": "The New York Times (news)", "domains": ["nytimes.com"], "exclude_hint": "opinion"},
    {"bias": "LEAN LEFT", "outlet": "NPR", "domains": ["npr.org"]},
    {"bias": "LEAN LEFT", "outlet": "Politico", "domains": ["politico.com"]},
    {"bias": "LEAN LEFT", "outlet": "ProPublica", "domains": ["propublica.org"]},
    {"bias": "LEAN LEFT", "outlet": "Semafor", "domains": ["semafor.com"]},
    {"bias": "LEAN LEFT", "outlet": "Time", "domains": ["time.com"]},
    {"bias": "LEAN LEFT", "outlet": "USA Today", "domains": ["usatoday.com"]},
    {"bias": "LEAN LEFT", "outlet": "The Washington Post", "domains": ["washingtonpost.com"]},
    {"bias": "LEAN LEFT", "outlet": "Yahoo News", "domains": ["news.yahoo.com", "yahoo.com/news"]},

    # CENTER
    {"bias": "CENTER", "outlet": "1440", "domains": ["join1440.com", "1440daily.com"]},
    {"bias": "CENTER", "outlet": "BBC News", "domains": ["bbc.com", "bbc.co.uk"]},
    {"bias": "CENTER", "outlet": "The Christian Science Monitor", "domains": ["csmonitor.com"]},
    {"bias": "CENTER", "outlet": "Forbes", "domains": ["forbes.com"]},
    {"bias": "CENTER", "outlet": "The Hill", "domains": ["thehill.com"]},
    {"bias": "CENTER", "outlet": "MarketWatch", "domains": ["marketwatch.com"]},
    {"bias": "CENTER", "outlet": "Morning Brew", "domains": ["morningbrew.com"]},
    {"bias": "CENTER", "outlet": "NewsNation", "domains": ["newsnationnow.com"]},
    {"bias": "CENTER", "outlet": "Newsweek", "domains": ["newsweek.com"]},
    {"bias": "CENTER", "outlet": "Reason", "domains": ["reason.com"]},
    {"bias": "CENTER", "outlet": "Reuters", "domains": ["reuters.com"]},
    {"bias": "CENTER", "outlet": "SAN (Straight Arrow News)", "domains": ["straightarrownews.com"]},
    {"bias": "CENTER", "outlet": "Tangle", "domains": ["readtangle.com", "tangle.news"]},
    {"bias": "CENTER", "outlet": "The Wall Street Journal (news)", "domains": ["wsj.com"], "exclude_hint": "opinion"},

    # LEAN RIGHT
    {"bias": "LEAN RIGHT", "outlet": "Daily Mail", "domains": ["dailymail.co.uk"]},
    {"bias": "LEAN RIGHT", "outlet": "The Dispatch", "domains": ["thedispatch.com"]},
    {"bias": "LEAN RIGHT", "outlet": "The Epoch Times", "domains": ["theepochtimes.com", "epochtimes.com"]},
    {"bias": "LEAN RIGHT", "outlet": "Fox Business", "domains": ["foxbusiness.com"]},
    {"bias": "LEAN RIGHT", "outlet": "The Free Press", "domains": ["thefp.com"]},
    {"bias": "LEAN RIGHT", "outlet": "Just the News", "domains": ["justthenews.com"]},
    {"bias": "LEAN RIGHT", "outlet": "National Review (news)", "domains": ["nationalreview.com"], "exclude_hint": "opinion"},
    {"bias": "LEAN RIGHT", "outlet": "New York Post (news)", "domains": ["nypost.com"], "exclude_hint": "opinion"},
    {"bias": "LEAN RIGHT", "outlet": "RealClear Politics", "domains": ["realclearpolitics.com"]},
    {"bias": "LEAN RIGHT", "outlet": "Upward", "domains": ["upward.news"]},
    {"bias": "LEAN RIGHT", "outlet": "The Wall Street Journal (opinion)", "domains": ["wsj.com"], "url_hint": "opinion"},
    {"bias": "LEAN RIGHT", "outlet": "Washington Examiner", "domains": ["washingtonexaminer.com"]},
    {"bias": "LEAN RIGHT", "outlet": "The Washington Times", "domains": ["washingtontimes.com"]},
    {"bias": "LEAN RIGHT", "outlet": "ZeroHedge", "domains": ["zerohedge.com"]},

    # RIGHT
    {"bias": "RIGHT", "outlet": "The American Conservative", "domains": ["theamericanconservative.com"]},
    {"bias": "RIGHT", "outlet": "The American Spectator", "domains": ["spectator.org"]},
    {"bias": "RIGHT", "outlet": "Blaze Media", "domains": ["theblaze.com", "blazemedia.com"]},
    {"bias": "RIGHT", "outlet": "Breitbart", "domains": ["breitbart.com"]},
    {"bias": "RIGHT", "outlet": "CBN", "domains": ["cbn.com"]},
    {"bias": "RIGHT", "outlet": "The Daily Caller", "domains": ["dailycaller.com"]},
    {"bias": "RIGHT", "outlet": "Daily Wire", "domains": ["dailywire.com"]},
    {"bias": "RIGHT", "outlet": "Fox News", "domains": ["foxnews.com"]},
    {"bias": "RIGHT", "outlet": "The Federalist", "domains": ["thefederalist.com"]},
    {"bias": "RIGHT", "outlet": "Independent Journal Review", "domains": ["ijr.com"]},
    {"bias": "RIGHT", "outlet": "National Review (opinion)", "domains": ["nationalreview.com"], "url_hint": "opinion"},
    {"bias": "RIGHT", "outlet": "New York Post (opinion)", "domains": ["nypost.com"], "url_hint": "opinion"},
    {"bias": "RIGHT", "outlet": "Newsmax", "domains": ["newsmax.com"]},
    {"bias": "RIGHT", "outlet": "OAN", "domains": ["oann.com"]},
    {"bias": "RIGHT", "outlet": "The Post Millennial", "domains": ["thepostmillennial.com"]},
    {"bias": "RIGHT", "outlet": "Washington Free Beacon", "domains": ["freebeacon.com"]},
]


def domain_regex(domains):
    escaped_domains = [domain.replace(".", r"\.") for domain in domains]
    return r"(^|://|\.|/)(" + "|".join(escaped_domains) + r")(/|$)"


def build_outlets_cte(outlets):
    rows = []
    for outlet in outlets:
        rows.append(
            "SELECT "
            f"{json.dumps(outlet['bias'])} AS bias_category, "
            f"{json.dumps(outlet['outlet'])} AS target_outlet, "
            f"r'{domain_regex(outlet['domains'])}' AS domain_pattern, "
            f"{json.dumps(outlet.get('url_hint'))} AS url_hint, "
            f"{json.dumps(outlet.get('exclude_hint'))} AS exclude_hint"
        )
    return "\n  UNION ALL\n  ".join(rows)


client = bigquery.Client()
outlets_cte = build_outlets_cte(OUTLETS)

query = f"""
WITH outlets AS (
  {outlets_cte}
),

base AS (
  SELECT
    DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(g.DATE AS STRING))) AS article_date,
    EXTRACT(YEAR FROM DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(g.DATE AS STRING)))) AS article_year,
    g.DocumentIdentifier AS url,
    g.SourceCommonName AS source_common_name,
    g.V2Themes,
    g.V2Tone
  FROM `gdelt-bq.gdeltv2.gkg_partitioned` g
  WHERE DATE(_PARTITIONTIME) BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
    AND g.DocumentIdentifier IS NOT NULL
    AND LOWER(g.DocumentIdentifier) LIKE 'http%'
),

joined AS (
  SELECT
    b.article_date,
    b.article_year,
    b.url,
    COALESCE(gal.title, gal.desc) AS headline,
    COALESCE(gal.outletName, b.source_common_name) AS source,
    LOWER(COALESCE(gal.lang, '')) AS lang,
    b.V2Themes,
    b.V2Tone
  FROM base b
  LEFT JOIN `gdelt-bq.gdeltv2.gal` gal
    ON b.url = gal.url
),

matched AS (
  SELECT
    o.bias_category,
    o.target_outlet,
    j.article_date,
    j.article_year,
    j.url,
    j.headline,
    j.source,
    j.lang,
    j.V2Tone,
    j.V2Themes
  FROM joined j
  JOIN outlets o
    ON REGEXP_CONTAINS(LOWER(j.url), o.domain_pattern)
  WHERE j.headline IS NOT NULL
    AND TRIM(j.headline) != ''
    AND j.lang = 'en'
    AND ARRAY_LENGTH(REGEXP_EXTRACT_ALL(TRIM(j.headline), r'\\S+')) >= {MIN_HEADLINE_WORDS}
    AND (o.url_hint IS NULL OR REGEXP_CONTAINS(LOWER(j.url), LOWER(o.url_hint)))
    AND (o.exclude_hint IS NULL OR NOT REGEXP_CONTAINS(LOWER(j.url), LOWER(o.exclude_hint)))
    AND (
      REGEXP_CONTAINS(
        LOWER(COALESCE(j.V2Themes, '')),
        r'politic|election|general_government|uspec_policy|epu_policy|tax_political_party|tax_fncact_(president|senator|governor|mayor|minister|prime_minister|congressman|congresswoman|lawmaker|officials)|wb_696_public_sector_management|wb_723_public_administration|wb_840_justice|legislation|democracy|diplomacy|negotiations'
      )
      OR
      REGEXP_CONTAINS(
        LOWER(j.headline),
        r'\b(election|campaign|vote|voting|voter|ballot|poll|polls|primary|caucus|president|white house|congress|senate|senator|house speaker|lawmakers|legislation|legislature|bill|policy|administration|democrat|democratic|republican|gop|liberal|conservative|supreme court|federal judge|governor|mayor|trump|biden|harris|cabinet|impeachment)\b'
      )
    )
),

deduplicated AS (
  SELECT *
  FROM matched
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY target_outlet, url
    ORDER BY article_date DESC
  ) = 1
),

ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY target_outlet
      ORDER BY rn_within_year, RAND()
    ) AS rn
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY target_outlet, article_year
        ORDER BY RAND()
      ) AS rn_within_year
    FROM deduplicated
  )
)

SELECT
  bias_category,
  target_outlet AS outlet,
  article_date,
  article_year,
  url,
  headline,
  source,
  lang,
  V2Tone,
  V2Themes
FROM ranked
WHERE rn <= {ARTICLES_PER_OUTLET}
ORDER BY bias_category, outlet, article_date DESC
"""

print("Starte BigQuery-Abfrage ...")
df = client.query(query).to_dataframe()
print(f"Geladene Zeilen: {len(df)}")

if "article_date" in df.columns:
    df["article_date"] = df["article_date"].astype(str)

if "article_year" in df.columns:
    df["article_year"] = pd.to_numeric(df["article_year"], errors="coerce")

df.insert(0, "id", [f"msg_{idx:06d}" for idx in range(1, len(df) + 1)])

records = df.to_dict(orient="records")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2, default=str)

counts = (
    df.groupby(["bias_category", "outlet"])
    .size()
    .reset_index(name="count")
    .sort_values(["bias_category", "outlet"])
)

print(f"Fertig. {len(records)} Zeilen gespeichert in: {OUTPUT_FILE}")
print("\nZeilen pro Medienhaus:")
print(counts.to_string(index=False))
