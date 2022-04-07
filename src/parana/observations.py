from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import logging

from src.service import ina_service
from src.parana import utils

DAYS_MOD = 60  # Largo de la corrida

now = datetime.now()
cod = f"{now.year}-{now.month}-{now.day}-{now.hour}"

f_fin_0 = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
f_inicio_0 = (f_fin_0 - timedelta(days=DAYS_MOD)).replace(hour=0, minute=0, second=0)

# Guarda un Id de la corrida tomando Año / mes / dia y hora de la corrida
logging.info('Id Corrida: ', cod)

Df_Estaciones = pd.DataFrame.from_dict({
    "id": [29, 30, 31, 52, 85, 1696, 1699],
    "nombre": ["Parana", "SantaFe", "Diamante", "SanFernando", "BsAs", "Martinez", "Nueva Palmira"],
    "series_id": [29, 30, 31, 52, 85, 3278, 3280],
    "cero_escala": [9.432, 8.378, 6.747, -0.53, 0, 0, 0.0275]
}).set_index("id")

df_obs = ina_service.obtain_obeservations_for_stations(Df_Estaciones, f_inicio_0, f_fin_0)

# Aguas arribas
l_idEst = [29, 30, 31]  # CB Aguas Arriba: Parana Santa Fe y Diamante
Df_EstacionesAA = Df_Estaciones[Df_Estaciones.index.isin(l_idEst)]
df_AA = df_obs[df_obs.id.isin(l_idEst)].copy()

# Margen Derecha
l_idE_MDer = [52, 85]
Df_EstacionesMD = Df_Estaciones[Df_Estaciones.index.isin(l_idE_MDer)]
df_MD = df_obs[df_obs.id.isin(l_idE_MDer)].copy()

# Margen izquierdo
l_idE_MIzq = [1696, 1699]
Df_EstacionesMI = Df_Estaciones[Df_Estaciones.index.isin(l_idE_MIzq)]
df_MI = df_obs[df_obs.id.isin(l_idE_MIzq)].copy()


def obtain_diffs(df, period):
    df.fecha = df.fecha.dt.round(period)
    max_date = df.fecha.max()
    df.set_index(["fecha", "id"], inplace=True)
    df = df.groupby([pd.Grouper(level=0, freq=period), pd.Grouper(level=1)]).mean()
    df.reindex(pd.date_range(start=f_inicio_0, end=max_date, freq=period), level=0)
    df = df.join(Df_Estaciones).droplevel(level=1)
    df.set_index("nombre", append=True, inplace=True)
    df[["valor"]].unstack("nombre")
    df = df.unstack(level=1)["valor"]
    df = df.join(df - df.shift(1), rsuffix="_diff")

    return df


"""### Paso 1:

Une las series en un DF Base:

Cada serie en una columna. Todas con la misma frecuencia, en este caso diaria.

También:
*   Calcula la frecuencia horaria de los datos.
*   Reemplaza Ceros por NAN.
*   Calcula diferencias entre valores concecutivos.

"""

df_AA = obtain_diffs(df_AA, "1D")

"""### Paso 2:
Elimina saltos:

Se establece un umbral_1: si la diferencia entre datos consecutivos supera este umbral_1, se fija si en el resto de las series tambien se produce el salto (se supera el umbral_1).

Si en todas las series se observa un salto se toma el dato como valido.

Si el salto no se produce en las tres o si es mayo al segundo umbral_2 (> que el 1ero) se elimina el dato.

"""

# Datos faltante
# Elimina Saltos
df_AA = utils.delete_jumps_parana_santa_fe_diamante(df_AA)
df_AA = df_AA.drop(['Parana_diff', 'SantaFe_diff', 'Diamante_diff'], axis=1)

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
df_AA['SantaFe'] = df_AA['SantaFe'].add(corim_SantaFe)
df_AA['Diamante'] = df_AA['Diamante'].add(corim_Diamante)

# Calcula media de a pares
mediaPS = df_AA[['Parana', 'SantaFe']].mean(axis=1, )
mediaPD = df_AA[['Parana', 'Diamante']].mean(axis=1, )
mediaSD = df_AA[['SantaFe', 'Diamante']].mean(axis=1, )

# Completo los faltantes
df_AA["Parana"].fillna(mediaSD)
df_AA["SantaFe"].fillna(mediaPD)
df_AA["Diamante"].fillna(mediaPS)

# Elimina los saltos grandes
umbral = 0.3
df_AA[(df_AA["Parana"] - mediaSD) > umbral] = np.nan
df_AA[(df_AA["SantaFe"] - mediaPD) > umbral] = np.nan
df_AA[(df_AA["Diamante"] - mediaPS) > umbral] = np.nan


"""Interpola de forma Linal"""

# Interpola para completa todos los fltantes
df_AA = df_AA.interpolate(method='linear', limit_direction='backward')

# Vuelve las series a su nivel original
df_AA['SantaFe'] = df_AA['SantaFe'].add(-corim_SantaFe)
df_AA['Diamante'] = df_AA['Diamante'].add(-corim_Diamante)

# Series final

df_aux_i = pd.DataFrame()  # Pasa lista a DF
cero_parana = Df_Estaciones[Df_Estaciones['nombre'] == 'Parana']['cero_escala'].values[0]
df_aux_i['Nivel'] = df_AA['Parana'] + cero_parana
df_aux_i['Caudal'] = np.nan
df_aux_i['Id_CB'] = Df_Estaciones[Df_Estaciones.nombre == 'Parana'].index.values[0]

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

df_MD = obtain_diffs(df_MD, "15m")

"""### Paso 2:
Elimina saltos:

Se establece un umbral_1: si la diferencia entre datos consecutivos supera este umbral_1, se fija si en el resto de las series tambien se produce el salto (se supera el umbral_1).

Si en todas las series se observa un salto se toma el dato como valido.

Si el salto no se produce en las tres o si es mayo al segundo umbral_2 (> que el 1ero) se elimina el dato.

"""

# Datos faltante
#  Elimina Saltos
df_MD = utils.delete_jumps_san_fernando_bs_as(df_MD)
df_MD = df_MD.drop(['SanFernando_diff', 'BsAs_diff'], axis=1)

"""### Paso 3:
Completa Faltantes en base a los datos en las otras series.

1.   Lleva las saries al mismo plano.
2.   Calcula meidas de a pares. Parana-Santa Fe , Parana-Diamanate, Parana-Diamante.
3.   Si no hay datos toma el de la media de las otras dos.
4.   Si la diferencia entre el dato y la media es mayor al umbral_3 elimina el dato.'''
"""

df_Niveles = df_MD.copy()

# Copia cada serie en un DF distinto
df_SFer = df_Niveles[['SanFernando']].copy()
df_BsAs = df_Niveles[['BsAs']].copy()

# Corrimiento Vertical
corim_BsAs = 0.2
df_BsAs['BsAs'] = df_BsAs['BsAs'].add(corim_BsAs)

# Corrimiento Temporal
df_BsAs.index = df_BsAs.index + pd.DateOffset(minutes=50)

# Crea DF para unir todas las series/ frec 5 minutos
index5m = pd.date_range(start=f_inicio_0, end=f_finMD,
                        freq='5min')  # Fechas desde f_inicio a f_fin con un paso de 5 minutos
df_5m = pd.DataFrame(index=index5m)  # Crea el Df con indexUnico
df_5m.index.rename('fecha', inplace=True)  # Cambia nombre incide por Fecha
df_5m.index = df_5m.index.round("5min")

# Une en df_5m
df_5m = df_5m.join(df_SFer, how='left')
df_5m = df_5m.join(df_BsAs, how='left')

# Calcula la media de las tres series. E interpola para completar todos los vacios
df_5m['medio'] = df_5m[['SanFernando', 'BsAs', ]].mean(axis=1, )
df_5m = df_5m.interpolate(method='linear', limit_direction='both')
# print('\nNaN medio: '+str(df_5m['medio'].isna().sum()))

# A cada DF de las series les une la serie media de las 3.
# Siempre se une por Izquierda
df_SFer = df_SFer.join(df_5m['medio'], how='left')
df_BsAs = df_BsAs.join(df_5m['medio'], how='left')


df_SFer = utils.complete_missings(df_SFer)
df_BsAs = utils.complete_missings(df_BsAs)

print('\nFaltentes luego de completar con serie media:')
print('NaN SFernando: ' + str(df_SFer['SanFernando'].isna().sum()))
print('NaN BsAs: ' + str(df_BsAs['BsAs'].isna().sum()))

# Vuelve a llevar las series a su lugar original
df_BsAs['BsAs'] = df_BsAs['BsAs'].add(-corim_BsAs)
df_BsAs.index = df_BsAs.index - pd.DateOffset(minutes=50)

# Une en df_
df_SFer.columns = ['SanFernando_f', 'medio']
df_BsAs.columns = ['BsAs_f', 'medio']

df_Niveles = df_Niveles.join(df_SFer['SanFernando_f'], how='left')
df_Niveles = df_Niveles.join(df_BsAs['BsAs_f'], how='left')

del df_SFer
del df_BsAs

# Interpola de forma Linal. Maximo 3 dias

# df_Niveles[nombre] = df_Niveles[nombre].replace(np.nan,-1)
print('\n Interpola para que no queden faltantes')
df_Niveles = df_Niveles.interpolate(method='linear', limit_direction='backward')
print('NaN SFernando: ' + str(df_Niveles['SanFernando_f'].isna().sum()))
print('NaN BsAs: ' + str(df_Niveles['BsAs_f'].isna().sum()))

df_aux_i = pd.DataFrame()  # Pasa lista a DF
cero_sanfer = Df_Estaciones[Df_Estaciones['nombre'] == 'SanFernando']['cero_escala'].values[0]
df_aux_i['Nivel'] = df_Niveles['SanFernando_f'] + cero_sanfer
df_aux_i['Fecha'] = df_Niveles.index
df_aux_i['Id_CB'] = Df_Estaciones[Df_Estaciones.nombre == 'SanFernando']["unid"].values[0]
df_aux_i.to_sql('DataEntrada', con=connLoc, if_exists='append', index=False)

del df_Niveles
del df_aux_i

"""## CB Frente Margen Izquierda"""

"""### Paso 1:
Une las series en un DF Base:

Cada serie en una columna. Todas con la misma frecuencia, en este caso diaria.

También:
*   Calcula la frecuencia horaria de los datos.
*   Calcula diferencias entre valores concecutivos.
"""

f_finMI = df_MI['fecha'].max()

indexUnico15M = pd.date_range(start=f_inicio_0, end=f_finMI, freq='15min')
df_base_CB_MI = pd.DataFrame(index=indexUnico15M)  # Crea el Df con indexUnico
df_base_CB_MI.index.rename('fecha', inplace=True)  # Cambia nombre incide por Fecha

for index, row in Df_EstacionesMI.iterrows():
    nombre = (row['nombre'])
    # print(nombre)
    df_var = df_MI[(df_MI['id'] == row['unid'])].copy()

    # Acomoda DF para unir
    df_var.set_index(pd.DatetimeIndex(df_var['fecha']),
                     inplace=True)  # Pasa la fecha al indice del dataframe (DatetimeIndex)
    del df_var['fecha']
    del df_var['id']
    df_var.columns = [nombre, ]

    # Une al DF Base.
    df_base_CB_MI = df_base_CB_MI.join(df_var, how='left')
del df_var

# print(df_base_CB_MI.tail(30))
df_base_CB_MI = df_base_CB_MI.interpolate(method='linear', limit=2, limit_direction='backward')
# print(df_base_CB_MI.tail(30))

indexUnico1H = pd.date_range(start=f_inicio_0, end=f_finMD,
                             freq='H')  # Fechas desde f_inicio a f_fin con un paso de 5 minutos
df_base_CB_MI_H = pd.DataFrame(index=indexUnico1H)  # Crea el Df con indexUnico
df_base_CB_MI_H.index.rename('fecha', inplace=True)
df_base_CB_MI_H = df_base_CB_MI_H.join(df_base_CB_MI, how='left')

df_base_CB_MI = df_base_CB_MI_H.copy()
del df_base_CB_MI_H
# print(df_base_CB_MI.tail(30))
for index, row in Df_EstacionesMI.iterrows():
    nombre = (row['nombre'])

    # Reemplaza Ceros por NAN
    # df_base[nombre] = df_base[nombre].replace(0, np.nan)

    # Calcula diferencias entre valores concecutivos
    VecDif = abs(np.diff(df_base_CB_MI[nombre].values))
    VecDif = np.append([0, ], VecDif)
    coldiff = 'Diff_' + nombre[:4]
    df_base_CB_MI[coldiff] = VecDif

"""### Paso 2:

Elimina saltos:

Se establece un umbral_1: si la diferencia entre datos consecutivos supera este umbral_1, se fija si en el resto de las series tambien se produce el salto (se supera el umbral_1).

Si en todas las series se observa un salto se toma el dato como valido.

Si el salto no se produce en las tres o si es mayo al segundo umbral_2 (> que el 1ero) se elimina el dato.
"""

# Datos faltante
# Elimina Saltos
df_base_CB_MI = utils.delete_jumps_nueva_palmira_martinez(df_base_CB_MI)

# Datos Faltantes Luego de limpiar saltos
print('\nDatos Faltantes Luego de limpiar saltos')

"""### Paso 3:

Completa Faltantes en base a los datos en las otras series.

1.   Lleva las saries al mismo plano.
2.   
3.   Si no hay datos toma el de la media de las otras dos.
4.   Si la diferencia entre el dato y la media es mayor al umbral_3 elimina el dato.'''
"""

# Copia cada serie en un DF distinto
df_NPal = df_base_CB_MI[['Nueva Palmira']].copy()
df_Mart = df_base_CB_MI[['Martinez']].copy()

# Corrimiento Vertical y Temporal
corim_Mart = 0.24
df_Mart['Martinez'] = df_Mart['Martinez'].add(corim_Mart)
df_Mart.index = df_Mart.index - pd.DateOffset(minutes=60)

# Crea DF para unir todas las series/ frec 1 hora
index1H = pd.date_range(start=f_inicio_0, end=f_finMI,
                        freq='1H')  # Fechas desde f_inicio a f_fin con un paso de 5 minutos
df_1H = pd.DataFrame(index=index1H)  # Crea el Df con indexUnico
df_1H.index.rename('fecha', inplace=True)  # Cambia nombre incide por Fecha
df_1H.index = df_1H.index.round("H")

# Une en df_1H
df_1H = df_1H.join(df_NPal, how='left')
df_1H = df_1H.join(df_Mart, how='left')

df_1H['Diff'] = df_1H['Nueva Palmira'] - df_1H['Martinez']
# print(df_1H['Diff'].describe())

# boxplot = df_1H.boxplot(column=['Diff'])


df_1H['Nueva Palmira'] = df_1H['Nueva Palmira'].interpolate(method='linear', limit_direction='backward')


################# Guarda para modelo
df_aux_i = pd.DataFrame()  # Pasa lista a DF
cero_NPalmira = Df_Estaciones[Df_Estaciones['nombre'] == 'Nueva Palmira']['cero_escala'].values[0]
df_aux_i['Nivel'] = df_1H['Nueva Palmira'] + cero_NPalmira
df_aux_i['Fecha'] = df_1H.index
df_aux_i['Id_CB'] = Df_Estaciones[Df_Estaciones.nombre == 'Nueva Palmira'][0]["unid"]
df_aux_i = df_aux_i.dropna()

df_aux_i