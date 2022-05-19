import pandas as pd

PARANA_ID = 29
SANTA_FE_ID = 30
DIAMANTE_ID = 31
SAN_FERNANDO_ID = 52
SAN_FERNANDO_FORECAST_ID = 1838
BSAS_ID = 85
MARTINEZ_ID = 1696
NUEVA_PALMIRA_ID = 1699
NUEVA_PALMIRA_FORECAST_ID = 1843

ID_MODELO = 308

Df_Estaciones = pd.DataFrame.from_dict(
    {
        "id": [
            PARANA_ID,
            SANTA_FE_ID,
            DIAMANTE_ID,
            SAN_FERNANDO_ID,
            BSAS_ID,
            MARTINEZ_ID,
            NUEVA_PALMIRA_ID,
        ],
        "nombre": [
            "Parana",
            "SantaFe",
            "Diamante",
            "SanFernando",
            "BsAs",
            "Martinez",
            "Nueva Palmira",
        ],
        "series_id": [29, 30, 31, 52, 85, 3278, 3280],
        "cero_escala": [9.432, 8.378, 6.747, -0.53, 0, 0, 0.0275],
    }
).set_index("id")

df_cb = pd.DataFrame.from_records(
    [
        {
            "FID": 1,
            "River": "AnaCua",
            "Reach": "Canal_AnaCua",
            "River_Stat": "25686.44",
            "Interval": "1DAY",
            "CondBorde": "Flow Hydrograph",
        },
        {
            "FID": 2,
            "River": "Parana",
            "Reach": "Embalse",
            "River_Stat": "1115600",
            "Interval": "1DAY",
            "CondBorde": "Flow Hydrograph",
        },
        {
            "FID": 3,
            "River": "Paraguay",
            "Reach": "Paraguay",
            "River_Stat": "375000",
            "Interval": "1DAY",
            "CondBorde": "Flow Hydrograph",
        },
        {
            "FID": 4,
            "River": "Parana",
            "Reach": "Palmas-Desemboca",
            "River_Stat": "-29.4",
            "Interval": "1DAY",
            "CondBorde": "Stage Hydrograph",
        },
        {
            "FID": 5,
            "River": "Parana",
            "Reach": "Bravo-Desembocad",
            "River_Stat": "0",
            "Interval": "1DAY",
            "CondBorde": "Stage Hydrograph",
        },
        {
            "FID": 6,
            "River": "Parana",
            "Reach": "Mini-Desembocadu",
            "River_Stat": "0",
            "Interval": "1DAY",
            "CondBorde": "Stage Hydrograph",
        },
        {
            "FID": 7,
            "River": "Parana",
            "Reach": "Guazu-6Desemboca",
            "River_Stat": "-37.96",
            "Interval": "1DAY",
            "CondBorde": "Stage Hydrograph",
        },
        {
            "FID": 8,
            "River": "Parana",
            "Reach": "BarcaGrande",
            "River_Stat": "0",
            "Interval": "1DAY",
            "CondBorde": "Stage Hydrograph",
        },
        {
            "FID": 9,
            "River": "Parana",
            "Reach": "Sauce",
            "River_Stat": "0",
            "Interval": "1DAY",
            "CondBorde": "Stage Hydrograph",
        },
    ]
)
