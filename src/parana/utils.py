import numpy as np


def delete_jumps_parana_santa_fe_diamante(df_base):
    umbral_1 = 0.3
    umbral_2 = 1.0

    # Parana
    for index, row in df_base.iterrows():
        if abs(row['Parana_diff']) > umbral_1:
            if (abs(row['SantaFe_diff']) > umbral_1) and (abs(row['Diamante_diff']) > umbral_1):
                if abs(row['Parana_diff']) > umbral_2:
                    df_base.loc[index, 'Parana'] = np.nan
                else:
                    # print('Los 3 presentan un salto. Se supone que esta ok.')
                    continue
            else:
                # print('Salto en Parana y StFe o Diamante')
                df_base.loc[index, 'Parana'] = np.nan
        else:
            continue

    # Santa Fe
    for index, row in df_base.iterrows():
        if abs(row['SantaFe_diff']) > umbral_1:
            if (abs(row['Parana_diff']) > umbral_1) and (abs(row['Diamante_diff']) > umbral_1):
                if abs(row['SantaFe_diff']) > umbral_2:
                    df_base.loc[index, 'SantaFe'] = np.nan
                else:
                    # print('Los 3 presentan un salto. Se supone que esta ok.')
                    continue
            else:
                # print('Salto en StFe y Parana o Diamante')
                df_base.loc[index, 'SantaFe'] = np.nan
        else:
            continue

    # Diamante
    for index, row in df_base.iterrows():
        if abs(row['Diamante_diff']) > umbral_1:
            if (abs(row['Parana_diff']) > umbral_1) and (abs(row['SantaFe_diff']) > umbral_1):
                if abs(row['Diamante_diff']) > umbral_2:
                    df_base.loc[index, 'Diamante'] = np.nan
                else:
                    # print('Los 3 presentan un salto. Se supone que esta ok.')
                    continue
            else:
                # print('Salto en Diamante y Parana o StFe')
                df_base.loc[index, 'Diamante'] = np.nan
        else:
            continue
    return df_base


def delete_jumps_san_fernando_bs_as(df_base):  # Elimina Saltos en la serie
    umbral_1 = 0.5
    umbral_2 = 1.0

    # SFernando
    for index, row in df_base.iterrows():
        if abs(row['SanFernando_diff']) > umbral_1:
            if abs(row['BsAs_diff']) > umbral_1:
                if abs(row['SanFernando_diff']) > umbral_2:
                    df_base.loc[index, 'SanFernando'] = np.nan
                else:
                    continue
                    # print('Los 3 presentan un salto. Se supone que esta ok.')
            else:
                # print('Salto en SanFer y BsAs o Brag')
                df_base.loc[index, 'SanFernando'] = np.nan
        else:
            continue
    # BsAs
    for index, row in df_base.iterrows():
        if abs(row['BsAs_diff']) > umbral_1:
            if abs(row['SanFernando_diff']) > umbral_1:
                if abs(row['BsAs_diff']) > umbral_2:
                    df_base.loc[index, 'BsAs'] = np.nan
                else:
                    continue
                    # print('Los 3 presentan un salto. Se supone que esta ok.')
            else:
                # print('Salto en BsAs y SFer o Braga')
                df_base.loc[index, 'BsAs'] = np.nan
        else:
            continue
    return df_base


def delete_jumps_nueva_palmira_martinez(df_base):  # Elimina Saltos en la serie
    umbral_1 = 0.3
    umbral_2 = 0.7

    # Nueva Palmira
    for index, row in df_base.iterrows():
        if abs(row['Nueva Palmira_diff']) > umbral_1:
            if abs(row['Martinez_diff']) > umbral_1:
                if abs(row['Nueva Palmira_diff']) > umbral_2:
                    df_base.loc[index, 'Nueva Palmira'] = np.nan
                else:
                    continue
                    # print('Los 2 presentan un salto. Se supone que esta ok.')
            else:
                # print('Salto en NPalmira')
                df_base.loc[index, 'Nueva Palmira'] = np.nan
        else:
            continue

    # Martinez
    for index, row in df_base.iterrows():
        if abs(row['Martinez_diff']) > umbral_1:
            if abs(row['Nueva Palmira_diff']) > umbral_1:
                if abs(row['Martinez_diff']) > umbral_2:
                    df_base.loc[index, 'Martinez'] = np.nan
                else:
                    continue
                    # print('Los 2 presentan un salto. Se supone que esta ok.')
            else:
                # print('Salto en Martinez')
                df_base.loc[index, 'Martinez'] = np.nan
        else:
            continue

    return df_base


def complete_missings(df_ConMedia):
    ncol = df_ConMedia.columns[0]
    for index, row in df_ConMedia.iterrows():
        if np.isnan(row[ncol]):
            df_ConMedia.loc[index, ncol] = row['medio']
    return df_ConMedia
