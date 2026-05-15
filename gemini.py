import os
import google.generativeai as genai # pyright: ignore[reportMissingImports]

def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-pro')
    return None

def get_movie_recommendation(user_query, available_movies):
    model = setup_gemini()
    if not model:
        return "Gemini API is not configured. Please set GEMINI_API_KEY."
    
    movie_list_str = ", ".join([m.title for m in available_movies])
    
    prompt = f"""
    You are CineVault's AI assistant. Based on the user's request: "{user_query}",
    recommend movies from this list: {movie_list_str}.
    Return a brief, helpful response suggesting the best matches from the list. 
    If no movies match, politely say so. Do not recommend movies that are not on the list.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return f"Error communicating with AI: {str(e)}"
