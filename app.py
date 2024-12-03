from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from forms import RegistrationForm 
from models import User6KP, db 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

app = Flask(__name__)

db_config = {
    'user': 'j1007852',
    'password': 'el|N#2}-F8',
    'host': 'srv201-h-st.jino.ru',
    'database': 'j1007852_13423'
}

app = Flask(__name__)
app.config['SECRET_KEY'] = '96546538566692901865' 
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"

db.init_app(app)

# обработка ошибок и безопасный парсинг
def parse_divan_ru(category): 
    url = urljoin("https://divan.ru", f"/category/{category}") 
    try: 
        response = requests.get(url, timeout=10) 
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'html.parser') 
 
        product_items = soup.find_all("div", class_="LlPhw") 
 
        results = [] 
        for item in product_items: 
            name_element = item.find("a", class_="ui-GPFV8 qUioe ProductName ActiveProduct") 
            price_element = item.find("span", class_="ui-LD-ZU KIkOH")   
 
            if name_element and price_element: 
                name = name_element.text.strip() 
                price_match = re.search(r"(\d+\.?\d*)", price_element.text.replace(' ', ''))  
                price = price_match.group(1) if price_match else None 
                 
                if name and price:  
                    results.append({'name': name, 'price': price}) 
 
        return results 
    except requests.exceptions.RequestException as e: 
        print(f"Ошибка парсинга {url}: {e}") 
        return [] 
    except Exception as e: 
        print(f"Непредвиденная ошибка: {e}") 
        return [] 

@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User6KP(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Пользователь успешно зарегистрирован!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Ошибка регистрации!', 'error')

    if request.method == 'POST' and 'category' in request.form:
        category = request.form['category']
        results = parse_divan_ru(category)
        if results:
            return render_template('results.html', results=results)
        else:
            flash('Товары по данной категории не найдены.', 'warning')

    return render_template('index.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 