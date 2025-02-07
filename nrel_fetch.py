import requests
import os
import psycopg2
from datetime import date

TODAY = date.today()
# Define the API URL
URL = 'https://developer.nrel.gov/api/alt-fuel-stations/v1.json'
# https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/
# https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/all/

STATE_CODES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]
api_key = os.getenv('NREL_ENERGY_TOKEN')
pg_un = os.getenv('PG_UN')
pg_pw = os.getenv('PG_PW')
pg_host = os.getenv('PG_HOST')
pg_port = os.getenv('PG_PORT')
pg_db = os.getenv('PG_DB')

def fetch_data(conn_params):    
    '''
    This is a test function to make sure the API is working
    '''
    # Make the GET request
    response = requests.get(URL, params=conn_params)

    # Check if the request was successful
    if response.status_code == 200:
        # Get JSON from response
        data = response.json()
        #print(data)
        for stat in data['fuel_stations']:
            print(f"id: {stat['id']}, name: {stat['station_name']}")
    else:
        print('Failed to retrieve data:', response.status_code)
    
    
def update_date_refreshed(conn_params, today):
    db_conn = psycopg2.connect(
        user=pg_un,
        password=pg_pw,
        host=pg_host,
        port=pg_port,
        database=pg_db
    )
    try:
        cursor = db_conn.cursor()
        
        # SQL update statement
        update_stmt = "UPDATE evses SET date_refreshed = %s"
        # Execute the SQL statement
        cursor.execute(update_stmt, (today,))
        
        # Commit the changes
        db_conn.commit()
        print("Date refreshed updated successfully")
    except Exception as error:
        print("Error while updating date_refreshed:", error)
        db_conn.rollback()
    finally:
        # Close the cursor and connection
        cursor.close()
        db_conn.close()

    
def refresh_db(conn_params):
    '''
    This is the real function to hit the API, grab all data, and load it into the pg db
    '''
    db_conn = psycopg2.connect(
        user=pg_un,
        password=pg_pw,
        host=pg_host,
        port=pg_port,
        database=pg_db
    )
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
                plugs_num INTEGER,
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
                station_name VARCHAR(255),
                date_refreshed DATE
            )
        """)
        print("getting json...")
        response = requests.get(URL, params=conn_params)
        if response.status_code == 200:
            data = response.json()
            print("data retrieved successfully")
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
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
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
                
        print("parsing json...")
        selected_data = [(stat['id'], stat['facility_type'], stat['restricted_access'], 
                          stat['updated_at'], stat['date_last_confirmed'], stat['open_date'], 
                          stat['latitude'], stat['longitude'], stat['ev_pricing'], 
                          stat['ev_network_web'], stat['ev_network'], 
                          stat['ev_connector_types'], stat['ev_level1_evse_num'], stat['ev_level2_evse_num'], 
                          stat['ev_dc_fast_num'], stat['ev_other_evse'], stat['access_code'], 
                          stat['expected_date'], stat['status_code'], stat['country'], 
                          stat['zip'], stat['state'], stat['city'], stat['street_address'], 
                          stat['station_name']) for stat in data['fuel_stations']]
        print("executing refresh commands...")
        cursor.executemany(insert_stmt, selected_data)
        
        db_conn.commit()
        print(f"{len(selected_data)} rows inserted successfully")
    except Exception as error: #(Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL: ", error)
        db_conn.rollback()
    finally:
        if db_conn:
            cursor.close()
            db_conn.close()
            print("PostgreSQL connection is closed")
        

def execute_sql_commands(conn_params, commands):
    # Connect to the PostgreSQL database
    db_conn = psycopg2.connect(
        user=pg_un,
        password=pg_pw,
        host=pg_host,
        port=pg_port,
        database=pg_db
    )
    cursor = db_conn.cursor()
    try:
        # Execute each command from the list
        for command in commands:
            print(f"executing sql commands: {commands[0:15]}...")
            cursor.execute(command)
        db_conn.commit()  # Commit the changes
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        db_conn.rollback()  # Rollback in case of error
    finally:
        cursor.close()
        db_conn.close()

if __name__ == "__main__":
    print("running nrel_fetch.py")
    params = {
        'fuel_type': 'ELEC',
        'access': 'public',
        'limit': 'all',
        'country': 'US',
        'api_key': api_key,
    }
    
    print("refreshing db...")
    refresh_db(params)
    
    print("creating connector_types table...")
    cmds = """
        CREATE TABLE IF NOT EXISTS public.ev_connector_types (
            id SERIAL PRIMARY KEY,
            evse_id INTEGER NOT NULL,
            connector_type VARCHAR(255),
            FOREIGN KEY (evse_id) REFERENCES public.evses (id)
        );
    """
    execute_sql_commands(params, [cmds])

    print("\nsplitting connector types...")
    cmds = """
        INSERT INTO public.ev_connector_types (evse_id, connector_type)
        SELECT id, unnest(string_to_array(regexp_replace(ev_connector_types, '[{}]', '', 'g'), ',')) AS connector_type
        FROM public.evses;
    """
    execute_sql_commands(params, [cmds])
    
    print("\nadding num_plugs column...")
    cmds = """
        ALTER TABLE evses ADD COLUMN IF NOT EXISTS plugs_num INTEGER;
        UPDATE evses SET plugs_num = COALESCE(ev_level1_evse_num, 0) + COALESCE(ev_level2_evse_num, 0) + COALESCE(ev_dc_fast_num, 0);
    """
    execute_sql_commands(params, [cmds])
    
    print("\nupdating date_refreshed...")
    update_date_refreshed(params, TODAY)
    
    print("nrel_fetch.py complete")
    
    
    