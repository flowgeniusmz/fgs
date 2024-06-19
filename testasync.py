import asyncio
from openai import OpenAI
from tavily import TavilyClient
from supabase import create_client as supabase_client
from googlemaps import Client as google_client
from googlesearch import search
from yelpapi import YelpAPI

import streamlit as st

# Initialize clients
oaiClient = OpenAI(api_key=st.secrets.openai.api_key)
supaClient = supabase_client(st.secrets.supabase.url, st.secrets.supabase.api_key_admin)
yelpClient = YelpAPI(api_key=st.secrets.yelp.api_key)
googClient = google_client(key=st.secrets.google.maps_api_key)
tavClient = TavilyClient(api_key=st.secrets.tavily.api_key)

class Tools:
    @staticmethod
    async def internet_search(query: str):
        """
        Performs an internet search using the provided query and returns a list of search results.

        Args:
            query (str): The search query.

        Returns:
            list: A list of URLs corresponding to the search results.
        """
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: list(search(term=query, advanced=True)))
        return response
    
    @staticmethod
    async def internet_research(query: str):
        """
        Performs advanced internet research using the provided query and returns the results.

        Args:
            query (str): The research query.

        Returns:
            dict: The research results, including answers and raw content.
        """
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: tavClient.search(query=query, search_depth="advanced", max_results=7, include_answer=True, include_raw_content=True))
        return response

    @staticmethod
    async def google_places_search(query: str):
        """
        Searches for business information using Google Places to gather details on location, ratings, and more.
        
        Parameters:
            query (str): The search query describing the business.
        
        Returns:
            dict: The search results with detailed information about the business.
        """
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: googClient.places(query=query, region="US"))
        return response
    
    @staticmethod
    async def yelp_search(query: str, zipcode: str):
        """
        Performs a search query using Yelp and retrieves detailed information for each business, aggregating useful data for insurance analysis.
        
        Parameters:
            query (str): The search query describing the type of business.
            zipcode (str): The zipcode of the business location.
        
        Returns:
            list: A list of businesses with basic information.
        """
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: yelpClient.search_query(term=query, location=zipcode))
        businesses = response['businesses']
        return businesses

async def execute_all_tasks(query: str, zipcode: str):
    tasks = [
        Tools.internet_search(query),
        Tools.internet_research(query),
        Tools.google_places_search(query),
        Tools.yelp_search(query, zipcode)
    ]

    responses = await asyncio.gather(*tasks)
    return {
        "internet_search": responses[0],
        "internet_research": responses[1],
        "google_places_search": responses[2],
        "yelp_search": responses[3]
    }

# Example usage:
query = "What is a chad?"
zipcode = "90210"

responses = asyncio.run(execute_all_tasks(query, zipcode))
print(responses)
