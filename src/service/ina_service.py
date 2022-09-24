import logging

import requests
import pandas as pd
from datetime import timedelta
import os


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
        headers={"Authorization": f"Bearer {os.getenv('INA_TOKEN')}"},
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


def C_id_corr_guar(id_Mod, est_id):
    ## Carga Simulados
    response = requests.get(
        "https://alerta.ina.gob.ar/a5/sim/calibrados/"
        + str(id_Mod)
        + "/corridas_guardadas",
        params={"var_id": "2", "estacion_id": str(est_id), "includeProno": False},
        headers={"Authorization": f"Bearer {os.getenv('INA_TOKEN')}"},
    )
    json_response = response.json()
    return json_response


def C_corr_guar(id_Mod, corrida_id):
    ## Carga Simulados
    response = requests.get(
        "https://alerta.ina.gob.ar/a5/sim/calibrados/"
        + str(id_Mod)
        + "/corridas_guardadas/"
        + str(corrida_id),
        params={"includeProno": True},
        headers={"Authorization": f"Bearer {os.getenv('INA_TOKEN')}"},
    )
    json_response = response.json()
    df_sim = pd.DataFrame.from_dict(
        json_response[0]["series"][0]["pronosticos"], orient="columns"
    )
    df_sim = df_sim.rename(columns={"timestart": "fecha", "valor": "h_sim"})
    df_sim = df_sim[["fecha", "h_sim"]]
    df_sim["fecha"] = pd.to_datetime(df_sim["fecha"])
    df_sim["h_sim"] = df_sim["h_sim"].astype(float)

    df_sim = df_sim.sort_values(by="fecha")
    df_sim.set_index(df_sim["fecha"], inplace=True)
    df_sim.index = df_sim.index.tz_convert(None)  # ("America/Argentina/Buenos_Aires")
    df_sim.index = df_sim.index - timedelta(hours=3)

    del df_sim["fecha"]
    return df_sim.groupby(level=0).mean()


def C_id_corr_ultimas(id_Mod, est_id):
    # Consulta los id de las corridas
    response = requests.get(
        "https://alerta.ina.gob.ar/a5/sim/calibrados/" + str(id_Mod) + "/corridas",
        params={"var_id": "2", "estacion_id": str(est_id), "includeProno": False},
        headers={"Authorization": f"Bearer {os.getenv('INA_TOKEN')}"},
    )
    json_res = response.json()
    return json_res


def C_corr_ultimas(id_Mod, corrida_id, est_id):
    response = requests.get(
        "https://alerta.ina.gob.ar/a5/sim/calibrados/"
        + str(id_Mod)
        + "/corridas/"
        + str(corrida_id),
        params={"var_id": "2", "estacion_id": str(est_id), "includeProno": True},
        headers={"Authorization": f"Bearer {os.getenv('INA_TOKEN')}"},
    )
    json_response = response.json()
    df_sim = pd.DataFrame.from_dict(
        json_response["series"][0]["pronosticos"], orient="columns"
    )
    df_sim = df_sim.rename(columns={"timestart": "fecha", "valor": "h_sim"})
    df_sim = df_sim[["fecha", "h_sim"]]
    df_sim["fecha"] = pd.to_datetime(df_sim["fecha"])
    df_sim["h_sim"] = df_sim["h_sim"].astype(float)

    df_sim = df_sim.sort_values(by="fecha")
    df_sim.set_index(df_sim["fecha"], inplace=True)
    df_sim.index = df_sim.index.tz_convert(None)  # ("America/Argentina/Buenos_Aires")
    df_sim.index = df_sim.index - timedelta(hours=3)

    del df_sim["fecha"]
    return df_sim


def obtain_curated_series(series_id, timestart, timeend):
    format_time = lambda d: d.strftime("%Y-%m-%d")

    url = f"https://alerta.ina.gob.ar/a5/obs/puntual/series/{series_id}/observaciones?&timestart={format_time(timestart)}&timeend={format_time(timeend)}"
    logging.info(f"Getting data for series id: {series_id} from {timestart} to {timeend} with url: {url}")
    response = requests.get(url)

    data = sorted(response.json(), key=lambda i: i["timestart"], reverse=False)
    data = [i for i in data if i["valor"]]

    logging.info(f"Obtained {len(data)} values. First value is from {data[0]['timestart']}. Last value is from {data[-1]['timestart']}")

    return [i["valor"] for i in data]


if __name__ == "__main__":
    from datetime import date
    logging.info = print
    print(obtain_curated_series(31554, date(2022, 6, 17), date(2022, 9, 30)))