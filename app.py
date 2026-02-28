from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, HealthData, UserPreference, Restaurant, MenuItem, CartItem, HealthCondition
from ml_recommender import FoodRecommender
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

recommender = FoodRecommender()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all()

        if Restaurant.query.first():
            return

        restaurants_data = [
            {'name': 'Saravana Bhavan','cuisine_type': 'South Indian (Tamil)','rating': 4.6,
             'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400',
             'description': 'Iconic vegetarian South Indian cuisine with authentic flavors'},
            {'name': 'Adyar Ananda Bhavan (A2B)','cuisine_type': 'South Indian (Tamil)','rating': 4.5,
             'image_url': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400',
             'description': 'Popular sweets and tiffin with wholesome meals'},
            {'name': 'Sangeetha Veg Restaurant','cuisine_type': 'South Indian (Tamil)','rating': 4.4,
             'image_url': 'https://images.unsplash.com/photo-1604908177072-df6f4b595b97?w=400',
             'description': 'Vegetarian South Indian staples and comfort food'},
            {'name': 'Murugan Idli Shop','cuisine_type': 'South Indian (Tamil)','rating': 4.5,
             'image_url': 'https://images.unsplash.com/photo-1625944525886-4b0f2b5756fa?w=400',
             'description': 'Soft idlis, dosas, podis, and traditional chutneys'},
            {'name': 'MTR - Mavalli Tiffin Room','cuisine_type': 'South Indian (Karnataka)','rating': 4.7,
             'image_url': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
             'description': 'Heritage Karnataka tiffin and meals since 1924'},
            {'name': 'Anjappar Chettinad','cuisine_type': 'South Indian (Chettinad)','rating': 4.3,
             'image_url': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=400',
             'description': 'Chettinad non-vegetarian specialties and spicy curries'},
            {'name': 'Nandhini Andhra','cuisine_type': 'South Indian (Andhra)','rating': 4.4,
             'image_url': 'https://images.unsplash.com/photo-1625944525886-4b0f2b5756fa?w=400',
             'description': 'Andhra meals, gongura flavors, and biryanis'},
            {'name': 'Udupi Sri Krishna','cuisine_type': 'South Indian (Udupi)','rating': 4.5,
             'image_url': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
             'description': 'Udupi classics: dosas, sambar rice, and temple food'},
            {'name': 'Kerala House','cuisine_type': 'South Indian (Kerala)','rating': 4.6,
             'image_url': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=400',
             'description': 'Kerala appam, stew, fish curry, and coconut-rich dishes'},
            {'name': 'The Dakshin Table','cuisine_type': 'South Indian (Multi-region)','rating': 4.4,
             'image_url': 'https://images.unsplash.com/photo-1604908177072-df6f4b595b97?w=400',
             'description': 'Millet-forward South Indian plates and beverages'},
        ]

        menu_items_data = {
            'Saravana Bhavan': [
                {'name':'Idli Sambar (2 pcs)','description':'Steamed rice cakes with sambar & chutney','price':89.0,'calories':300,'protein':10,'carbs':54,'fats':5,'fiber':6,'sugar':6,'sodium':620,'saturated_fat':1.5,'cholesterol':0,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'Medium'},
                {'name':'Medu Vada Sambar (2 pcs)','description':'Crisp lentil doughnuts with sambar','price':99.0,'calories':420,'protein':12,'carbs':40,'fats':22,'fiber':8,'sugar':4,'sodium':700,'saturated_fat':4,'cholesterol':0,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Masala Dosa','description':'Crispy dosa with spiced potato masala','price':129.0,'calories':520,'protein':12,'carbs':70,'fats':18,'fiber':6,'sugar':4,'sodium':680,'saturated_fat':6,'cholesterol':0,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Ghee Roast Dosa','description':'Crispy dosa roasted with ghee','price':149.0,'calories':600,'protein':10,'carbs':72,'fats':24,'fiber':5,'sugar':4,'sodium':650,'saturated_fat':10,'cholesterol':30,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Ven Pongal + Sambar','description':'Rice-lentil porridge with sambar','price':109.0,'calories':380,'protein':12,'carbs':55,'fats':10,'fiber':5,'sugar':4,'sodium':650,'saturated_fat':3,'cholesterol':5,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Lemon Rice','description':'Tangy tempered rice with peanuts','price':119.0,'calories':450,'protein':8,'carbs':70,'fats':14,'fiber':5,'sugar':4,'sodium':700,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Curd Rice','description':'Yogurt rice tempered with spices','price':119.0,'calories':420,'protein':12,'carbs':58,'fats':12,'fiber':2,'sugar':7,'sodium':620,'saturated_fat':6,'cholesterol':20,'is_vegetarian':True,'category':'Rice','glycemic_index':'Medium'},
                {'name':'Vegetable Uttapam','description':'Thick dosa topped with mixed veggies','price':129.0,'calories':420,'protein':12,'carbs':62,'fats':12,'fiber':7,'sugar':6,'sodium':640,'saturated_fat':3,'cholesterol':0,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Rava Kesari','description':'Semolina dessert with ghee & sugar','price':79.0,'calories':300,'protein':5,'carbs':50,'fats':10,'fiber':2,'sugar':24,'sodium':120,'saturated_fat':4,'cholesterol':15,'is_vegetarian':True,'category':'Dessert','glycemic_index':'High'},
                {'name':'Filter Coffee','description':'South Indian coffee with milk','price':35.0,'calories':60,'protein':2,'carbs':8,'fats':2,'fiber':0,'sugar':6,'sodium':40,'saturated_fat':1,'cholesterol':5,'is_vegetarian':True,'category':'Beverage','glycemic_index':'Low'},
            ],
            'Adyar Ananda Bhavan (A2B)': [
                {'name':'Mini Tiffin','description':'Idli, vada, pongal, small dosa & coffee','price':199.0,'calories':680,'protein':20,'carbs':98,'fats':24,'fiber':10,'sugar':10,'sodium':1100,'saturated_fat':8,'cholesterol':35,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'High'},
                {'name':'Ragi Dosa','description':'Finger millet dosa with chutney & sambar','price':129.0,'calories':360,'protein':12,'carbs':48,'fats':10,'fiber':8,'sugar':3,'sodium':520,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'is_diabetic_friendly':True,'category':'Breakfast','glycemic_index':'Low'},
                {'name':'Podi Dosa','description':'Dosa dusted with spicy podi & ghee','price':139.0,'calories':560,'protein':12,'carbs':70,'fats':20,'fiber':6,'sugar':4,'sodium':680,'saturated_fat':7,'cholesterol':15,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Poori Masala','description':'Deep-fried bread with potato masala','price':129.0,'calories':520,'protein':10,'carbs':62,'fats':20,'fiber':5,'sugar':4,'sodium':780,'saturated_fat':5,'cholesterol':10,'is_vegetarian':True,'category':'Bread','glycemic_index':'High'},
                {'name':'Veg Thali (Meals)','description':'Assorted curries, dal, rice, roti, dessert','price':249.0,'calories':780,'protein':24,'carbs':105,'fats':26,'fiber':12,'sugar':14,'sodium':1200,'saturated_fat':8,'cholesterol':35,'is_vegetarian':True,'category':'Main','glycemic_index':'High'},
                {'name':'Sambar Rice','description':'Rice mixed with hearty sambar','price':119.0,'calories':430,'protein':12,'carbs':68,'fats':8,'fiber':8,'sugar':6,'sodium':640,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Tamarind Rice (Puliyodarai)','description':'Spiced tamarind-flavored rice','price':119.0,'calories':460,'protein':8,'carbs':72,'fats':12,'fiber':5,'sugar':6,'sodium':700,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Mysore Pak','description':'Ghee-rich chickpea flour sweet','price':99.0,'calories':360,'protein':6,'carbs':44,'fats':18,'fiber':2,'sugar':28,'sodium':90,'saturated_fat':10,'cholesterol':25,'is_vegetarian':True,'category':'Dessert','glycemic_index':'High'},
                {'name':'Buttermilk','description':'Spiced chilled buttermilk (chaas)','price':45.0,'calories':70,'protein':4,'carbs':8,'fats':2,'fiber':0,'sugar':5,'sodium':180,'saturated_fat':1,'cholesterol':5,'is_vegetarian':True,'is_low_sodium':True,'category':'Beverage','glycemic_index':'Low'},
                {'name':'Idiyappam with Kurma','description':'String hoppers with vegetable kurma','price':149.0,'calories':420,'protein':10,'carbs':68,'fats':10,'fiber':5,'sugar':4,'sodium':620,'saturated_fat':4,'cholesterol':10,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
            ],
            'Sangeetha Veg Restaurant': [
                {'name':'Onion Rava Dosa','description':'Semolina dosa with onions','price':139.0,'calories':520,'protein':12,'carbs':70,'fats':18,'fiber':5,'sugar':4,'sodium':700,'saturated_fat':6,'cholesterol':5,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Paper Roast Dosa','description':'Ultra-thin crispy dosa','price':149.0,'calories':520,'protein':10,'carbs':72,'fats':16,'fiber':4,'sugar':3,'sodium':660,'saturated_fat':5,'cholesterol':0,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Ghee Pongal','description':'Rice-lentil pongal finished with ghee','price':119.0,'calories':420,'protein':12,'carbs':56,'fats':12,'fiber':5,'sugar':4,'sodium':650,'saturated_fat':5,'cholesterol':10,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Parotta with Veg Kurma','description':'Layered bread with mixed veg kurma','price':159.0,'calories':600,'protein':12,'carbs':72,'fats':22,'fiber':6,'sugar':6,'sodium':780,'saturated_fat':8,'cholesterol':15,'is_vegetarian':True,'category':'Bread','glycemic_index':'High'},
                {'name':'Vegetable Kurma','description':'Coconut-based mixed vegetable curry','price':129.0,'calories':320,'protein':8,'carbs':20,'fats':22,'fiber':6,'sugar':6,'sodium':620,'saturated_fat':10,'cholesterol':0,'is_vegetarian':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Bisibelebath','description':'Lentil, rice, veggie hot pot','price':129.0,'calories':460,'protein':14,'carbs':72,'fats':10,'fiber':8,'sugar':6,'sodium':700,'saturated_fat':3,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Rasam Rice','description':'Light tangy rasam mixed with rice','price':109.0,'calories':380,'protein':8,'carbs':66,'fats':6,'fiber':5,'sugar':5,'sodium':580,'saturated_fat':1,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Plain Dosa','description':'Classic fermented dosa','price':99.0,'calories':420,'protein':8,'carbs':68,'fats':10,'fiber':4,'sugar':3,'sodium':560,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Sweet Lassi','description':'Yogurt-based sweet drink','price':79.0,'calories':220,'protein':6,'carbs':34,'fats':6,'fiber':0,'sugar':28,'sodium':140,'saturated_fat':4,'cholesterol':20,'is_vegetarian':True,'category':'Beverage','glycemic_index':'High'},
                {'name':'Semiya Payasam','description':'Vermicelli milk pudding','price':89.0,'calories':320,'protein':6,'carbs':48,'fats':10,'fiber':1,'sugar':30,'sodium':120,'saturated_fat':6,'cholesterol':25,'is_vegetarian':True,'category':'Dessert','glycemic_index':'High'},
            ],
            'Murugan Idli Shop': [
                {'name':'Idli (3 pcs)','description':'Soft idlis with chutneys & sambar','price':99.0,'calories':420,'protein':14,'carbs':81,'fats':5,'fiber':8,'sugar':7,'sodium':700,'saturated_fat':1.5,'cholesterol':0,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'Medium'},
                {'name':'Podi Idli','description':'Idlis tossed with spiced podi & ghee','price':119.0,'calories':460,'protein':14,'carbs':80,'fats':10,'fiber':8,'sugar':7,'sodium':720,'saturated_fat':5,'cholesterol':10,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Curry Leaf Rice','description':'Tempered rice with fresh curry leaves','price':129.0,'calories':440,'protein':8,'carbs':70,'fats':12,'fiber':6,'sugar':4,'sodium':640,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Idiyappam + Coconut Milk','description':'String hoppers with coconut milk','price':149.0,'calories':460,'protein':8,'carbs':76,'fats':12,'fiber':5,'sugar':7,'sodium':520,'saturated_fat':9,'cholesterol':5,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Kothu Parotta (Veg)','description':'Shredded parotta stir-fry with veggies','price':169.0,'calories':640,'protein':12,'carbs':82,'fats':24,'fiber':6,'sugar':6,'sodium':820,'saturated_fat':8,'cholesterol':15,'is_vegetarian':True,'category':'Bread','glycemic_index':'High'},
                {'name':'Kambu (Pearl Millet) Dosa','description':'Millet dosa with chutney','price':129.0,'calories':340,'protein':12,'carbs':44,'fats':10,'fiber':8,'sugar':3,'sodium':500,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'is_diabetic_friendly':True,'category':'Breakfast','glycemic_index':'Low'},
                {'name':'Sambar Vada','description':'Lentil vada soaked in sambar','price':109.0,'calories':380,'protein':12,'carbs':38,'fats':18,'fiber':8,'sugar':4,'sodium':680,'saturated_fat':4,'cholesterol':0,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Lemon Sevai','description':'Seasoned rice noodles','price':119.0,'calories':420,'protein':8,'carbs':68,'fats':10,'fiber':4,'sugar':4,'sodium':600,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'High'},
                {'name':'Thayir Vadai','description':'Curd-based chilled vada','price':109.0,'calories':360,'protein':10,'carbs':36,'fats':16,'fiber':4,'sugar':7,'sodium':560,'saturated_fat':6,'cholesterol':20,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Sukku Malli Coffee','description':'Dry ginger & coriander coffee','price':40.0,'calories':50,'protein':1,'carbs':7,'fats':1,'fiber':0,'sugar':5,'sodium':30,'saturated_fat':0.5,'cholesterol':0,'is_vegetarian':True,'is_low_sodium':True,'category':'Beverage','glycemic_index':'Low'},
            ],
            'MTR - Mavalli Tiffin Room': [
                {'name':'Rava Idli','description':'Semolina idli with chutney','price':109.0,'calories':320,'protein':10,'carbs':48,'fats':10,'fiber':5,'sugar':4,'sodium':560,'saturated_fat':3,'cholesterol':5,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'Medium'},
                {'name':'Benne Masala Dosa','description':'Butter-laden masala dosa','price':159.0,'calories':620,'protein':12,'carbs':72,'fats':24,'fiber':6,'sugar':4,'sodium':700,'saturated_fat':10,'cholesterol':30,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Bisibelebath','description':'Karnataka-style lentil rice','price':129.0,'calories':460,'protein':14,'carbs':72,'fats':10,'fiber':8,'sugar':6,'sodium':680,'saturated_fat':3,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Mangalore Buns','description':'Sweet banana puri','price':129.0,'calories':480,'protein':8,'carbs':72,'fats':16,'fiber':4,'sugar':14,'sodium':540,'saturated_fat':4,'cholesterol':10,'is_vegetarian':True,'category':'Bread','glycemic_index':'High'},
                {'name':'Akki Rotti','description':'Rice roti with chutney','price':119.0,'calories':360,'protein':8,'carbs':58,'fats':10,'fiber':6,'sugar':3,'sodium':560,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Bread','glycemic_index':'High'},
                {'name':'Avalakki (Poha)','description':'Beaten rice with peanuts & spices','price':119.0,'calories':380,'protein':8,'carbs':66,'fats':10,'fiber':6,'sugar':5,'sodium':560,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Kesari Bath','description':'Semolina-saffron dessert','price':89.0,'calories':320,'protein':5,'carbs':52,'fats':10,'fiber':2,'sugar':28,'sodium':120,'saturated_fat':4,'cholesterol':15,'is_vegetarian':True,'category':'Dessert','glycemic_index':'High'},
                {'name':'Poori Sagu','description':'Poori with mixed veg sagu','price':139.0,'calories':540,'protein':10,'carbs':64,'fats':20,'fiber':6,'sugar':6,'sodium':720,'saturated_fat':5,'cholesterol':10,'is_vegetarian':True,'category':'Bread','glycemic_index':'High'},
                {'name':'Filter Coffee','description':'Strong decoction coffee','price':45.0,'calories':60,'protein':2,'carbs':8,'fats':2,'fiber':0,'sugar':6,'sodium':40,'saturated_fat':1,'cholesterol':5,'is_vegetarian':True,'category':'Beverage','glycemic_index':'Low'},
                {'name':'Curd Rice','description':'Karnataka-style yogurt rice','price':119.0,'calories':420,'protein':12,'carbs':58,'fats':12,'fiber':2,'sugar':7,'sodium':620,'saturated_fat':6,'cholesterol':20,'is_vegetarian':True,'category':'Rice','glycemic_index':'Medium'},
            ],
            'Anjappar Chettinad': [
                {'name':'Chicken Chettinad','description':'Roasted spices chicken curry','price':249.0,'calories':380,'protein':34,'carbs':12,'fats':20,'fiber':4,'sugar':3,'sodium':700,'saturated_fat':6,'cholesterol':110,'is_vegetarian':False,'is_low_carb':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Mutton Sukka','description':'Dry-fried spiced mutton','price':279.0,'calories':420,'protein':32,'carbs':10,'fats':26,'fiber':3,'sugar':2,'sodium':680,'saturated_fat':10,'cholesterol':120,'is_vegetarian':False,'is_low_carb':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Fish Fry (Meen Varuval)','description':'Shallow-fried spiced fish','price':249.0,'calories':420,'protein':32,'carbs':12,'fats':24,'fiber':2,'sugar':1,'sodium':620,'saturated_fat':6,'cholesterol':95,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Prawn Masala','description':'Tiger prawn in spicy masala','price':269.0,'calories':360,'protein':28,'carbs':10,'fats':18,'fiber':2,'sugar':2,'sodium':640,'saturated_fat':4,'cholesterol':160,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Egg Curry','description':'Boiled eggs in spiced gravy','price':179.0,'calories':320,'protein':18,'carbs':10,'fats':20,'fiber':3,'sugar':3,'sodium':640,'saturated_fat':5,'cholesterol':240,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Kothu Parotta (Chicken)','description':'Shredded parotta with egg & chicken','price':229.0,'calories':680,'protein':28,'carbs':68,'fats':28,'fiber':6,'sugar':6,'sodium':860,'saturated_fat':9,'cholesterol':160,'is_vegetarian':False,'category':'Bread','glycemic_index':'High'},
                {'name':'Chicken Biryani (Chettinad)','description':'Seeraga samba rice biryani','price':259.0,'calories':620,'protein':28,'carbs':68,'fats':22,'fiber':4,'sugar':4,'sodium':880,'saturated_fat':8,'cholesterol':95,'is_vegetarian':False,'category':'Rice','glycemic_index':'High'},
                {'name':'Crab Masala','description':'Crab cooked in Chettinad spices','price':299.0,'calories':380,'protein':30,'carbs':8,'fats':22,'fiber':2,'sugar':2,'sodium':700,'saturated_fat':6,'cholesterol':140,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Pepper Chicken','description':'Black pepper tempered chicken','price':239.0,'calories':360,'protein':32,'carbs':8,'fats':18,'fiber':2,'sugar':2,'sodium':640,'saturated_fat':4,'cholesterol':110,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Lemon Soda','description':'Sparkling lemon drink','price':50.0,'calories':80,'protein':0,'carbs':20,'fats':0,'fiber':0,'sugar':20,'sodium':70,'saturated_fat':0,'cholesterol':0,'is_vegetarian':True,'category':'Beverage','glycemic_index':'High'},
            ],
            'Nandhini Andhra': [
                {'name':'Andhra Veg Meals','description':'Rice, dal, curries, chutney, fryums','price':239.0,'calories':780,'protein':22,'carbs':110,'fats':24,'fiber':12,'sugar':10,'sodium':1200,'saturated_fat':8,'cholesterol':15,'is_vegetarian':True,'category':'Main','glycemic_index':'High'},
                {'name':'Gongura Chicken','description':'Tangy sorrel leaf chicken curry','price':249.0,'calories':380,'protein':34,'carbs':12,'fats':20,'fiber':4,'sugar':3,'sodium':720,'saturated_fat':6,'cholesterol':110,'is_vegetarian':False,'is_low_carb':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Hyderabadi Egg Curry','description':'Eggs simmered in spicy gravy','price':179.0,'calories':340,'protein':18,'carbs':10,'fats':22,'fiber':3,'sugar':3,'sodium':660,'saturated_fat':6,'cholesterol':240,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Pesarattu (Green Gram Dosa)','description':'Moong dal dosa with ginger chutney','price':129.0,'calories':360,'protein':16,'carbs':46,'fats':10,'fiber':8,'sugar':3,'sodium':500,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'is_diabetic_friendly':True,'category':'Breakfast','glycemic_index':'Low'},
                {'name':'Ulavacharu Rice','description':'Horse gram rasam mixed with rice','price':139.0,'calories':440,'protein':12,'carbs':70,'fats':10,'fiber':8,'sugar':5,'sodium':620,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Andhra Chicken Biryani','description':'Spicy biryani with chicken','price':259.0,'calories':640,'protein':30,'carbs':70,'fats':24,'fiber':4,'sugar':5,'sodium':920,'saturated_fat':9,'cholesterol':110,'is_vegetarian':False,'category':'Rice','glycemic_index':'High'},
                {'name':'Mirchi Bajji','description':'Stuffed & fried green chili fritters','price':99.0,'calories':360,'protein':8,'carbs':36,'fats':20,'fiber':6,'sugar':3,'sodium':540,'saturated_fat':3,'cholesterol':0,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Curd Rice','description':'Yogurt rice with tempering','price':119.0,'calories':420,'protein':12,'carbs':58,'fats':12,'fiber':2,'sugar':7,'sodium':620,'saturated_fat':6,'cholesterol':20,'is_vegetarian':True,'category':'Rice','glycemic_index':'Medium'},
                {'name':'Tomato Pappu','description':'Andhra tomato dal','price':119.0,'calories':280,'protein':14,'carbs':28,'fats':8,'fiber':8,'sugar':6,'sodium':540,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Buttermilk (Majjiga)','description':'Lightly spiced buttermilk','price':45.0,'calories':70,'protein':4,'carbs':8,'fats':2,'fiber':0,'sugar':5,'sodium':180,'saturated_fat':1,'cholesterol':5,'is_vegetarian':True,'is_low_sodium':True,'category':'Beverage','glycemic_index':'Low'},
            ],
            'Udupi Sri Krishna': [
                {'name':'Set Dosa + Sagu','description':'Soft set dosas with veg sagu','price':139.0,'calories':520,'protein':12,'carbs':72,'fats':16,'fiber':6,'sugar':5,'sodium':680,'saturated_fat':5,'cholesterol':10,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Neer Dosa + Veg Stew','description':'Rice crepes with coconut veg stew','price':149.0,'calories':480,'protein':10,'carbs':64,'fats':16,'fiber':5,'sugar':6,'sodium':620,'saturated_fat':8,'cholesterol':10,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Mangalore Fish Curry','description':'Kokum & coconut fish curry','price':249.0,'calories':380,'protein':30,'carbs':10,'fats':22,'fiber':2,'sugar':2,'sodium':680,'saturated_fat':8,'cholesterol':95,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Udupi Sambar Rice','description':'Rice mixed with Udupi sambar','price':119.0,'calories':430,'protein':12,'carbs':68,'fats':8,'fiber':8,'sugar':6,'sodium':640,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Kosambari','description':'Moong-cucumber-carrot salad','price':79.0,'calories':160,'protein':8,'carbs':18,'fats':6,'fiber':6,'sugar':4,'sodium':220,'saturated_fat':1,'cholesterol':0,'is_vegetarian':True,'is_vegan':True,'is_low_sodium':True,'is_heart_healthy':True,'category':'Salad','glycemic_index':'Low'},
                {'name':'Pineapple Sheera','description':'Semolina dessert with pineapple','price':89.0,'calories':320,'protein':5,'carbs':52,'fats':10,'fiber':2,'sugar':28,'sodium':120,'saturated_fat':4,'cholesterol':15,'is_vegetarian':True,'category':'Dessert','glycemic_index':'High'},
                {'name':'Puliyogare','description':'Tamarind rice, Udupi style','price':119.0,'calories':460,'protein':8,'carbs':72,'fats':12,'fiber':5,'sugar':6,'sodium':700,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Goli Baje','description':'Mangalore fritters','price':99.0,'calories':360,'protein':8,'carbs':34,'fats':20,'fiber':3,'sugar':4,'sodium':540,'saturated_fat':3,'cholesterol':0,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Ragi Mudde + Sambar','description':'Finger millet balls with sambar','price':139.0,'calories':380,'protein':12,'carbs':50,'fats':10,'fiber':10,'sugar':3,'sodium':540,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'is_diabetic_friendly':True,'category':'Main','glycemic_index':'Low'},
                {'name':'Tender Coconut Water','description':'Fresh coconut water','price':60.0,'calories':45,'protein':0,'carbs':11,'fats':0,'fiber':0,'sugar':10,'sodium':30,'saturated_fat':0,'cholesterol':0,'is_vegetarian':True,'is_low_sodium':True,'category':'Beverage','glycemic_index':'Low'},
            ],
            'Kerala House': [
                {'name':'Appam + Veg Stew','description':'Soft hoppers with coconut veg stew','price':159.0,'calories':480,'protein':10,'carbs':64,'fats':16,'fiber':5,'sugar':6,'sodium':620,'saturated_fat':8,'cholesterol':10,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'High'},
                {'name':'Puttu + Kadala Curry','description':'Steamed rice flour logs with chickpea curry','price':159.0,'calories':460,'protein':14,'carbs':68,'fats':10,'fiber':10,'sugar':5,'sodium':600,'saturated_fat':4,'cholesterol':0,'is_vegetarian':True,'category':'Breakfast','glycemic_index':'Medium'},
                {'name':'Kerala Fish Curry','description':'Spicy tangy fish curry','price':249.0,'calories':360,'protein':30,'carbs':10,'fats':20,'fiber':2,'sugar':2,'sodium':680,'saturated_fat':6,'cholesterol':95,'is_vegetarian':False,'category':'Curry','glycemic_index':'Low'},
                {'name':'Malabar Parotta + Chicken Curry','description':'Layered parotta with chicken curry','price':269.0,'calories':680,'protein':30,'carbs':72,'fats':28,'fiber':6,'sugar':6,'sodium':860,'saturated_fat':9,'cholesterol':110,'is_vegetarian':False,'category':'Bread','glycemic_index':'High'},
                {'name':'Avial','description':'Mixed veggies in coconut-yogurt base','price':139.0,'calories':300,'protein':8,'carbs':20,'fats':20,'fiber':8,'sugar':6,'sodium':520,'saturated_fat':8,'cholesterol':10,'is_vegetarian':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Beetroot Thoran','description':'Stir-fried beetroot with coconut','price':119.0,'calories':200,'protein':4,'carbs':18,'fats':12,'fiber':6,'sugar':8,'sodium':320,'saturated_fat':6,'cholesterol':0,'is_vegetarian':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Kerala Sambar Rice','description':'Rice mixed with Kerala sambar','price':119.0,'calories':430,'protein':12,'carbs':68,'fats':8,'fiber':8,'sugar':6,'sodium':640,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Pazham Pori','description':'Banana fritters','price':99.0,'calories':360,'protein':4,'carbs':56,'fats':14,'fiber':3,'sugar':24,'sodium':260,'saturated_fat':4,'cholesterol':0,'is_vegetarian':True,'category':'Dessert','glycemic_index':'High'},
                {'name':'Sambharam (Buttermilk)','description':'Kerala spiced buttermilk','price':50.0,'calories':70,'protein':4,'carbs':8,'fats':2,'fiber':0,'sugar':5,'sodium':180,'saturated_fat':1,'cholesterol':5,'is_vegetarian':True,'is_low_sodium':True,'category':'Beverage','glycemic_index':'Low'},
                {'name':'Ada Pradhaman','description':'Rice ada jaggery coconut milk payasam','price':109.0,'calories':360,'protein':5,'carbs':56,'fats':12,'fiber':2,'sugar':30,'sodium':140,'saturated_fat':10,'cholesterol':10,'is_vegetarian':True,'category':'Dessert','glycemic_index':'High'},
            ],
            'The Dakshin Table': [
                {'name':'Millet Masala Dosa','description':'Mixed millet dosa with potato masala','price':149.0,'calories':380,'protein':12,'carbs':50,'fats':12,'fiber':8,'sugar':3,'sodium':540,'saturated_fat':3,'cholesterol':5,'is_vegetarian':True,'is_diabetic_friendly':True,'category':'Breakfast','glycemic_index':'Low'},
                {'name':'Ragi Idli + Sambar','description':'Finger millet idlis with sambar','price':129.0,'calories':320,'protein':12,'carbs':44,'fats':8,'fiber':8,'sugar':3,'sodium':520,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'is_diabetic_friendly':True,'category':'Breakfast','glycemic_index':'Low'},
                {'name':'Paneer Chettinad','description':'Spicy Chettinad masala paneer','price':219.0,'calories':380,'protein':22,'carbs':16,'fats':24,'fiber':4,'sugar':4,'sodium':680,'saturated_fat':12,'cholesterol':55,'is_vegetarian':True,'category':'Curry','glycemic_index':'Low'},
                {'name':'Veg Kurma + Idiyappam','description':'String hoppers with veg kurma','price':159.0,'calories':460,'protein':10,'carbs':68,'fats':12,'fiber':5,'sugar':5,'sodium':620,'saturated_fat':6,'cholesterol':10,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Lemon Rice','description':'Tempered lemon rice with peanuts','price':119.0,'calories':450,'protein':8,'carbs':70,'fats':14,'fiber':5,'sugar':4,'sodium':700,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'category':'Rice','glycemic_index':'High'},
                {'name':'Sambar Vada','description':'Lentil vada soaked in sambar','price':109.0,'calories':380,'protein':12,'carbs':38,'fats':18,'fiber':8,'sugar':4,'sodium':680,'saturated_fat':4,'cholesterol':0,'is_vegetarian':True,'category':'Tiffin','glycemic_index':'Medium'},
                {'name':'Rasam Soup','description':'Peppery tomato-tamarind broth','price':79.0,'calories':90,'protein':2,'carbs':12,'fats':2,'fiber':2,'sugar':4,'sodium':260,'saturated_fat':0.5,'cholesterol':0,'is_vegetarian':True,'is_low_sodium':True,'category':'Main','glycemic_index':'Low'},
                {'name':'Curd Rice','description':'Cooling yogurt rice','price':119.0,'calories':420,'protein':12,'carbs':58,'fats':12,'fiber':2,'sugar':7,'sodium':620,'saturated_fat':6,'cholesterol':20,'is_vegetarian':True,'category':'Rice','glycemic_index':'Medium'},
                {'name':'Mixed Millet Pongal','description':'Millet-based savory pongal','price':139.0,'calories':340,'protein':12,'carbs':46,'fats':10,'fiber':8,'sugar':3,'sodium':520,'saturated_fat':2,'cholesterol':0,'is_vegetarian':True,'is_diabetic_friendly':True,'category':'Tiffin','glycemic_index':'Low'},
                {'name':'Strong Filter Coffee','description':'Traditional decoction coffee','price':45.0,'calories':60,'protein':2,'carbs':8,'fats':2,'fiber':0,'sugar':6,'sodium':40,'saturated_fat':1,'cholesterol':5,'is_vegetarian':True,'category':'Beverage','glycemic_index':'Low'},
            ],
        }

        image_map = {
            'idli': 'https://images.unsplash.com/photo-1625944525886-4b0f2b5756fa?w=300',
            'vada': 'https://images.unsplash.com/photo-1625944525886-4b0f2b5756fa?w=300',
            'dosa': 'https://images.unsplash.com/photo-1604908177072-df6f4b595b97?w=300',
            'uttapam': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=300',
            'pongal': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'biryani': 'https://images.unsplash.com/photo-1605478032743-04a0bbbd8d7a?w=300',
            'parotta': 'https://images.unsplash.com/photo-1628294895950-2bf31dfba4bd?w=300',
            'kurma': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=300',
            'sambar': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=300',
            'rasam': 'https://images.unsplash.com/photo-1606991901872-0e6ca869baa3?w=300',
            'lemon rice': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'curd rice': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'kesari': 'https://images.unsplash.com/photo-1551024709-8f23befc6cf7?w=300',
            'mysore pak': 'https://images.unsplash.com/photo-1551024709-8f23befc6cf7?w=300',
            'payasam': 'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=300',
            'lassi': 'https://images.unsplash.com/photo-1567620832903-9fc6debc7030?w=300',
            'coffee': 'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=300',
            'buttermilk': 'https://images.unsplash.com/photo-1551024709-8f23befc6cf7?w=300',
            'fish': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=300',
            'chicken': 'https://images.unsplash.com/photo-1604908177072-df6f4b595b97?w=300',
            'mutton': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=300',
            'egg': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=300',
            'crab': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=300',
            'prawn': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=300',
            'appam': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'puttu': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'avial': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=300',
            'thoran': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=300',
            'kosambari': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'ragi': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'millet': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'neer dosa': 'https://images.unsplash.com/photo-1604908177072-df6f4b595b97?w=300',
            'parotta': 'https://images.unsplash.com/photo-1519431458145-6e1759a1bd36?w=300',
        }

        category_fallback = {
            'breakfast': 'https://images.unsplash.com/photo-1625944525886-4b0f2b5756fa?w=300',
            'tiffin': 'https://images.unsplash.com/photo-1625944525886-4b0f2b5756fa?w=300',
            'rice': 'https://images.unsplash.com/photo-1604908177072-df6f4b595b97?w=300',
            'curry': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=300',
            'main': 'https://images.unsplash.com/photo-1589307004173-3c95204aed21?w=300',
            'bread': 'https://images.unsplash.com/photo-1519431458145-6e1759a1bd36?w=300',
            'salad': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300',
            'dessert': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=300',
            'beverage': 'https://images.unsplash.com/photo-1498804103079-a6351b050096?w=300',
        }

        def assign_image(name, category):
            nm = (name or '').lower()
            for key, url in image_map.items():
                if key in nm:
                    return url
            cat = (category or '').lower()
            return category_fallback.get(cat, 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=300')

        for rest in restaurants_data:
            restaurant = Restaurant(**rest)
            db.session.add(restaurant)
            db.session.flush()

            for item in menu_items_data[rest['name']]:
                item['restaurant_id'] = restaurant.id
                item['image_url'] = assign_image(item.get('name'), item.get('category'))
                for tag in ['is_vegetarian','is_vegan','is_gluten_free','is_low_carb','is_low_sodium',
                            'is_low_sugar','is_heart_healthy','is_diabetic_friendly']:
                    if tag not in item:
                        item[tag] = False
                db.session.add(MenuItem(**item))

        db.session.commit()
        print("Database initialized with 10 South Indian restaurants (100 items, rupee prices, dish images).")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        health_data = HealthData(user_id=user.id)
        preferences = UserPreference(user_id=user.id)
        health_conditions = HealthCondition(user_id=user.id)
        db.session.add_all([health_data, preferences, health_conditions])
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    restaurants = Restaurant.query.all()
    return render_template('home.html', restaurants=restaurants)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    health_data = HealthData.query.filter_by(user_id=current_user.id).first()
    if not health_data:
        health_data = HealthData(user_id=current_user.id)
        db.session.add(health_data)
        db.session.commit()

    preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.session.add(preferences)
        db.session.commit()

    health_conditions = HealthCondition.query.filter_by(user_id=current_user.id).first()
    if not health_conditions:
        health_conditions = HealthCondition(user_id=current_user.id)
        db.session.add(health_conditions)
        db.session.commit()

    if request.method == 'POST':
        try:
            health_data.weight = float(request.form.get('weight') or 0)
            health_data.height = float(request.form.get('height') or 0)
            health_data.age = int(request.form.get('age') or 0)
            health_data.gender = request.form.get('gender', 'male')
            health_data.steps = int(request.form.get('steps') or 0)
            health_data.heart_rate = int(request.form.get('heart_rate') or 0)
            health_data.sleep_hours = float(request.form.get('sleep_hours') or 0)

            health_data.blood_sugar = float(request.form.get('blood_sugar') or 0)
            health_data.blood_pressure_systolic = int(request.form.get('bp_systolic') or 0)
            health_data.blood_pressure_diastolic = int(request.form.get('bp_diastolic') or 0)
            health_data.cholesterol_total = float(request.form.get('cholesterol_total') or 0)

            preferences.is_vegetarian = 'is_vegetarian' in request.form
            preferences.is_vegan = 'is_vegan' in request.form
            preferences.is_gluten_free = 'is_gluten_free' in request.form
            preferences.is_dairy_free = 'is_dairy_free' in request.form
            preferences.is_low_carb = 'is_low_carb' in request.form
            preferences.is_low_sodium = 'is_low_sodium' in request.form
            preferences.is_low_fat = 'is_low_fat' in request.form
            preferences.allergies = request.form.get('allergies', '')
            preferences.favorite_cuisines = request.form.get('favorite_cuisines', '')

            health_conditions.has_diabetes = 'has_diabetes' in request.form
            health_conditions.diabetes_type = request.form.get('diabetes_type', '')
            health_conditions.has_hypertension = 'has_hypertension' in request.form
            health_conditions.has_high_cholesterol = 'has_high_cholesterol' in request.form
            health_conditions.has_heart_disease = 'has_heart_disease' in request.form
            health_conditions.has_kidney_disease = 'has_kidney_disease' in request.form
            health_conditions.has_liver_disease = 'has_liver_disease' in request.form
            health_conditions.has_thyroid_disorder = 'has_thyroid_disorder' in request.form
            health_conditions.has_celiac_disease = 'has_celiac_disease' in request.form
            health_conditions.has_ibs = 'has_ibs' in request.form
            health_conditions.has_gerd = 'has_gerd' in request.form
            health_conditions.has_obesity = 'has_obesity' in request.form
            health_conditions.has_anemia = 'has_anemia' in request.form
            health_conditions.other_conditions = request.form.get('other_conditions', '')
            health_conditions.current_medications = request.form.get('current_medications', '')

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            print(f"Error updating profile: {e}")
            flash('Error updating profile', 'error')

    return render_template('profile.html',
                           health_data=health_data,
                           preferences=preferences,
                           health_conditions=health_conditions)

@app.route('/restaurant/<int:restaurant_id>')
@login_required
def restaurant_menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()

    health_data = HealthData.query.filter_by(user_id=current_user.id).first()
    preferences = UserPreference.query.filter_by(user_id=current_user.id).first()
    health_conditions = HealthCondition.query.filter_by(user_id=current_user.id).first()

    recommendations = []
    if health_data and health_data.weight and health_data.height:
        recommendations = recommender.get_recommendations(
            menu_items,
            health_data,
            preferences,
            health_conditions
        )
    else:
        recommendations = [{'item': item, 'score': 0, 'match_percentage': 50, 'warnings': [], 'is_safe': True}
                           for item in menu_items]

    return render_template('menu.html',
                           restaurant=restaurant,
                           recommendations=recommendations,
                           health_conditions=health_conditions)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, menu_item_id=item_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, menu_item_id=item_id)
        db.session.add(cart_item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item added to cart'})

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.menu_item.price * item.quantity for item in cart_items)
    total_calories = sum(item.menu_item.calories * item.quantity for item in cart_items)
    total_protein = sum(item.menu_item.protein * item.quantity for item in cart_items)
    return render_template('cart.html',
                           cart_items=cart_items,
                           total=total,
                           total_calories=total_calories,
                           total_protein=total_protein)

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    quantity = int(request.json.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    db.session.commit()
    return jsonify({'success': True})

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/sync_fitbit')
@login_required
def sync_fitbit():
    flash('Fitbit sync feature - OAuth implementation needed', 'info')
    return redirect(url_for('profile'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)