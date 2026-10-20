import streamlit as st
import requests
import urllib.parse
from bs4 import BeautifulSoup

st.set_page_config(page_title="Drama & Cast Finder", page_icon="🎬", layout="centered")
MDL_BASE_URL = "https://microdramalist.com/api/v1"

st.title("🎬 Drama & Cast Finder")

with st.sidebar:
    st.header("Settings")
    scrapingbee_key = st.text_input("ScrapingBee API Key", type="password")

def get_platform_links_by_title(title: str):
    try:
        search_res = requests.get(f"{MDL_BASE_URL}/search", params={"q": title}).json()
        if not search_res:
            return None
        mdid = search_res[0]["id"]
        drama_details = requests.get(f"{MDL_BASE_URL}/dramas/{mdid}").json()
        return {
            "title": drama_details.get("title"),
            "mdid": mdid,
            "availableOn": drama_details.get("availableOn", [])
        }
    except Exception as e:
        st.error(f"Error: {e}")
        return None

tab1, tab2 = st.tabs(["Search Title", "IMDb Search"])

with tab1:
    query_title = st.text_input("Enter Drama Title", placeholder="e.g. Zooton Gone Wrong")
    if st.button("Search Drama Platforms", use_container_width=True):
        if query_title:
            res = get_platform_links_by_title(query_title)
            if res:
                st.success(f"Found: {res['title']}")
                for p in res.get("availableOn", []):
                    st.write(f"- [{p.get('name', 'Link')}]({p.get('url', '#')})")
            else:
                st.warning("No drama found.")
