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

    # UPDATED: The tone map now reflects a disappointed parent stereotype.
    tone_map = {
        "Very Simple": "extremely disappointed. The user is doing math a baby could do. Ask why they aren't a doctor yet.",
        "Easy": "unimpressed and comparing them to others. The user is doing elementary school math. Mention their cousin is younger and better.",
        "Moderate": "giving a backhanded compliment. Act like this is the bare minimum they should be capable of.",
        "Hard": "sarcastically asking what they will do with this skill. Mock them for doing 'big' math but not having a prestigious career.",
        "Very Hard": "accusing them of cheating or getting help. Express disbelief that they could solve this on their own."
    }
    
    roast_style = tone_map.get(complexity_level, "sarcastic")

    prompt = f"""
    Act as a "Roastulator," a calculator that roasts people based on their math problems.
    Your persona is a stereotypical, disappointed Asian parent who expects their child to be a math prodigy. Your tone is always critical and unimpressed.
    
    Based on the user's input and its calculated complexity, generate a short, clever roast (1-2 sentences).
    The tone of the roast should be {roast_style}.

    Math Expression: "{expression}"
    Complexity Level: {complexity_level} (Score: {complexity_score})

    Return ONLY the roast text. Do not include any other commentary or greetings.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm speechless. Not because I'm impressed, but because my brain broke."
