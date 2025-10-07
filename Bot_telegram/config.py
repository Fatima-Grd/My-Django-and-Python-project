import os

API_TOKEN = os.environ.get('TOKEN')    
CHANNEL_CID = int(os.environ.get('CHANNEL_CID'))             
PRODUCTS_CHANNEL = int(os.environ.get('PRODUCTS_CHANNEL'))


admins = eval(os.environ.get('admins'))           



config = {'user': os.environ.get('database_user'), 'password': os.environ.get('database_pass'),
           'host': os.environ.get('host'), 'database': os.environ.get('database_name')}

DATABASE = os.environ.get('database_name')


