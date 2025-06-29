import streamlit as st
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.agent import AIAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to get API keys from Streamlit secrets first, then from .env
def get_api_keys():
    try:
        # For Streamlit Cloud deployment
        groq_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        serpapi_key = st.secrets.get("SERPAPI_API_KEY", os.getenv("SERPAPI_API_KEY"))
        return groq_key, serpapi_key
    except:
        # For local development
        return os.getenv("GROQ_API_KEY"), os.getenv("SERPAPI_API_KEY")
    
    
# Page configuration
st.set_page_config(
    page_title="🚀 AI-Powered-Recruitment-Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-strong { color: #17a2b8; font-weight: bold; }
    .score-good { color: #ffc107; font-weight: bold; }
    .score-fair { color: #fd7e14; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def get_score_class(score):
    """Get CSS class based on score"""
    if score >= 80:
        return "score-excellent"
    elif score >= 70:
        return "score-strong"
    elif score >= 60:
        return "score-good"
    elif score >= 40:
        return "score-fair"
    else:
        return "score-poor"

def get_fit_level(score):
    """Get fit level based on score"""
    if score >= 80:
        return "🌟 Excellent Fit"
    elif score >= 70:
        return "⭐ Strong Fit"
    elif score >= 60:
        return "👍 Good Fit"
    elif score >= 40:
        return "🤔 Fair Fit"
    else:
        return "❌ Poor Fit"

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 AI-Powered-Recruitment-Agent</h1>', unsafe_allow_html=True)
    st.markdown("**Intelligent recruitment automation powered by AI**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key Status
        groq_key, serpapi_key = get_api_keys()
        
        if groq_key and serpapi_key:
            st.success("✅ API Keys Configured")
        else:
            st.error("❌ API Keys Missing")
            st.markdown("**For local development:**")
            st.code("""
# Add to .env file:
GROQ_API_KEY=your_groq_key
SERPAPI_API_KEY=your_serpapi_key
            """)
            st.markdown("**For Streamlit Cloud:**")
            st.info("Add secrets in Streamlit Cloud dashboard")
        
        st.markdown("---")
        
        # Settings
        st.subheader("⚙️ Settings")
        max_candidates = st.slider("Max Candidates to Process", 1, 10, 5)
        
        # Example candidates
        st.subheader("💡 Example Candidates")
        if st.button("Load AI/ML Examples"):
            st.session_state.candidates_list = [
                "Andrej Karpathy",
                "Shreya Shankar", 
                "Sebastian Ruder",
                "Chris Olah",
                "Dario Amodei"
            ]
            st.success("AI/ML candidates loaded!")
        
        if st.button("Load Software Engineer Examples"):
            st.session_state.candidates_list = [
                "John Carmack",
                "Jeff Dean", 
                "Guido van Rossum",
                "Brendan Eich",
                "Anders Hejlsberg"
            ]
            st.success("Software Engineer candidates loaded!")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Job Description")
        job_description = st.text_area(
            "Enter the job description:",
            height=200,
            placeholder="""Software Engineer, ML Research at AI Company

We're looking for candidates with:
- 3+ years experience in machine learning
- Strong Python programming skills
- Experience with LLMs and production ML systems
- PhD or Master's degree in Computer Science preferred
- Experience at top tech companies (Google, OpenAI, Meta, etc.)
- Located in San Francisco Bay Area or remote"""
        )
    
    with col2:
        st.header("👥 Candidates")
        
        # Initialize candidates list
        if 'candidates_list' not in st.session_state:
            st.session_state.candidates_list = []
        
        # Add candidate input
        with st.form("add_candidate_form"):
            new_candidate = st.text_input("Add candidate name:")
            submitted = st.form_submit_button("➕ Add Candidate")
            
            if submitted and new_candidate:
                if new_candidate not in st.session_state.candidates_list:
                    st.session_state.candidates_list.append(new_candidate)
                    st.success(f"Added: {new_candidate}")
                else:
                    st.warning("Candidate already in list")
        
        # Display current candidates
        if st.session_state.candidates_list:
            st.subheader("Current Candidates:")
            for i, candidate in enumerate(st.session_state.candidates_list):
                col_name, col_remove = st.columns([3, 1])
                with col_name:
                    st.write(f"{i+1}. {candidate}")
                with col_remove:
                    if st.button("🗑️", key=f"remove_{i}"):
                        st.session_state.candidates_list.pop(i)
                        st.rerun()
        
        # Clear all button
        if st.session_state.candidates_list:
            if st.button("🗑️ Clear All Candidates"):
                st.session_state.candidates_list = []
                st.success("All candidates cleared!")
    
    # Run Analysis Button
    st.markdown("---")
    if st.button("🚀 Start AI Sourcing Analysis", type="primary", use_container_width=True):
        if not job_description.strip():
            st.error("Please enter a job description")
            return
        
        if not st.session_state.candidates_list:
            st.error("Please add at least one candidate")
            return
        
        if not (groq_key and serpapi_key):
            st.error("Please configure API keys in .env file")
            return
        
        # Limit candidates
        candidates_to_process = st.session_state.candidates_list[:max_candidates]
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize agent
            status_text.text("🤖 Initializing AI Agent...")
            agent = AIAgent()
            
            # Run pipeline
            status_text.text("🔍 Starting candidate analysis...")
            progress_bar.progress(10)
            
            results = agent.run_full_pipeline(job_description, candidates_to_process)
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store results in session state
            st.session_state.results = results
            
            # Display results
            display_results(results)
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.exception(e)
    
    # Display previous results if available
    if 'results' in st.session_state:
        st.markdown("---")
        st.header("📊 Previous Results")
        display_results(st.session_state.results)

def display_results(results):
    """Display the analysis results"""
    
    if not results or 'top_candidates' not in results:
        st.warning("No results to display")
        return
    
    # Summary metrics
    st.subheader("📈 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Candidates Found", results.get('candidates_found', 0))
    
    with col2:
        st.metric("Execution Time", f"{results.get('execution_time', 0):.1f}s")
    
    with col3:
        avg_score = sum(c.get('score', 0) for c in results['top_candidates']) / len(results['top_candidates']) if results['top_candidates'] else 0
        st.metric("Average Score", f"{avg_score:.1f}")
    
    with col4:
        excellent_count = sum(1 for c in results['top_candidates'] if c.get('score', 0) >= 80)
        st.metric("Excellent Fits", excellent_count)
    
    # Pipeline summary
    if 'pipeline_summary' in results:
        st.subheader("🎯 Fit Distribution")
        summary = results['pipeline_summary']
        
        # Create pie chart
        labels = ['Excellent', 'Strong', 'Good', 'Fair', 'Poor']
        values = [
            summary.get('excellent_fits', 0),
            summary.get('strong_fits', 0),
            summary.get('good_fits', 0),
            summary.get('fair_fits', 0),
            summary.get('poor_fits', 0)
        ]
        
        # Only create pie chart if there are values
        if sum(values) > 0:
            fig = px.pie(
                values=values, 
                names=labels,
                color_discrete_sequence=['#28a745', '#17a2b8', '#ffc107', '#fd7e14', '#dc3545']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Candidates list
    st.subheader("👥 Candidate Analysis")
    
    for i, candidate in enumerate(results['top_candidates']):
        with st.expander(f"🏆 #{i+1} {candidate.get('name', 'Unknown')} - {get_fit_level(candidate.get('score', 0))}"):
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Basic info
                st.markdown("**📊 Score & Info**")
                score = candidate.get('score', 0)
                st.markdown(f"**Score:** <span class='{get_score_class(score)}'>{score}/100</span>", unsafe_allow_html=True)
                st.write(f"**Company:** {candidate.get('company', 'N/A')}")
                st.write(f"**Location:** {candidate.get('location', 'N/A')}")
                st.write(f"**Education:** {candidate.get('education', 'N/A')}")
                
                # LinkedIn link
                linkedin_url = candidate.get('linkedin_url', '')
                if linkedin_url:
                    st.markdown(f"**[🔗 LinkedIn Profile]({linkedin_url})**")
            
            with col2:
                # Outreach message
                st.markdown("**💌 Personalized Outreach Message**")
                message = candidate.get('outreach_message', 'No message generated')
                
                # Display message in a styled container
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                    font-family: 'Segoe UI', sans-serif;
                    line-height: 1.5;
                    margin: 0.5rem 0;
                    white-space: pre-wrap;
                ">
{message}
                </div>
                """, unsafe_allow_html=True)
                
                # Simple copy instruction
                st.caption("💡 Select the text above to copy the message")
            
            # Detailed scoring if available
            if 'scoring_explanation' in candidate:
                st.markdown("**🎯 Detailed Scoring**")
                scoring = candidate['scoring_explanation']
                
                score_cols = st.columns(5)
                metrics = [
                    ('Technical Skills', scoring.get('technical_skills', 0)),
                    ('Experience', scoring.get('experience_level', 0)),
                    ('Education', scoring.get('education_background', 0)),
                    ('Company', scoring.get('company_prestige', 0)),
                    ('Location', scoring.get('location_fit', 0))
                ]
                
                for col, (metric, value) in zip(score_cols, metrics):
                    col.metric(metric, f"{value}/100")
                
                if 'reasoning' in scoring:
                    st.markdown("**💭 AI Reasoning:**")
                    st.info(scoring['reasoning'])
    
    # Simple results summary at the end
    st.subheader("📋 Results Summary")
    st.success(f"Analysis completed! Found {results.get('candidates_found', 0)} candidates in {results.get('execution_time', 0):.1f} seconds.")

if __name__ == "__main__":
    main()