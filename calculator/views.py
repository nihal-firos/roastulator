# calculator/views.py

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from . import utils  # Import the new utils file

# --- Django Views ---

def index(request):
    """
    Renders the main calculator page.
    """
    return render(request, 'calculator/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def roast_api(request):
    """
    API endpoint to evaluate a math expression and get a roast.
    """
    try:
        data = json.loads(request.body)
        expression = data.get('expression')

        if not expression:
            return JsonResponse({'error': 'Expression not provided.'}, status=400)

        # Use the helper functions from utils.py
        try:
            result = utils.eval_expr(expression)
        except (ValueError, TypeError, ZeroDivisionError) as e:
            return JsonResponse({
                'error': str(e),
                'roast': "You broke the calculator. Are you proud of yourself?"
            }, status=400)

        complexity_score = utils.calculate_complexity(expression)
        complexity_level = utils.get_complexity_level(complexity_score)
        roast_message = utils.generate_roast(expression, complexity_score, complexity_level)

        return JsonResponse({
            'result': result,
            'roast': roast_message,
            'complexity_score': complexity_score,
            'complexity_level': complexity_level
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected server error occurred: {str(e)}'}, status=500)
