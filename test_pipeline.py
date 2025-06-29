from app.agent import AIAgent
import json

def main():
    """Test the complete AI Agent pipeline"""
    
    # Initialize the agent
    agent = AIAgent()
    
    # Job description matching your project requirements
    # Job description from Windsurf posting
    job_description = """
Software Engineer, ML Research - Windsurf
Location: Mountain View, CA (On-site)
Company: Windsurf (Formerly Codeium) - Forbes AI 50 Company

About the Company:
Windsurf (formerly Codeium) is a Forbes AI 50 company building the future of developer productivity through AI. With over 200 employees and $243M raised across multiple rounds including a Series C, Windsurf provides cutting-edge in-editor autocomplete, chat assistants, and full IDEs powered by proprietary LLMs. Their user base spans hundreds of thousands of developers worldwide, reflecting strong product-market fit and commercial traction.

Role and Responsibilities:
• Train and fine-tune LLMs focused on developer productivity
• Design and prioritize experiments for product impact
• Analyze results, conduct ablation studies, and document findings
• Convert ML discoveries into scalable product features
• Participate in the ML reading group and contribute to knowledge sharing

Job Requirements:
• 2+ years in software engineering with fast promotions
• Strong software engineering and systems thinking skills
• Proven experience training and iterating on large production neural networks
• Strong GPA from a top CS undergrad program (MIT, Stanford, CMU, UIUC, etc.)
• Familiarity with tools like Copilot, ChatGPT, or Windsurf is preferred
• Deep curiosity for the code generation space
• Excellent documentation and experimentation discipline
• Prior experience with applied research (not purely academic publishing)
• Must be able to work in Mountain View, CA full-time onsite
• Excited to build product-facing features from ML research

Interview Process:
1. Recruiter Chat (15 min)
2. Virtual Algorithm Round (LeetCode-style, 45 min)
3. Virtual ML Case Study (1 hour)
4. Onsite (3 hours): Additional ML case, implementation project, and culture interview
5. Offer Extended

Compensation: $140,000 - $300,000 + Equity
Location: Mountain View, CA (Full-time, On-site)
Company ID: SRN2025-10918
"""
    
       # Test candidate list - ML Research focused candidates
    candidate_names = [
        "Andrej Karpathy",     # Former Tesla AI Director, OpenAI researcher
        "Shreya Shankar",      # Stanford PhD, ML systems researcher
        "Karpathy",            # Alternative search for Andrej
        "Chris Manning",       # Stanford NLP Professor
        "Sebastian Ruder"      # NLP researcher, Google DeepMind
    ]
    
    print("************ Testing Complete AI Agent Pipeline ************")
    print("=" * 60)
    
    # Run the full pipeline
    results = agent.run_full_pipeline(job_description, candidate_names)
    
    # Export results to JSON for demo
    filename = agent.export_results_json(results)
    
    # Display formatted results
    print("\n************* FINAL RESULTS: **************")
    print("-" * 50)
    
    if results["status"] == "success":
        print(f"Job ID: {results['job_id']}")
        print(f" Candidates Found: {results['candidates_found']}")
        print(f"Execution Time: {results['execution_time']}s")
        
        print("\nTOP CANDIDATES:")
        for i, candidate in enumerate(results['top_candidates'][:3], 1):
            print(f"\n{i}. {candidate['name']}")
            print(f"   Score: {candidate['score']:.1f}/100 ({candidate['fit_level']})")
            print(f"   Company: {candidate['company']}")
            print(f"   Location: {candidate['location']}")
            print(f"   LinkedIn: {candidate['linkedin_url']}")
            print(f"   Message Preview: {candidate['outreach_message'][:100]}...")
            
        print(f"\n Full results saved to: {filename}")
        
    else:
        print(f"Pipeline failed: {results['message']}")

if __name__ == "__main__":
    main()