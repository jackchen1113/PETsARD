"""Generate 10,000 fake citizen records with realistic distributions.

Column names use ASCII (English) to avoid encoding issues in the PETsARD
YAML workflow on Windows; the values are kept in Traditional Chinese.
Output: citizens.csv (UTF-8 without BOM)
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(20260101)

NUM_ROWS = 10000

# 城市 with population-like weights
cities = pd.DataFrame(
    {
        "city": [
            "新北市", "臺北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市",
            "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
            "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣",
        ],
        "weight": [
            30, 20, 16, 19, 14, 20, 3, 4, 2, 4, 4, 9, 4, 5, 4, 6, 3, 2, 2, 1, 1, 0.3,
        ],
    }
)
city_weights = cities["weight"] / cities["weight"].sum()
cities_arr = rng.choice(cities["city"].values, size=NUM_ROWS, p=city_weights)

genders = rng.choice(["男", "女"], size=NUM_ROWS, p=[0.5, 0.5])

# Age: mixture to mimic population pyramid (young + middle-aged dominant)
age_base = np.concatenate(
    [
        rng.normal(32, 10, int(NUM_ROWS * 0.6)),
        rng.normal(60, 12, int(NUM_ROWS * 0.3)),
        rng.normal(12, 6, int(NUM_ROWS * 0.1)),
    ]
)
ages = np.clip(np.round(age_base), 0, 100).astype(int)
ages = ages[:NUM_ROWS]
rng.shuffle(ages)

education_levels = ["國小", "國中", "高中職", "專科", "大學", "碩士", "博士"]
education_probs = [0.05, 0.10, 0.25, 0.15, 0.28, 0.14, 0.03]
education = rng.choice(education_levels, size=NUM_ROWS, p=education_probs)
edu_index = np.array([education_levels.index(e) for e in education])

# Income (NTD/year) depends on age, education, and noise
prof_income_base = 12_000 + 0.16 * ages * 12_000 + edu_index * 38_000
income_noise = rng.normal(0, 150_000, NUM_ROWS)
annual_income = np.clip(np.round(prof_income_base + income_noise), 0, 5_000_000).astype(int)

# Occupation correlated with age & education
occupation_pool = [
    "教師", "軟體工程師", "醫師", "護理師", "公務員", "業務人員",
    "餐飲服務", "零售業", "製造業作業員", "營造業工人", "農林漁牧", "計程車司機",
    "自由業",
]
occ_profiles = [
    ("學生", lambda a, e: a < 26 and e < 3, 0.8),
    ("退休", lambda a, e: a >= 60, 0.7),
    ("家管", lambda a, e: (30 <= a <= 55), 0.12),
    ("失業", lambda a, e: (20 <= a <= 55), 0.04),
]
occupation = []
for i in range(NUM_ROWS):
    age, e = ages[i], edu_index[i]
    chosen = None
    for occ, cond, prob in occ_profiles:
        if cond(age, e) and rng.random() < prob:
            chosen = occ
            break
    if chosen is None:
        chosen = rng.choice(occupation_pool)
    occupation.append(chosen)
occupation = np.array(occupation)

# Marital status correlated with age
marital = []
for i in range(NUM_ROWS):
    age = ages[i]
    if age < 22:
        marital.append("未婚")
    elif age < 35:
        marital.append(rng.choice(["未婚", "已婚"], p=[0.45, 0.55]))
    elif age < 60:
        marital.append(rng.choice(["已婚", "離婚"], p=[0.82, 0.18]))
    else:
        marital.append(rng.choice(["已婚", "離婚", "喪偶"], p=[0.7, 0.1, 0.2]))
marital = np.array(marital)

household_size = rng.choice(
    np.arange(1, 9), size=NUM_ROWS, p=[0.08, 0.25, 0.3, 0.2, 0.1, 0.04, 0.02, 0.01]
)

residence_years = np.clip(
    np.round(ages * rng.uniform(0.05, 0.95, NUM_ROWS)), 0, 70
).astype(int)

df = pd.DataFrame(
    {
        "city": cities_arr,
        "gender": genders,
        "age": ages,
        "education": education,
        "occupation": occupation,
        "marital_status": marital,
        "annual_income": annual_income,
        "household_size": household_size,
        "residence_years": residence_years,
    }
)

df.to_csv("citizens.csv", index=False, encoding="utf-8")
print(f"Generated {len(df):,} rows -> citizens.csv")
print(df.dtypes)