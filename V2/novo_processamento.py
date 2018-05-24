# Filtra os dados
# cat ModoApi_Data.csv | awk -F "," '{print $2","$3","$4","$8}' > Filtered_ModoApi_Data.csv

# retira as linhas com False
# cat data/Filtered_ModoApi_Data.csv | grep -v "False" > data/True_Filtered_ModoApi_Data.csv

# retira as linhas com NaN
# cat data/True_Filtered_ModoApi_Data.csv | grep -v ",," > data/NaN_True_Filtered_ModoApi_Data.csv

# retira as linhas com Cabecalho
# cat data/NaN_True_Filtered_ModoApi_Data.csv | grep -v "LocationID" > data/Header_NaN_True_Filtered_ModoApi_Data.csv

# converte datas em timestemp
# cat data/Header_NaN_True_Filtered_ModoApi_Data.csv | awk -F ',' '{cmd="date -d \""$3"\" +%s"; cmd| getline $3; close(cmd); print $1","$2","$3","$4}'  > data/Timestemp_Header_NaN_True_Filtered_ModoApi_Data.csv

import pandas as pd
import numpy as np
import datetime as dt
import pytz

df = pd.read_csv('data/miFiltered_ModoApi_Data.csv')
df = df.dropna()
df = df[df['StartTime'] != 'False']
# df.loc[df['LocationID'].str.contains(non_numeric) == True]

# visualizar os dados apagados
# df.loc[pd.to_numeric(df['StartTime'], errors='coerce').isnull()]

# apaga linhas nao numeriacas
df['LocationID'] = pd.to_numeric(df['LocationID'], errors='coerce')
df = df.dropna()

df.to_csv('data/Filtered_ModoApi_Data.csv')


df.count()

df = df.dropna()
df.count()

df

# Formatando os dados para tipos mais apropriados
types = {
    'LocationID': int,
    'CarID': int,
    'StartTime': int
    }

df = df.astype(dtype=types)

# cat data/miFiltered_ModoApi_Data.csv | awk -F ',' '{cmd="date -d \""$3"\" +%s"; cmd| getline $3; close(cmd); print $1","$2","$3","$4} > '

df.dtypes


df['Teste'] = df['CaptureTime'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))

# pd.to_datetime(df['CaptureTime'], )

df
