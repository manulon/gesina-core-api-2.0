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
