import google.generativeai as genai
from django.conf import settings
from django.shortcuts import render
from .models import Review
import json
import re

genai.configure(api_key=settings.GEMINI_API_KEY)


def home(request):
    return render(request, "home.html")


def clean_ai_json(text):
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def generate_review(request):
    ai_review_text = None
    product_name = ""
    extra_input = ""
    rating = ""

    if request.method == "POST":
        product_name = request.POST.get("product_name", "").strip()
        extra_input = request.POST.get("extra_input", "").strip()
        rating = request.POST.get("rating", "").strip()

        if product_name and rating:
            prompt = f"""
                Write a detailed customer review for the product "{product_name}".
                Use the following additional details or context: "{extra_input}".
                Include the given rating: {rating}.
                Always include balanced pros and cons, even if the product is excellent.
                Structure the output in strict JSON format with these fields:
                - title: short review title
                - rating: integer {rating}
                - pros: list of pros (at least 3 items)
                - cons: list of cons (at least 3 items)
                - review: detailed review text
                Do NOT add markdown, code blocks, or extra text. ONLY output valid JSON containing ALL fields.
                """

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)

            cleaned_text = clean_ai_json(response.text)

            try:
                ai_review_text = json.loads(cleaned_text)

                # Save review to database
                Review.objects.create(
                    product_name=product_name,
                    extra_input=extra_input,
                    rating=int(ai_review_text.get("rating", rating)),
                    title=ai_review_text.get("title", ""),
                    pros=ai_review_text.get("pros", []),
                    cons=ai_review_text.get("cons", []),
                    review=ai_review_text.get("review", "")
                )

            except json.JSONDecodeError:
                ai_review_text = {
                    "error": "Failed to parse AI output.",
                    "raw": response.text
                }
        else:
            ai_review_text = {"error": "Please enter a product name and rating."}

    return render(request, "generate_review.html", {
        "ai_review_text": ai_review_text,
        "product_name": product_name,
        "extra_input": extra_input,
        "rating": rating
    })


def view_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')  # latest first
    return render(request, "view_reviews.html", {'reviews': reviews})
