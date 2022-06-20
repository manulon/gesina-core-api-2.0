# -*- coding: utf-8 -*-
from datetime import timedelta
import pandas as pd
import numpy as np

from src.parana import (
    PARANA_ID,
    NUEVA_PALMIRA_ID,
    SAN_FERNANDO_ID,
    ID_MODELO,
    SAN_FERNANDO_FORECAST_ID,
    NUEVA_PALMIRA_FORECAST_ID,
)
from src.service import ina_service


def forecast(df):
    f_fin_obs = df.reset_index().groupby("Id_CB").max()["fecha"].min()
    f_inicio_prono = f_fin_obs.replace(hour=0, minute=0, second=0, microsecond=0)
    f_fin_prono = f_fin_obs + timedelta(days=5)

    df_parana = df[df.Id_CB == PARANA_ID]
    index = pd.date_range(
        start=df_parana.index.max() + timedelta(days=1), end=f_fin_prono, freq="D"
    )
    df_aux_i_prono = pd.DataFrame(index=index, columns=["Nivel", "Caudal", "Id_CB"])
    df_aux_i_prono["Nivel"] = df_parana["Nivel"][-1]
    df_aux_i_prono["Caudal"] = np.nan
    df_aux_i_prono["Id_CB"] = PARANA_ID
    df_parana = pd.concat([df_parana, df_aux_i_prono])

    df_san_fernando = df[df.Id_CB == SAN_FERNANDO_ID]
    df_san_fernando_sim = ArmaProno(
        ID_MODELO, SAN_FERNANDO_FORECAST_ID, f_inicio_prono, f_fin_prono
    )
    df_san_fernando = df_san_fernando.combine_first(df_san_fernando_sim)

    df_nueva_palmira = df[df.Id_CB == NUEVA_PALMIRA_ID]
    df_nueva_palmira_sim = ArmaProno(
        ID_MODELO, NUEVA_PALMIRA_FORECAST_ID, f_inicio_prono, f_fin_prono
    )
    df_nueva_palmira = df_nueva_palmira.combine_first(df_nueva_palmira_sim)

    forecast_df = pd.DataFrame(
        {
            "Parana": pd.to_numeric(df_parana["Nivel"]),
            "SanFernando": pd.to_numeric(df_san_fernando["Nivel"]),
            "NuevaPalmira": pd.to_numeric(df_nueva_palmira["Nivel"]),
        }
    )

    forecast_df = forecast_df.interpolate(method="linear", limit_direction="backward")
    forecast_df.groupby([pd.Grouper(level=0, freq="H")]).mean()

    aux = forecast_df["SanFernando"] - forecast_df["NuevaPalmira"]

    forecast_df["Lujan"] = forecast_df["SanFernando"]
    forecast_df["SanAntonio"] = forecast_df["SanFernando"] - (aux * 0.024)
    forecast_df["CanaldelEste"] = forecast_df["SanFernando"] - (aux * 0.077)
    forecast_df["Palmas"] = forecast_df["SanFernando"] - (aux * 0.123)
    forecast_df["Palmas b"] = forecast_df["SanFernando"] - (aux * 0.227)
    forecast_df["Mini"] = forecast_df["SanFernando"] - (aux * 0.388)
    forecast_df["LaBarquita"] = forecast_df["SanFernando"] - (aux * 0.427)
    forecast_df["BarcaGrande"] = forecast_df["SanFernando"] - (aux * 0.493)
    forecast_df["Correntoso"] = forecast_df["SanFernando"] - (aux * 0.598)
    forecast_df["Guazu"] = forecast_df["SanFernando"] - (aux * 0.800)
    forecast_df["Sauce"] = forecast_df["SanFernando"] - (aux * 0.900)
    forecast_df["Bravo"] = forecast_df["NuevaPalmira"]
    forecast_df["Gutierrez"] = forecast_df["NuevaPalmira"]

    forecast_df = forecast_df.round(3)

    ## Lujan
    df_entry_points = pd.DataFrame(
        index=forecast_df.index, data={"Lujan": 10, "Gualeguay": 10, "Ibicuy": 50}
    )

    return forecast_df, df_entry_points


def ArmaProno(id_Mod, est_id, f_i_prono, f_f_prono):
    ## Consulta id de las corridas Guardadas
    corridas_guardadas = pd.DataFrame.from_dict(
        ina_service.C_id_corr_guar(id_Mod, est_id)
    )
    corridas_guardadas["Fuente"] = "Guardada"

    ## Consulta id de las Ultimas Corridas
    ultimas_corridas = pd.DataFrame.from_dict(
        ina_service.C_id_corr_ultimas(id_Mod, est_id)
    )
    ultimas_corridas["Fuente"] = "Ultimas"

    index1H = pd.date_range(start=f_i_prono, end=f_f_prono, freq="1H")
    df_pronos = pd.DataFrame(columns=["h_sim"], index=index1H)
    corridas = pd.concat([corridas_guardadas, ultimas_corridas]).sort_index()[-10:]

    for idx, corrida in corridas.iterrows():
        if corrida["Fuente"] == "Guardada":
            df_pronos.update(ina_service.C_corr_guar(id_Mod, corrida["cor_id"]))
        if corrida["Fuente"] == "Ultimas":
            df_pronos.update(
                ina_service.C_corr_ultimas(id_Mod, corrida["cor_id"], est_id)
            )

    df_pronos.rename(columns={"h_sim": "Nivel"}, inplace=True)
    return df_pronos.dropna()
