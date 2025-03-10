from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from ..constants.database import DATABASE_URL
from .agent import agent_repository

class ToolRepository:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def create_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tool record or update if exists"""
        # First check if tool with same name exists
        check_query = "SELECT id FROM tools WHERE name = %(name)s;"
        self.cursor.execute(check_query, tool_data)
        existing_tool = self.cursor.fetchone()

        if existing_tool:
            # Update existing tool
            query = """
                UPDATE tools 
                SET description = %(description)s,
                    file_content = %(file_content)s,
                    updated_at = NOW()
                WHERE name = %(name)s
                RETURNING id, name, description, file_content, created_at, updated_at;
            """
        else:
            # Insert new tool
            query = """
                INSERT INTO tools (
                    name, 
                    description, 
                    file_content,
                    created_at, 
                    updated_at
                )
                VALUES (
                    %(name)s, 
                    %(description)s, 
                    %(file_content)s,
                    NOW(), 
                    NOW()
                )
                RETURNING id, name, description, file_content, created_at, updated_at;
            """
        print(f"Executing SQL query: {self.cursor.mogrify(query, tool_data).decode()}")

        self.cursor.execute(query, tool_data)
        self.conn.commit()
        return self.cursor.fetchone()

    def get_tool(self, tool_id: int) -> Dict[str, Any]:
        """Get an tool by ID"""
        query = "SELECT * FROM tools WHERE id = %s;"
        self.cursor.execute(query, (tool_id,))
        return self.cursor.fetchone()

    def update_tool(self, tool_id: int, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing tool"""
        query = """
            UPDATE tools 
            SET name = %(name)s,
                description = %(description)s,
                file_content = %(file_content)s,
                updated_at = NOW()
            WHERE id = %(id)s
            RETURNING id, name, description, file_content, created_at, updated_at;
        """
        tool_data['id'] = tool_id
        self.cursor.execute(query, tool_data)
        self.conn.commit()
        return self.cursor.fetchone()

    def delete_tool(self, tool_name: str) -> bool:
        """Delete an tool"""
        agents = agent_repository.list_agents_by_tool(tool_name)
        if len(agents) > 0:
            raise Exception(f"Tool {tool_name} is used by {", ".join([agent['name'] for agent in agents])} agent(s)")
        query = "DELETE FROM tools WHERE name = %s;"
        self.cursor.execute(query, (tool_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def list_tools(self) -> list[Dict[str, Any]]:
        """List all tools"""
        query = "SELECT * FROM tools ORDER BY created_at DESC;"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def __del__(self):
        """Close database connection when object is destroyed"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

tool_repository = ToolRepository()

