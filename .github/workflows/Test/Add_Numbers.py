from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML = '''
<!doctype html>
<html lang="en">
  <head>
    <title>Add Two Numbers</title>
  </head>
  <body>
    <h2>Add Two Numbers</h2>
    <form method="post">
      <label>Enter the first number:</label>
      <input type="text" name="num1"><br><br>
      <label>Enter the second number:</label>
      <input type="text" name="num2"><br><br>
      <input type="submit" value="Add">
    </form>
    {% if result is not none %}
      <h3>The sum of {{ num1 }} and {{ num2 }} is: {{ result }}</h3>
    {% elif error %}
      <h3 style="color:red;">{{ error }}</h3>
    {% endif %}
  </body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def add_numbers():
    result = None
    error = None
    num1 = num2 = ''
    if request.method == 'POST':
        num1 = request.form.get('num1', '')
        num2 = request.form.get('num2', '')
        try:
            result = float(num1) + float(num2)
        except ValueError:
            error = 'Please enter valid numbers.'
    return render_template_string(HTML, result=result, num1=num1, num2=num2, error=error)

if __name__ == '__main__':
    app.run(debug=True)