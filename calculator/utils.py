# calculator/utils.py

import ast
import operator as op
import os
import google.generativeai as genai
from dotenv import load_dotenv  # Import the load_dotenv function

# --- Safe Expression Evaluation ---

# Supported operators
operators = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg
}

def eval_expr(expr):
    """
    Safely evaluates a string math expression.
    """
    try:
        return eval_(ast.parse(expr, mode='eval').body)
    except (TypeError, SyntaxError, KeyError, ZeroDivisionError) as e:
        # Re-raise known safe exceptions to be caught by the view
        raise ValueError(f"Invalid or unsafe expression: {e}")
    except Exception:
        # Catch any other unexpected errors
        raise ValueError("An unexpected error occurred during evaluation.")


def eval_(node):
    """
    Recursively evaluates an abstract syntax tree node.
    """
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        # Raise an error for any unsupported node types (like function calls, etc.)
        raise TypeError(f"Unsupported type: {type(node).__name__}")

# --- Complexity Scoring ---

def calculate_complexity(expr):
    """
    Calculates a complexity score for a given math expression.
    """
    score = 0
    try:
        tree = ast.parse(expr)
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                score += 1
                if isinstance(node.op, (ast.Mult, ast.Div)):
                    score += 1 
            if isinstance(node, ast.Pow):
                score += 3
        # Add points for length and parentheses
        score += len(expr) // 5
        score += expr.count('(') * 2
        return score
    except (SyntaxError, ValueError):
        return 0

def get_complexity_level(score):
    """
    Categorizes the complexity score into a human-readable level.
    """
    if score <= 3:
        return "Very Simple"
    elif score <= 7:
        return "Easy"
    elif score <= 12:
        return "Moderate"
    elif score <= 20:
        return "Hard"
    else:
        return "Very Hard"

# --- Gemini API Integration ---

def generate_roast(expression, complexity_score, complexity_level):
    """
    Generates a roast message using the Gemini API.
    """
    load_dotenv()  # Load variables from the .env file
    api_key = os.getenv("GOOGLE_API_KEY") # Use os.getenv which is equivalent to os.environ.get
    if not api_key:
        return "API key not configured. The developer is probably getting roasted for this."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # UPDATED: The tone map now uses creative personas for more variety.
    tone_map = {
        "Very Simple": "Act like a dramatic supervillain who is offended by how basic this math is.",
        "Easy": "Act like a sassy comedian. Use witty one-liners and rhetorical questions to mock their need for a calculator.",
        "Moderate": "Act like a bored, genius teenager who is forced to help with homework. Be condescending and a little bit lazy.",
        "Hard": "Act like a pirate who just found treasure, but the treasure is this math problem. Be sarcastically impressed and use pirate slang.",
        "Very Hard": "Act like a space AI from the future that finds human math quaint and adorable. Be patronizingly impressed, as if talking to a clever pet."
    }
    
    roast_style = tone_map.get(complexity_level, "sarcastic")

    prompt = f"""
    You are the "Roastulator," a calculator with a sharp wit. Your goal is to generate a funny, clever, and unique roast for every user. Avoid repeating yourself.
    
    Adopt the following persona for your roast: "{roast_style}"

    Generate a short roast (1-2 sentences) based on this persona and the user's math problem.

    Math Expression: "{expression}"
    Complexity Level: {complexity_level}

    Return ONLY the roast text. Do not add any extra commentary or greetings.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "My circuits sizzled trying to come up with a roast. I guess you win this round."
