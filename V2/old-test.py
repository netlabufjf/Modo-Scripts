
# coding: utf-8

# In[2]:

# get_ipython().magic('matplotlib inline')
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import datetime
import pytz

# A mudança foi que estou ordenando as viagens e as reservas antes de qualquer alteração
# Agora ta sem um dos breaks e sem a concatenacao das viagens
# Retirei os breaks
print('COMECOU O INTRAVEL!!!')

# ## Lendo e filtrando os dados coletados da API

# In[3]:

# Lendo dados coletados da API
df = pd.read_csv('../ModoApi_Data.csv')


# In[3]:

def str_to_datetime(df_time):
    """
    Reformatando de string para datetime.

    Parameters
    ----------
    df_time : pandas.DataFrame, string
        Dataframe com strings a serem convertidas para datetime.

    Returns
    ----------
    date_list : pandas.DataFrame, datetime
        Dataframe com valores em datetime para possíveis fusos de Vancouver.

    """
    date_list = []

    # Formatos de fuso horário comum de Vancouver e
    # fuso horário característico de horário de verão
    format_string = ['%Y-%m-%d %H:%M:%S.%f-08:00', '%Y-%m-%d %H:%M:%S.%f-07:00',
                     '%Y-%m-%d %H:%M:%S-08:00', '%Y-%m-%d %H:%M:%S-07:00',
                     '%Y-%m-%d %H:%M:%S.%f','%Y-%m-%d %H:%M:%S']

    print(datetime.datetime.now())
    for date in df_time:
        for fmt in format_string:
            try:
                date_list.append(datetime.datetime.strptime(str(date), fmt))
                break
            except:
                pass

    print(datetime.datetime.now())
    return pd.DataFrame(date_list)


# In[4]:

def get_car_ids(car_list):
    """
    Coleta todos os IDs de carros coletados, sem repetições, de uma lista.

    Parameters
    -----------
    car_list : int list ou pandas.DataFrame
        Lista de todos os IDs coletados.

    Returns
    ----------
    car_ids : int
        Lista com todos os IDs já coletados, sem repetições.

    Notes
    ---------
    A coleta dos IDs é realizada de tal forma para obter IDs de veículos que
    por utilização da API podem não ser retornados, como os que estão em manutenção
    não estão na frota atual.
    """

    car_ids = []

    for car in car_list:
        if (car in car_ids):
            continue
        else:
            car_ids.append(car)

    return car_ids


# In[5]:

# Retirando dados nan
#df.dropna(axis=0, how='any', inplace=True)

#Limpando dados
df.drop(['Unnamed: 0'], axis=1, inplace=True)
df = df[df['CarID'] != 'CarID']
df.dropna(how='any', axis=0, inplace=True)

# Formatando os dados para tipos mais apropriados
types = {
    'LocationID': int,
    'CarID': int,
    'FullyAvailable': float,
    'PartlyAvailable': float,
    'NotAvailable': float,
    'StartTime': str,
    'EndTime': str,
    'Duration': str,
    'RequestStart': int,
    'RequestEnd': int,
    'RequestDuration': int
}

df = df.astype(dtype=types)

# Convertendo datetime strings para o tipo datetime
df['CaptureTime'] = str_to_datetime(df['CaptureTime'])

# Retirando colunas que não serão utilizadas
#df.drop(['LocationID', 'EndTime', 'RequestEnd'], axis=1, inplace=True)

df.drop(['LocationID', 'FullyAvailable', 'PartlyAvailable', 'NotAvailable',
         'Duration', 'EndTime', 'RequestEnd', 'RequestDuration'], axis=1, inplace=True)

# Coletando todos os IDs dos veículos
car_ids = get_car_ids(df['CarID'])

#df.drop('CarID', axis=1, inplace=True)

# Retirando todos com o atributo start time == False (estão parados)
df = df[df['StartTime'] != 'False']

# ## Porcentagem de carros ocupados a cada minuto

# In[6]:

def convert_datetime_timezone(dt, tz1, tz2):
    """
    Converte uma hora no fuso UTC ou São Paulo para um provável fuso de Vancouver.

    Parameters
    ------------
    dt : unix timestamp
        Timestamp a ser convertido para outro fuso horário.

    tz1, tz2 : Timezone String
        Time zone atual e a que a hora irá ser convertida.

    Returns
    ----------
    dt : unix timestamp
        Timestamp já convertida para o fuso de Vancouver.

    """

    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.fromtimestamp(dt)
    dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)

    try:
        dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S-07:00")
  # Except para evitar um erro pela mudança de fuso horário\n",
    except Exception as e:
        print(e)
# Diminui 1 hora para se adaptar\n",
        #dt = dt - datetime.timedelta(hours=1)
        dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S-08:00")

#    try:
        # Fuso horário comum de Vancouver
#        dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S-08:00")
#    except:
        # Fuso horário característico de horário de verão em Vancouver
#        dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S-07:00")

    dt = int(dt.timestamp())

    return dt


# In[7]:

# Eliminando intervalos de disponibilidade futuros
print('Tamanho antes: '+str(len(df)))
for car in car_ids:

    df[df['CarID'] == car].drop_duplicates(subset='CaptureTime', keep='first', inplace=True)

# Retirando dados nan
df.dropna(axis=0, how='any', inplace=True)
print('Tamanho depois: '+str(len(df)))

# In[9]:

in_travel = 0
andando_weekdays = []
andando_weekends = []

# Ordenando dados base
df = df.sort_values(by=['CaptureTime','CarID'])



# Percorre todo o dataframe para verificar quais carros estão andando em dado minuto
for i in range(1, len(df)):
    capture_time_atual = int(df['CaptureTime'].iloc[i].timestamp())
    capture_time_atual = convert_datetime_timezone(capture_time_atual, 'UTC', 'America/Vancouver')

    capture_time_anterior = int(df['CaptureTime'].iloc[i-1].timestamp())
    capture_time_anterior = convert_datetime_timezone(capture_time_anterior, 'UTC', 'America/Vancouver')

    start_time = int(df['StartTime'].iloc[i])
    start_time = convert_datetime_timezone(start_time, 'America/Sao_Paulo', 'America/Vancouver')

    request_start = df['RequestStart'].iloc[i]
    request_start = convert_datetime_timezone(request_start, 'America/Sao_Paulo', 'America/Vancouver')

    # Enquanto está no mesmo minuto, é analisado se o carro está andando
    if (capture_time_atual == capture_time_anterior):
        if (start_time > request_start):
            in_travel += 1
    else:
        porcentagem = (in_travel/len(car_ids))*100

        # Verifica que a data está entre segunda(1) e sexta(5)
        if (int(datetime.datetime.fromtimestamp(capture_time_anterior).strftime('%w')) > 0 and
            int(datetime.datetime.fromtimestamp(capture_time_anterior).strftime('%w')) < 6):
            andando_weekdays.append([capture_time_anterior, in_travel, porcentagem])
        else:
            andando_weekends.append([capture_time_anterior, in_travel, porcentagem])
        in_travel = 0

dfIn_Travel_weekdays = pd.DataFrame(andando_weekdays, columns=['capture_time', 'total_in_travel', 'percentage'])
dfIn_Travel_weekends = pd.DataFrame(andando_weekends, columns=['capture_time', 'total_in_travel', 'percentage'])


# In[10]:

def from_timestamp_list(timestamp_list):

    datetime_list = []

    for date in timestamp_list:
        datetime_list.append(datetime.datetime.fromtimestamp(int(date)))

    return pd.DataFrame(datetime_list)


# In[11]:

# Formatando os dados de unix timestamp para datetime

dfWeekdays = dfIn_Travel_weekdays

dfWeekdays['capture_time'] = from_timestamp_list(dfWeekdays['capture_time'])


dfWeekends = dfIn_Travel_weekends

dfWeekends['capture_time'] = from_timestamp_list(dfWeekends['capture_time'])


# In[14]:

dfWeekends.to_csv('weekends_diminuindo.csv', index=False, encoding='utf-8')
dfWeekdays.to_csv('weekdays_diminuindo.csv', index=False, encoding='utf-8')


# In[17]:

#dfWeekends = pd.read_csv('weekends_diminuindo.csv')
#dfWeekdays = pd.read_csv('weekdays_diminuindo.csv')

dfWeekdays['capture_time'] = pd.to_datetime(dfWeekdays['capture_time'])
dfWeekends['capture_time'] = pd.to_datetime(dfWeekends['capture_time'])

# In[12]:

# Plot da porcentagem de carros alocados em dias de semana
#plt.plot(dfWeekdays['capture_time'],dfWeekdays['percentage'])
#plt.gcf().autofmt_xdate()
# plt.show()


# In[13]:

# Plot da porcentagem de carros alocados em dias de final de semana
#plt.plot(dfWeekends['capture_time'],dfWeekends['percentage'])
#plt.gcf().autofmt_xdate()
# plt.show()


# ## Porcentagem média de carros ocupados em cada minuto

# In[26]:

# Faz a media das porcentagens para todos os minutos de uma certa quantidade de dias
def media(df, num_dias):

    media = []
    minutes_of_day = 1440
    ant = -1
    valores = pd.DataFrame()
    # Loop que irá verificar um dia de registros(24h = 1440 min) visualizando cada minuto
    for i in range(minutes_of_day-1):
        count = 0
        # Irá percorrer os dias seguintes para encontrar as outras incidencias do mesmo minuto
        for j in range(i, num_dias * minutes_of_day, minutes_of_day-80):

            try:
                # Por conta de filtros os indices não estão exatos
                # Ele irá procurar em um intervalo o minuto desejado
                for c in range(j, j+3000):
                    #Se tiver o mesma hora e minuto somamos a média, além de ser diferente do valor anterior
                    if (df['capture_time'].iloc[c].minute == df['capture_time'].iloc[i].minute and
                        df['capture_time'].iloc[c].hour == df['capture_time'].iloc[i].hour and
                        int(df['capture_time'].iloc[c].day) != ant):

                        valores = valores.append([df['percentage'].iloc[c]])

                        #variavel para evitar pegar valores repetidos
                        ant = int(df['capture_time'].iloc[c].day)

                        # Atualiza o j para onde o minuto foi encontrado
                        j=c
                        count += 1
                        break

            except Exception as e:
                #print(e)
                break
        print(str(count)+"   "+str(i))

        # Registra somente a hora, media e desvio padrão das porcentagens dos dias
        media.append([df['capture_time'].iloc[i].strftime('%H:%M'), float(valores.mean()), float(valores.std())])
        valores = pd.DataFrame()

    media = pd.DataFrame(media, columns=['time', 'mean', 'std'])

    # Formatando a hora para datetime
    for i in range(len(media)):
        media['time'].iloc[i] = datetime.datetime.strptime(media['time'].iloc[i], '%H:%M').time()

    return media


# In[20]:

# Fazendo a média das porcentagens de cada dia
dfWeekdays = dfWeekdays.sort_values(by='capture_time')
mediaWeekdays = media(dfWeekdays, 32)

dfWeekends = dfWeekends.sort_values(by='capture_time')
mediaWeekends = media(dfWeekends, 20)

# In[22]:

mediaWeekdays.to_csv('mediaWeekdays.csv', index=False, encoding='utf-8')
mediaWeekends.to_csv('mediaWeekends.csv', index=False, encoding='utf-8')


# In[9]:

#mediaWeekdays = pd.read_csv('mediaWeekdays_diminuindo.csv')
#mediaWeekends = pd.read_csv('mediaWeekends_diminuindo.csv')


# In[10]:

# Ordenando pelo tempo
mediaWeekdays = mediaWeekdays.sort_values(by=['time'])
mediaWeekends = mediaWeekends.sort_values(by=['time'])


# # Gráficos de porcentagem média de carros ocupados em cada minuto

# In[11]:

import numpy as np

# Plot da media das porcentagens dos dias de semana
fig, ax = plt.subplots()
# Curva dos carros andando
ax.plot(range(len(mediaWeekdays['time'])),mediaWeekdays['mean'], label='Carros Ocupados')

# Curvas representando o intervalo de desvio padrão
ax.plot(range(len(mediaWeekdays['time'])), mediaWeekdays['mean']+mediaWeekdays['std'], alpha=150, c='gray', label='Desvio Padrão')
ax.plot(range(len(mediaWeekdays['time'])), mediaWeekdays['mean']-mediaWeekdays['std'], alpha=150, c='gray')

# Modificando os labels das horas
ax.xaxis.set_ticks(np.arange(0, 1441, 120))

fig.canvas.draw()

labels = [item.get_text() for item in ax.get_xticklabels()]
labels = range(0,26,2)

ax.set_xticklabels(labels)

# Legendas e label dos eixos
plt.legend(bbox_to_anchor=(0.01, 0.99), loc=2, borderaxespad=0.2)
plt.ylabel('Percentual')
plt.xlabel('Horario')

# Salvando o plot
plt.savefig('Weekdays_v2.pdf', bbox_inches='tight')

# plt.show()


# In[12]:

import numpy as np

# Plot da media das porcentagens dos dias de semana
fig, ax = plt.subplots()
# Curva dos carros andando
ax.plot(range(len(mediaWeekends['time'])),mediaWeekends['mean'], label='Carros Reservados')

# Curvas representando o intervalo de desvio padrão
ax.plot(range(len(mediaWeekends['time'])), mediaWeekends['mean']+mediaWeekends['std'], alpha=150, c='gray', label='Desvio Padrão')
ax.plot(range(len(mediaWeekends['time'])), mediaWeekends['mean']-mediaWeekends['std'], alpha=150, c='gray')

# Modificando os labels das horas
ax.xaxis.set_ticks(np.arange(0, 1441, 120))

fig.canvas.draw()

labels = [item.get_text() for item in ax.get_xticklabels()]
labels = range(0,26,2)

ax.set_xticklabels(labels)

# Legendas e label dos eixos
plt.legend(bbox_to_anchor=(0.01, 0.99), loc=2, borderaxespad=0.2)
plt.ylabel('Percentual')
plt.xlabel('Horário')

# Salvando o plot
plt.savefig('Weekends_v2.pdf', bbox_inches='tight')

# plt.show()


# ## Extração das porcentagens de carros reservados

# In[19]:

# CSV criado a partir dos dados coletados do arquivo ModoApi_Data_Filter
#dfTravels = pd.read_csv('travels_v2.csv')
dfTravels = pd.read_csv('../travels_sem_reduzir_v1.csv')

# Concatenando reservas consecutivas
dfTravels = dfTravels.sort_values(by=['car_id', 'start'])


# ##  Função para contar a porcentagem de carros reservados nos dias passados como parâmetro

# In[15]:

# A função deve receber os valores previamente separados como somente dias de semana ou finais de semana
def cont_reservas(dfDays):
# Coletando todos os minutos de captura
    datas = pd.to_datetime(dfWeekends['capture_time'])
    datas = pd.DataFrame(datas)

    dfReservas = pd.concat([dfTravels['car_id'], dfTravels['start'], dfTravels['end']], axis=1)

    # Ordenando os valores pelo tempo de inicio das reservas
    dfReservas = dfReservas.sort_values(by='start')

    cont_reservas = [0]*len(datas)

    # Percorrendo para cada id dos veículos
    for car in car_ids:
        print(car)
        reservas = dfReservas[dfReservas['car_id'] == car]
        timeline = []

        # Percorrendo todas as datas da coleta
        for i in range(len(datas)):
            data_timestamp = datas['capture_time'].iloc[i].timestamp()
            data = datas['capture_time'].iloc[i]
            estava_reservado = False

            # Percorrendo os intervalos de cada viagem
            for j in range(len(reservas)):
                # Verificando se o horário está entre o intervalo
                if (dfReservas['start'].iloc[j] <= data_timestamp <= dfReservas['end'].iloc[j]):
                    timeline.append(1)
                    estava_reservado = True
                    break

            # Se o veiculo não estava reservado em dado minuto
            if (not estava_reservado):
                timeline.append(0)

        # Somando os valores se estava ou não reservado
        cont_reservas = [x + y for x, y in zip(timeline, cont_reservas)]

    mean_reservas = [(x/len(car_ids))*100 for x in cont_reservas]
    reservas = pd.DataFrame()
    reservas['total_reserves'] = cont_reservas
    reservas['percentage'] = mean_reservas
    reservas['datetime'] = datas['capture_time']

    return reservas


# In[20]:

dfR_Weekdays = cont_reservas(dfWeekdays)
dfR_Weekends = cont_reservas(dfWeekends)


# In[21]:

dfR_Weekends.to_csv('r_weekends_v2.csv', index=False, encoding='utf-8')
dfR_Weekdays.to_csv('r_weekdays_v2.csv', index=False, encoding='utf-8')


# In[13]:

# dfR_Weekdays =  pd.read_csv('r_weekdays_v2.csv')
# dfR_Weekends =  pd.read_csv('r_weekends_v2.csv')


# In[22]:

# Formatando os dias para datetime
dfR_Weekdays['datetime'] = pd.to_datetime(dfR_Weekdays['datetime'])
dfR_Weekends['datetime'] = pd.to_datetime(dfR_Weekends['datetime'])


# In[23]:

# Plot da porcentagem de carros alocados em dias de semana
plt.plot(dfR_Weekdays['datetime'],dfR_Weekdays['percentage'])
plt.gcf().autofmt_xdate()
# plt.show()


# In[24]:

# Plot da porcentagem de carros alocados em dias de semana
plt.plot(dfR_Weekends['datetime'],dfR_Weekends['percentage'])
plt.gcf().autofmt_xdate()
# plt.show()


# In[30]:

# Fazendo a média das porcentagens de cada dia
dfR_Weekdays = dfR_Weekdays.sort_values(by='datetime')
dfR_Weekdays['capture_time'] = dfR_Weekdays['datetime']
dfmediaR_Weekdays = media(dfR_Weekdays, 32)
# Ordenando pelo tempo
dfmediaR_Weekdays = dfmediaR_Weekdays.sort_values(by='time')
dfmediaR_Weekdays.to_csv('media_r_weekdays.csv', index=False, encoding='utf-8')

dfR_Weekends = dfR_Weekends.sort_values(by='datetime')
dfR_Weekends['capture_time'] = dfR_Weekends['datetime']
dfmediaR_Weekends = media(dfR_Weekends, 20)
# Ordenando pelo tempo
dfmediaR_Weekends = dfmediaR_Weekends.sort_values(by='time')
dfmediaR_Weekends.to_csv('media_r_weekends.csv', index=False, encoding='utf-8')




# # Plotagem final da porcentagem de carros reservados e ocupados

# In[29]:

import numpy as np
import matplotlib

matplotlib.rc('font', size=12)

# Plot das porcentagens dos fins de semana
fig, (ax1, ax2) = plt.subplots(1, 2)

fig.set_size_inches(14,4.5)



# Curva dos carros andando

ax1.plot(range(len(mediaWeekdays['time'])),mediaWeekdays['mean'], label='Carros Ocupados')

# Curvas representando o intervalo de desvio padrão
ax1.plot(range(len(mediaWeekdays['time'])), mediaWeekdays['mean']+mediaWeekdays['std'], alpha=150, c='gray')
ax1.plot(range(len(mediaWeekdays['time'])), mediaWeekdays['mean']-mediaWeekdays['std'], alpha=150, c='gray')


# Curva dos carros reservados
ax1.plot(range(len(dfmediaR_Weekdays['time'])),dfmediaR_Weekdays['mean'], label='Carros Reservados', c='r', ls='--')

# Curvas representando o intervalo de desvio padrão
ax1.plot(range(len(dfmediaR_Weekdays['time'])), dfmediaR_Weekdays['mean']+dfmediaR_Weekdays['std'], alpha=150, c='#FA8072', ls='--')
ax1.plot(range(len(dfmediaR_Weekdays['time'])), dfmediaR_Weekdays['mean']-dfmediaR_Weekdays['std'], alpha=150, c='#FA8072', ls='--')


# Modificando os labels das horas e das porcentagens
ax1.xaxis.set_ticks(np.arange(0, 1441, 120))
ax1.yaxis.set_ticks(np.arange(0, 110, 10))

fig.canvas.draw()

labels = [item.get_text() for item in ax1.get_xticklabels()]
labels = range(0,26,2)

ax1.set_xticklabels(labels)

# Eixo y de 0 a 100%
ax1.set_ylim([0,100])

# Legendas e label dos eixos
ax1.legend(bbox_to_anchor=(0.01, 0.99), loc=2, borderaxespad=0.2)
ax1.set_ylabel('Percentual')
ax1.set_xlabel('Horário')




# Curva dos carros andando
ax2.plot(range(len(mediaWeekends['time'])),mediaWeekends['mean'], label='Carros Ocupados')

# Curvas representando o intervalo de desvio padrão
ax2.plot(range(len(mediaWeekends['time'])), mediaWeekends['mean']+mediaWeekends['std'], alpha=150, c='gray')
ax2.plot(range(len(mediaWeekends['time'])), mediaWeekends['mean']-mediaWeekends['std'], alpha=150, c='gray')


# Curva dos carros reservados
ax2.plot(range(len(dfmediaR_Weekends['time'])),dfmediaR_Weekends['mean'], label='Carros Reservados', c='r', ls='--')

# Curvas representando o intervalo de desvio padrão
ax2.plot(range(len(dfmediaR_Weekends['time'])), dfmediaR_Weekends['mean']+dfmediaR_Weekends['std'], alpha=150, c='#FA8072', ls='--')
ax2.plot(range(len(dfmediaR_Weekends['time'])), dfmediaR_Weekends['mean']-dfmediaR_Weekends['std'], alpha=150, c='#FA8072', ls='--')

# Modificando os labels das horas e das porcentagens
ax2.xaxis.set_ticks(np.arange(0, 1441, 120))
ax2.yaxis.set_ticks(np.arange(0, 110, 10))

fig.canvas.draw()

labels = [item.get_text() for item in ax2.get_xticklabels()]
labels = range(0,26,2)

ax2.set_xticklabels(labels)

# Eixo y de 0 a 100%
ax2.set_ylim([0,100])

# Legendas e label dos eixos
ax2.legend(bbox_to_anchor=(0.55, 0.99), loc=2, borderaxespad=0.1)
ax2.set_ylabel('Percentual')
ax2.set_xlabel('Horário')


plt.savefig('Viagens_sem_reduzir_v2.pdf')
