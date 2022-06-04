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

ID_MODELO = 445

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
        "series_id": [29, 30, 31, 52, 85, 26285, 3280],
        "cero_escala": [9.432, 8.378, 6.747, -0.53, 0, 0, 0.0275],
    }
).set_index("id")

border_conditions_points = pd.DataFrame.from_records(
    [
        {
            "river": "Bravo",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "Mini",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "BarcaGrande",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "Sauce",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "LaBarquita",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "CanaldelEste",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "Lujan",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "SanAntonio",
            "reach": "Desembocadura",
            "river_stat": "0",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "Palmas",
            "reach": "Desembocadura",
            "river_stat": "6246.783",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "Gutierrez",
            "reach": "Desembocadura",
            "river_stat": "1960.748",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "Guazu",
            "reach": "Desembocadura",
            "river_stat": "8000",
            "interval": "1HOUR",
            "border_condition": "Stage Hydrograph",
        },
    ]
)

entry_points = pd.DataFrame.from_records(
    [
        {
            "river": "Parana",
            "reach": "ParanaAA",
            "river_stat": "224000",
            "interval": "1DAY",
            "border_condition": "Stage Hydrograph",
        },
        {
            "river": "Lujan",
            "reach": "1",
            "river_stat": "30.664",
            "interval": "1HOUR",
            "border_condition": "Flow Hydrograph",
        },
        {
            "river": "Ibicuy",
            "reach": "Ibicuy",
            "river_stat": "67.930*",
            "interval": "1HOUR",
            "border_condition": "Lateral Inflow Hydrograph",
        },
    ]
)
