import pyodbc
import json
import datetime
from templates import get_template


def load_lookups(lookup_file):
    with open(lookup_file,'r') as read_file:
        return json.load(read_file)

class awos_generator():
    def __init__(self, conn, sql, template, output):
        self.conn = conn
        self.sql = sql
        self.template = template
        self.output = output

    def execute_query(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.sql)
        
        self.columns = [column[0] for column in self.cursor.description]

    def parse_data(self):
        self.data = {}

        for row in self.cursor:
            for column in range(0,len(self.columns)):
                self.data[self.columns[column]] = row[column]

    def format_time(self):
        self.data['DATESTAMP'] = self.data['DATESTAMP'].strftime('%d/%m/%Y %H:%M:%S')

    def lookupweather(self, sensor):
        try: self.data[sensor] = weatherlookup[sensor]
        except KeyError: self.data[sensor] = "No significant weather observed"

    def set_runway(self):
        if self.data['RIU'] == '1': self.data['RIU'] = '08'
        elif self.data['RIU'] == '2': self.data['RIU'] = '26'
        else: print("ERROR! - Invalid ruway value")

    def render(self):
        self.rendered = get_template(self.template).render(self.data)

    def write(self):
        file = open(self.output, "w")
        file.write(self.rendered)
        file.close


# SQL Server connection config
conn = pyodbc.connect('DRIVER={SQL Server};'
                     'SERVER=172.18.0.5;'
                     'DATABASE=airport2020_supp;'
                     'UID=awosdata;'
                     'PWD=Airport1937!;')

# SQL Query to selct the most recent dataset
sql = """/****** Script for SelectMostRecent command from SSMS  ******/
SELECT TOP (1) [ID]
      ,[DATESTAMP]
      ,[DP_1_A]
      ,[DP_1_C]
      ,[RH_A]
      ,[RH_C]
      ,[TA_A]
      ,[TA_C]
      ,[BGL_A]
      ,[BGL_C]
      ,[MORKM_A]
      ,[MORKM_B]
      ,[MORKM_C]
      ,[REWX_A]
      ,[REWX_C]
      ,[WX_A]
      ,[WX_C]
      ,[D_A]
      ,[D_C]
      ,[S_A]
      ,[S_C]
      ,[MET_QFE_A]
      ,[MET_QFE_C]
      ,[ANGLE_FLASH1_B]
      ,[ANGLE_FLASH2_B]
      ,[ANGLE_FLASH3_B]
      ,[ANGLE_FLASH4_B]
      ,[DIST_FLASH1_B]
      ,[DIST_FLASH2_B]
      ,[DIST_FLASH3_B]
      ,[DIST_FLASH4_B]
      ,[NUM_FLASHES_B]
      ,[TS_B]
      ,[CLD1_A]
      ,[CLD1_C]
      ,[CLD2_A]
      ,[CLD2_C]
      ,[CLD3_A]
      ,[CLD3_C]
      ,[VER_VIS_A]
      ,[VER_VIS_C]
      ,[RIU]
  FROM [Airport2020_SUPP].[dbo].[JER_AWOS]
  order by datestamp desc  """

template = 'awos.html'
output = 'output/awos.html'

weatherlookup = load_lookups('weatherlookup.json')

awos = awos_generator(conn, sql, template, output)

awos.execute_query()
awos.parse_data()
awos.format_time()
awos.lookupweather('WX_A')
awos.lookupweather('WX_C')
awos.set_runway()
awos.render()
awos.write()