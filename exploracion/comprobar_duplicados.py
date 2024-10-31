"""
Comprueba los duplicados del dataset Spanish_Housing_Dataset.
"""

import pandas as pd

path = './explorar/data/Spanish_Housing_Dataset/spanish_houses.csv'
df = pd.read_csv(path)

df_sin_duplicados = df.drop_duplicates()

print('duplicados eliminados: ' + str(df.shape[0] - df_sin_duplicados.shape[0]))

df_sin_duplicados.to_csv('./explorar/data/Spanish_Housing_Dataset/df_sin_duplicados.csv', index=False, encoding='utf-8')

# # keep=False muestra todas las filas duplicadas
# duplicados = df[df.duplicated(subset=['loc_full', 'ad_description'], keep=False)]

# num_duplicados = duplicados.groupby(['loc_full', 'ad_description']).size().reset_index(name='conteo')

# duplicados.to_csv('duplicados.csv', index=False, encoding='utf-8')

# if not num_duplicados.empty:
#     print("Filas duplicadas basándonos en 'loc_full' y 'ad_description':")
#     print(num_duplicados)
# else:
#     print("No se encontraron duplicados basados en 'loc_full' y 'ad_description'.")
