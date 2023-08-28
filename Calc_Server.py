from flask import Flask, request, jsonify, render_template_string
import sqlite3
calc = Flask(__name__)
conn = sqlite3.connect('calc_operations.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        expression TEXT,
        result REAL
    )
''')
conn.commit()
conn.close()
@calc.route('/')
def home():
    return """
    <h1>Welcome to the Calculator Server!</h1>
    <h2>Available Requests:</h2>
    <ul>
        <li><a href="/history">/history</a> - View the last 20 operations</li>
        <li>Perform calculations in this format:
            <ul>
                <li><a href="/5/plus/3">/5/plus/3</a></li>
                <!-- ... (similar lines for other operations) ... -->
            </ul>
        </li>
    </ul>
    """
@calc.route('/<path:expression>', methods=['GET'])
def calculate(expression):
    operations = expression.split('/')
    question = str(float(operations[0]))
    answer = None
    try:
        result = float(operations[0])
        for i in range(1, len(operations), 2):
            operator = operations[i]
            operand = float(operations[i + 1])
            if operator == 'plus':
                result += operand
                question += "+" + str(operand)
            elif operator == 'minus':
                result -= operand
                question += "-" + str(operand)
            elif operator == 'into':
                result *= operand
                question += "*" + str(operand)
            elif operator == 'by':
                result /= operand
                question += "/" + str(operand)
            else:
                return "Invalid Expression", 400
        answer = result
    except Exception as e:
        return f"Error: {str(e)}", 400
    conn = sqlite3.connect('calc_operations.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO history (expression, result) VALUES (?, ?)', (question, answer))
    conn.commit()
    conn.close()
    return jsonify({"Question" : question , "Answer" : answer})
@calc.route('/history')
def history():
    conn = sqlite3.connect('calc_operations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT expression, result FROM history ORDER BY id DESC LIMIT 20')
    history_data = cursor.fetchall()
    conn.close()
    history_html = "<h1>Operation History:</h1><ul>"
    for operation in history_data:
        history_html += f"<li>{operation[0]} = {operation[1]}</li>"
    history_html += "</ul>"
    return render_template_string(history_html)
calc.run(host='localhost', port=3000)
