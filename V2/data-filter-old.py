
# coding: utf-8

# In[1]:

import pandas as pd
import datetime
import pytz

df = pd.read_csv('../../ModoApi_Data.csv')


# ## Filtrando e formatando os dados

# In[2]:

#Limpando dados
df.drop(['Unnamed: 0'], axis=1, inplace=True)
df = df[df['CarID'] != 'CarID']
df.dropna(thresh=9, inplace=True)
df.dropna(thresh=6, inplace=True)


# In[3]:

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
df['CaptureTime'] = pd.to_datetime(df['CaptureTime'])

df.drop(['LocationID', 'Duration', 'RequestDuration'], axis=1, inplace=True)

# Coletando os IDs dos carros
car_ids = []
for i in range(len(df)):
    if (df['CarID'].iloc[i] in car_ids):
        continue
    else:
        car_ids.append(df['CarID'].iloc[i])


# ## Funções para manipulação do tempo

# In[4]:

# Converte hora dada a time zone atual, a zona a ser convertida e a diferença de tempo
def convert_datetime_timezone(dt, tz1, tz2, str_diff):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.fromtimestamp(dt)
    dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    try:
        dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S"+str_diff)
    # Except para evitar um erro pela mudança de fuso horário
    except Exception as e:
        print(e)
        # Diminui 1 hora para se adaptar
        # dt = dt - datetime.timedelta(hours=1)
        dt = datetime.datetime.strptime(str(dt),"%Y-%m-%d %H:%M:%S"+'-08:00')
    
    dt = int(dt.timestamp())

    return dt


# In[5]:

# Faz a diferença entre duas horas dadas e retorna em minutos
def Hour_Diff(h1,h2):
    h1Aux = datetime.datetime.fromtimestamp(h1)
    h2Aux = datetime.datetime.fromtimestamp(h2)
    diff = abs((h1Aux - h2Aux)).total_seconds()/60
    
    return diff


# ## Filtro para classificação dos dados

# In[6]:

new_travel = []
cancel = []
parked = []
special_travel = []

for j in range(len(car_ids)):
    carID = car_ids[j]
    carDF = []
    
    carDF = df[df['CarID'] == carID]
    carDF = carDF.sort_values(by=['CaptureTime'])
    
    for i in range(1, len(carDF)):
        try:
            # Extração com base no Start Time
            # Convertendo todos os timestamps para o fuso horário de vancouver
            start_time_atual = int(carDF['StartTime'].iloc[i])
            start_time_atual = convert_datetime_timezone(start_time_atual, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            start_time_anterior = int(carDF['StartTime'].iloc[i-1])
            start_time_anterior = convert_datetime_timezone(start_time_anterior, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            request_start_atual = carDF['RequestStart'].iloc[i]
            request_start_atual = convert_datetime_timezone(request_start_atual, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            request_start_anterior = carDF['RequestStart'].iloc[i-1]
            request_start_anterior = convert_datetime_timezone(request_start_anterior, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            capture_timestamp = int(carDF['CaptureTime'].iloc[i].timestamp())
            capture_timestamp = convert_datetime_timezone(capture_timestamp, 'UTC', 'America/Vancouver', '-07:00')
            
            #Verifica se a coleta começou com o carro parado
            if (i == 1 and start_time_atual == request_start_atual):
                
                start_parked = capture_timestamp                
                
            
            # Verifica se a coleta começou com o carro andando
            if (i == 1 and start_time_atual > request_start_atual): 
                
                # Registra uma nova viagem
                new_travel.append([carID, capture_timestamp, start_time_atual, True])
            
            # Se o inicio do tempo de disponibilidade > tempo de requisição E estava Parado temos uma nova viagem.  
            elif (start_time_atual > request_start_atual and start_time_anterior == request_start_anterior):
                
                # Registra uma nova viagem
                new_travel.append([carID, capture_timestamp, start_time_atual, True])
                
                # Registra o final do tempo em que estava estacionado
                if (start_parked > 0):
                    parked.append([carID, start_parked, capture_timestamp])
                    start_parked = -1


            #Se o inicio do tempo de disponibilidade anterior < tempo de disponibilidade atual E está andando temos uma nova viagem/extensão.
            elif (start_time_anterior < start_time_atual and start_time_atual > request_start_atual):
                
                new_travel.append([carID, capture_timestamp, start_time_atual, False])

            
            # Se estava andando e agora está parado.
            if (start_time_atual == request_start_atual and start_time_anterior > request_start_anterior):
                
                # Inicio do tempo estacionado
                start_parked = capture_timestamp

                if(new_travel != []):
                   
                    # Se a diferença entre hora atual e o inicio da ultima viagem < 30 min => cancelamento
                    # Senão => Diminuição/Cancelamento
                    if (Hour_Diff(capture_timestamp, new_travel[-1][1]) < 30):
                        
                        cancel.append([carID, capture_timestamp, start_time_anterior, True])

                    #Tolerância de 20 min para dizer que foi uma diminuição ou cancelamento em vez de um termino de viagem
                    elif(Hour_Diff(capture_timestamp, new_travel[-1][2]) > 20):
                        
                        cancel.append([carID, capture_timestamp, start_time_anterior, False])

            
            # Se acontecer um aumento do tempo de diponibilidade enquanto está andando, ocorreu um cancelamento ou diminuição
            if (start_time_atual > request_start_atual and start_time_anterior > start_time_atual):
                
                cancel.append([carID, capture_timestamp, start_time_anterior, False])             
            
            
            # Extração com base no End Time
            end_time_atual = float(carDF['EndTime'].iloc[i])
            end_time_atual = convert_datetime_timezone(end_time_atual, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            end_time_anterior = float(carDF['EndTime'].iloc[i-1])
            end_time_anterior = convert_datetime_timezone(end_time_anterior, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            request_end_atual = carDF['RequestEnd'].iloc[i]
            request_end_atual = convert_datetime_timezone(request_end_atual, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            request_end_anterior = carDF['RequestEnd'].iloc[i-1]
            request_end_anterior = convert_datetime_timezone(request_end_anterior, 'America/Sao_Paulo', 'America/Vancouver','-07:00')
            
            # Se estava com um horário marcado de fim de disponibilidade e agora está livre até o dia seguinte houve um cancelamento
            if (end_time_anterior < request_end_anterior and end_time_atual == request_end_atual):
                
                cancel.append([carID, capture_timestamp, end_time_anterior, True])
                

            # Se a janela de disponibilidade diminuiu pelo end time foi agendada uma nova viagem/extensão
            if (end_time_anterior > end_time_atual and end_time_anterior < request_end_anterior):
                
                new_travel.append([carID, end_time_atual, end_time_anterior, False])
            
            # Se a janela de disponibilidade aumentou pelo end time ocorreu um cancelamento/diminuição 
            elif (end_time_anterior < end_time_atual and end_time_atual < request_end_atual):
                
                cancel.append([carID, capture_timestamp, end_time_anterior, False])
                
            # Se antes estava sem fim da janela de disponibilidade e agora end time < request_end
            # Temos uma nova viagem mas sem ter como dizer a sua duração
            if (end_time_anterior == request_end_anterior and end_time_atual < request_end_atual):
                
                special_travel.append([carID, capture_timestamp, end_time_atual])
                
                    
        except Exception as e:
            print('Loop:'+str(e))
            # Exception será gerada nos casos em que o carro não está disponível
            continue

dfTravels = pd.DataFrame(new_travel,columns=['car_id', 'start', 'end', 'only_new_reserves'])
dfCancel = pd.DataFrame(cancel, columns=['car_id', 'capture_time', 'previous_start', 'only_cancel'])
dfParked = pd.DataFrame(parked, columns=['car_id', 'start', 'end'])
dfSpecial_Travel = pd.DataFrame(special_travel, columns=['car_id', 'capture_time', 'start'])


dfTravels.to_csv('travels_sem_reduzir_v1.csv', index=False, encoding='utf-8')
dfCancel.to_csv('cancel_sem_reduzir_v1.csv', index=False, encoding='utf-8')
dfParked.to_csv('parked_sem_reduzir_v1.csv', index=False, encoding='utf-8')
