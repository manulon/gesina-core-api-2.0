import datetime
import json
import logging

import requests
import pandas as pd
from datetime import timedelta, datetime

from src import config, logger


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
        "{config.ina_url/obs/puntual/series/" + str(serie_id) + "/observaciones",
        params={"timestart": timestart, "timeend": timeend},
        headers={"Authorization": f"Bearer {config.ina_token}"},
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
        f"{config.ina_url}/sim/calibrados/" + str(id_Mod) + "/corridas_guardadas",
        params={"var_id": "2", "estacion_id": str(est_id), "includeProno": False},
        headers={"Authorization": f"Bearer {config.ina_token}"},
    )
    json_response = response.json()
    return json_response


def C_corr_guar(id_Mod, corrida_id):
    ## Carga Simulados
    response = requests.get(
        f"{config.ina_url}/sim/calibrados/"
        + str(id_Mod)
        + "/corridas_guardadas/"
        + str(corrida_id),
        params={"includeProno": True},
        headers={"Authorization": f"Bearer {config.ina_token}"},
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
        f"{config.ina_url}/sim/calibrados/" + str(id_Mod) + "/corridas",
        params={"var_id": "2", "estacion_id": str(est_id), "includeProno": False},
        headers={"Authorization": f"Bearer {config.ina_token}"},
    )
    json_res = response.json()
    return json_res


def C_corr_ultimas(id_Mod, corrida_id, est_id):
    response = requests.get(
        f"{config.ina_url}/sim/calibrados/"
        + str(id_Mod)
        + "/corridas/"
        + str(corrida_id),
        params={"var_id": "2", "estacion_id": str(est_id), "includeProno": True},
        headers={"Authorization": f"Bearer {config.ina_token}"},
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


def obtain_curated_series(series_id, calibration_id, timestart, timeend):
    format_time = lambda d: d.strftime("%Y-%m-%d")
    timestart = timestart - timedelta(1)
    timeend = timeend + timedelta(1)

    url = f"{config.ina_url}/sim/calibrados/{calibration_id}/corridas/last?series_id={series_id}&timestart={format_time(timestart)}&timeend={format_time(timeend)}"
    logger.error(
        f"Getting data for series id: {series_id} from {timestart} to {timeend} with url: {url}"
    )
    response = request_with_retries(url)

    if not response.status_code == 200:
        logger.error(
            f"Error obtaining values for the serie with id {series_id} and the calibration id {calibration_id}"
        )

    logger.error(f"Answered: {response.json()}")

    data = response.json()["series"][0]["pronosticos"]

    data = sorted(data, key=lambda i: i[0], reverse=False)
    data = [i for i in data if i[2]]

    logger.error(
        f"Obtained {len(data)} values. First value is from {data[0][0]}. Last value is from {data[-1][0]}"
    )

    return [round(float(i[2]), 3) for i in data]


def send_info_to_ina(
    forecast_date, dates, values, series_id, calibration_id, win_logger
):
    if "test" in config.ina_url_envio:
        calibration_id = 288
        config.ina_token = "test-token"

    url = f"{config.ina_url_envio}/sim/calibrados/{calibration_id}/corridas"
    win_logger.info(f"Sending series to INA. URL: {url}")

    pronosticos = [
        {"timestart": t.isoformat(), "timeend": t.isoformat(), "valor": v}
        for t, v in zip(dates, values)
    ]

    data = {
        "forecast_date": forecast_date.isoformat(),
        "series": [
            {
                "series_table": "series",
                "series_id": series_id,
                "pronosticos": pronosticos,
            }
        ],
    }

    headers = {"Authorization": f"Bearer {config.ina_token}"}

    print(json.dumps(data))

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code < 300:
            win_logger.info(
                f"Successfully sent info to INA. Response status: {response.status_code} \r\n {response.content.decode('utf8')} "
            )
        else:
            win_logger.error(
                f"Error sending info to INA. Response status: {response.status_code} \r\n Body: {response.content.decode('utf8')} "
            )
    except Exception as e:
        win_logger.error(f"Error sending info to INA: {e}")

def validate_connection_to_service(calibration_id, serie_id):
    format_time = lambda d: d.strftime("%Y-%m-%d")
    timestart = datetime.now() - timedelta(2)
    timeend = datetime.now() + timedelta(1)

    url = f"https://alerta.ina.gob.ar/a5/sim/calibrados/{calibration_id}/corridas/last?series_id={serie_id}&timestart={format_time(timestart)}&timeend={format_time(timeend)}"
    response = request_with_retries(url)
    if not response.status_code == 200 or not response.json()["series"]:
        return False
    return True


def request_with_retries(url):
    response = None
    for i in range(config.max_retries):
        response = requests.get(
            url, headers={"Authorization": f"Bearer {config.ina_token}"}
        )
        if response.status_code == 200:
            break
    return response


if __name__ == "__main__":
    from datetime import date

    logging.info = print
    # print(obtain_curated_series(31564, 487, date(2022, 9, 17), date(2022, 11, 1)))

    forecast_date = datetime.datetime.now()
    dates = [datetime.datetime.now() - timedelta(i) for i in range(10)]
    values = list(range(10))
    series_id = 8
    calibration_id = 288
    logger = logging.getLogger("foo")
    logger.info = print
    logger.error = print

    send_info_to_ina(forecast_date, dates, values, series_id, calibration_id, logger)
