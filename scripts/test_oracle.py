import oracledb
import config

connection = None
try:
    #config_dsn = '10.233.160.135:1521/SSR'
    connection = oracledb.connect(
        user=config.username,
        password=config.password,
        dsn=config.dsn)

    # show the version of the Oracle Database
    print(connection.version)
except oracledb.Error as error:
    print(error)
finally:
    # release the connection
    if connection:
        connection.close()
