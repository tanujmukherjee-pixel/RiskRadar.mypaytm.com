from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from ..constants.database import DATABASE_URL

class AgentRepository:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent record or update if exists"""
        # First check if agent with same name exists
        check_query = "SELECT id FROM agents WHERE name = %(name)s;"
        self.cursor.execute(check_query, agent_data)
        existing_agent = self.cursor.fetchone()

        if existing_agent:
            # Update existing agent
            query = """
                UPDATE agents 
                SET description = %(description)s,
                    tools = %(tools)s,
                    system_prompt = %(system_prompt)s,
                    approach_prompt = %(approach_prompt)s,
                    output_prompt = %(output_prompt)s,
                    updated_at = NOW()
                WHERE name = %(name)s
                RETURNING id, name, description, tools, system_prompt, approach_prompt, output_prompt, created_at, updated_at;
            """
        else:
            # Insert new agent
            query = """
                INSERT INTO agents (
                    name, 
                    description, 
                    tools, 
                    system_prompt,
                    approach_prompt,
                    output_prompt,
                    created_at, 
                    updated_at
                )
                VALUES (
                    %(name)s, 
                    %(description)s, 
                    %(tools)s,
                    %(system_prompt)s,
                    %(approach_prompt)s, 
                    %(output_prompt)s,
                    NOW(), 
                    NOW()
                )
                RETURNING id, name, description, tools, system_prompt, approach_prompt, output_prompt, created_at, updated_at;
            """
        print(f"Executing SQL query: {self.cursor.mogrify(query, agent_data).decode()}")

        self.cursor.execute(query, agent_data)
        self.conn.commit()
        return self.cursor.fetchone()

    def get_agent(self, agent_id: int) -> Dict[str, Any]:
        """Get an agent by ID"""
        query = "SELECT * FROM agents WHERE id = %s;"
        self.cursor.execute(query, (agent_id,))
        return self.cursor.fetchone()

    def update_agent(self, agent_id: int, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent"""
        query = """
            UPDATE agents 
            SET name = %(name)s,
                description = %(description)s,
                tools = %(tools)s,
                system_prompt = %(system_prompt)s,
                approach_prompt = %(approach_prompt)s,
                output_prompt = %(output_prompt)s,
                updated_at = NOW()
            WHERE id = %(id)s
            RETURNING id, name, description, tools, system_prompt, approach_prompt, output_prompt, created_at, updated_at;
        """
        agent_data['id'] = agent_id
        self.cursor.execute(query, agent_data)
        self.conn.commit()
        return self.cursor.fetchone()

    def delete_agent(self, agent_name: str) -> bool:
        """Delete an agent"""
        query = "DELETE FROM agents WHERE name = %s;"
        self.cursor.execute(query, (agent_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def list_agents(self) -> list[Dict[str, Any]]:
        """List all agents"""
        query = "SELECT * FROM agents ORDER BY created_at DESC;"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def list_agents_by_tool(self, tool_name: str) -> list[Dict[str, Any]]:
        """List all agents by tool"""
        query = "SELECT * FROM agents WHERE tools LIKE %s ORDER BY created_at DESC;"
        self.cursor.execute(query, (f"%{tool_name}%",))
        return self.cursor.fetchall()

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

def get_repository():
    return AgentRepository()