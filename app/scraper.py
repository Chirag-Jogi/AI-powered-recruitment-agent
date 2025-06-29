# app/scraper.py

import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
import re
load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Define a function that searches for LinkedIn profiles
# Parameters: name (person's name), job_title (their job title)
# Returns: LinkedIn URL as string or None if not found

def search_linkedin_profile(name: str, job_title: str = "") -> dict | None:
    # Try exact name first (more accurate)
    exact_query = f'"{name}" site:linkedin.com/in'
    
    params = {
        "engine": "google",
        "q": exact_query,
        "api_key": SERPAPI_API_KEY,
        "num": 5,  # Get more results to find exact match
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # print(f"[DEBUG] Search query: {exact_query}")
    # print(f"[DEBUG] API Response keys: {list(results.keys()) if results else 'None'}")
    
    try:
        if "organic_results" not in results:
            # print("No 'organic_results' key found in response")
            return None
        
        # IMPORTANT: Filter results to find exact name match
        target_result = None
        for result in results["organic_results"]:
            result_title = result.get("title", "").lower()
            search_name = name.lower()
            
            # Check if the search name is in the result title
            if search_name in result_title:
                target_result = result
                # print(f"[DEBUG] Found exact match: {result_title}")
                break
        
        # If no exact match found, try with job title
        if not target_result and job_title:
            fallback_query = f'"{name}" "{job_title}" site:linkedin.com/in'
            params["q"] = fallback_query
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # print(f"[DEBUG] Fallback query: {fallback_query}")
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    result_title = result.get("title", "").lower()
                    if name.lower() in result_title:
                        target_result = result
                        # print(f"[DEBUG] Found fallback match: {result_title}")
                        break
        
        # If still no match, take first result as last resort
        if not target_result and "organic_results" in results and results["organic_results"]:
            target_result = results["organic_results"][0]
            # print(f"[DEBUG] Using first result as fallback")
        
        if not target_result:
            return None
        
        # Extract data from the selected result
        title = target_result.get("title", "")
        link = target_result.get("link", "")
        snippet = target_result.get("snippet", "")

        # Extract name from title
        name_match = re.match(r"^(.*?)\s*[-|–]", title)
        extracted_name = name_match.group(1).strip() if name_match else title.strip()

        # Enhanced company extraction from multiple sources (NO HARDCODING)
        company_from_title = ""
        company_from_snippet = ""
        company_from_extensions = ""
        
        # Method 1: Extract from title pattern (improved)
        if title and " - " in title:
            title_parts = title.split(" - ")
            if len(title_parts) >= 2:
                # Try different positions for company
                for part in reversed(title_parts[1:]):  # Skip name, check from end
                    part = part.strip()
                    # Skip obvious non-company parts
                    if part and not any(word in part.lower() for word in ["linkedin", "profile", "bio", "about", "view", "contact"]):
                        if len(part) > 2:  # Must be more than 2 characters
                            company_from_title = part
                            break

        # Method 2: Extract from snippet using smart patterns
        if snippet:
            # Look for "at [Company]" patterns
            at_pattern = re.search(r'\bat\s+([A-Z][a-zA-Z0-9\s&\.,\-]+?)(?:\s*[.,:;]|\s+(?:in|as|for|where|during)\s|\s*$)', snippet, re.IGNORECASE)
            if at_pattern:
                potential_company = at_pattern.group(1).strip()
                # Clean up common endings
                potential_company = re.sub(r'[.,:;]+$', '', potential_company)
                if len(potential_company) > 2 and len(potential_company.split()) <= 4:  # Reasonable company name length
                    company_from_snippet = potential_company

            # Look for "Company + role" patterns if no "at" found
            if not company_from_snippet:
                role_pattern = re.search(r'([A-Z][a-zA-Z0-9\s&\.,\-]+?)\s+(?:researcher|scientist|engineer|developer|director|manager|analyst|intern|lead|head)', snippet, re.IGNORECASE)
                if role_pattern:
                    potential_company = role_pattern.group(1).strip()
                    potential_company = re.sub(r'[.,:;]+$', '', potential_company)
                    if len(potential_company) > 2 and len(potential_company.split()) <= 4:
                        company_from_snippet = potential_company

        # Method 3: Extract from rich_snippet extensions (dynamic)
        if "rich_snippet" in target_result and "top" in target_result["rich_snippet"]:
            extensions = target_result["rich_snippet"]["top"].get("extensions", [])
            
            for ext in extensions:
                # Skip obvious location and role extensions
                if any(loc in ext.lower() for loc in ["india", "usa", "uk", "canada", "california", "texas", "new york", "mumbai", "delhi", "bangalore", "pune", "hyderabad", "chennai", "area", "region", "state", "country"]):
                    continue
                if any(role in ext.lower() for role in ["years", "experience", "ago", "months", "intern", "student", "graduate"]):
                    continue
                
                # Look for capitalized words (potential company names)
                words = ext.split()
                capitalized_words = [word for word in words if word and word[0].isupper() and len(word) > 2]
                
                if capitalized_words and len(capitalized_words) <= 3:  # Reasonable company name
                    # Join capitalized words
                    potential_company = ' '.join(capitalized_words)
                    if len(potential_company) > 2:
                        company_from_extensions = potential_company
                        break

        # Choose the best company name (prioritize: snippet > extensions > title)
        company = (
            company_from_snippet or 
            company_from_extensions or 
            company_from_title or 
            "N/A"
        )
        
        # Final cleanup - remove common noise
        if company != "N/A":
            # Remove LinkedIn-specific noise
            company = re.sub(r'\s*[-–]\s*LinkedIn.*$', '', company, flags=re.IGNORECASE)
            company = re.sub(r',?\s*an?\s+inc\s+\d+.*', '', company, flags=re.IGNORECASE)
            company = re.sub(r'\s+', ' ', company).strip()  # Clean extra spaces
            
            # Remove trailing punctuation
            company = re.sub(r'[.,:;!?]+$', '', company)
            
            # If it's too short or looks like noise, set to N/A
            if len(company) <= 2 or company.lower() in ["the", "and", "or", "inc", "ltd", "llc"]:
                company = "N/A"

        # Extract rich data from rich_snippet for location and role
        location = ""
        current_role = ""
        
        if "rich_snippet" in target_result and "top" in target_result["rich_snippet"]:
            extensions = target_result["rich_snippet"]["top"].get("extensions", [])
            for ext in extensions:
                if any(location_word in ext.lower() for location_word in ["india", "usa", "uk", "canada", "california", "texas", "new york", "mumbai", "delhi", "bangalore", "pune", "hyderabad", "chennai", "indore"]):
                    location = ext
                elif any(keyword in ext.lower() for keyword in ["intern", "engineer", "developer", "analyst", "scientist", "manager"]):
                    current_role = ext

        # Extract education from snippet
        education = ""
        if "b.tech" in snippet.lower() or "bachelor" in snippet.lower():
            education = "B.Tech Computer Science"
        elif "m.tech" in snippet.lower() or "master" in snippet.lower():
            education = "Master's degree"
        elif "phd" in snippet.lower() or "ph.d" in snippet.lower():
            education = "PhD"
        elif "student" in snippet.lower():
            education = "Student"

        candidate_data = {
            "name": extracted_name,
            "headline": title,
            "title": title,  # Added this for messenger compatibility
            "company": company,
            "location": location,
            "url": link,
            "linkedin_url": link,  # Added this for compatibility
            "snippet": snippet,
            "education": education,
            "current_role": current_role,
        }
        
        # Debug print to see extraction sources
        # print(f"[DEBUG] Company extraction - Title: '{company_from_title}', Snippet: '{company_from_snippet}', Extensions: '{company_from_extensions}', Final: '{company}'")
        
        return candidate_data
        
    except (KeyError, IndexError) as e:
        # print(f"[DEBUG] Error in extraction: {e}")
        return None