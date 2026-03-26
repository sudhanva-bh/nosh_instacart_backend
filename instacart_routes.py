"""
instacart_routes.py
--------------------
Flask Blueprint for proxying requests to the Instacart Developer Platform API.

Usage:
    from instacart_routes import instacart_bp
    app.register_blueprint(instacart_bp)
"""

import os
import requests
from flask import Blueprint, request, jsonify
instacart_bp = Blueprint("instacart", __name__, url_prefix="/api")

INSTACART_API_URL = "https://connect.dev.instacart.tools/idp/v1/products/products_link"


def _get_api_key() -> str:
    """
    Retrieve the Instacart API key from the environment.
    Raises RuntimeError if the key is not configured.
    """
    api_key = os.environ.get("INSTACART_API_KEY")
    if not api_key:
        raise RuntimeError(
            "INSTACART_API_KEY is not set. "
            "Add it to your .env file and ensure python-dotenv is loaded."
        )
    return api_key


@instacart_bp.route("/generate-instacart-list", methods=["POST"])
def generate_instacart_list():
    """
    POST /api/generate-instacart-list

    Accepts a JSON body:
    {
        "title":      "My Shopping List",          # required
        "link_type":  "shopping_list",             # optional, defaults to "shopping_list"
        "line_items": [                            # required
            { "name": "Apples", "quantity": 2, "unit": "each" },
            ...
        ]
    }

    Returns:
        200  { "products_link_url": "<url>" }
        400  { "error": "<validation message>" }
        502  { "error": "<upstream error message>" }
        500  { "error": "<internal error message>" }
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    title = body.get("title")
    if not title:
        return jsonify({"error": "'title' is required."}), 400

    line_items = body.get("line_items")
    if not line_items or not isinstance(line_items, list):
        return jsonify({"error": "'line_items' must be a non-empty array."}), 400

    link_type = body.get("link_type", "shopping_list")

    for idx, item in enumerate(line_items):
        for field in ("name", "quantity", "unit"):
            if field not in item:
                return (
                    jsonify(
                        {
                            "error": (
                                f"line_items[{idx}] is missing required field '{field}'."
                            )
                        }
                    ),
                    400,
                )

    instacart_payload = {
        "title": title,
        "link_type": link_type,
        "line_items": line_items,
    }

    try:
        api_key = _get_api_key()
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.post(
            INSTACART_API_URL,
            json=instacart_payload,
            headers=headers,
            timeout=10,  # seconds
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return (
            jsonify({"error": "Request to Instacart API timed out. Please retry."}),
            502,
        )
    except requests.exceptions.HTTPError as http_err:
        # Surface the upstream status code and body for easier debugging
        try:
            upstream_detail = response.json()
        except Exception:
            upstream_detail = response.text

        return (
            jsonify(
                {
                    "error": f"Instacart API returned an error: {http_err}",
                    "detail": upstream_detail,
                }
            ),
            502,
        )
    except requests.exceptions.RequestException as req_err:
        return (
            jsonify({"error": f"Failed to reach Instacart API: {req_err}"}),
            502,
        )

    data = response.json()
    products_link_url = data.get("products_link_url")

    if not products_link_url:
        return (
            jsonify(
                {
                    "error": "Instacart API response did not contain 'products_link_url'.",
                    "raw_response": data,
                }
            ),
            502,
        )

    return jsonify({"products_link_url": products_link_url}), 200
