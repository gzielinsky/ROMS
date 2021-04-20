###################### ÍNDICE TEMPORAL MOTUCLIENT BASH #######

import datetime 
from datetime import date

####################### ENTRE COM A DATA DESEJADA ############

data_ini = datetime.date(day=10, month=4, year=2021)
data_end = datetime.date(day=12, month=4, year=2021)


#############################################################
today = date.today()
indice_ini = today-data_ini
indice_end = today-data_end

indice_ini=-indice_ini.days
indice_end=-indice_end.days
