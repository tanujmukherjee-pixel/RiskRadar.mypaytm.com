import psycopg2
from psycopg2.extras import RealDictCursor
from ..constants.database import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

class MultiAgentRepository:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def list_multi_agents(self):
        try:
            self.cursor.execute("SELECT * FROM multi_agents")
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching multi agents: {e}")
            return []
    

def get_repository():
    return MultiAgentRepository()
    
    
