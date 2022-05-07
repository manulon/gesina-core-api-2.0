# -*- coding: utf-8 -*-
from datetime import timedelta
import pandas as pd
import numpy as np

from src.parana import PARANA_ID, NUEVA_PALMIRA_ID, SAN_FERNANDO_ID, ID_MODELO
from src.service import ina_service

# id obs / id prono frente
# TODO: Ver que significan los segundos ids
Id_EstLocal = {"Parana": 29, "SanFernando": [52, 1838], "NuevaPalmira": [1699, 1843]}


def forecast(df):
    df.index.grup


def ArmaProno(id_Mod, est_id, f_i_prono, f_f_prono):
    ## Consulta id de las corridas Guardadas
    json_res = ina_service.C_id_corr_guar(id_Mod, est_id)
    print("Cantidad de corridas Guardada: ", len(json_res))
    # Las guarda en una lista
    lst_corridas = []
    lst_pronoday = []
    for corridas in range(len(json_res)):
        lst_corridas.append(json_res[corridas]["cor_id"])
        lst_pronoday.append(json_res[corridas]["forecast_date"])

    # DF de Id y Fecha de las corridas Guardadas
    df_id_cg = pd.DataFrame(
        lst_corridas,
        index=lst_pronoday,
        columns=[
            "cor_id",
        ],
    )
    df_id_cg.index = pd.to_datetime(df_id_cg.index)
    df_id_cg.index = df_id_cg.index.tz_convert(None)
    df_id_cg.index = df_id_cg.index - timedelta(hours=3)
    df_id_cg["Fuente"] = "Guardada"

    # Filtra las corridas, se queda con las ultimas.
    # Ahora no hace nada porque se estan tomando las ultimas solamente.
    df_id_cg = df_id_cg[df_id_cg.index > f_i_prono].sort_index()

    ## Consulta id de las Ultimas Corridas
    json_res = ina_service.C_id_corr_ultimas(id_Mod, est_id)
    print("Cantidad de corridas Ultimas: ", len(json_res))
    # Los guarda en una lista
    lst_corridas = []
    lst_pronoday = []
    for corridas in range(len(json_res)):
        lst_corridas.append(json_res[corridas]["cor_id"])
        lst_pronoday.append(json_res[corridas]["forecast_date"])

    # DF de Id y Fecha de las Ultimas corridas
    df_id_cu = pd.DataFrame(
        lst_corridas,
        index=lst_pronoday,
        columns=[
            "cor_id",
        ],
    )
    df_id_cu.index = pd.to_datetime(df_id_cu.index)
    df_id_cu.index = df_id_cu.index.tz_convert(None)
    df_id_cu.index = df_id_cu.index - timedelta(hours=3)
    df_id_cu["Fuente"] = "Ultimas"

    df_id = pd.concat([df_id_cg, df_id_cu]).sort_index()
    # Arma un DF vacio que va llenando
    index1H = pd.date_range(start=f_i_prono, end=f_f_prono, freq="1H")
    df_pronos_all = pd.DataFrame(columns=["h_sim", "cor_id"], index=index1H)

    # Consulta cada corrida y va actualizando el Df
    for index, row in df_id.T.iteritems():
        idCor = row["cor_id"]
        try:
            if row["Fuente"] == "Guardada":
                df_sim_i = ina_service.C_corr_guar(id_Mod, idCor, est_id)
            if row["Fuente"] == "Ultimas":
                df_sim_i = ina_service.C_corr_ultimas(id_Mod, idCor, est_id)

            df_sim_i["cor_id"] = idCor
            df_pronos_all.update(df_sim_i)
        except:
            print("Error en corrida: ", idCor)
    return df_pronos_all


"""# Prono"""
sql_q = """SELECT min(Fecha) as minF FROM (SELECT Id_CB, max(Fecha) as Fecha FROM DataEntrada GROUP BY Id_CB);"""
df = pd.read_sql(sql_q, connLoc)
f_fin_obs = pd.to_datetime(df["minF"].values[0])
f_inicio_prono = (f_fin_obs - timedelta(days=2)).replace(
    hour=0, minute=0, second=0, microsecond=0
)
f_fin_prono = f_fin_obs + timedelta(days=5)

"""## Parana"""

# Carga parana desde la bbdd local
param = [
    PARANA_ID,
]
sql_h_obs = """SELECT Fecha, Nivel FROM DataEntrada WHERE Id_CB = ?;"""
df_Parana_Obs = pd.read_sql(sql_h_obs, connLoc, params=param)

keys = pd.to_datetime(df_Parana_Obs["Fecha"], format="%Y-%m-%d")
df_Parana_Obs.set_index(keys, inplace=True)
del df_Parana_Obs["Fecha"]
df_Parana_Obs.index.rename("fecha", inplace=True)

# Pronostico. Por ahora solo se repite el ultimo valor los proximos 4 días
fecha_0 = df_Parana_Obs.index.max() + timedelta(days=1)
index1dia = pd.date_range(start=fecha_0, end=f_fin_prono, freq="D")
df_aux_i_prono = pd.DataFrame(
    index=index1dia, columns=["Nivel", "Fecha", "Caudal", "Id_CB"]
)
df_aux_i_prono["Nivel"] = df_Parana_Obs["Nivel"][-1]
df_aux_i_prono["Fecha"] = df_aux_i_prono.index
df_aux_i_prono["Caudal"] = np.nan
df_aux_i_prono["Id_CB"] = PARANA_ID

df_aux_i_prono.to_sql("DataEntrada", con=connLoc, if_exists="append", index=False)

"""## San Fernando"""
estacion_id_SF = Id_EstLocal["SanFernando"][1]
id_obs_SF = SAN_FERNANDO_ID

# Consulta Prono Ya generado
df_SF_sim = ArmaProno(ID_MODELO, estacion_id_SF, f_inicio_prono, f_fin_prono)
df_SF_sim = df_SF_sim.dropna()

# Carga San Fernando desde la bbdd local
param = [
    id_obs_SF,
]
sql_h_obs = """SELECT Fecha, Nivel as h_obs FROM DataEntrada WHERE Id_CB = ?;"""
df_SF_Obs = pd.read_sql(sql_h_obs, connLoc, params=param)
keys = pd.to_datetime(df_SF_Obs["Fecha"])
df_SF_Obs.set_index(keys, inplace=True)
del df_SF_Obs["Fecha"]
df_SF_Obs.index.rename("fecha", inplace=True)

# Guarda en BBDD Local
f_guarda = df_SF_Obs.index.max()
df_sim_guarda = df_SF_sim[df_SF_sim.index > f_guarda].copy()

df_sim_guarda = df_sim_guarda[
    [
        "h_sim",
    ]
]

# Pasa a Cero IGN
# df_sim_guarda['h_sim'] = df_sim_guarda['h_sim'] - 0.53
df_sim_guarda["emision"] = cod
df_sim_guarda["Id"] = SAN_FERNANDO_ID

df_sim_guarda.to_sql(
    "PronoFrente", con=connLoc, if_exists="replace", index=True, index_label="Fecha"
)

"""##   Nueva Palmira"""

estacion_id_NP = Id_EstLocal["NuevaPalmira"][1]
id_NP_obs = NUEVA_PALMIRA_ID

# Consulta Prono Ya generado
df_NP_sim = ArmaProno(ID_MODELO, estacion_id_NP, f_inicio_prono, f_fin_prono)
df_NP_sim = df_NP_sim.dropna()

# Carga NP desde la bbdd local
param = [
    id_NP_obs,
]
sql_h_obs = """SELECT Fecha, Nivel as h_obs FROM DataEntrada WHERE Id_CB = ?;"""
df_NP_Obs = pd.read_sql(sql_h_obs, connLoc, params=param)
keys = pd.to_datetime(df_NP_Obs["Fecha"])
df_NP_Obs.set_index(keys, inplace=True)
del df_NP_Obs["Fecha"]
df_NP_Obs.index.rename("fecha", inplace=True)

# Guarda en BBDD Local
f_guarda = df_NP_Obs.index.max()
df_sim_guarda = df_NP_sim[df_NP_sim.index > f_guarda].copy()
df_sim_guarda = df_sim_guarda[
    [
        "h_sim",
    ]
]

# Pasa a Cero IGN
# df_sim_guarda['h_sim'] = df_sim_guarda['h_sim'] + 0.0275

df_sim_guarda["emision"] = cod
df_sim_guarda["Id"] = NUEVA_PALMIRA_ID

print(df_sim_guarda.head(2))

df_sim_guarda.to_sql(
    "PronoFrente", con=connLoc, if_exists="append", index=True, index_label="Fecha"
)

"""# Frente

## San Fernando
"""

paramCBF = [
    SAN_FERNANDO_ID,
]
sql_query = """SELECT Nivel, Fecha FROM DataEntrada WHERE Id_CB = ?"""
df_CB_SF = pd.read_sql_query(sql_query, connLoc, params=paramCBF)
keys = pd.to_datetime(
    df_CB_SF["Fecha"]
)  # , format='%Y-%m-%d')								#Convierte a formato fecha la columna [fecha]
df_CB_SF.set_index(
    pd.DatetimeIndex(keys), inplace=True
)  # Pasa la fecha al indice del dataframe (DatetimeIndex)
del df_CB_SF["Fecha"]  # Elimina el campo fecha que ya es index
df_CB_SF.index.rename("Fecha", inplace=True)  # Cambia el nombre del indice
df_CB_SF["SanFernando"] = df_CB_SF["Nivel"]
del df_CB_SF["Nivel"]

# Prono
sql_query = """SELECT Fecha, h_sim as Nivel FROM PronoFrente WHERE Id = ?"""
df_CB_SF_Prono = pd.read_sql_query(sql_query, connLoc, params=paramCBF)
keys = pd.to_datetime(
    df_CB_SF_Prono["Fecha"]
)  # , format='%Y-%m-%d')								#Convierte a formato fecha la columna [fecha]
df_CB_SF_Prono.set_index(
    pd.DatetimeIndex(keys), inplace=True
)  # Pasa la fecha al indice del dataframe (DatetimeIndex)
del df_CB_SF_Prono["Fecha"]  # Elimina el campo fecha que ya es index
df_CB_SF_Prono.index.rename("Fecha", inplace=True)  # Cambia el nombre del indice
df_CB_SF_Prono["SanFernando"] = df_CB_SF_Prono["Nivel"]
del df_CB_SF_Prono["Nivel"]

df_CB_SF = pd.concat([df_CB_SF, df_CB_SF_Prono], ignore_index=False)

"""## Nueva Palmira"""

paramCBF = [
    NUEVA_PALMIRA_ID,
]
sql_query = """SELECT Nivel, Fecha FROM DataEntrada WHERE Id_CB = ?"""
df_CB_NP = pd.read_sql_query(sql_query, connLoc, params=paramCBF)
keys = pd.to_datetime(
    df_CB_NP["Fecha"]
)  # , format='%Y-%m-%d')								#Convierte a formato fecha la columna [fecha]
df_CB_NP.set_index(
    pd.DatetimeIndex(keys), inplace=True
)  # Pasa la fecha al indice del dataframe (DatetimeIndex)
del df_CB_NP["Fecha"]  # Elimina el campo fecha que ya es index
df_CB_NP.index.rename("Fecha", inplace=True)  # Cambia el nombre del indice
df_CB_NP["NuevaPalmira"] = df_CB_NP["Nivel"]
del df_CB_NP["Nivel"]

# Prono
sql_query = """SELECT Fecha, h_sim as Nivel FROM PronoFrente WHERE Id = ?"""
df_CB_NP_Prono = pd.read_sql_query(sql_query, connLoc, params=paramCBF)
keys = pd.to_datetime(
    df_CB_NP_Prono["Fecha"]
)  # , format='%Y-%m-%d')								#Convierte a formato fecha la columna [fecha]
df_CB_NP_Prono.set_index(
    pd.DatetimeIndex(keys), inplace=True
)  # Pasa la fecha al indice del dataframe (DatetimeIndex)
del df_CB_NP_Prono["Fecha"]  # Elimina el campo fecha que ya es index
df_CB_NP_Prono.index.rename("Fecha", inplace=True)  # Cambia el nombre del indice
df_CB_NP_Prono["NuevaPalmira"] = df_CB_NP_Prono["Nivel"]
del df_CB_NP_Prono["Nivel"]

"""## Prepara series para Interpolar"""

df_CB_NP = pd.concat([df_CB_NP, df_CB_NP_Prono], ignore_index=False)

indexUnico = pd.date_range(
    start=df_CB_SF.index.min(), end=df_CB_SF_Prono.index.max(), freq="H"
)  # Fechas desde f_inicio a f_fin con un paso de 5 minutos
df_CB_F = pd.DataFrame(index=indexUnico)

df_CB_F = df_CB_F.join(df_CB_SF, how="left")
df_CB_F = df_CB_F.join(df_CB_NP, how="left")

del df_CB_SF
del df_CB_SF_Prono
del df_CB_NP
del df_CB_NP_Prono

df_CB_F["SanFernando"] = df_CB_F["SanFernando"].interpolate(
    method="linear", limit_direction="backward"
)
df_CB_F["NuevaPalmira"] = df_CB_F["NuevaPalmira"].interpolate(
    method="linear", limit_direction="backward"
)

"""## Interpola Frente"""

df_CB_F["aux"] = df_CB_F["SanFernando"] - df_CB_F["NuevaPalmira"]

df_CB_F["Lujan"] = df_CB_F["SanFernando"]
df_CB_F["SanAntonio"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.024)
df_CB_F["CanaldelEste"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.077)
df_CB_F["Palmas"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.123)
df_CB_F["Palmas b"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.227)
df_CB_F["Mini"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.388)
df_CB_F["LaBarquita"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.427)
df_CB_F["BarcaGrande"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.493)
df_CB_F["Correntoso"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.598)
df_CB_F["Guazu"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.800)
df_CB_F["Sauce"] = df_CB_F["SanFernando"] - (df_CB_F["aux"] * 0.900)
df_CB_F["Bravo"] = df_CB_F["NuevaPalmira"]
df_CB_F["Gutierrez"] = df_CB_F["NuevaPalmira"]

del df_CB_F["aux"]
df_CB_F["Fecha"] = df_CB_F.index

df_CB_F2 = pd.melt(
    df_CB_F,
    id_vars=["Fecha"],
    value_vars=[
        "Lujan",
        "SanAntonio",
        "CanaldelEste",
        "Palmas",
        "Palmas b",
        "Mini",
        "LaBarquita",
        "BarcaGrande",
        "Correntoso",
        "Guazu",
        "Sauce",
        "Bravo",
        "Gutierrez",
    ],
    var_name="Estacion",
    value_name="Nivel",
)
df_CB_F2["Nivel"] = df_CB_F2["Nivel"].round(3)

df_CB_F2.to_sql("CB_FrenteDelta", con=connLoc, if_exists="replace", index=False)
connLoc.commit()

### Temporal Agrega condBorde Lujan, Gualeguay y Ibicuy
print("\nTemporal:  ----------------------------------------")
print("Agrega condBorde Lujan, Gualeguay y Ibicuy: Q cte")
## Lujan
df_aux_i = pd.DataFrame()
df_aux_i["Fecha"] = df_CB_F.index
df_aux_i["Nivel"] = np.nan
df_aux_i["Caudal"] = 10
df_aux_i["Id_CB"] = 10  # Lujan
df_aux_i.to_sql("DataEntrada", con=connLoc, if_exists="append", index=False)

## Gualeguay
df_aux_i = pd.DataFrame()
df_aux_i["Fecha"] = df_CB_F.index
df_aux_i["Nivel"] = np.nan
df_aux_i["Caudal"] = 10
df_aux_i["Id_CB"] = 11  # Gualeguay
df_aux_i.to_sql("DataEntrada", con=connLoc, if_exists="append", index=False)

## Ibicuy
df_aux_i = pd.DataFrame()
df_aux_i["Fecha"] = df_CB_F.index
df_aux_i["Nivel"] = np.nan
df_aux_i["Caudal"] = 50
df_aux_i["Id_CB"] = 12  # Ibicuy
df_aux_i.to_sql("DataEntrada", con=connLoc, if_exists="append", index=False)

del df_CB_F
