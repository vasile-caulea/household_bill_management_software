import cx_Oracle

import gu


class DBConn:
    _instance = None
    __connection = None
    __cursor = None
    cx_Oracle.init_oracle_client(lib_dir=r'C:\instantclient_21_7')
    __dsn = cx_Oracle.makedsn('bd-dc.cs.tuiasi.ro', 1539, 'orcl')

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def connect(cls, usr, pasw):
        from gu import msgQueue
        try:
            print('Connecting to database...')
            cls.__connection: cx_Oracle.Connection = cx_Oracle.connect(user=usr, password=pasw, dsn=cls.__dsn,
                                                                       encoding="UTF-8")
            cls.__cursor: cx_Oracle.Cursor = cls.__connection.cursor()

            msgQueue.put(True)
            print('Connected to dabatabase successfully...')
        except cx_Oracle.DatabaseError as e:
            msgQueue.put(str(e))
            print(e)

    def execute(self, command) -> cx_Oracle.Cursor:
        try:
            value = self.__cursor.execute(command)
            gu.log_info('Success: ' + command)
            return value
        except cx_Oracle.DatabaseError as e:
            print('Error executing command:', command)
            print(e)
            raise e

    def commit(self):
        self.__connection.commit()
