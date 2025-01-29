from typing import Dict, List, Optional
import httpx
from datetime import datetime, timedelta
from ..llm.react import ReActAgent
from ..llm.query import QueryAgent

class PulseAPI:
    def __init__(self):
        self.base_url = "https://pulse.bi.mypaytm.com/api/v1"
        self.druid_url = "https://paytmprod.implycloud.com/p/3f93cc1e-b9d1-4bf8-9a97-87392e98cfc6/console/druid/druid/v2"
        self.react_agent = ReActAgent()
        self.query_agent = QueryAgent()
        
    async def list_funnels(self) -> List[Dict]:
        """
        Fetch list of available funnels from Pulse
        """
        url = f"{self.base_url}/chart/list/funnelhub_viz"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                self.react_agent.log_error(f"Failed to fetch funnels: {str(e)}")
                raise

    async def get_funnel_data(self, slice_id: int, time_range: Optional[Dict] = None) -> Dict:
        """
        Fetch funnel data for a specific slice ID with ReAct agent integration
        """
        url = f"{self.base_url}/chart/data"
        
        if not time_range:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            time_range = {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }

        payload = {
            "slice_id": slice_id,
            "form_data": {
                "slice_id": slice_id,
                "viz_type": "funnelhub_viz",
                "time_range": time_range,
                "adhoc_filters": [],
                "extra_filters": []
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                self.react_agent.log_error(f"Failed to fetch funnel data: {str(e)}")
                raise

    async def query_druid(self, query: Dict) -> Dict:
        """
        Execute a Druid query with query agent integration
        """
        try:
            # Let query agent process and optimize the query
            processed_query = self.query_agent.process_query(query)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.druid_url, json=processed_query)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.react_agent.log_error(f"Druid query failed: {str(e)}")
            raise

    async def get_prepaid_funnel_metrics(self, time_range: Optional[Dict] = None) -> Dict:
        """
        Get metrics for the RU Prepaid Realtime funnel with analysis
        """
        PREPAID_FUNNEL_ID = 7036
        try:
            funnel_data = await self.get_funnel_data(PREPAID_FUNNEL_ID, time_range)
            
            # Use ReAct agent to analyze the funnel data
            analysis = self.react_agent.analyze_funnel_metrics(funnel_data)
            
            return {
                "raw_data": funnel_data,
                "analysis": analysis,
                "metrics": {
                    "conversion_rate": analysis.get("conversion_rate"),
                    "drop_off_points": analysis.get("drop_off_points"),
                    "recommendations": analysis.get("recommendations")
                }
            }
        except Exception as e:
            self.react_agent.log_error(f"Failed to analyze prepaid funnel: {str(e)}")
            raise

    async def get_funnel_stages(self, funnel_id: int) -> List[Dict]:
        """
        Get the stages configuration for a specific funnel with ReAct agent insights
        """
        try:
            funnel_data = await self.get_funnel_data(funnel_id)
            stages = funnel_data.get("form_data", {}).get("stages", [])
            
            # Use ReAct agent to analyze stages and provide insights
            stage_insights = self.react_agent.analyze_funnel_stages(stages)
            
            return {
                "stages": stages,
                "insights": stage_insights,
                "optimization_suggestions": stage_insights.get("optimization_suggestions")
            }
        except Exception as e:
            self.react_agent.log_error(f"Failed to analyze funnel stages: {str(e)}")
            raise 