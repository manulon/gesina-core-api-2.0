from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import logging

from src.service import ina_service
from src.parana import utils, Df_Estaciones


def obtain_observations(days=60, starttime=datetime.now()):
    cod = f"{starttime.year}-{starttime.month}-{starttime.day}-{starttime.hour}"

    f_fin_0 = (starttime + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    f_inicio_0 = (f_fin_0 - timedelta(days=days)).replace(hour=0, minute=0, second=0)

    # Guarda un Id de la corrida tomando Año / mes / dia y hora de la corrida
    logging.info("Id Corrida: ", cod)

    df_obs = ina_service.obtain_obeservations_for_stations(
        Df_Estaciones, f_inicio_0, f_fin_0
    )

    return pd.concat(
        [
            obtain_upstream(df_obs, Df_Estaciones, f_inicio_0),
            obtain_left_margin(df_obs, Df_Estaciones, f_inicio_0),
            obtain_rigth_margin(df_obs, Df_Estaciones, f_inicio_0),
        ]
    )


def reindex(df, period, f_inicio_0):
    df.fecha = df.fecha.dt.round(period)
    max_date = df.fecha.max()
    df.set_index(["fecha", "id"], inplace=True)
    df = df.groupby([pd.Grouper(level=0, freq=period), pd.Grouper(level=1)]).mean()
    df.reindex(pd.date_range(start=f_inicio_0, end=max_date, freq=period), level=0)

    return df


def obtain_diffs(df, Df_Estaciones):
    df = df.join(Df_Estaciones).droplevel(level=1)
    df.set_index("nombre", append=True, inplace=True)
    df[["valor"]].unstack("nombre")
    df = df.unstack(level=1)["valor"]
    df = df.join(df - df.shift(1), rsuffix="_diff")

    return df


def obtain_upstream(df_obs, Df_Estaciones, f_inicio_0):
    # Aguas arribas
    l_idEst = [29, 30, 31]  # CB Aguas Arriba: Parana Santa Fe y Diamante
    df_AA = df_obs[df_obs.id.isin(l_idEst)].copy()

    """### Paso 1:
    
    Une las series en un DF Base:
    
    Cada serie en una columna. Todas con la misma frecuencia, en este caso diaria.
    
    También:
    *   Calcula la frecuencia horaria de los datos.
    *   Reemplaza Ceros por NAN.
    *   Calcula diferencias entre valores concecutivos.
    
    """

    df_AA = reindex(df_AA, "1D", f_inicio_0)
    df_AA = obtain_diffs(df_AA, Df_Estaciones)

    """### Paso 2:
    Elimina saltos:
    
    Se establece un umbral_1: si la diferencia entre datos consecutivos supera este umbral_1, se fija si en el resto de las series tambien se produce el salto (se supera el umbral_1).
    
    Si en todas las series se observa un salto se toma el dato como valido.
    
    Si el salto no se produce en las tres o si es mayo al segundo umbral_2 (> que el 1ero) se elimina el dato.
    
    """

    # Datos faltante
    # Elimina Saltos
    df_AA = utils.delete_jumps_parana_santa_fe_diamante(df_AA)
    df_AA = df_AA.drop(["Parana_diff", "SantaFe_diff", "Diamante_diff"], axis=1)

    """### Paso 3:
    Completa Faltantes en base a los datos en las otras series.
    1. Lleva las saries al mismo plano.
    2. Calcula meidas de a pares. Parana-Santa Fe , Parana-Diamanate, Parana-Diamante.
    3. Si no hay datos toma el de la media de las otras dos.
    4. Si la diferencia entre el dato y la media es mayor al umbral_3 elimina el dato.
    """

    # Llevo a la misma face y plano de referencia
    corim_SantaFe = -0.30
    corim_Diamante = -0.30
    df_AA["SantaFe"] = df_AA["SantaFe"].add(corim_SantaFe)
    df_AA["Diamante"] = df_AA["Diamante"].add(corim_Diamante)

    # Calcula media de a pares
    mediaPS = df_AA[["Parana", "SantaFe"]].mean(
        axis=1,
    )
    mediaPD = df_AA[["Parana", "Diamante"]].mean(
        axis=1,
    )
    mediaSD = df_AA[["SantaFe", "Diamante"]].mean(
        axis=1,
    )

    # Completo los faltantes
    df_AA["Parana"].fillna(mediaSD)
    df_AA["SantaFe"].fillna(mediaPD)
    df_AA["Diamante"].fillna(mediaPS)

    # Elimina los saltos grandes
    umbral = 0.3
    df_AA[(df_AA["Parana"] - mediaSD) > umbral] = np.nan
    df_AA[(df_AA["SantaFe"] - mediaPD) > umbral] = np.nan
    df_AA[(df_AA["Diamante"] - mediaPS) > umbral] = np.nan

    """Interpola de forma Linial"""

    # Interpola para completa todos los fltantes
    df_AA = df_AA.interpolate(method="linear", limit_direction="backward")

    # Vuelve las series a su nivel original
    df_AA["SantaFe"] = df_AA["SantaFe"].add(-corim_SantaFe)
    df_AA["Diamante"] = df_AA["Diamante"].add(-corim_Diamante)

    # Series final

    df_aux_i = pd.DataFrame()  # Pasa lista a DF
    cero_parana = Df_Estaciones[Df_Estaciones["nombre"] == "Parana"][
        "cero_escala"
    ].values[0]
    df_aux_i["Nivel"] = df_AA["Parana"] + cero_parana
    df_aux_i["Caudal"] = np.nan
    df_aux_i["Id_CB"] = Df_Estaciones[Df_Estaciones.nombre == "Parana"].index.values[0]

    return df_aux_i


def obtain_rigth_margin(df_obs, Df_Estaciones, f_inicio_0):
    # Margen Derecha
    l_idE_MDer = [52, 85]
    df_MD = df_obs[df_obs.id.isin(l_idE_MDer)].copy()

    """## CB Frente Margen Derecha"""

    # Margen Derecha
    """### Paso 1:
    Une las series en un DF Base:
    Cada serie en una columna.
    Todas con la misma frecuencia, en este caso diaria.
    
    También:
    *   Calcula la frecuencia horaria de los datos.
    *   Calcula diferencias entre valores concecutivos.'''
    """

    df_MD = reindex(df_MD, "5min", f_inicio_0)
    df_MD = obtain_diffs(df_MD, Df_Estaciones)

    """### Paso 2:
    Elimina saltos:
    
    Se establece un umbral_1: si la diferencia entre datos consecutivos supera este umbral_1, se fija si en el resto de las series tambien se produce el salto (se supera el umbral_1).
    
    Si en todas las series se observa un salto se toma el dato como valido.
    
    Si el salto no se produce en las tres o si es mayo al segundo umbral_2 (> que el 1ero) se elimina el dato.
    
    """

    # Datos faltante
    #  Elimina Saltos
    df_MD = utils.delete_jumps_san_fernando_bs_as(df_MD)
    df_MD = df_MD.drop(["SanFernando_diff", "BsAs_diff"], axis=1)

    """### Paso 3:
    Completa Faltantes en base a los datos en las otras series.
    
    1.   Lleva las saries al mismo plano.
    2.   Calcula meidas de a pares. Parana-Santa Fe , Parana-Diamanate, Parana-Diamante.
    3.   Si no hay datos toma el de la media de las otras dos.
    4.   Si la diferencia entre el dato y la media es mayor al umbral_3 elimina el dato.'''
    """

    # Corrimiento Vertical
    corim_BsAs = 0.2
    df_MD["BsAs"] = df_MD["BsAs"].add(corim_BsAs)

    # Corrimiento Temporal
    df_MD["BsAs"] = df_MD["BsAs"].shift(periods=50, freq="min")

    # Calcula la media de las tres series. E interpola para completar todos los vacios
    df_MD["medio"] = df_MD[["SanFernando", "BsAs"]].mean(
        axis=1,
    )
    df_MD = df_MD.interpolate(method="linear", limit_direction="both")

    df_MD = utils.complete_missings(df_MD)

    # Vuelve a llevar las series a su lugar original
    df_MD["BsAs"] = df_MD["BsAs"].add(-corim_BsAs)
    df_MD["BsAs"] = df_MD["BsAs"].shift(periods=-50, freq="min")

    cero_sanfer = Df_Estaciones[Df_Estaciones["nombre"] == "SanFernando"][
        "cero_escala"
    ].values[0]
    df_MD["SanFernando"] = df_MD["SanFernando"] + cero_sanfer

    # Interpola de forma Linial. Maximo 3 dias
    df_MD = df_MD.interpolate(method="linear", limit_direction="backward")

    df_aux_i = pd.DataFrame()  # Pasa lista a DF
    df_aux_i["Nivel"] = df_MD["SanFernando"]
    df_aux_i["Caudal"] = np.nan
    df_aux_i["Id_CB"] = Df_Estaciones[
        Df_Estaciones.nombre == "SanFernando"
    ].index.values[0]

    return df_aux_i


def obtain_left_margin(df_obs, Df_Estaciones, f_inicio_0):
    # Margen izquierdo
    l_idE_MIzq = [1696, 1699]
    df_MI = df_obs[df_obs.id.isin(l_idE_MIzq)].copy()

    """## CB Frente Margen Izquierda"""

    """### Paso 1:
    Une las series en un DF Base:
    
    Cada serie en una columna. Todas con la misma frecuencia, en este caso diaria.
    
    También:
    *   Calcula la frecuencia horaria de los datos.
    *   Calcula diferencias entre valores concecutivos.
    """

    df_MI = reindex(df_MI, "15min", f_inicio_0)
    df_MI = obtain_diffs(df_MI, Df_Estaciones)
    df_MI = df_MI.interpolate(method="linear", limit=2, limit_direction="backward")

    """### Paso 2:
    
    Elimina saltos:
    
    Se establece un umbral_1: si la diferencia entre datos consecutivos supera este umbral_1, se fija si en el resto de las series tambien se produce el salto (se supera el umbral_1).
    
    Si en todas las series se observa un salto se toma el dato como valido.
    
    Si el salto no se produce en las tres o si es mayo al segundo umbral_2 (> que el 1ero) se elimina el dato.
    """

    # Elimina Saltos
    df_MI = utils.delete_jumps_nueva_palmira_martinez(df_MI)

    """### Paso 3:
    
    Completa Faltantes en base a los datos en las otras series.
    
    1.   Lleva las saries al mismo plano.
    2.   
    3.   Si no hay datos toma el de la media de las otras dos.
    4.   Si la diferencia entre el dato y la media es mayor al umbral_3 elimina el dato.'''
    """

    # Corrimiento Vertical y Temporal
    corim_Mart = 0.24
    df_MI["Martinez"] = df_MI["Martinez"].add(corim_Mart)
    df_MI["Martinez"] = df_MI["Martinez"].shift(periods=-60, freq="min")

    df_MI["Nueva Palmira"] = df_MI["Nueva Palmira"].interpolate(
        method="linear", limit_direction="backward"
    )

    ################# Guarda para modelo
    df_aux_i = pd.DataFrame()  # Pasa lista a DF
    cero_NPalmira = Df_Estaciones[Df_Estaciones["nombre"] == "Nueva Palmira"][
        "cero_escala"
    ].values[0]
    df_aux_i["Nivel"] = df_MI["Nueva Palmira"] + cero_NPalmira
    df_aux_i["Id_CB"] = Df_Estaciones[
        Df_Estaciones.nombre == "Nueva Palmira"
    ].index.values[0]

    df_aux_i = df_aux_i.dropna()

    return df_aux_i


if __name__ == "__main__":
    print(obtain_observations())
