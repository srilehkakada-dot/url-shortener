from flask import Flask, request, jsonify, redirect, render_template, abort
from database import init_db, add_link, get_link, get_all_links, delete_link, increment_clicks
import validators

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    long_url = data.get("url", "").strip()
    custom_alias = data.get("alias", "").strip().lower()

    if not long_url:
        return jsonify({"error": "URL is required."}), 400

    if not validators.url(long_url):
        return jsonify({"error": "Invalid URL. Please include https://."}), 400

    if custom_alias:
        if len(custom_alias) < 3:
            return jsonify({"error": "Alias must be at least 3 characters."}), 400
        if not custom_alias.replace("-", "").replace("_", "").isalnum():
            return jsonify({"error": "Alias can only contain letters, numbers, hyphens, and underscores."}), 400
        existing = get_link(custom_alias)
        if existing:
            return jsonify({"error": "This alias is already taken."}), 409

    code = add_link(long_url, custom_alias if custom_alias else None)
    short_url = request.host_url + code

    return jsonify({"short_url": short_url, "code": code}), 201


@app.route("/api/links", methods=["GET"])
def list_links():
    links = get_all_links()
    return jsonify(links)


@app.route("/api/links/<code>", methods=["DELETE"])
def remove_link(code):
    deleted = delete_link(code)
    if not deleted:
        return jsonify({"error": "Link not found."}), 404
    return jsonify({"message": "Link deleted."}), 200


@app.route("/<code>")
def redirect_to_url(code):
    link = get_link(code)
    if not link:
        abort(404)
    increment_clicks(code)
    return redirect(link["original_url"], code=302)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Short link not found."}), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)