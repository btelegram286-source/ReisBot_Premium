import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from github_manager import GitHubManager
from render_manager import RenderManager
import telebot
from flask_login import login_required

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def dashboard():
    """Render the dashboard page."""
    return render_template("dashboard.html")

@app.route("/start_bot", methods=["GET"])
def start_bot():
    """Start the Telegram bot."""
    if bot:
        try:
            bot.polling(none_stop=True)
            flash("Bot başlatıldı!", "success")
        except Exception as e:
            logger.error(f"Bot başlatma hatası: {e}")
            flash("Bot başlatılamadı!", "danger")
    else:
        flash("Bot tanımlı değil veya BOT_TOKEN eksik.", "warning")
    return redirect(url_for("dashboard"))

@app.route("/upload_zip", methods=["POST"])
@login_required
def upload_zip():
    """Upload a zip file to GitHub."""
    zip_file_path = request.form.get("zip_file_path")
    repo_name = request.form.get("repo_name")
    
    if not zip_file_path or not repo_name:
        flash("Zip dosyası yolu ve repo adı gerekli.", "warning")
        return redirect(url_for("dashboard"))
    
    result = github_manager.upload_zip_to_repo(repo_name, zip_file_path)
    flash(result, "info")
    return redirect(url_for("dashboard"))
