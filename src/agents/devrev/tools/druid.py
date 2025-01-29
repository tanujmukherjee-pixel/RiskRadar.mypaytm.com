import requests
from datetime import datetime
from dateutil import parser
import pandas as pd
from ....utils.api import post_request, get_request
import json
import urllib.parse
import matplotlib.pyplot as plt
from typing import List, Dict, Union
import numpy as np
import os

def get_all_funnels():
    """
    Fetches all the funnels from the druid
    """
    headers = {
            "Cookie": "_clck=1upy6g3%7C2%7Cfsx%7C0%7C1833; session=.eJwtkUuP2jAYRf9K5TWtbMfxg11KQyg00CQzA2lVoc-xTTKFBOVFYTT_vZHa5ZXu4txz39DRtbYr0bxvBztDx8qgOQLsEw7S-EJjhanPQehCF9wZBr7g4FzBFDg1tZSxnuOWK86xpAUTknpYEzDUWmIoFIQTyQVhhQDATFgsmWQaF74h2KPGV5hh4YivCzz1idSaGjRD56aAs51YbD2lBoZ-YnxDH3o0_4nuQNUnwEG69y-Cf3k-7eyK_S7LfXq4DF77Mj6VQ5gvKHnoXbjMOmP7y2tuyi0MSQVpjC2t_bUL42al9I_h2nxVVTPeO8-4upeQ59Ful3VSbM_pY21lv82Cjym-JY-RufD70Dwl0YVSuwjv7WsEuz-r8bHpPPEy8uSwbIeNvMbnpRuPt5sM6yCCxSnfBO45C9I4Wyar6EDjanH4HEf8W-1JvhagcL1PujLARPjTXvTr_f_o47VtxsrYdlJxaprT5GSGhs62_54iSmH0_hdWcoyH.Z5eFmA.zQAF7VrkccTUtDO6cI5T3fV2mtM",
            "Content-Type": "application/json",
        }

    funnel_reponse = get_request("https://pulse.bi.mypaytm.com/api/v1/chart/list/funnelhub_viz", headers)
    result = [
        {
            "funnel_name": item["slice_name"],
            "goal": item["goal"],
            "vertical_name": item["vertical_name"],
            "product_name": item["product_name"],
            "id": item["id"]
        }
        for item in funnel_reponse["result"]
    ]
    return result

def fetch_base_query(funnel_id, funnel_name):
    """
    Fetches the base query for the funnel
    """
    headers = {
        "Cookie": "_clck=1upy6g3%7C2%7Cfsx%7C0%7C1833; session=.eJwtkUuP2jAYRf9K5TWtbMfxg11KQyg00CQzA2lVoc-xTTKFBOVFYTT_vZHa5ZXu4txz39DRtbYr0bxvBztDx8qgOQLsEw7S-EJjhanPQehCF9wZBr7g4FzBFDg1tZSxnuOWK86xpAUTknpYEzDUWmIoFIQTyQVhhQDATFgsmWQaF74h2KPGV5hh4YivCzz1idSaGjRD56aAs51YbD2lBoZ-YnxDH3o0_4nuQNUnwEG69y-Cf3k-7eyK_S7LfXq4DF77Mj6VQ5gvKHnoXbjMOmP7y2tuyi0MSQVpjC2t_bUL42al9I_h2nxVVTPeO8-4upeQ59Ful3VSbM_pY21lv82Cjym-JY-RufD70Dwl0YVSuwjv7WsEuz-r8bHpPPEy8uSwbIeNvMbnpRuPt5sM6yCCxSnfBO45C9I4Wyar6EDjanH4HEf8W-1JvhagcL1PujLARPjTXvTr_f_o47VtxsrYdlJxaprT5GSGhs62_54iSmH0_hdWcoyH.Z5eFmA.zQAF7VrkccTUtDO6cI5T3fV2mtM",
        "Content-Type": "application/json",
    }
    query_context = get_request(f"https://pulse.bi.mypaytm.com/api/v1/chart/{funnel_id}", headers)["result"]["query_context"]

    query_params = {
        "form_data": f'{{"slice_id":{funnel_id}}}',
        "slice_name": funnel_name,
        "viz_type": "funnelhub_viz",
    }
    encoded_params = urllib.parse.urlencode(query_params)
    url = f"https://pulse.bi.mypaytm.com/api/v1/chart/data?{encoded_params}"

    payload = json.loads(query_context)
    payload["result_type"] = "query"
    base_query = post_request(url, headers, payload)
    return json.loads(base_query["result"][0]["query"])


def execute_query_pulse(basequery: str, segment: str, start_date: str, end_date: str) -> str:
    """
    Takes query as json input and returns result of it after querrying pulse
    Data returned corresponds to the user visits to the app for the query
    :query: druid query in json format
    :segment: segment to be applied to the query
    :start_date: start date of the query in format "2025-01-01T00:00:00+05:30"
    :end_date: end date of the query in format "2025-01-22T00:00:00+05:30"
    :return: result of the query in json format with values as count of user visiting that page
    """ 
    try:
        api_url = "https://paytmprod.implycloud.com/p/3f93cc1e-b9d1-4bf8-9a97-87392e98cfc6/console/druid/druid/v2"
        
        headers = {
            "Cookie": "connect.sid=s%3AWmz6QbXicl0HceKt7A1tpn3Nf0ytxqqp.VcjszXj2l%2B3EGpKCCPDixB4bSSltp4IjkNTyENkpEpg",
            "Content-Type": "application/json",
        }

        date_format = '%Y-%m-%dT%H:%M:%S+05:30'
        start_date = parser.parse(start_date).strftime(date_format)
        end_date = parser.parse(end_date).strftime(date_format)

        payload = json.loads(basequery)
        response = post_request(api_url, headers, payload)
        return response
    except requests.RequestException as e:
        print(e)
        return f"Error querying pulse: {str(e)}"
    
def fetch_all_segments():
    """
    Fetches all relevant segments for the query
    """
    try:
        file_path = "data/agents/devrev/tools/Funnel Hub _ Definitions - Segment mapping.csv"
        segments = pd.read_csv(file_path)
        segments["Segment"] = segments["Segment Name"]
        segments["Condition"] = segments["Segment Definition"]
        segments.drop(columns=["Segment Name", "Segment Definition"], inplace=True)
        return segments
    except Exception as e:
        print(e)
        return f"Error fetching segments: {str(e)}"

def plot_graph(observations: List[Dict[str, Union[str, int, float]]], title: str = "Funnel Analysis") -> str:
    """
    Plots a line graph using matplotlib from the funnel observations
    
    Args:
        observations: List of dictionaries containing stage names and their values
        title: Title for the graph (default: "Funnel Analysis")
    
    Returns:
        str: Path to the saved plot image
    """
    try:
        # Extract stages and values
        stages = [obs.get('stage', f'Stage {i+1}') for i, obs in enumerate(observations)]
        values = [float(obs.get('value', 0)) for obs in observations]

        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(stages, values, 'bo-', linewidth=2, markersize=8)
        
        # Customize the plot
        plt.title(title, fontsize=14, pad=20)
        plt.xlabel('Funnel Stages', fontsize=12)
        plt.ylabel('Count/Value', fontsize=12)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of each point
        for i, value in enumerate(values):
            plt.text(i, value, f'{value:,.0f}', 
                    ha='center', va='bottom')
        
        # Add grid for better readability
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/agents/devrev/plots/funnel_analysis_{timestamp}.png"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        print(f"Error plotting graph: {str(e)}")
        return f"Error plotting graph: {str(e)}"

def plot_comparison_graph(observations_list: List[List[Dict]], labels: List[str], title: str = "Funnel Comparison") -> str:
    """
    Plots multiple funnel observations for comparison
    
    Args:
        observations_list: List of observation lists, each containing stage data
        labels: Labels for each funnel line
        title: Title for the graph
    
    Returns:
        str: Path to the saved plot image
    """
    try:
        plt.figure(figsize=(14, 7))
        
        # Get all unique stages
        all_stages = []
        for observations in observations_list:
            stages = [obs.get('stage', f'Stage {i+1}') for i, obs in enumerate(observations)]
            all_stages.extend(stages)
        unique_stages = list(dict.fromkeys(all_stages))
        
        # Plot each funnel line
        for i, (observations, label) in enumerate(zip(observations_list, labels)):
            stages = [obs.get('stage', f'Stage {i+1}') for i, obs in enumerate(observations)]
            values = [float(obs.get('value', 0)) for obs in observations]
            
            plt.plot(stages, values, 'o-', linewidth=2, markersize=8, label=label)
            
            # Add value labels
            for j, value in enumerate(values):
                plt.text(j, value, f'{value:,.0f}', 
                        ha='center', va='bottom')
        
        # Customize the plot
        plt.title(title, fontsize=14, pad=20)
        plt.xlabel('Funnel Stages', fontsize=12)
        plt.ylabel('Count/Value', fontsize=12)
        plt.legend()
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/agents/devrev/plots/funnel_comparison_{timestamp}.png"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        print(f"Error plotting comparison graph: {str(e)}")
        return f"Error plotting comparison graph: {str(e)}"

def plot_funnel_metrics(observations: List[Dict], title: str = "Funnel Metrics Analysis") -> str:
    """
    Plots funnel metrics from the given observations format
    
    Args:
        observations: List of dictionaries containing timestamp and result metrics
        title: Title for the graph
    
    Returns:
        str: Path to the saved plot image
    """
    try:
        # Extract the latest observation
        latest_obs = observations[0]['result']  # Using first observation since it's the most recent
        
        # Define the funnel stages in order
        stages = ['Category Landing', 'Amount', 'Payment Gateway', 'Summary', 'POS']
        values = [latest_obs.get(stage, 0) for stage in stages]
        
        # Create the plot
        plt.figure(figsize=(14, 8))
        
        # Plot funnel stages
        plt.plot(range(len(stages)), values, 'bo-', linewidth=2, markersize=10, label='User Count')
        
        # Add value labels on points
        for i, value in enumerate(values):
            plt.text(i, value, f'{value:,.0f}', 
                    ha='center', va='bottom')
        
        # Add conversion rates between stages
        for i in range(len(stages)-1):
            current_stage = stages[i]
            next_stage = stages[i+1]
            conversion_key = f"{current_stage}_VS_{next_stage}"
            
            if conversion_key in latest_obs:
                conversion_rate = latest_obs[conversion_key]
                mid_x = (i + (i + 1)) / 2
                mid_y = (values[i] + values[i + 1]) / 2
                
                # Add conversion rate label with arrow
                plt.annotate(
                    f'{conversion_rate:,.2f}%',
                    xy=(mid_x, mid_y),
                    xytext=(0, 30),
                    textcoords='offset points',
                    ha='center',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
                )
        
        # Customize the plot
        plt.title(title, fontsize=14, pad=20)
        plt.xlabel('Funnel Stages', fontsize=12)
        plt.ylabel('User Count', fontsize=12)
        
        # Set x-axis labels
        plt.xticks(range(len(stages)), stages, rotation=45, ha='right')
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/agents/devrev/plots/funnel_metrics_{timestamp}.png"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    except Exception as e:
        print(f"Error plotting funnel metrics: {str(e)}")
        return f"Error plotting funnel metrics: {str(e)}"