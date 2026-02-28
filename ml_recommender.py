class FoodRecommender:
    def __init__(self):
        pass
    
    def calculate_bmi(self, weight, height):
        
        if not weight or not height or height == 0:
            return 22
        height_m = height / 100
        return weight / (height_m ** 2)
    
    def get_bmi_category(self, bmi):
        
        if bmi < 18.5:
            return 'underweight'
        elif bmi < 25:
            return 'normal'
        elif bmi < 30:
            return 'overweight'
        else:
            return 'obese'
    
    def calculate_daily_needs(self, health_data):

        if not health_data or not health_data.weight or not health_data.height or not health_data.age:
            return {
                'calories': 2000,
                'protein': 150,
                'carbs': 200,
                'fats': 67
            }

        if health_data.gender and health_data.gender.lower() == 'male':
            bmr = 88.362 + (13.397 * health_data.weight) + (4.799 * health_data.height) - (5.677 * health_data.age)
        else:
            bmr = 447.593 + (9.247 * health_data.weight) + (3.098 * health_data.height) - (4.330 * health_data.age)

        steps = health_data.steps or 5000
        if steps < 5000:
            activity_factor = 1.2
        elif steps < 7500:
            activity_factor = 1.375
        elif steps < 10000:
            activity_factor = 1.55
        else:
            activity_factor = 1.725  # Very active
        
        daily_calories = bmr * activity_factor

        return {
            'calories': daily_calories,
            'protein': (daily_calories * 0.30) / 4,
            'carbs': (daily_calories * 0.40) / 4,
            'fats': (daily_calories * 0.30) / 9
        }
    
    def check_health_conditions(self, item, health_conditions):
        
        warnings = []
        penalty = 0
        
        if not health_conditions:
            return warnings, penalty

        if health_conditions.has_diabetes:
            if item.carbs > 75:
                warnings.append(f"🚫 Very high carbs ({int(item.carbs)}g) - avoid for diabetes")
                penalty += 20
            elif item.carbs > 60:
                warnings.append(f"⚠️ High carbs ({int(item.carbs)}g) - monitor blood sugar")
                penalty += 10
            elif item.carbs > 45:
                warnings.append(f"ℹ️ Moderate carbs ({int(item.carbs)}g) - eat with caution")
                penalty += 5
            
            if hasattr(item, 'sugar') and item.sugar:
                if item.sugar > 20:
                    warnings.append(f"🚫 Very high sugar ({int(item.sugar)}g) - not recommended")
                    penalty += 15
                elif item.sugar > 15:
                    warnings.append(f"⚠️ High sugar ({int(item.sugar)}g) - may spike blood glucose")
                    penalty += 10
                elif item.sugar > 10:
                    warnings.append(f"ℹ️ Moderate sugar ({int(item.sugar)}g)")
                    penalty += 3
            
            if hasattr(item, 'glycemic_index') and item.glycemic_index:
                if item.glycemic_index == 'High':
                    warnings.append("⚠️ High glycemic index - rapid blood sugar spike")
                    penalty += 8
                elif item.glycemic_index == 'Medium':
                    penalty += 2
            
            if item.fiber >= 7:
                penalty -= 3

        if health_conditions.has_hypertension:
            if hasattr(item, 'sodium') and item.sodium:
                if item.sodium > 1000:
                    warnings.append(f"🚫 Very high sodium ({int(item.sodium)}mg) - dangerous for BP")
                    penalty += 20
                elif item.sodium > 700:
                    warnings.append(f"⚠️ High sodium ({int(item.sodium)}mg) - may raise blood pressure")
                    penalty += 12
                elif item.sodium > 500:
                    warnings.append(f"ℹ️ Moderate sodium ({int(item.sodium)}mg) - monitor intake")
                    penalty += 5
            
            if hasattr(item, 'saturated_fat') and item.saturated_fat:
                if item.saturated_fat > 8:
                    warnings.append(f"⚠️ High saturated fat ({int(item.saturated_fat)}g)")
                    penalty += 5

        if health_conditions.has_high_cholesterol:
            if hasattr(item, 'saturated_fat') and item.saturated_fat:
                if item.saturated_fat > 10:
                    warnings.append(f"🚫 Very high saturated fat ({int(item.saturated_fat)}g) - raises LDL")
                    penalty += 15
                elif item.saturated_fat > 7:
                    warnings.append(f"⚠️ High saturated fat ({int(item.saturated_fat)}g) - limit intake")
                    penalty += 10
                elif item.saturated_fat > 5:
                    warnings.append(f"ℹ️ Moderate saturated fat ({int(item.saturated_fat)}g)")
                    penalty += 4
            
            if hasattr(item, 'cholesterol') and item.cholesterol:
                if item.cholesterol > 150:
                    warnings.append(f"⚠️ High cholesterol ({int(item.cholesterol)}mg)")
                    penalty += 8
                elif item.cholesterol > 100:
                    penalty += 3
            
            if item.fiber >= 8:
                penalty -= 4

        if health_conditions.has_heart_disease:
            if hasattr(item, 'sodium') and item.sodium and item.sodium > 600:
                warnings.append(f"⚠️ High sodium - not heart healthy")
                penalty += 10
            
            if hasattr(item, 'saturated_fat') and item.saturated_fat and item.saturated_fat > 6:
                warnings.append(f"⚠️ High saturated fat - avoid for heart health")
                penalty += 10
            
            if item.fats > 25:
                warnings.append(f"ℹ️ High fat content ({int(item.fats)}g)")
                penalty += 5

        if health_conditions.has_kidney_disease:
            if item.protein > 35:
                warnings.append(f"🚫 Very high protein ({int(item.protein)}g) - may stress kidneys")
                penalty += 15
            elif item.protein > 28:
                warnings.append(f"⚠️ High protein ({int(item.protein)}g) - consult your doctor")
                penalty += 8
            
            if hasattr(item, 'sodium') and item.sodium and item.sodium > 600:
                warnings.append(f"⚠️ High sodium - hard on kidneys")
                penalty += 8
            
            if hasattr(item, 'potassium') and item.potassium and item.potassium > 700:
                warnings.append(f"⚠️ High potassium - limit with kidney disease")
                penalty += 8

        if health_conditions.has_obesity:
            if item.calories > 650:
                warnings.append(f"⚠️ High calorie ({int(item.calories)} cal) - portion control needed")
                penalty += 10
            elif item.calories > 550:
                warnings.append(f"ℹ️ Moderate-high calories ({int(item.calories)} cal)")
                penalty += 5
            
            if hasattr(item, 'sugar') and item.sugar and item.sugar > 15:
                warnings.append(f"⚠️ High sugar content")
                penalty += 5
            
            if item.fats > 25:
                penalty += 5
            
            if item.protein >= 25:
                penalty -= 3
            if item.fiber >= 8:
                penalty -= 3

        if health_conditions.has_liver_disease:
            if item.fats > 20:
                warnings.append(f"ℹ️ High fat - may stress liver")
                penalty += 5
            
            if hasattr(item, 'sodium') and item.sodium and item.sodium > 700:
                warnings.append(f"⚠️ High sodium - limit with liver disease")
                penalty += 5

        if health_conditions.has_celiac_disease:
            if hasattr(item, 'is_gluten_free') and not item.is_gluten_free:
                warnings.append("🚫 CONTAINS GLUTEN - MUST AVOID with Celiac disease")
                penalty = 100

        if health_conditions.has_ibs:
            if item.fiber > 12:
                warnings.append(f"ℹ️ Very high fiber - may trigger IBS symptoms")
                penalty += 3
            
            if item.fats > 25:
                warnings.append(f"ℹ️ High fat - may trigger IBS")
                penalty += 3

        if health_conditions.has_gerd:
            if item.fats > 20:
                warnings.append(f"ℹ️ High fat - may worsen acid reflux")
                penalty += 4

        if health_conditions.has_anemia:
            if item.protein >= 25:
                penalty -= 2

        if health_conditions.has_thyroid_disorder:
            if hasattr(item, 'sodium') and item.sodium and item.sodium > 700:
                warnings.append(f"ℹ️ High sodium - monitor with thyroid condition")
                penalty += 3
        
        return warnings, max(0, penalty)
    
    def check_dietary_preferences(self, item, preferences):
        
        if not preferences:
            return True
        
        if preferences.is_vegetarian and not item.is_vegetarian:
            return False
        
        if preferences.is_vegan and not item.is_vegan:
            return False
        
        if preferences.is_gluten_free and hasattr(item, 'is_gluten_free') and not item.is_gluten_free:
            return False
        
        if preferences.allergies:
            allergies = [a.strip().lower() for a in preferences.allergies.split(',')]
            item_name = (item.name or '').lower()
            item_desc = (item.description or '').lower()
            
            for allergy in allergies:
                if allergy in item_name or allergy in item_desc:
                    return False
        
        return True
    
    def get_recommendations(self, menu_items, health_data, user_preferences, health_conditions=None):
        if not menu_items:
            return []
        
        recommendations = []
        daily_needs = self.calculate_daily_needs(health_data)
        
        for item in menu_items:

            if not self.check_dietary_preferences(item, user_preferences):
                continue

            score = 60  

            warnings, health_penalty = self.check_health_conditions(item, health_conditions)
            score -= health_penalty

            if item.protein >= 35:
                score += 8
            elif item.protein >= 28:
                score += 6
            elif item.protein >= 20:
                score += 4
            elif item.protein >= 15:
                score += 2

            if item.fiber >= 12:
                score += 8
            elif item.fiber >= 9:
                score += 6
            elif item.fiber >= 6:
                score += 4
            elif item.fiber >= 4:
                score += 2

            if 300 <= item.calories <= 500:
                score += 5
            elif 250 <= item.calories <= 600:
                score += 3
            elif 200 <= item.calories <= 650:
                score += 1

            if hasattr(item, 'sugar') and item.sugar:
                if item.sugar < 5:
                    score += 4
                elif item.sugar < 10:
                    score += 2
                elif item.sugar < 15:
                    score += 1

            if hasattr(item, 'sodium') and item.sodium:
                if item.sodium < 300:
                    score += 4
                elif item.sodium < 500:
                    score += 2
                elif item.sodium < 700:
                    score += 1

            if hasattr(item, 'saturated_fat') and item.saturated_fat:
                if item.saturated_fat < 3:
                    score += 3
                elif item.saturated_fat < 5:
                    score += 2
                elif item.saturated_fat < 7:
                    score += 1

            tag_bonus = 0
            if hasattr(item, 'is_diabetic_friendly') and item.is_diabetic_friendly:
                tag_bonus += 3
            if hasattr(item, 'is_heart_healthy') and item.is_heart_healthy:
                tag_bonus += 3
            if hasattr(item, 'is_low_sodium') and item.is_low_sodium:
                tag_bonus += 2
            if item.is_vegetarian:
                tag_bonus += 1
            if item.is_vegan:
                tag_bonus += 2
            score += min(10, tag_bonus)

            preference_bonus = 0
            if user_preferences:
                if user_preferences.is_low_carb and item.carbs < 30:
                    preference_bonus += 4
                elif user_preferences.is_low_carb and item.carbs < 40:
                    preference_bonus += 2
                
                if user_preferences.is_low_fat and item.fats < 15:
                    preference_bonus += 4
                elif user_preferences.is_low_fat and item.fats < 20:
                    preference_bonus += 2
                
                if user_preferences.is_low_sodium:
                    if hasattr(item, 'is_low_sodium') and item.is_low_sodium:
                        preference_bonus += 3
            score += min(10, preference_bonus)

            condition_bonus = 0
            if health_conditions:
                if health_conditions.has_diabetes:
                    if hasattr(item, 'glycemic_index') and item.glycemic_index == 'Low':
                        condition_bonus += 4
                    if hasattr(item, 'is_diabetic_friendly') and item.is_diabetic_friendly:
                        condition_bonus += 3
                    if item.fiber >= 7:
                        condition_bonus += 2
                
                if health_conditions.has_heart_disease or health_conditions.has_high_cholesterol:
                    if hasattr(item, 'is_heart_healthy') and item.is_heart_healthy:
                        condition_bonus += 4
                    if item.fiber >= 8:
                        condition_bonus += 2
                
                if health_conditions.has_hypertension:
                    if hasattr(item, 'is_low_sodium') and item.is_low_sodium:
                        condition_bonus += 5
                
                if health_conditions.has_obesity:
                    if item.calories < 400 and item.protein >= 20 and item.fiber >= 6:
                        condition_bonus += 5
            score += min(10, condition_bonus)

            score = max(0, min(100, score))
            is_safe = score >= 70 and health_penalty < 25
            
            recommendations.append({
                'item': item,
                'score': score,
                'match_percentage': int(score),
                'warnings': warnings,
                'is_safe': is_safe
            })

        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
