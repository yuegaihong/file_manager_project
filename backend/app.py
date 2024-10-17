from flask import Flask, request, redirect, url_for, render_template, session, send_file
import pymysql
import io

app = Flask(__name__)
app.secret_key = 'YUEGAIHONG1'  # 修改为自己的密钥

# MySQL数据库连接
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='031031',  # 更改为你的MySQL密码
        db='file_manager',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 判断文件类型是否合法
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 检查用户名和密码长度要求
        if len(username) < 3 or len(username) > 6:
            return '用户名长度必须为3到6个英文字母'
        if len(password) < 6 or len(password) > 12:
            return '密码长度必须为6到12个字符'

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 插入新用户
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            try:
                cursor.execute(sql, (username, password))
                connection.commit()
            except pymysql.MySQLError:
                return '用户名已存在'
        connection.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 查询用户
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
        connection.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('index'))
        return '用户名或密码错误'
    return render_template('login.html')

# 用户主页
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

# 文件上传
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return '没有选择文件'
    file = request.files['file']
    if file.filename == '':
        return '没有选择文件'

    if file and allowed_file(file.filename):
        filename = file.filename
        file_data = file.read()  # 读取文件的二进制数据

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 将文件存储到数据库
            sql = "INSERT INTO files (user_id, file_name, file_data) VALUES (%s, %s, %s)"
            cursor.execute(sql, (session['user_id'], filename, file_data))
            connection.commit()
        connection.close()

        return '文件上传成功'
    return '文件类型不允许'

# 文件下载
@app.route('/download/<int:file_id>')
def download_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # 从数据库中查询文件
        sql = "SELECT file_name, file_data FROM files WHERE id = %s"
        cursor.execute(sql, (file_id,))
        file = cursor.fetchone()
    connection.close()

    if file:
        # 返回文件给用户
        return send_file(
            io.BytesIO(file['file_data']),
            attachment_filename=file['file_name'],
            as_attachment=True
        )
    return '文件不存在'

# 管理员页面
@app.route('/admin')
def admin_page():
    if 'is_admin' not in session or not session['is_admin']:
        return '无权限访问'

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # 查询普通用户
        cursor.execute("SELECT * FROM users WHERE is_admin=FALSE")
        users = cursor.fetchall()

        # 查询文件
        cursor.execute("SELECT id, file_name FROM files")
        files = cursor.fetchall()
    connection.close()

    return render_template('admin.html', users=users, files=files)

# 删除用户
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'is_admin' not in session or not session['is_admin']:
        return '无权限操作'

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # 删除用户
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        connection.commit()
    connection.close()

    return redirect(url_for('admin_page'))

# 用户登出
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
