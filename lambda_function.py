# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

# Required for the API
import requests
import json

import random

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = (
            "Welcome to the nutrition consultant application!"
            " You have multiple options:"
            " 1. Create Profile"
            " 2. Search food information"
            " 3. Create Diet Plan"
            " 4. Calculate food intake"
            " 5. Dish suggestions with caloric range"
            " 6. Handle vitamin deficiency"
            " 7. Autocomplete food ingredients"
            " 8. Get fasting types"
            " 9. Convert nutrients into calories"
            " 10. Food fun facts")

        # If the user either does not reply to the welcome message or says something
        # that is not understood, they will be prompted again with this text.

        # Needed for class CalculateFoodIntake
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["foodCaloriesSum"] = 0
        session_attr["foodCarbohydratesSum"] = 0
        session_attr["foodProteinsSum"] = 0
        session_attr["foodFatSum"] = 0

        reprompt_text = "Please try writing Create Profile"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .ask(reprompt_text)
                .response
        )


class FoodInfoHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("FoodInfoIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Ask me how many calories certain food has!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class FoodRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("FoodRequestIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        foodtype = slots["foodtype"].value

        create_foodtype_url = "https://api.edamam.com/api/food-database/v2/parser?app_id=cf568ffc&app_key=4ab5d97c9657f25c95983fd710a96627&ingr=" + foodtype + "&nutrition-type=cooking"

        response_API = requests.get(create_foodtype_url)
        data = response_API.json()
        food_calories = data['hints'][0]['food']['nutrients']['ENERC_KCAL']  # Amount of Calories
        food_carbohydrates = data['hints'][0]['food']['nutrients']['CHOCDF']  # Amount of Carbohydrates
        food_protein = data['hints'][0]['food']['nutrients']['PROCNT']  # Amount of Protein
        food_fat = data['hints'][0]['food']['nutrients']['FAT']  # Amount of Fat

        speak_output = "A " + str(foodtype) + " has " + str(food_calories) + " calories, " + str(
            food_carbohydrates) + " grams of carbohydrates, " + str(food_protein) + " grams of proteins and " + str(
            food_fat) + " grams of fat."
        reprompt = "Do you want to try more food?"

        return (
            handler_input.response_builder.speak(speak_output).ask(reprompt).response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = (
            "Sorry, that didn't work. You have the following options:"
            " 1. Create Profile"
            " 2. Search food information"
            " 3. Create Diet Plan"
            " 4. Calculate food intake"
            " 5. Dish suggestions with caloric range"
            " 6. Handle vitamin deficiency"
            " 7. Autocomplete food ingredients"
            " 8. Get fasting types"
            " 9. Convert nutrients into calories"
            " 10. Food fun facts")

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ProfileHandler(AbstractRequestHandler):
    """Handler for AskTime Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CreateProfile")(handler_input)

    def handle(self, handler_input):
        speak_output = "Please state your name."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class NameHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NameHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userName = slots["name"].value
        speak_output = "Hello " + userName + "! How old are you?"

        # "a" - Append - Opens a file for appending, creates the file if it does not exist
        f = open("/tmp/tempfile.txt", "a")
        f.write(userName)
        f.close()
        # open and read the file after the appending:
        f = open("/tmp/tempfile.txt", "r")
        readFile = (f.read())
        f.close()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class AgeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AgeHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userAge = slots["age"].value
        handler_input.attributes_manager.session_attributes["age"] = userAge
        speak_output = "You're only " + userAge + "? How much do you weigh if I may ask?"

        # handler_input.response_builder.speak(speak_output)
        # return handler_input.response_builder.response
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


class WeightHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("WeightHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userWeight = slots["weight"].value
        handler_input.attributes_manager.session_attributes["weight"] = userWeight
        speak_output = "So you're weighing " + userWeight + " . And how tall are you?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


class HeightHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HeightHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userHeight = slots["height"].value
        handler_input.attributes_manager.session_attributes["height"] = userHeight

        if (int(userHeight) <= 160):
            speak_output = "You're small! Are you a man or a woman?"
        else:
            speak_output = "You're big! Are you a man or a woman?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Calculates the BMI
# Gender: Female
# Weight: 55 kg
# Height: 160 cm
# Step 1: ((Height in cm)^2)/10000) = ((160)^2)/10000 = 2.56
# Step 2: (Weight)/2.56 = 21.5
class BMICalculator(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GenderHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userGender = slots["gender"].value
        handler_input.attributes_manager.session_attributes["gender"] = userGender
        calcWeight = handler_input.attributes_manager.session_attributes["weight"]
        calcHeight = handler_input.attributes_manager.session_attributes["height"]

        step1 = (float(calcHeight) * float(calcHeight)) / 10000  # (160*160)/10000 = 2.56
        step2 = (float(calcWeight) / step1)  # 55 / 2.56 = 21.5

        if (step2 <= 18.5):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you are slightly underweight.  Do you want to know what your daily basal metabolic rate is?"
        elif (step2 > 18.5 or roundBMI <= 24.9):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and your weight is in the normal range. Do you want to know what your daily basal metabolic rate is?"
        elif (step2 >= 25 or roundBMI <= 29.9):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you are overweight. Do you want to know what your daily basal metabolic rate is?"
        elif (step2 >= 30 or roundBMI <= 34.9):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you are very overweight.  Do you want to know what your daily basal metabolic rate is?"
        elif (step2 >= 35 or roundBMI <= 39.9):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you have second-degree obesity. Do you want to know what your daily basal metabolic rate is?"
        else:
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you have third-degree obesity. Do you want to know what your daily basal metabolic rate is?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Calculates the calories (basal metabolism) a person needs per day
# Formula Women: 655.1 + (9.6 * weight in kg) + (1.8 * height in cm) - (4.7 * age)
# Formula Men: 66.47 + (13,7 * weight in kg) + (5 * height in cm) - (6,8 * age)
class CaloriesCalculator(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaloriesHandler")(handler_input)

    def handle(self, handler_input):
        userGender = handler_input.attributes_manager.session_attributes["gender"]
        calcAge = handler_input.attributes_manager.session_attributes["age"]
        calcWeight = handler_input.attributes_manager.session_attributes["weight"]
        calcHeight = handler_input.attributes_manager.session_attributes["height"]

        formulawomen = float(655.1 + (9.6 * float(calcWeight) + (1.8 * float(calcHeight) - (4.7 * float(calcAge)))))
        roundCaloriesWomen = round(formulawomen, 2)
        formulamen = float(66.47 + (13.7 * float(calcWeight) + (5 * float(calcHeight) - (6.8 * float(calcAge)))))
        roundCaloriesMen = round(formulamen, 2)

        handler_input.attributes_manager.session_attributes["caloriesMen"] = roundCaloriesMen
        handler_input.attributes_manager.session_attributes["caloriesWomen"] = roundCaloriesWomen

        if (userGender == "Mann"):
            speak_output = "Your daily basal metabolic rate is about " + str(
                roundCaloriesMen) + " calories. Do you want to lose, gain or maintain your weight?"
        else:
            speak_output = "Your daily basal metabolic rate is about " + str(
                roundCaloriesWomen) + " calories. Do you want to lose, gain or maintain your weight?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# TODO: Class for DietHandler ()
class DietHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DietHandler")(handler_input)

    def handle(self, handler_input):
        speak_output = "Unfortunately this function has not been fully implemented yet. Please try next time!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


class GainWeight(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GainWeightHandler")(handler_input)

    def handle(self, handler_input):
        userGender = handler_input.attributes_manager.session_attributes["gender"]
        roundCaloriesWomen = handler_input.attributes_manager.session_attributes["caloriesWomen"]
        roundCaloriesMen = handler_input.attributes_manager.session_attributes["caloriesMen"]

        caloricSurplusWomen = float(roundCaloriesWomen + 300)
        caloricSurplusMen = float(roundCaloriesMen + 500)

        # speak_output = "caloricSurplusMen: " + str(caloricSurplusMen) + " userGender: " + userGender

        if (userGender == "Woman"):
            speak_output = "You have to eat " + str(caloricSurplusWomen) + " calories to gain weight to build muscle."
        else:
            speak_output = "You have to eat " + str(caloricSurplusMen) + " calories to gain weight to build muscle."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


class LoseWeight(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("LoseWeightHandler")(handler_input)

    def handle(self, handler_input):
        userGender = handler_input.attributes_manager.session_attributes["gender"]
        roundCaloriesWomen = handler_input.attributes_manager.session_attributes["caloriesWomen"]
        roundCaloriesMen = handler_input.attributes_manager.session_attributes["caloriesMen"]

        caloricDeficitWomen = float(roundCaloriesWomen - 300)
        caloricDeficitMen = float(roundCaloriesMen - 500)

        if (userGender == "Woman"):
            speak_output = "You have to eat " + str(caloricDeficitWomen) + " calories to lose weight."
        else:
            speak_output = "You have to eat " + str(caloricDeficitMen) + " calories to lose weight."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )
    # Man könnte hier ebenfalls alles zusammenrechnen an den Kalorien die man gegessen hat, um zu schauen ob man im Defizit ist oder nicht


class MaintainWeight(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MaintainWeightHandler")(handler_input)

    def handle(self, handler_input):
        userGender = handler_input.attributes_manager.session_attributes["gender"]
        roundCaloriesWomen = handler_input.attributes_manager.session_attributes["caloriesWomen"]
        roundCaloriesMen = handler_input.attributes_manager.session_attributes["caloriesMen"]

        if (userGender == "Woman"):
            speak_output = "You have to eat " + str(roundCaloriesWomen) + " calories to lose weight."
        else:
            speak_output = "You have to eat " + str(roundCaloriesMen) + " calories to lose weight."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


class FoodIntakeInfoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("FoodIntakeInfoHandler")(handler_input)

    def handle(self, handler_input):
        speak_output = "Tell me what you have eaten today or calculate the nutritional values of other food."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CalculateFoodIntake(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CalculateFoodIntake")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        foodtype = slots["foodtype"].value
        create_foodtype_url = "https://api.edamam.com/api/food-database/v2/parser?app_id=cf568ffc&app_key=4ab5d97c9657f25c95983fd710a96627&ingr=" + foodtype + "&nutrition-type=cooking"

        # Make an API request to get the nutrients of food
        response_API = requests.get(create_foodtype_url)
        data = response_API.json()
        # Get the data from the JSON URL
        food_calories = data['hints'][0]['food']['nutrients']['ENERC_KCAL']  # Amount of Calories
        food_carbohydrates = data['hints'][0]['food']['nutrients']['CHOCDF']  # Amount of Carbohydrates
        food_protein = data['hints'][0]['food']['nutrients']['PROCNT']  # Amount of Protein
        food_fat = data['hints'][0]['food']['nutrients']['FAT']  # Amount of Fat

        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["food_calories"] = food_calories
        session_attr["food_carbohydrates"] = food_carbohydrates
        session_attr["food_protein"] = food_protein
        session_attr["food_fat"] = food_fat

        sumOfCalories = food_calories
        sumOfCarbohydrates = food_carbohydrates
        sumOfProteins = food_protein
        sumOfFats = food_fat

        # Round up the numbers to two decimals
        session_attr["foodCaloriesSum"] += round(sumOfCalories, 2)
        session_attr["foodCarbohydratesSum"] += round(sumOfCarbohydrates, 2)
        session_attr["foodProteinsSum"] += round(sumOfProteins, 2)
        session_attr["foodFatSum"] += round(sumOfFats, 2)

        speak_output = "Add more food or say Calculate."

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Outputs the nutritional values we calculated in the class CalculateFoodIntake
class CalculateFoodIntakeSum(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CalculateFoodIntakeSum")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes

        speak_output = "Total: " + str(session_attr["foodCaloriesSum"]) + " calories. Carbohydrates:  " + str(
            session_attr["foodCarbohydratesSum"]) + " grams. Fats: " + str(
            session_attr["foodFatSum"]) + " grams. Proteins " + str(session_attr["foodProteinsSum"]) + " grams"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Skill 5 (Dish suggestions with caloric range)
class DishSuggestionsInfoIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DishSuggestionsInfoIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Tell me a food item and a caloric range. (Example: Egg Range 100 to 300)"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Skill 5 (Dish suggestions with caloric range)
# Invocation {food} range {rangeFrom} to {rangeTo}
# Invocation: I want to eat {food} with a caloric range from {rangeFrom} to {rangeTo}
class DishSuggestionsUserInput(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DishSuggestionsUserInput")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        foodsuggestion = slots["food"].value
        caloricRangeFrom = slots["rangeFrom"].value
        caloricRangeTo = slots["rangeTo"].value

        handler_input.attributes_manager.session_attributes["food"] = foodsuggestion
        handler_input.attributes_manager.session_attributes["rangeFrom"] = caloricRangeFrom
        handler_input.attributes_manager.session_attributes["rangeTo"] = caloricRangeTo

        # Make an API call to get dishes for the specified calories range
        create_foodtype_url = "https://api.edamam.com/api/food-database/v2/parser?app_id=cf568ffc&app_key=4ab5d97c9657f25c95983fd710a96627&ingr=" + str(
            foodsuggestion) + "&nutrition-type=cooking&calories=" + str(caloricRangeFrom) + "-" + str(caloricRangeTo)
        response_API = requests.get(create_foodtype_url)
        data = response_API.json()

        # Empty array to store the results in
        food_label = []
        dishCalories = []
        dishCarbohydrates = []
        dishProteins = []
        dishFats = []

        food_carbohydrates = data['hints'][0]['food']['nutrients']['CHOCDF']  # Amount of Carbohydrates
        food_protein = data['hints'][0]['food']['nutrients']['PROCNT']  # Amount of Protein
        food_fat = data['hints'][0]['food']['nutrients']['FAT']  # Amount of Fat

        # For loop which iterates through food labels in JSON
        for i in range(1, 7):
            food_label.append(str(data['hints'][i]['food']['label']))
            dishCalories.append(str(data['hints'][i]['food']['nutrients']['ENERC_KCAL']))  # Calories
            dishCarbohydrates.append(str(data['hints'][i]['food']['nutrients']['CHOCDF']))  # Carbohydrates
            dishProteins.append(str(data['hints'][i]['food']['nutrients']['PROCNT']))  # Proteins
            dishFats.append(str(data['hints'][i]['food']['nutrients']['FAT']))  # Fat

        if (str(food_label[1]) != "" and str(food_label[2]) != "" and str(food_label[3]) != "" and str(
                food_label[4]) != ""):
            speak_output = "You could try out the following dishes: 1. " + str(food_label[1]) + " 2. " + str(
                food_label[2]) + " 3. " + str(food_label[3]) + ", and 4. " + str(food_label[
                                                                                     4]) + ". Do you want to know the details of one of the dishes? (Example: Yes details second dish.)"
        else:
            speak_output = "Sorry, I couldn't find any dishes for this caloric range. Do you want to retry it?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Skill 5 (Dish suggestions with caloric range)
# Invocation:
class DishDetails(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DishDetails")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        dishnumber = slots["dishnumber"].value  # One, Two, Three, Four

        foodsuggestion = handler_input.attributes_manager.session_attributes["food"]
        caloricRangeFrom = handler_input.attributes_manager.session_attributes["rangeFrom"]
        caloricRangeTo = handler_input.attributes_manager.session_attributes["rangeTo"]

        # Make an API call to get dishes for the specified calories range
        create_foodtype_url = "https://api.edamam.com/api/food-database/v2/parser?app_id=cf568ffc&app_key=4ab5d97c9657f25c95983fd710a96627&ingr=" + str(
            foodsuggestion) + "&nutrition-type=cooking&calories=" + str(caloricRangeFrom) + "-" + str(caloricRangeTo)
        response_API = requests.get(create_foodtype_url)
        data = response_API.json()

        # Empty array to store the results in
        food_label = []
        dishCalories = []
        dishCarbohydrates = []
        dishProteins = []
        dishFats = []

        # For loop which iterates through food labels in JSON
        for i in range(1, 7):
            food_label.append(str(data['hints'][i]['food']['label']))
            dishCalories.append(str(data['hints'][i]['food']['nutrients']['ENERC_KCAL']))  # Calories
            dishCarbohydrates.append(str(data['hints'][i]['food']['nutrients']['CHOCDF']))  # Carbohydrates
            dishProteins.append(str(data['hints'][i]['food']['nutrients']['PROCNT']))  # Proteins
            dishFats.append(str(data['hints'][i]['food']['nutrients']['FAT']))  # Fat

        if (dishnumber == "first"):
            speak_output = "The dish " + str(food_label[1]) + " contains " + str(dishCalories[1]) + " calories, " + str(
                dishCarbohydrates[1]) + " grams of carbohydrates, " + str(
                dishProteins[1]) + " grams of proteins and " + str(dishFats[1]) + " grams of fats."
        elif (dishnumber == "second"):
            speak_output = "The dish " + str(food_label[2]) + " contains " + str(dishCalories[2]) + " calories, " + str(
                dishCarbohydrates[2]) + " grams of carbohydrates, " + str(
                dishProteins[2]) + " grams of proteins and " + str(dishFats[2]) + " grams of fats."
        elif (dishnumber == "third"):
            speak_output = "The dish " + str(food_label[3]) + " contains " + str(dishCalories[3]) + " calories, " + str(
                dishCarbohydrates[3]) + " grams of carbohydrates, " + str(
                dishProteins[3]) + " grams of proteins and " + str(dishFats[3]) + " grams of fats."
        elif (dishnumber == "fourth"):
            speak_output = "The dish " + str(food_label[4]) + " contains " + str(dishCalories[4]) + " calories, " + str(
                dishCarbohydrates[4]) + " grams of carbohydrates, " + str(
                dishProteins[4]) + " grams of proteins and " + str(dishFats[4]) + " grams of fats."
        else:
            speak_output = "Sorry, I couldn't find the details for your dish. Are you sure you said something like Yes details first/second/third/fourth dish? Just try again. "

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Intent: Handle vitamin deficiency
class VitaminDeficiency(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("VitaminDeficiency")(handler_input)

    def handle(self, handler_input):
        speak_output = "How are you feeling today?"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


class VitaminDeficiencyUserInput(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("VitaminDeficiencyUserInput")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        feeling = slots["feeling"].value

        # Store the feeling of the user in a session attribute
        handler_input.attributes_manager.session_attributes["feeling"] = feeling

        # Vitamin B1

        if (feeling == "like I have dry eyes" or feeling == "dry eyes"):
            speak_output = "Maybe you have vitamin A deficiency. Do you want to know the benefits of vitamin A are?"
        elif (
                feeling == "tired" or feeling == "restless" or feeling == "like I cannot concentrate" or feeling == "cannot concentrate" or feeling == "sick"):
            speak_output = "Maybe you have vitamin B deficiency. Do you want to know what the benefits of vitamin B are?"
        elif (feeling == "headache"):
            speak_output = "Maybe you have vitamin C deficiency. Do you want to know what the benefits of vitamin C are?"
        elif (feeling == "back pain"):
            speak_output = "Maybe you have vitamin D deficiency. Do you want to know the benefits of vitamin D?"
        elif (
                feeling == "difficulties walking" or feeling == "muscle weakness" or feeling == "like I have circulatory problems"):
            speak_output = "Maybe you have vitamin E deficiency. Do you want to know what the benefits of vitamin E are?"
        elif (feeling == "bruises" or feeling == "my nose bleeds"):
            speak_output = "Maybe you have vitamin K deficiency. Do you want to know what the benefits of vitamin K?"
        else:
            speak_output = "Sorry, I don't understand how you feel. Please retry."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class VitaminBenefits(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("VitaminBenefits")(handler_input)

    def handle(self, handler_input):

        userFeeling = handler_input.attributes_manager.session_attributes["feeling"]

        if (userFeeling == "like I have dry eyes") or (userFeeling == "dry eyes"):
            speak_output = "Vitamin A helps with ..."
        elif (userFeeling == "tired" or (userFeeling == "restless") or (userFeeling == "like I cannot concentrate") or (
                userFeeling == "cannot concentrate") or (userFeeling == "sick") or (userFeeling == "nauseous")):
            speak_output = "Vitamin B helps with ... "
        elif (userFeeling == "headache"):
            speak_output = "Vitamin C is useful for ... "
        elif (userFeeling == "back pain"):
            speak_output = "Vitamin D is useful for ... "
        elif (userFeeling == "difficulties walking" or (userFeeling == "muscle weakness") or (
                userFeeling == "like I have circulatory problems")):
            speak_output = "Vitamin E is ... "
        elif (userFeeling == "bruises" or (userFeeling == "my nose bleeds")):
            speak_output = "Vitamin K is..."
        else:
            speak_output = "Sorry, there was a problem. Please restart the skill."

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Skill 10
class FoodFunFacts(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("FoodFunFacts")(handler_input)

    def handle(self, handler_input):

        # Generates a random number from 0 to 10
        value = random.randint(0, 10)

        if (value == 0):
            speak_output = (
                "Crackers have holes in them for a reason."
                " During the baking process, if the crackers have holes in them, it prevents air bubbles from ruining the product.")
        elif (value == 1):
            speak_output = (
                "Ketchup used to be used as a medicine."
                " Back in the early 1800s, people thought tomatoes had medicinal qualities."
                " One doctor claimed they could treat diarrhea and indigestion, so he made a recipe for a type of tomato ketchup which then became a pill.")
        elif (value == 2):
            speak_output = (
                "White chocolate isn’t chocolate."
                " Its name is deceiving because white chocolate doesn’t have any components of regular chocolate."
                " It’s just a mixture of sugar, milk, vanilla, lecithin, and cocoa butter.")
        elif (value == 3):
            speak_output = (
                "Peppers don’t actually burn your mouth."
                " There’s a chemical in chili peppers called capsaicin that tricks your mouth into feeling like it’s being burned – that’s why spicy food hurts.")
        elif (value == 4):
            speak_output = (
                "Cheese is the most stolen food in the world."
                " In fact, it’s stolen so much it has its own percentage! About 4% of all cheese made around the globe ends up stolen.")
        elif (value == 5):
            speak_output = (
                "One in four hazelnuts ends up in Nutella."
                " Since they’re in such high demand, some universities are trying to grow them in labs in order to negate global shortages.")
        elif (value == 6):
            speak_output = (
                "Certain music can make you drink faster."
                " Researchers had an experiment to see how people’s drinking habits changed based on the music that was playing."
                " Loud music seemed to make people drink more, and faster.")
        elif (value == 7):
            speak_output = (
                "Expiration dates on bottled water have nothing to do with the water."
                " Water can’t expire – but the bottle it’s in can. Plastic bottles will eventually start leaking chemicals into the water."
                " It won’t make the water harmful to drink, but it will make it taste less fresh.")
        elif (value == 8):
            speak_output = (
                "Honey is bee vomit."
                " When bees collect nectar, they drink it and keep it in their stomach"
                " Once they’re back at the hive, they regurgitate the nectar into the hive.")
        elif (value == 9):
            speak_output = (
                " French fries originated in Belgium, not France!"
                " They are only called French fries because they are French cut.")
        elif (value == 10):
            speak_output = (
                "Strawberries are not berries."
                " Technically, berries only have seeds on the inside, a rule which is obviously broken by strawberries!")
        else:
            print("Sorry, I think there's some kind of issue. Please retry.")

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(FoodInfoHandler())
sb.add_request_handler(FoodRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(ProfileHandler())
sb.add_request_handler(NameHandler())
sb.add_request_handler(AgeHandler())
sb.add_request_handler(WeightHandler())
sb.add_request_handler(HeightHandler())
sb.add_request_handler(BMICalculator())
sb.add_request_handler(CaloriesCalculator())
sb.add_request_handler(DietHandler())
sb.add_request_handler(LoseWeight())
sb.add_request_handler(GainWeight())
sb.add_request_handler(MaintainWeight())
sb.add_request_handler(FoodIntakeInfoHandler())
sb.add_request_handler(CalculateFoodIntake())
sb.add_request_handler(CalculateFoodIntakeSum())
sb.add_request_handler(DishSuggestionsInfoIntent())
sb.add_request_handler(DishSuggestionsUserInput())
sb.add_request_handler(DishDetails())
sb.add_request_handler(VitaminDeficiency())
sb.add_request_handler(VitaminDeficiencyUserInput())
sb.add_request_handler(VitaminBenefits())
sb.add_request_handler(FoodFunFacts())

# IntentReflectorHandler should be the last one, so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()