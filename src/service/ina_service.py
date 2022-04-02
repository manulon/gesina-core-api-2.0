import requests
import pandas as pd
from datetime import timedelta


def obtain_obeservations_for_stations(timestart, timeend, stations):

    df = pd.DataFrame(columns=['fecha', 'valor', 'id'])
    for index, row in stations.T.iteritems():
        id_serie = row['series_id']
        df_obs = obtain_observations(id_serie, timestart.strftime("%Y-%m-%d"), timeend.strftime("%Y-%m-%d"))
        print(df_obs.tail(2))
        # print(df_obs['fecha'].max())
        df_obs['id'] = row['unid']
        df = pd.concat([df, df_obs], ignore_index=True)

    return df


def obtain_observations(serie_id, timestart, timeend):
    timestart = timestart.strftime("%Y-%m-%d")
    timeend = timeend.strftime("%Y-%m-%d")

    response = requests.get(
        'https://alerta.ina.gob.ar/a5/obs/puntual/series/' + str(serie_id) + '/observaciones',
        params={'timestart': timestart, 'timeend': timeend},
        headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlNhbnRpYWdvIEd1aXp6YXJkaSIsImlhdCI6MTUxNjIzOTAyMn0.YjqQYMCh4AIKSsSEq-QsTGz3Q4WOS5VE-CplGQdInfQ'}, )
    json_response = response.json()

    df_obs_i = pd.DataFrame.from_dict(json_response, orient='columns')
    df_obs_i = df_obs_i[['timestart', 'valor']]
    df_obs_i = df_obs_i.rename(columns={'timestart': 'fecha'})

    df_obs_i['fecha'] = pd.to_datetime(df_obs_i['fecha'])
    df_obs_i['valor'] = df_obs_i['valor'].astype(float)

    df_obs_i = df_obs_i.sort_values(by='fecha')
    df_obs_i.set_index(df_obs_i['fecha'], inplace=True)

    df_obs_i.index = df_obs_i.index.tz_convert(None)  # ("America/Argentina/Buenos_Aires")
    df_obs_i.index = df_obs_i.index - timedelta(hours=3)

    df_obs_i['fecha'] = df_obs_i.index
    df_obs_i = df_obs_i.reset_index(drop=True)
    return df_obs_i
