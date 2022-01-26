import psycopg2
import config
from configparser import ConfigParser
def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def checkAccountInfo(query):
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(query)

        user_info_list = cursor.fetchall()
        conn.close()
        return user_info_list
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn.close()


def checkAccountExist(cursor, chat_id):
    cursor.execute("select username from accounts")
    user_list = cursor.fetchall()
    print(user_list)
    for user in user_list:
        if str(chat_id) in user:
            return True
    return False

def saveUserContractAddress(chat_id, contract_addr, amount):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        if checkAccountExist(cur,chat_id):
            print("user exist")
            sql = "UPDATE accounts SET contract="+ "'" +contract_addr + "'" +" WHERE username = '" + str(chat_id) + "';"
            print(sql)
            # execute the query
            cur.execute(sql)
            print("Table updated..")
        else:
            query = "INSERT INTO accounts (username, contract, amount) VALUES (%s, %s, %s);"
            data = (chat_id, contract_addr, amount)
            cur.execute(query, data)

            print("new user")
        conn.commit()
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')



def saveUserTimerInterval(chat_id, timer):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if checkAccountExist(cur,chat_id):
            sql = "UPDATE accounts SET timer="+ "'" + timer + "'" +" WHERE username = '" + str(chat_id) + "';"
            cur.execute(sql)
        else:
            query = "INSERT INTO accounts (timer) VALUES (%s);"
            data = (chat_id, timer)
            cur.execute(query, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def saveUserAmount(chat_id, amount):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if checkAccountExist(cur,chat_id):
            sql = "UPDATE accounts SET amount="+ "'" + amount + "'" +" WHERE username = '" + str(chat_id) + "';"
            cur.execute(sql)
        else:
            query = "INSERT INTO accounts (amount) VALUES (%s);"
            data = (chat_id, amount)
            cur.execute(query, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def saveUserAlarmState(chat_id,  state):
    conn = None
    alarm_state = str(state)
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if checkAccountExist(cur,chat_id):
            sql = "UPDATE accounts SET active="+ "'" + alarm_state + "'" +" WHERE username = '" + str(chat_id) + "';"
            cur.execute(sql)
        else:
            query = "INSERT INTO accounts (active) VALUES (%s);"
            data = (chat_id, alarm_state)
            cur.execute(query, data)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()