import pandas as pd


def make_flat_table(data):
    data = data.dropna(axis=1, how="all")
    data = data.drop(index=data.index[:3])
    data.index = range(len(data.index)) # После удаления строк удаляются и индексы, поэтому сбивается нумерация, исправляем
    data.columns = ['name', 'art', 'sale_date', 'region', 'client_type', 'manager', 'client', 'quantity', 'sale_value', 'cost']
    data['art'] = data['art'].apply(lambda x: str(x) if pd.notnull(x) else x)  # convert all sku to str
    stores = [
        "Склад Новосибирск", "Оптовый Кемерово", "Склад Новосибирск Брак", "Брак Кемерово", 
        "Оптовый", "Выставочный Кемерово", "Выставочный Новосибирск", "Склад Новосибирск Транзит",
        "Склад Новосибирск (АМС)", "Оптовый Кемерово (АМС)", "Склад Новосибирск Брак (АМС)", "Брак Кемерово (АМС)", 
        "Оптовый (АМС)", "Выставочный Кемерово (АМС)", "Выставочный Новосибирск (АМС)", "Склад Новосибирск Транзит (АМС)",
        ]
    skus = list(data.art.dropna().unique())

    data['store'] = ""
    data['SKU'] = ""
    for item in range(data.index[-1]):
        #print(item)
        if data.loc[item, 'name'] in stores:
            data.loc[item, "store"] = data.loc[item, "name"]
        else:
            if item != 0:
                data.loc[item, "store"] = data.loc[item - 1, "store"]
            
    # Заполняем колонку "регион", 'клиент'
    for item in range(data.index[-1]):
        #print(item)
        if data.loc[item, 'art'] in skus:
            data.loc[item, "SKU"] = data.loc[item, "art"]
        else:
            if item != 0:
                data.loc[item, "SKU"] = data.loc[item - 1, "SKU"]

    data = data[['sale_date', 'quantity', 'store', 'SKU', 'cost', 'sale_value', 'client_type', 'region', 'manager']]
    data['cost'] = data['cost'].fillna(0) 
    data['sale_value'] = data['sale_value'].fillna(0) 
    data = data.dropna(subset=['client_type'])
    data["sale_date"] = pd.to_datetime(data['sale_date'], errors='coerce', format='%d.%m.%Y  %H:%M:%S').dt.date
    data.index = range(len(data.index)) # После удаления строк удаляются и индексы, поэтому сбивается нумерация, исправляем
    data = data.replace('Оптовый Кемерово', 'Kemerovo Main')
    data = data.replace('Оптовый', 'Kemerovo Main')
    data = data.replace('Склад Новосибирск', 'Novosibirsk Main')
    data = data.replace('Склад Новосибирск Брак', 'Novosibirsk Defect')
    data = data.replace('Брак Кемерово', 'Kemerovo Defect')
    data = data.replace('Выставочный Кемерово', 'Kemerovo Main')
    data = data.replace('Выставочный Новосибирск', 'Novosibirsk Main')
    data = data.replace('Склад Новосибирск Транзит', 'Novosibirsk Main')

    data = data.replace('Выставочный Кемерово (АМС)', 'Kemerovo Main')
    data = data.replace('Выставочный Новосибирск (АМС)', 'Novosibirsk Main')
    data = data.replace('Оптовый Кемерово (АМС)', 'Kemerovo Main')
    data = data.replace('Оптовый (АМС)', 'Kemerovo Main')
    data = data.replace('Склад Новосибирск (АМС)', 'Novosibirsk Main')
    data = data.replace('Склад Новосибирск Брак (АМС)', 'Novosibirsk Defect')
    data = data.replace('Брак Кемерово (АМС)', 'Kemerovo Defect')
    data = data.replace('Склад Новосибирск Транзит (АМС)', 'Novosibirsk Main')
    
    data['quantity']   = data['quantity'].astype('Int32')
    data['cost']       = data['cost'].astype('float64')
    data['sale_value'] = data['sale_value'].astype('float64')

    return data


def make_flat_table_inv(data):
    data = data.dropna(axis=1, how="all")
    data = data.drop(index=data.index[:3])
    data.index = range(len(data.index)) # После удаления строк удаляются и индексы, поэтому сбивается нумерация, исправляем
    data.columns = ['name', 'art', 'beg', 'in', 'out', 'end']
    skus = list(data.art.dropna().unique())
    data['store'] = ""
    data['SKU'] = ""
    stores = [
        "Склад Новосибирск", "Оптовый Кемерово", "Склад Новосибирск Брак", "Брак Кемерово", 
        "Оптовый", "Выставочный Кемерово", "Выставочный Новосибирск", "Склад Новосибирск Транзит",
        "Склад Новосибирск (АМС)", "Оптовый Кемерово (АМС)", "Склад Новосибирск Брак (АМС)", "Брак Кемерово (АМС)", 
        "Оптовый (АМС)", "Выставочный Кемерово (АМС)", "Выставочный Новосибирск (АМС)", "Склад Новосибирск Транзит (АМС)",
        ]

    ##### Find the most recent date
    # column_with_dates = list(data.name.dropna().unique())
    # data_str = " ".join(column_with_dates)
    # dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", data_str)

    # # Convert dates to pandas datetime
    # dates = pd.to_datetime(dates, format="%d.%m.%Y")

    # # Find the most recent date
    # most_recent_date = dates.max().strftime('%d.%m.%Y')
    #####################################################

    # fill sku
    for item in range(data.index[-1]):
        if data.loc[item, 'art'] in skus:
            data.loc[item, "SKU"] = data.loc[item, "art"]
        else:
            if item != 0:
                data.loc[item, "SKU"] = data.loc[item - 1, "SKU"]
                
    for item in range(data.index[-1]):
        if data.loc[item, 'name'] in stores:
            data.loc[item, "store"] = data.loc[item, "name"]
        else:
            if item != 0:
                data.loc[item, "store"] = data.loc[item - 1, "store"]

    data['in']  = data['in'].fillna(0)
    data['out'] = data['out'].fillna(0)

    # for item in range(1, data.index[-1]):
    #     is_next_item_date = False
    #     next_item = str(data.loc[item+1, 'name'])
    #     pattern = r"\d{2}\.\d{2}\.\d{4}"
    #     if re.fullmatch(pattern, next_item):
    #         is_next_item_date = True          

    #     if pd.isna(data.loc[item, 'name']) and data.loc[item-1, 'name'] in stores and is_next_item_date == False:
    #         data.loc[item, 'name'] = most_recent_date
    #     elif pd.isna(data.loc[item, 'name']) and data.loc[item-1, 'name'] in stores:
    #         if pd.isna(data.loc[item, 'beg']):
    #             data.loc[item+1, 'beg'] = 0
    #         else:
    #             data.loc[item+1, 'beg'] = data.loc[item, 'beg']
    #     elif not pd.isna(data.loc[item, 'name']) and data.loc[item-1, 'name'] in stores:
    #         data.loc[item, 'beg'] = 0
    #         data.loc[item, 'end'] = data.loc[item, 'beg'] + data.loc[item, 'in'] - data.loc[item, 'out']        
    #     else:
    #         data.loc[item, 'end'] = data.loc[item, 'beg'] + data.loc[item, 'in'] - data.loc[item, 'out']

    # for item in range(data.index[-1]):
    #     if pd.isna(data.loc[item, 'beg']):
    #         data.loc[item, 'beg'] = data.loc[item-1, 'end']
    #         data.loc[item, 'end'] = data.loc[item, 'beg'] + data.loc[item, 'in'] - data.loc[item, 'out']

    data = data.dropna(subset=['name'])
    df = data[~data['art'].isin(skus)]
    df = df[~df['name'].isin(stores)]
    df = df[~df['name'].isin(["Итого"])]
    df = df[['name', 'beg', 'end', 'store', 'SKU']]
    df = df.rename(columns={'name': 'date'})
    df["date"] = pd.to_datetime(df['date'], errors='coerce', format='%d.%m.%Y').dt.date
    df = df.replace('Оптовый Кемерово', 'Kemerovo Main')
    df = df.replace('Оптовый', 'Kemerovo Main')
    df = df.replace('Склад Новосибирск', 'Novosibirsk Main')
    df = df.replace('Склад Новосибирск Транзит', 'Novosibirsk Transit')
    df = df.replace('Склад Новосибирск Резерв', 'Novosibirsk Reserve')
    df = df.replace('Склад транзит Кемерово-Новосибирск', 'Kemerovo Transit')
    df = df.replace('Оптовый Кемерово (АМС)', 'Kemerovo Main')
    df = df.replace('Оптовый (АМС)', 'Kemerovo Main')
    df = df.replace('Склад Новосибирск (АМС)', 'Novosibirsk Main')
    df = df.replace('Склад Новосибирск Транзит (АМС)', 'Novosibirsk Transit')
    df = df.replace('Склад Новосибирск Резерв (АМС)', 'Novosibirsk Reserve')
    df = df.replace('Склад транзит Кемерово-Новосибирск (АМС)', 'Kemerovo Transit')

    df['end'] = df['end'].astype('Int32')  
    data.index = range(len(data.index)) # После удаления строк удаляются и индексы, поэтому сбивается нумерация, исправляем
    df = df.query('store != ""')
    df = df.fillna(0)
    return df