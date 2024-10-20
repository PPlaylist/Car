from flask import Flask, render_template, request, redirect, url_for, session, flash

# Flask 애플리케이션 인스턴스 생성
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 세션을 사용하기 위한 비밀 키

# 로그인 페이지로 리다이렉트하는 '/' 경로
@app.route('/')
def index():
    return redirect(url_for('login'))

# 가상 데이터베이스로 사용할 딕셔너리 (유저와 딜러 목록)
users = {
    "customer": [],
    "dealer": []
}

# 차량 정보
vehicles = {
    "5XYP3DHC9NG310533": {
        "owner": "John Doe",
        "email": "johndoe@example.com",
        "phone": "555-1234",
        "card": "1234-5678-9876-5432",
        "vin": "5XYP3DHC9NG310533",
        "location": "New York, NY",
        "status": "locked",
        "engine": "off",
        "horn": "off",
        "lights": "off",
        "camera": "off",
        "trunk": "closed",
        "clarkson": "off",
        "blinkers": "off"
    },
    "1HGCM82633A004352": {  # 두 번째 차량 정보
        "owner": "Jane Smith",
        "email": "janesmith@example.com",
        "phone": "555-5678",
        "card": "9876-5432-1234-5678",
        "vin": "1HGCM82633A004352",
        "location": "Los Angeles, CA",
        "status": "unlocked",
        "engine": "on",
        "horn": "off",
        "lights": "on",
        "camera": "off",
        "trunk": "open",
        "clarkson": "off",
        "blinkers": "on"
    }
}

# 1. 정상적인 유저 회원가입 페이지
@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        vin = request.form['vin']  # VIN 번호 추가
        phone = request.form['phone']  # 전화번호 추가

        # 중복 사용자 확인
        if any(user['username'] == username for user in users['customer']):
            flash("Username already exists!")
            return redirect(url_for('user_register'))

        # 유저 추가 (VIN 번호와 전화번호 포함)
        users["customer"].append({
            "username": username,
            "password": password,
            "email": email,
            "vin": vin,  # VIN 번호 저장
            "phone": phone  # 전화번호 저장
        })

        flash("User registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('user_register.html')

# 2. 딜러 정상적인 회원가입 불가 페이지
@app.route('/dealer/register', methods=['GET', 'POST'])
def dealer_register_denied():
    return render_template('dealer_access_denied.html')

# 3. 딜러 비정상적인 URL로만 접근 가능 (특정 URL에서만 가입 가능)
@app.route('/dealer/special-register', methods=['GET', 'POST'])
def dealer_register_special():
    token = request.args.get('token')
    if token != 'dealerspecialtoken':
        return "Unauthorized access to dealer registration.", 403

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # 중복 사용자 확인
        if any(user['username'] == username for user in users['dealer']):
            flash("Username already exists!")
            return redirect(url_for('dealer_register_special', token=token))

        # 딜러 추가
        users["dealer"].append({
            "username": username,
            "password": password,
            "email": email
        })

        flash("Dealer registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('dealer_register.html')

# 4. 딜러 모드: 차량 정보 탈취 및 원격 제어 (자동으로 조회)
@app.route('/dealer/exploit', methods=['GET'])
def dealer_exploit():
    if 'username' not in session or session['user_type'] != 'dealer':
        return redirect(url_for('login'))

    # 모든 차량 정보를 자동으로 조회
    vehicle_list = vehicles.values()  # 등록된 모든 차량 정보를 조회

    return render_template('dealer_exploit.html', vehicles=vehicle_list)

# 로그인 페이지 (유저 및 딜러 모두 사용)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 유저 확인
        user_type = None
        for user in users["customer"]:
            if user['username'] == username and user['password'] == password:
                user_type = 'customer'
                break
        for user in users["dealer"]:
            if user['username'] == username and user['password'] == password:
                user_type = 'dealer'
                break

        if user_type:
            session['username'] = username
            session['user_type'] = user_type
            flash(f"Welcome, {username}! You are logged in as a {user_type}.")
            if user_type == 'dealer':
                return redirect(url_for('dealer_exploit'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!")
            return redirect(url_for('login'))
    return render_template('login.html')

# 유저 대시보드 (정상적인 로그인 후 유저가 접근)
@app.route('/dashboard')
def dashboard():
    if 'username' not in session or session['user_type'] != 'customer':
        flash("Please log in to access the dashboard.")
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'])

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
