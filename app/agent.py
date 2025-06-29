from typing import List, Dict, Optional
from .scraper import search_linkedin_profile
from .scorer import score_candidate
from .messenger import generate_outreach_message
import json
import time

class AIAgent:
    """
    AI-powered recruitment agent for automated candidate sourcing and outreach.
    
    Workflow: Job Input → LinkedIn Search → Profile Scoring → Outreach Generation
    """
    
    def __init__(self):
        self.job_cache = {}
        self.results_cache = {}

    """**********************************LinkedIn SEARCH METHOD*******************************************"""    

    def search_linkedin(self, job_description: str, candidate_names: List[str]) -> List[Dict]:
        """
        Step 1: Candidate Discovery via LinkedIn Search
        
        Args:
            job_description: Target job requirements
            candidate_names: List of candidate names to search
            
        Returns:
            List of enriched candidate profiles
        """
        print(f"🔍 Searching LinkedIn for {len(candidate_names)} candidates...")
        candidates = []
        
        # Extract job title for better search accuracy
        job_title = self._extract_job_title(job_description)
        
        for i, name in enumerate(candidate_names, 1):
            print(f"  [{i}/{len(candidate_names)}] Searching: {name}")
            
            try:
                profile_data = search_linkedin_profile(name, job_title)
                
                if profile_data and profile_data.get("name"):
                    # Enrich profile data
                    enriched_candidate = {
                        "name": profile_data.get("name"),
                        "headline": profile_data.get("headline", ""),
                        "title": profile_data.get("headline", ""),
                        "company": profile_data.get("company", "N/A"),
                        "location": profile_data.get("location", "N/A"),
                        "linkedin_url": profile_data.get("url", ""),
                        "snippet": profile_data.get("snippet", ""),
                        "education": profile_data.get("education", ""),
                        "current_role": profile_data.get("current_role", ""),
                        "profile_data": profile_data
                    }
                    candidates.append(enriched_candidate)
                    print(f"Found: {enriched_candidate['name']} at {enriched_candidate['company']}")
                else:
                    print(f"Not found: {name}")

            except Exception as e:
                print(f" Error searching {name}: {str(e)}")
                
            # Rate limiting
            time.sleep(1)

        print(f"Successfully found {len(candidates)} LinkedIn profiles")
        return candidates


    '''**********************************SCORING METHOD*******************************************'''

    def score_candidates(self, candidates: List[Dict], job_description: str) -> List[Dict]:
        """
        Step 2: Candidate Fit Scoring using AI
        
        Args:
            candidates: List of candidate profiles
            job_description: Job requirements for scoring
            
        Returns:
            List of candidates with scores and detailed breakdowns
        """
        print(f"Scoring {len(candidates)} candidates against job requirements...")
        scored_candidates = []
        
        for i, candidate in enumerate(candidates, 1):
            print(f"  [{i}/{len(candidates)}] Scoring: {candidate['name']}")
            
            try:
                # Score candidate using AI (your existing scorer.py)
                score_result = score_candidate(candidate, job_description)
                
                scored_candidate = {
                    **candidate,  # Keep all original data
                    "score": score_result.get("final_score", 0),
                    "score_breakdown": score_result.get("explanation", {}),
                    "fit_level": self._categorize_fit(score_result.get("final_score", 0))
                }
                
                scored_candidates.append(scored_candidate)
                print(f" SCORE: {scored_candidate['score']:.1f}/100 ({scored_candidate['fit_level']})")
                
            except Exception as e:
                print(f" Error scoring {candidate['name']}: {str(e)}")
                # Add candidate with 0 score if scoring fails
                scored_candidates.append({
                    **candidate,
                    "score": 0,
                    "score_breakdown": {"error": str(e)},
                    "fit_level": "Error"
                })
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"🏆 Top candidate: {scored_candidates[0]['name']} ({scored_candidates[0]['score']:.1f}/100)")
        return scored_candidates
    
    '''**********************************OUTREACH GENERATION METHOD*******************************************'''

    def generate_outreach(self, candidates: List[Dict], job_description: str, top_n: int = 5) -> List[Dict]:
        """
        Step 3: Personalized Outreach Message Generation
        
        Args:
            candidates: Scored candidate list
            job_description: Job context for messaging
            top_n: Number of top candidates to generate messages for (default: 5)
            
        Returns:
            List of candidates with personalized outreach messages
        """
        top_candidates = candidates[:top_n]
        print(f"Generating outreach messages for top {len(top_candidates)} candidates...")
        
        outreach_results = []
        
        for i, candidate in enumerate(top_candidates, 1):
            print(f"  [{i}/{len(top_candidates)}] Generating message for: {candidate['name']}")
            
            try:
                # Generate personalized message using your existing messenger.py
                message = generate_outreach_message(candidate, job_description)
                
                outreach_candidate = {
                    **candidate,  # Keep all data
                    "outreach_message": message,
                    "message_generated": True,
                    "key_highlights": self._extract_highlights(candidate)
                }
                
                outreach_results.append(outreach_candidate)
                print(f"Message generated ({len(message)} characters)")
                
            except Exception as e:
                print(f"Error generating message for {candidate['name']}: {str(e)}")
                outreach_results.append({
                    **candidate,
                    "outreach_message": f"Error generating message: {str(e)}",
                    "message_generated": False,
                    "key_highlights": []
                })
        
        return outreach_results    
    
    '''**********************************MAIN PIPELINE METHOD*******************************************'''

    def run_full_pipeline(self, job_description: str, candidate_names: List[str]) -> Dict:
        """
        Complete recruitment pipeline: Search → Score → Generate Messages
        
        Args:
            job_description: Job posting details
            candidate_names: List of candidate names to evaluate
            
        Returns:
            Complete results with candidates, scores, and outreach messages
        """
        print("AI SOURCING AGENT - Starting Full Pipeline")
        print("=" * 60)
        
        start_time = time.time()
        
        # Step 1: LinkedIn Search
        print("\n STEP 1: LinkedIn Profile Discovery")
        candidates = self.search_linkedin(job_description, candidate_names)
        
        if not candidates:
            return {
                "status": "failed",
                "message": "No candidates found on LinkedIn",
                "candidates_found": 0,
                "results": []
            }
        
        # Step 2: AI Scoring
        print("\n STEP 2: AI-Powered Candidate Scoring")
        scored_candidates = self.score_candidates(candidates, job_description)
        
        # Step 3: Outreach Generation
        print("\n STEP 3: Personalized Outreach Generation")
        final_results = self.generate_outreach(scored_candidates, job_description)
        
        # Generate summary
        execution_time = time.time() - start_time
        summary = self._generate_summary(final_results, execution_time)
        
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print(summary)
        
        return {
            "status": "success",
            "job_id": self._generate_job_id(job_description),
            "candidates_found": len(candidates),
            "candidates_scored": len(scored_candidates),
            "execution_time": round(execution_time, 2),
            "top_candidates": final_results,
            "summary": summary
        }   


    '''**********************************HELPER METHODS*******************************************'''

    def export_results_json(self, results: Dict, filename: str = None) -> str:
        """Export results to JSON file for demo/API"""
        if not filename:
            filename = f"AI_results_{results.get('job_id', 'job')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results exported to: {filename}")
        return filename
    
    def _extract_job_title(self, job_description: str) -> str:
        """Extract job title from description for LinkedIn search"""
        lines = job_description.strip().split('\n')
        if lines:
            # Get first line and clean it
            title = lines[0].split(' - ')[0].strip()
            return title
        return "Software Engineer"
    
    def _categorize_fit(self, score: float) -> str:
        """Categorize candidate fit based on score"""
        if score >= 80:
            return "Excellent Fit"
        elif score >= 70:
            return "Strong Fit"
        elif score >= 60:
            return "Good Fit"
        elif score >= 50:
            return "Moderate Fit"
        else:
            return "Poor Fit"
    
    def _extract_highlights(self, candidate: Dict) -> List[str]:
        """Extract key highlights from candidate profile"""
        highlights = []
        
        if candidate.get("company") and candidate["company"] != "N/A":
            highlights.append(f"Experience at {candidate['company']}")
        
        if candidate.get("score", 0) >= 70:
            highlights.append("Strong technical fit")
        
        if candidate.get("location"):
            highlights.append(f"Located in {candidate['location']}")
        
        return highlights
    
    def _generate_job_id(self, job_description: str) -> str:
        """Generate unique job ID"""
        import hashlib
        title = self._extract_job_title(job_description).lower().replace(" ", "-")
        hash_suffix = hashlib.md5(job_description.encode()).hexdigest()[:6]
        return f"{title}-{hash_suffix}"
    
    def _generate_summary(self, results: List[Dict], execution_time: float) -> str:
        """Generate execution summary for demo"""
        if not results:
            return "No candidates processed."
        
        total = len(results)
        excellent = len([c for c in results if c.get("score", 0) >= 80])
        strong = len([c for c in results if 70 <= c.get("score", 0) < 80])
        good = len([c for c in results if 60 <= c.get("score", 0) < 70])
        
        top_candidate = results[0] if results else None
        
        summary = f"""
        EXECUTION SUMMARY:
        • Total Candidates: {total}
        • Excellent Fits (80+): {excellent}
        • Strong Fits (70-79): {strong}  
        • Good Fits (60-69): {good}
        • Top Candidate: {top_candidate['name'] if top_candidate else 'None'} ({top_candidate.get('score', 0):.1f}/100)
        • Execution Time: {execution_time:.1f}s
                """.strip()
        
        return summary

# Convenience function for quick testing 
def run_single_candidate(candidate_name: str, candidate_title: str, job_description: str) -> Dict:
    """Quick function to test single candidate"""
    agent = AIAgent()
    results = agent.run_full_pipeline(job_description, [candidate_name])
    return results