import requests
import os
import psycopg2

# Define the API URL
url = 'https://developer.nrel.gov/api/alt-fuel-stations/v1.json'
# https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/
# https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/all/
api_key = os.getenv('NREL_ENERGY_TOKEN')
pg_un = os.getenv('PG_UN')
pg_pw = os.getenv('PG_PW')
pg_host = os.getenv('PG_HOST')
pg_port = os.getenv('PG_PORT')
pg_db = os.getenv('PG_DB')
params = {
    'fuel_type': 'ELEC',
    'access': 'public',
    'limit': 'all',
    'country': 'US',
    'state': 'CO',
    'api_key': api_key,
}

db_conn = psycopg2.connect(
            user=pg_un,
            password=pg_pw,
            host=pg_host,
            port=pg_port,
            database=pg_db
        )

def fetch_data():    
    '''
    This is a test function to make sure the API is working
    '''
    # Make the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Get JSON from response
        data = response.json()
        #print(data)
        for stat in data['fuel_stations']:
            print(f"id: {stat['id']}, name: {stat['station_name']}")
    else:
        print('Failed to retrieve data:', response.status_code)
    
def refresh_db():
    '''
    This is the real function to hit the API, grab all data, and load it into the pg db
    '''
    try:
        cursor = db_conn.cursor()
        # postgres datatypes: https://www.postgresql.org/docs/current/datatype.html 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evses (
                id INTEGER PRIMARY KEY,
                facility_type VARCHAR(100),
                restricted_access BOOLEAN,
                updated_at TIMESTAMPTZ,
                date_last_confirmed DATE,
                open_date DATE,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                ev_pricing VARCHAR(255),
                ev_network_web VARCHAR(255),
                ev_network VARCHAR(255),
                ev_connector_types VARCHAR(255),
                ev_level1_evse_num INTEGER,
                ev_level2_evse_num INTEGER,
                ev_dc_fast_num INTEGER,
                ev_other_evse VARCHAR(255),
                access_code VARCHAR(50),
                expected_date DATE,
                status_code VARCHAR(10),
                country VARCHAR(10),
                zip VARCHAR(10),
                state VARCHAR(10),
                city VARCHAR(50),
                street_address VARCHAR(255),
                station_name VARCHAR(255)
            )
        """)
        
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
        else:
            print('Failed to retrieve data:', response.status_code)
        
        
        insert_stmt = """INSERT INTO evses 
            (id, facility_type, restricted_access, 
            updated_at, date_last_confirmed, open_date, 
            latitude, longitude, ev_pricing, 
            ev_network_web, ev_network, ev_connector_types, 
            ev_level1_evse_num, ev_level2_evse_num, ev_dc_fast_num, 
            ev_other_evse, access_code, expected_date, 
            status_code, country, zip, state, city, 
            street_address, station_name) 
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (id) DO UPDATE SET
                facility_type = EXCLUDED.facility_type,
                restricted_access = EXCLUDED.restricted_access,
                updated_at = EXCLUDED.updated_at,
                date_last_confirmed = EXCLUDED.date_last_confirmed,
                open_date = EXCLUDED.open_date,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                ev_pricing = EXCLUDED.ev_pricing,
                ev_network_web = EXCLUDED.ev_network_web,
                ev_network = EXCLUDED.ev_network,
                ev_connector_types = EXCLUDED.ev_connector_types,
                ev_level1_evse_num = EXCLUDED.ev_level1_evse_num,
                ev_level2_evse_num = EXCLUDED.ev_level2_evse_num,
                ev_dc_fast_num = EXCLUDED.ev_dc_fast_num,
                ev_other_evse = EXCLUDED.ev_other_evse,
                access_code = EXCLUDED.access_code,
                expected_date = EXCLUDED.expected_date,
                status_code = EXCLUDED.status_code,
                country = EXCLUDED.country,
                zip = EXCLUDED.zip,
                state = EXCLUDED.state,
                city = EXCLUDED.city,
                street_address = EXCLUDED.street_address,
                station_name = EXCLUDED.station_name
            """
                
        selected_data = [(stat['id'], stat['facility_type'], stat['restricted_access'], 
                          stat['updated_at'], stat['date_last_confirmed'], stat['open_date'], 
                          stat['latitude'], stat['longitude'], stat['ev_pricing'], 
                          stat['ev_network_web'], stat['ev_network'], 
                          stat['ev_connector_types'], stat['ev_level1_evse_num'], stat['ev_level2_evse_num'], 
                          stat['ev_dc_fast_num'], stat['ev_other_evse'], stat['access_code'], 
                          stat['expected_date'], stat['status_code'], stat['country'], 
                          stat['zip'], stat['state'], stat['city'], stat['street_address'], 
                          stat['station_name']) for stat in data['fuel_stations']]
        cursor.executemany(insert_stmt, selected_data)
        
        db_conn.commit()
        print("Data inserted successfully")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL: ", error)
    finally:
        # closing database connection.
        if db_conn:
            cursor.execute("SELECT * FROM evses ORDER BY updated_at DESC LIMIT 10")  # Adjust table name and limit as needed
            sampleRows = cursor.fetchall()
            for row in sampleRows:
                print(row)
            
            cursor.close()
            db_conn.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    print("running nrel_fetch.py")
    
    #fetch_data()
    
    refresh_db()
    