import sqlite3, pandas as pd
df = pd.read_csv("glp1_trials_clean.csv")
conn = sqlite3.connect("glp1_trials.db")
df.to_sql("trials", conn, if_exists="replace", index=False)
# one row per trial-indication (multi-label) for indication analysis
ind = df[["nct_id", "start_year", "indications"]].assign(indication=df["indications"].str.split("; ")).explode("indication")
ind[["nct_id", "start_year", "indication"]].to_sql("trial_indications", conn, if_exists="replace", index=False)

def q(title, sql):
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)
    print(pd.read_sql(sql, conn).to_string(index=False))

q("Q1 Top sponsors", """SELECT sponsor_clean, COUNT(*) n, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM trials),1) pct
    FROM trials GROUP BY 1 ORDER BY n DESC LIMIT 10""")
q("Q2 Novo+Lilly share of trial starts by year", """SELECT CAST(start_year AS INT) yr, COUNT(*) n,
    ROUND(100.0*SUM(sponsor_clean IN ('Novo Nordisk','Eli Lilly'))/COUNT(*),1) novo_lilly_pct,
    ROUND(100.0*SUM(funder_type='INDUSTRY' AND sponsor_clean NOT IN ('Novo Nordisk','Eli Lilly'))/COUNT(*),1) other_industry_pct
    FROM trials WHERE start_year BETWEEN 2019 AND 2025 GROUP BY 1 ORDER BY 1""")
q("Q3 Indication growth (multi-label), 2021 vs 2025", """SELECT indication,
    SUM(start_year=2021) n_2021, SUM(start_year=2025) n_2025,
    SUM(start_year BETWEEN 2024 AND 2026) n_2024_26
    FROM trial_indications GROUP BY 1 ORDER BY n_2025 DESC""")
q("Q4 Mechanism mix by start year", """SELECT CAST(start_year AS INT) yr, mechanism, COUNT(*) n FROM trials
    WHERE start_year BETWEEN 2022 AND 2026 AND mechanism NOT IN ('GLP-1 RA','Other/Unclassified')
    GROUP BY 1,2 ORDER BY 1, n DESC""")
q("Q5 Phase mix for newer-mechanism trials", """SELECT mechanism, phase, COUNT(*) n FROM trials
    WHERE mechanism IN ('Triple agonist','GLP-1/glucagon dual','Amylin','Oral small-molecule')
    GROUP BY 1,2 ORDER BY 1, n DESC""")
q("Q6 Industry vs academic", "SELECT funder_type, COUNT(*) n FROM trials GROUP BY 1 ORDER BY n DESC")
q("Q7 India footprint", """SELECT CAST(start_year AS INT) yr, COUNT(*) n, SUM(has_india_site) india_trials
    FROM trials WHERE start_year BETWEEN 2019 AND 2025 GROUP BY 1 ORDER BY 1""")
q("Q8 Status / stall rate", """SELECT status, COUNT(*) n, ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM trials),1) pct
    FROM trials GROUP BY 1 ORDER BY n DESC""")
q("Q9 Challengers (non Novo/Lilly industry) by new-mechanism trials", """SELECT sponsor_clean, COUNT(*) n FROM trials
    WHERE funder_type='INDUSTRY' AND sponsor_clean NOT IN ('Novo Nordisk','Eli Lilly')
    AND mechanism IN ('Triple agonist','GLP-1/glucagon dual','Amylin','Oral small-molecule','Other/Unclassified')
    GROUP BY 1 ORDER BY n DESC LIMIT 12""")
conn.close()
