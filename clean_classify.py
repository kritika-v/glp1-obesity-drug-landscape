"""Clean + classify GLP-1 / obesity trials from a ClinicalTrials.gov CSV export."""
import re
import pandas as pd

df = pd.read_csv("ctg_studies_raw.csv")   # rename to your file name
print("Raw rows:", len(df))

# ---------- 1. Basic cleaning ----------
df = df.drop_duplicates("NCT Number")
df["Phases"] = df["Phases"].fillna("NOT_APPLICABLE").str.replace("|", "/", regex=False)
df["start_year"] = pd.to_datetime(df["Start Date"], errors="coerce").dt.year
df = df.rename(columns={"NCT Number": "nct_id", "Study Title": "title", "Study Status": "status",
                        "Conditions": "conditions", "Interventions": "interventions",
                        "Sponsor": "sponsor", "Phases": "phase", "Enrollment": "enrollment",
                        "Funder Type": "funder_type", "Locations": "locations"})

# ---------- 2. Sponsor normalisation (extend this list yourself) ----------
sponsor_map = {
    "Novo Nordisk A/S": "Novo Nordisk",
    "Eli Lilly and Company": "Eli Lilly",
    "Innovent Biologics (Suzhou) Co. Ltd.": "Innovent",
    "Hangzhou Sciwind Biosciences Co., Ltd.": "Sciwind",
    "Merck Sharp & Dohme LLC": "Merck",
    "Hangzhou Zhongmei Huadong Pharmaceutical Co., Ltd.": "Huadong Medicine",
    "BrightGene Bio-Medical Technology Co., Ltd.": "BrightGene",
}
big_pharma = {"Novo Nordisk", "Eli Lilly", "Boehringer Ingelheim", "Merck", "AstraZeneca", "Sanofi", "Pfizer"}
chinese_cos = {"Innovent", "Sciwind", "Huadong Medicine", "BrightGene"}
df["sponsor_clean"] = df["sponsor"].replace(sponsor_map)
def sponsor_type(r):
    if r["sponsor_clean"] in big_pharma: return "Big pharma"
    if r["sponsor_clean"] in chinese_cos: return "Chinese biotech"
    if r["funder_type"] == "INDUSTRY": return "Other biotech/industry"
    return "Academic/Gov/Other"
df["sponsor_type"] = df.apply(sponsor_type, axis=1)

# ---------- 3. Mechanism classification (from intervention text) ----------
drug_class = {
    "GLP-1 RA":              ["semaglutide", "liraglutide", "dulaglutide", "exenatide", "ecnoglutide",
                              "efpeglenatide", "lixisenatide", "beinaglutide", "supaglutide", "polyethylene glycol loxenatide",
                              "ozempic", "wegovy", "rybelsus", "victoza", "saxenda", "trulicity", "byetta", "bydureon",
                              "glp-1 medication", "glp-1 receptor agonist", "glp1", "xw003", "ideglira", "icosema", "glucagon-like peptide 1"],
    "GIP/GLP-1 dual":        ["tirzepatide", "zepbound", "mounjaro", "gip/glp-1", "ly3298176"],
    "GLP-1/glucagon dual":   ["survodutide", "bi 456906", "mazdutide", "efinopegdutide", "ibi362", "ly3305677"],
    "Triple agonist":        ["retatrutide", "ly3437943"],
    "Amylin":                ["cagrilintide", "cagrisema", "petrelintide"],
    "Oral small-molecule":   ["orforglipron", "danuglipron", "ly3502970"],
}
def classify_mech(text):
    t = str(text).lower()
    found = [k for k, drugs in drug_class.items() if any(d in t for d in drugs)]
    if "cagrisema" in t and "Amylin" not in found:
        found.append("Amylin")
    return found

df["mech_list"] = df["interventions"].apply(classify_mech)
df["mechanism"] = df["mech_list"].apply(
    lambda m: "Other/Unclassified" if not m else (m[0] if len(m) == 1 else "Multi-class (combo/head-to-head)"))

# ---------- 4. Indication classification (multi-label) ----------
indication_rules = {
    "Obesity/Overweight":   r"obes|overweight|weight (loss|manage|reduc)|body weight",
    "Type 2 Diabetes":      r"type 2 diab|t2d|diabetes mellitus, type 2|type2",
    "Type 1 Diabetes":      r"type 1 diab|t1d",
    "MASH/Fatty Liver":     r"mash|nash|steato|fatty liver|nafld|masld",
    "Cardiovascular":       r"cardio|heart|myocard|atheroscl|coronary|hypertens|stroke|vascular",
    "Kidney (CKD)":         r"kidney|renal|nephro|ckd",
    "Sleep Apnea":          r"sleep apnea|apnoea|osa\b",
    "PCOS/Reproductive":    r"pcos|polycystic|infertil",
    "Neuro/Addiction":      r"alzheimer|parkinson|alcohol|addict|smoking|dementia|cognit",
    "Musculoskeletal":      r"osteoarth|knee|sarcopen",
}
def classify_ind(row):
    t = f"{row['conditions']} {row['title']}".lower()
    hits = [k for k, pat in indication_rules.items() if re.search(pat, t)]
    return hits or ["Other"]
df["indications"] = df.apply(classify_ind, axis=1)
df["primary_indication"] = df["indications"].apply(lambda x: x[0])
df["indications"] = df["indications"].apply("; ".join)

# ---------- 5. Country footprint ----------
def countries(loc):
    if pd.isna(loc): return []
    out = set()
    for site in str(loc).split("|"):
        parts = [p.strip() for p in site.split(",")]
        if parts: out.add(parts[-1])
    return sorted(out)
df["country_list"] = df["locations"].apply(countries)
df["n_countries"] = df["country_list"].apply(len)
df["has_india_site"] = df["country_list"].apply(lambda c: "India" in c)
df["countries"] = df["country_list"].apply("; ".join)

keep = ["nct_id", "title", "status", "phase", "enrollment", "start_year", "sponsor", "sponsor_clean",
        "funder_type", "sponsor_type", "mechanism", "indications", "primary_indication", "n_countries",
        "has_india_site", "countries", "conditions", "interventions"]
df[keep].to_csv("glp1_trials_clean.csv", index=False)
print("Saved", len(df), "rows -> glp1_trials_clean.csv")
print(df["mechanism"].value_counts())
