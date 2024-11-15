# -*- coding: utf-8 -*-

import streamlit as st
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

def search_pubmed(author, affiliation, start_year, end_year, email):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    query = f"{author}[Author] AND {affiliation}[Affiliation] AND ({start_year}:{end_year}[Date - Publication])"
   
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 100,
        "retmode": "xml",
        "tool": "MyTool",
        "email": email
    }
   
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        root = ET.fromstring(response.read())
   
    id_list = [id_elem.text for id_elem in root.findall(".//Id")]
    return id_list

def fetch_citations(id_list, email):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    ids = ",".join(id_list)
   
    params = {
        "db": "pubmed",
        "id": ids,
        "retmode": "xml",
        "rettype": "medline",
        "tool": "MyTool",
        "email": email
    }
   
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as response:
        root = ET.fromstring(response.read())
   
    citations = []
    for article in root.findall(".//PubmedArticle"):
        # Title
        title = article.find(".//ArticleTitle").text
       
        # DOI
        doi_elem = article.find(".//ArticleId[@IdType='doi']")
        doi = doi_elem.text if doi_elem is not None else "N/A"
       
        # Authors
        authors = []
        for author in article.findall(".//Author"):
            last_name = author.find("LastName")
            initials = author.find("Initials")
            if last_name is not None and initials is not None:
                authors.append(f"{last_name.text} {initials.text}")
        authors_str = ", ".join(authors)
       
        # Details
        journal = article.find(".//Journal/Title").text
        year = article.find(".//PubDate/Year")
        year = year.text if year is not None else ""
        volume = article.find(".//Volume")
        volume = volume.text if volume is not None else ""
        issue = article.find(".//Issue")
        issue = issue.text if issue is not None else ""
        pages = article.find(".//MedlinePgn")
        pages = pages.text if pages is not None else ""
       
        details = f"{journal}. {year}"
        if volume:
            details += f";{volume}"
        if issue:
            details += f"({issue})"
        if pages:
            details += f":{pages}"
       
        # PubMed ID
        pmid = article.find(".//PMID").text
       
        # Construct NLM format citation
        citation = f"{title}. doi: {doi}. {authors_str}. {details}. PubMed PMID: {pmid}."
        citations.append(citation)
   
    return citations

def main():
    st.title("PubMed Author Search")

    # User inputs
    email = st.text_input("Enter your email")
    author = st.text_input("Enter the author name")
    affiliation = st.text_input("Enter the institution name")
    start_year = st.text_input("Enter start year (e.g., 2020)", "2024")
    end_year = st.text_input("Enter end year (e.g., 2024)", "2024")
    
    # Search and display results
    if st.button("Search Publications"):
        if email and author and affiliation:
            st.write(f"Searching for publications by {author} from {affiliation} between {start_year} and {end_year}:")
            id_list = search_pubmed(author, affiliation, start_year, end_year, email)
           
            if id_list:
                citations = fetch_citations(id_list, email)
                for citation in citations:
                    st.write(citation)
            else:
                st.write("No publications found.")
        else:
            st.error("Please provide your email, author name, and institution name.")

if __name__ == "__main__":
    main()
