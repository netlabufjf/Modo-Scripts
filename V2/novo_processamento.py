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

df = pd.read_csv('data/Header_NaN_True_Filtered_ModoApi_Data.csv',
                 names=["LocationID", "CarID", "CaptureTime", "StartTime"])
df.count()
# limpa registros com nulo
df = df.dropna()

df.dtypes

types = {
    'LocationID': int,
    'CarID': int,
    'StartTime': int}

df = df.astype(dtype=types)

df.count()

df

df['CaptureTime'] = pd.to_datetime(df['CaptureTime'])


df['CaptureTime'] = df['CaptureTime'].astype('int64')//1e9


df.to_csv('data/Timestemp_Header_NaN_True_Filtered_ModoApi_Data.csv', index=False)

df

# Dom, 5 de Nov, 02:00 - 1509854400
# Dom, 15 de Out, 00:00 - 1508036400

df[df.CaptureTime < 1508036400].count()
df[(df.CaptureTime > 1508036400) & (df.CaptureTime < 1509854400)].count()
df[df.CaptureTime > 1509854400].count()

# ate dia 15/10 diminui 4h
df.loc[df.CaptureTime < 1508036400, "CaptureTime"] = df["CaptureTime"] - (4*3600)

# do dia 15/10 até dia 05/11 diminui 5h
df.loc[(df.CaptureTime > 1508036400) & (df.CaptureTime < 1509854400),
       "CaptureTime"] = df["CaptureTime"] - (5*3600)

# do dia 05/11 pra frente diminui 6h
df.loc[df.CaptureTime > 1509854400, "CaptureTime"] = df["CaptureTime"] - (6*3600)

df.to_csv('data/Vancouver_Timestemp_Header_NaN_True_Filtered_ModoApi_Data.csv', index=False)

df

# ordena pelo carro, hora de captura e start
df.sort_values(by=['CarID', 'CaptureTime', 'StartTime'], inplace=True)

min = df.CaptureTime.min()
max = df.StartTime.max()

minutosTotais = (max-min)/60

dfCarId = df.groupby(['CarID'], as_index=False).count().CarID.copy()

# para cada carro foi criado um vetor com todos os minutos possiveis de reserva
dfTimelineReservas = pd.DataFrame(columns=['CarID', 'Minuto', 'Reserva'])

for carId in dfCarId:
    inicio = min
    for i in range(0, minutosTotais):
        minutoAtual = inicio + i*60
        if(df[(df['CaptureTime'] <= minutoAtual) & (df['StartTime'] > minutoAtual)].empty):
            linha = {'CarID': carId, 'Minuto': minutoAtual, 'Reserva': False}
            dfTimelineReservas = dfTimelineReservas.append(linha, ignore_index=True)
        else:
            linha = {'CarID': carId, 'Minuto': minutoAtual, 'Reserva': True}
            dfTimelineReservas = dfTimelineReservas.append(linha, ignore_index=True)

dfTimelineReservas.to_csv('data/Processados.csv', index=False)


# do dia 15/10 ate o dia 05/11

# do dia 05/11 pra frente


# apaga linhas com dados com False
# df = df[df['StartTime'] != 'False']
# df.loc[df['LocationID'].str.contains(non_numeric) == True]

# visualizar os dados apagados
# df.loc[pd.to_numeric(df['StartTime'], errors='coerce').isnull()]

# apaga linhas nao numeriacas
# df['LocationID'] = pd.to_numeric(df['LocationID'], errors='coerce')
# df = df.dropna()
#
# df.to_csv('data/Filtered_ModoApi_Data.csv')
#
#
# df.count()
#
# df = df.dropna()
# df.count()
#
# df
#
# # Formatando os dados para tipos mais apropriados
# types = {
#     'LocationID': int,
#     'CarID': int,
#     'StartTime': int
# }
#
# df = df.astype(dtype=types)
#
# # cat data/miFiltered_ModoApi_Data.csv | awk -F ',' '{cmd="date -d \""$3"\" +%s"; cmd| getline $3; close(cmd); print $1","$2","$3","$4} > '
#
# df.dtypes
#
#
# df['Teste'] = df['CaptureTime'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))
#
# # pd.to_datetime(df['CaptureTime'], )
#
# df
