import pyodbc
import json
import datetime
import logging

from templates import get_template


logging.basicConfig(format='[%(asctime)s.%(msecs)03d] - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.DEBUG)

def load_lookups(lookup_file):
    logging.info('Reading file %s', lookup_file)
    with open(lookup_file,'r') as read_file:
        logging.debug('DONE!')
        return json.load(read_file)

class awos_generator():
    def __init__(self, conn, sql, template, output):
        self.conn = conn
        self.sql = sql
        self.template = template
        self.output = output

    def execute_query(self):
        logging.info('Querying SQL Database')
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.sql)
        
        self.columns = [column[0] for column in self.cursor.description]
        logging.debug('DONE!')

    def parse_data(self):
        self.data = {}

        for row in self.cursor:
            for column in range(0,len(self.columns)):
                self.data[self.columns[column]] = row[column]

    # Format last server refresh time into the format dd/mm/yy HH:MM:SS
    def format_time(self):
        self.data['DATESTAMP'] = self.data['DATESTAMP'].strftime('%d/%m/%Y %H:%M:%S')

    # Lookup the provided weather code and convert it into a test description
    def lookupweather(self, sensor):
        logging.info('Looking up weather value for sensor %s', sensor)
        self.data[sensor] = self.data[sensor].strip()
        try: 
            weather_out = weatherlookup[self.data[sensor]]
            logging.debug("Value in '%s', Lookup value out '%s'", self.data[sensor], weather_out)
        except KeyError:
            weather_out = '-'
            logging.warning("Input value '%s' did not match a value in weatherlookup.json", self.data[sensor])

        self.data[sensor] = weather_out
        logging.debug('DONE!')

    # Replaces cloud value with a '-' when there are no clouds
    def zero_cloudheight(self, cloudfields):
        for cloudfield in cloudfields:
            if self.data[cloudfield] == '0': self.data[cloudfield] = '-'
    
    # Replaces boolean Runway 'RIU' value with the appropriate runway lable '08' or '26'
    def set_runway(self):
        if self.data['RIU'] == '1': self.data['RIU'] = '08'
        elif self.data['RIU'] == '2': self.data['RIU'] = '26'
        else: logging.error('Invalid runway value "%s", expected "1" or "2"', self.data['RIU'])

    def render(self):
        logging.info('Rendering output from template')
        self.rendered = get_template(self.template).render(self.data)
        logging.debug('DONE!')

    def write(self):
        logging.info('Writing output to file %s', self.output)
        file = open(self.output, "w")
        file.write(self.rendered)
        file.close
        logging.debug('DONE!')


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
awos.zero_cloudheight(['CLD1_A', 'CLD1_C', 'CLD2_A', 'CLD2_C', 'CLD3_A', 'CLD3_C'])
awos.set_runway()
awos.render()
awos.write()