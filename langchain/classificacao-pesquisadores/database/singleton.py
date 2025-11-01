import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extensions import connection
from psycopg2.extensions import cursor
from typing import Optional

class DatabaseConnection:
    """
    Classe Singleton para gerenciar
    uma conexão com o banco de dados PostgreSQL.
    
    Garante que apenas uma conexão esteja ativa por vez
    e tenta se reconectar automaticamente se a conexão for perdida.
    """
    
    # A única instância da classe
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[connection] = None
    _db_params: dict = {}
    
    def __new__(cls):
        """
        Implementa o padrão Singleton.
        Se a instância ainda não existe, ela é criada.
        """
        # Verifica se a instância ainda não foi criada
        if cls._instance is None:
            print("Criando nova instância Singleton 'DatabaseConnection'...")

            # Cria a nova instância
            cls._instance = super().__new__(cls)
            
            # Inicializa os atributos da instância na primeira vez
            cls._instance._connection = None
            
            # Carrega as variáveis de ambiente
            load_dotenv()
            cls._instance._db_params = {
                'host': 'localhost',
                'port': os.getenv('DB_PORT', 5432),
                'database': os.getenv('DB_NAME'),
                'user': os.getenv('DB_USERNAME'),
                'password': os.getenv('DB_SENHA')
            }
                    
        return cls._instance

    def _connect(self) -> Optional[connection]:
        """
        Método privado para estabelecer uma nova conexão.
        """
        try:
            self._connection = psycopg2.connect(**self._db_params)
            print("Nova conexão com o PostgreSQL estabelecida.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Erro ao conectar ao PostgreSQL: {error}")
            self._connection = None

    def get_connection(self):
        """
        Método público para obter a conexão com o banco de dados.

        Verifica se a conexão existe ou se foi fechada.
        Se necessário, tenta (re)conectar.
        """
        # Verifica se a conexão não existe (None) ou se foi fechada (conn.closed != 0)
        if self._connection is None or self._connection.closed != 0:
            print("Conexão inexistente ou fechada. Tentando conectar...")
            self._connect()
        
        # Opcional: Ping para garantir que a conexão está realmente viva.
        if self._connection:
            try:
                # Usar um cursor para verificar a conexão
                with self._connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except psycopg2.OperationalError:
                # A conexão foi perdida (ex: rede caiu, banco reiniciou)
                print("Conexão perdida (falha no ping). Tentando reconectar...")
                self._connect()

        return self._connection

    def close(self):
        """
        Fecha a conexão se ela estiver aberta.
        """
        if self._connection and self._connection.closed == 0:
            self._connection.close()
            print("Conexão com o PostgreSQL fechada.")
            self._connection = None # Garante que a próxima chamada crie uma nova conexão