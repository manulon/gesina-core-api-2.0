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
    df_san_fernando = df_san_fernando.combine(df_san_fernando_sim)

    df_nueva_palmira = df[df.Id_CB == NUEVA_PALMIRA_ID]
    df_nueva_palmira_sim = ArmaProno(
        ID_MODELO, NUEVA_PALMIRA_FORECAST_ID, f_inicio_prono, f_fin_prono
    )
    df_nueva_palmira = df_nueva_palmira.combine(df_nueva_palmira_sim)


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
    df_pronos = pd.DataFrame(columns=["h_sim", "cor_id"], index=index1H)
    corridas = pd.concat([corridas_guardadas, ultimas_corridas]).sort_index()[-10:]

    for idx, corrida in corridas.iterrows():
        if corrida["Fuente"] == "Guardada":
            df_pronos.update(ina_service.C_corr_guar(id_Mod, corrida["cor_id"], est_id))
        if corrida["Fuente"] == "Ultimas":
            df_pronos.update(
                ina_service.C_corr_ultimas(id_Mod, corrida["cor_id"], est_id)
            )

    return df_pronos.dropna()


"""## Prepara series para Interpolar"""

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
