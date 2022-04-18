import requests
import pandas as pd
from datetime import timedelta


def obtain_obeservations_for_stations(stations, timestart, timeend):
    dfs = []
    for index, row in stations.T.iteritems():
        id_serie = row["series_id"]
        df_obs = obtain_observations(
            id_serie, timestart.strftime("%Y-%m-%d"), timeend.strftime("%Y-%m-%d")
        )
        df_obs["id"] = index
        dfs.append(df_obs)

    return pd.concat(dfs, ignore_index=True)


def obtain_observations(serie_id, timestart, timeend):
    response = requests.get(
        "https://alerta.ina.gob.ar/a5/obs/puntual/series/"
        + str(serie_id)
        + "/observaciones",
        params={"timestart": timestart, "timeend": timeend},
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlNhbnRpYWdvIEd1aXp6YXJkaSIsImlhdCI6MTUxNjIzOTAyMn0.YjqQYMCh4AIKSsSEq-QsTGz3Q4WOS5VE-CplGQdInfQ"
        },
    )
    json_response = response.json()

    df_obs_i = pd.DataFrame.from_dict(json_response, orient="columns")
    df_obs_i = df_obs_i[["timestart", "valor"]]
    df_obs_i = df_obs_i.rename(columns={"timestart": "fecha"})

    df_obs_i["fecha"] = pd.to_datetime(df_obs_i["fecha"])
    df_obs_i["valor"] = df_obs_i["valor"].astype(float)

    df_obs_i = df_obs_i.sort_values(by="fecha")

    df_obs_i["fecha"] = df_obs_i.fecha.dt.tz_convert(None)
    df_obs_i["fecha"] = df_obs_i.fecha - timedelta(hours=3)

    return df_obs_i
