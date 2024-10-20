# 로그인 페이지로 리다이렉트하는 '/' 경로
@app.route('/')
def index():
    return redirect(url_for('login'))

# 대시보드 경로
@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session['user_type'] != 'customer':
        flash("Please log in to access the dashboard.")
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'])
