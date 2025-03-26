import numpy as np

####### Params for categroical values #######

PLAYING_TIME = { # moyenne
    "Any": np.nan,
    "Short (0-30 min)": 15,
    "Medium (30-60 min)": 45,
    "Long (60-120 min)": 90,
    "Very long (120+ min)": 120
}

AGE = { # moyenne
    "Any": np.nan,
    "Toddler (0-3 years)": 1.5,
    "Child (4-12 years)": 8,
    "Teenager (12-18 years)": 15,
    "Adult (18+ years)": 18
}

YEAR_PUBLISHED = {  # Average
    "Any": np.nan,
    "Oldschool (< 1851)": 1850,
    "Ancient (1851 - 1979)": 1915,
    "Modern (1980-2000)": 1990,
    "Recent (2000-2019)": 2009,
    "New (2020+)": 2020
}

CLUSTER_MAP = {
    0: "The Forgotten → Flops & unknown games",
    1: "Hidden Treasures → Niche games underappreciated",
    2: "Must Have → Popular well-rated classics",
    3: "Challengers → Mid-tier popularity games"
}

CLUSTER_CENTERS = [
    #     average  ,   User rated
    [3.04758271e-01, 9.10375542e-01],  # Cluster 0
    [6.66641581e+00, 1.39517327e+02],  # Cluster 1
    [7.65193971e+00, 6.26958406e+04],  # Cluster 2
    [7.31720972e+00, 1.62397414e+04]  # Cluster 3
]
