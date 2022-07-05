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

# Required for generating random numbers
import random

# Required for DynamoDB
import os
import boto3

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Defining the database region, table name and dynamodb persistence adapter
ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')
ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = (
            "Welcome to the nutrition consultant application!"
            " You have multiple options:"
            " - 1. Create Profile"  # done
            " - 2. Search Food Information"  # done
            " - 3. Get Session Logs"  # done
            " - 4. Calculate Food Intake"  # done
            " - 5. Dish Suggestions With Caloric Range"  # done
            " - 6. Handle Vitamin Deficiency"  # done
            " - 7. Autocomplete Food Ingredients"  # done
            " - 8. Get Nutrient Information"  # done
            " - 9. Convert Nutrients Into Calories"  # done
            " - 10. Food Fun Facts" # done
            " - 11. Load Profile" # multi profile support not done
            " - 12. Delete Session Logs and Profile"  # done
        )  # done

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


# Option 2: Search food information
class FoodInfoHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("FoodInfoIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Ask me how many calories certain food has! Ask, for instance, 'How many calories does a banana have?'"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 2: Search food information
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
        speech = "Unfortunately, that did not work. Retry using a different phrase or use an option from 1 to 11."
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

        speak_output = "Sorry, that didn't work. Retry or use an option from 1 to 11."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 1: Create Profile
class ProfileHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CreateProfile")(handler_input)

    def handle(self, handler_input):
        speak_output = "Please state your name. Say, for instance, 'My name is Alexa.'"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 1: Create Profile
class NameHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NameHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userName = slots["name"].value

        # "a" - Append - Opens a file for appending, creates the file if it does not exist
        f = open("/tmp/profile.txt", "a")
        f.write("User: " + str(userName) + ". ")
        f.close()
        # open and read the file after the appending:
        # f = open("/tmp/profile.txt", "r")
        # readFile = (f.read())
        # f.close()

        # Store user's name in DB
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_name"] = userName
        handler_input.attributes_manager.save_persistent_attributes()

        speak_output = "Hello " + str(userName) + "! How old are you?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 1: Create Profile
class AgeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AgeHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userAge = int(slots["age"].value)
        handler_input.attributes_manager.session_attributes["age"] = userAge

        f = open("/tmp/profile.txt", "a")
        f.write("Age: " + str(userAge) + ". ")
        f.close()

        # Store user's age in DB
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_age"] = userAge
        handler_input.attributes_manager.save_persistent_attributes()

        speak_output = "You're only " + str(userAge) + "? How much do you weigh if I may ask?"

        # handler_input.response_builder.speak(speak_output)
        # return handler_input.response_builder.response
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 1: Create Profile
class WeightHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("WeightHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userWeight = int(slots["userweight"].value)
        handler_input.attributes_manager.session_attributes["userweight"] = userWeight

        f = open("/tmp/profile.txt", "a")
        f.write("Weight: " + str(userWeight) + " kg. ")
        f.close()

        # Store user's weight in DB
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_weight"] = userWeight
        handler_input.attributes_manager.save_persistent_attributes()

        speak_output = "So you're weighing " + str(userWeight) + " kilograms. How tall are you?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 1: Create Profile
class HeightHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("HeightHandler")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userHeight = int(slots["userheight"].value)
        handler_input.attributes_manager.session_attributes["userheight"] = userHeight

        f = open("/tmp/profile.txt", "a")
        f.write("Height: " + str(userHeight) + " cm. ")
        f.close()

        # Store user's weight in DB
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_height"] = userHeight
        handler_input.attributes_manager.save_persistent_attributes()

        if (int(userHeight) <= 160):
            speak_output = "You're small! Tell me your gender and I'll calculate your Body Mass Index (BMI)."
        else:
            speak_output = "You're big! Tell me your gender and I'll calculate your Body Mass Index (BMI)."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 1: Create Profile
# Calculates the BMI
# Gender: Female
# Weight: 55 kg
# Height: 160 cm
# Step 1: ((Height in cm)^2)/10000) = ((160)^2)/10000 = 2.56
# Step 2: (Weight)/2.56 = 21.5
class BMICalculator(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BMICalculator")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        userGender = slots["gender"].value
        handler_input.attributes_manager.session_attributes["gender"] = userGender

        calcWeight = handler_input.attributes_manager.session_attributes["userweight"]
        calcHeight = handler_input.attributes_manager.session_attributes["userheight"]

        step1 = (float(calcHeight) * float(calcHeight)) / 10000  # (160*160)/10000 = 2.56
        step2 = (float(calcWeight) / step1)  # 55 / 2.56 = 21.5

        speak_output = "calcWeight: " + str(calcWeight) + " and calcHeight: " + str(calcHeight) + " step2: " + str(
            round(step2, 2))

        f = open("/tmp/profile.txt", "a")
        f.write("BMI: " + str(round(step2, 2)) + ". ")
        f.close()

        # Store user's BMI in DB
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_bmi"] = str(round(step2, 2))
        handler_input.attributes_manager.save_persistent_attributes()

        # Store the data in logs
        f = open("/tmp/profile.txt", "a")
        f.write("BMI: " + str(round(step2, 2)) + ". ")
        f.close()

        # Store user's BMI in DB
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_bmi"] = str(round(step2, 2))
        handler_input.attributes_manager.save_persistent_attributes()

        if (step2 <= 18.5):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you are slightly underweight.  Do you want to know what your daily basal metabolic rate is?"
        elif (step2 > 18.5 or round(step2, 2) <= 24.9):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and your weight is in the normal range. Do you want to know what your daily basal metabolic rate is?"
        elif (step2 >= 25 or round(step2, 2) <= 29.9):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you are overweight. Do you want to know what your daily basal metabolic rate is?"
        elif (step2 >= 30 or round(step2, 2) <= 34.9):
            speak_output = "Your BMI is " + str(round(step2,
                                                      2)) + " and you are very overweight.  Do you want to know what your daily basal metabolic rate is?"
        elif (step2 >= 35 or round(step2, 2) <= 39.9):
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


# Option 1: Create Profile
# Calculates the calories (basal metabolism) a person needs per day
# Formula Women: 655.1 + (9.6 * weight in kg) + (1.8 * height in cm) - (4.7 * age)
# Formula Men: 66.47 + (13,7 * weight in kg) + (5 * height in cm) - (6,8 * age)
class CaloriesCalculator(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaloriesCalculator")(handler_input)

    def handle(self, handler_input):
        userGender = handler_input.attributes_manager.session_attributes["gender"]
        calcAge = handler_input.attributes_manager.session_attributes["age"]
        calcWeight = handler_input.attributes_manager.session_attributes["userweight"]
        calcHeight = handler_input.attributes_manager.session_attributes["userheight"]

        formulamen = float(66.47 + (13.7 * float(calcWeight) + (5 * float(calcHeight) - (6.8 * float(calcAge)))))
        roundCaloriesMen = round(formulamen, 2)

        formulawomen = float(655.1 + (9.6 * float(calcWeight) + (1.8 * float(calcHeight) - (4.7 * float(calcAge)))))
        roundCaloriesWomen = round(formulawomen, 2)

        handler_input.attributes_manager.session_attributes["caloriesMen"] = roundCaloriesMen
        handler_input.attributes_manager.session_attributes["caloriesWomen"] = roundCaloriesWomen

        if (userGender == "man" or userGender == "a male" or userGender == "a man" or userGender == "male"):
            f = open("/tmp/profile.txt", "a")
            f.write("Daily basal metabolic rate :" + str(roundCaloriesMen) + ".")
            f.close()

            # Store user's Calories in DB (male)
            # persistent_attributes = handler_input.attributes_manager.persistent_attributes
            # persistent_attributes["user_calories"] = str(roundCaloriesMen)
            # handler_input.attributes_manager.save_persistent_attributes()

            speak_output = "Your daily basal metabolic rate is about " + str(
                roundCaloriesMen) + " calories. Do you want to lose, gain or maintain your weight?"
        elif (
                userGender == "woman" or userGender == "female" or userGender == "girl" or userGender == "a woman" or userGender == "a girl"):
            f = open("/tmp/profile.txt", "a")
            f.write("Daily basal metabolic rate :" + str(roundCaloriesWomen) + ". ")
            f.close()

            # Store user's Calories in DB (female)
            # persistent_attributes = handler_input.attributes_manager.persistent_attributes
            # persistent_attributes["user_calories"] = str(roundCaloriesWomen)
            # handler_input.attributes_manager.save_persistent_attributes()

            speak_output = "Your daily basal metabolic rate is about " + str(
                roundCaloriesWomen) + " calories. Do you want to lose, gain or maintain your weight?"
        else:
            speak_output = "I could not identify your gender, sorry. Ask me to calculate your calories again, and I'll retry."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 1: Create Profile
class GainWeightHandler(AbstractRequestHandler):
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
            speak_output = "You have to eat " + str(
                caloricSurplusWomen) + " calories daily to gain weight to build muscle."
        else:
            speak_output = "You have to eat " + str(
                caloricSurplusMen) + " calories daily to gain weight to build muscle."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 1: Create Profile
class LoseWeightHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("LoseWeightHandler")(handler_input)

    def handle(self, handler_input):
        userGender = handler_input.attributes_manager.session_attributes["gender"]
        roundCaloriesWomen = handler_input.attributes_manager.session_attributes["caloriesWomen"]
        roundCaloriesMen = handler_input.attributes_manager.session_attributes["caloriesMen"]

        caloricDeficitWomen = float(roundCaloriesWomen - 300)
        caloricDeficitMen = float(roundCaloriesMen - 500)

        if (userGender == "Woman"):
            speak_output = "You have to eat " + str(caloricDeficitWomen) + " calories daily to lose weight."
        else:
            speak_output = "You have to eat " + str(caloricDeficitMen) + " calories daily to lose weight."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 1: Create Profile
class MaintainWeight(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("MaintainWeight")(handler_input)

    def handle(self, handler_input):
        userGender = handler_input.attributes_manager.session_attributes["gender"]
        roundCaloriesWomen = handler_input.attributes_manager.session_attributes["caloriesWomen"]
        roundCaloriesMen = handler_input.attributes_manager.session_attributes["caloriesMen"]

        if (userGender == "Woman"):
            speak_output = "You have to eat around " + str(
                roundCaloriesWomen) + " calories daily to maintain your weight."
        else:
            speak_output = "You have to eat around " + str(
                roundCaloriesMen) + " calories daily to maintain your weight."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 3: Get Session Logs
class SessionLogs(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SessionLogs")(handler_input)

    def handle(self, handler_input):
        f = open("/tmp/profile.txt", "r")
        readFile = (f.read())
        f.close()

        speak_output = "I have stored the following logs in this session: " + readFile

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                # .ask(reprompt_text)
                .response
        )


# Option 4: Calculate Food Intake
class FoodIntakeInfoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("FoodIntakeInfoHandler")(handler_input)

    def handle(self, handler_input):
        speak_output = "Tell me what you have eaten today or calculate the nutritional values of other food. Say, for example, 'I have eaten apple today'."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 4: Calculate Food Intake
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

        speak_output = "Add more food or say 'Calculate'."

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 4: Calculate Food Intake
# Outputs the nutritional values we calculated in the class CalculateFoodIntake
class CalculateFoodIntakeSum(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CalculateFoodIntakeSum")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes

        f = open("/tmp/profile.txt", "a")
        f.write("Food intake today : - " + str(round(session_attr["foodCaloriesSum"], 2)) + " calories. - " + str(
            round(session_attr["foodCarbohydratesSum"], 2)) + " g carbohydrates - " + str(
            round(session_attr["foodFatSum"], 2)) + " g fat - " + str(
            round(session_attr["foodProteinsSum"], 2)) + " g proteins. ")
        f.close()

        # Store user's food intake in DB (female)
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_foodintakeCalories"] = str(round(session_attr["foodCaloriesSum"], 2))
        persistent_attributes["user_foodintakeCarbohydrates"] = str(round(session_attr["foodCarbohydratesSum"], 2))
        persistent_attributes["user_foodintakeFat"] = str(round(session_attr["foodFatSum"], 2))
        persistent_attributes["user_foodintakeProteins"] = str(round(session_attr["foodProteinsSum"], 2))
        handler_input.attributes_manager.save_persistent_attributes()

        speak_output = "Total: " + str(round(session_attr["foodCaloriesSum"], 2)) + " calories. Carbohydrates:  " + str(
            round(session_attr["foodCarbohydratesSum"], 2)) + " grams. Fats: " + str(
            round(session_attr["foodFatSum"], 2)) + " grams. Proteins " + str(
            round(session_attr["foodProteinsSum"], 2)) + " grams"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 5 (Dish Suggestions With Caloric Range)
class DishSuggestionsInfoIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DishSuggestionsInfoIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Tell me a food item and a caloric range. (Example: Egg Range 100 to 300)"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 5: Dish suggestions with caloric range
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
                                                                                     4]) + ". Do you want to know the details of one of the dishes? (Say, for example, 'Yes details second dish.')"
        else:
            speak_output = "Sorry, I couldn't find any dishes for this caloric range. Do you want to retry it?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 5: Dish Suggestions With Caloric Range
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

        if (dishnumber == "first" or dishnumber == "1st"):
            speak_output = "The dish " + str(food_label[1]) + " contains " + str(dishCalories[1]) + " calories, " + str(
                dishCarbohydrates[1]) + " grams of carbohydrates, " + str(
                dishProteins[1]) + " grams of proteins and " + str(dishFats[1]) + " grams of fats."
        elif (dishnumber == "second" or dishnumber == "2nd"):
            speak_output = "The dish " + str(food_label[2]) + " contains " + str(dishCalories[2]) + " calories, " + str(
                dishCarbohydrates[2]) + " grams of carbohydrates, " + str(
                dishProteins[2]) + " grams of proteins and " + str(dishFats[2]) + " grams of fats."
        elif (dishnumber == "third" or dishnumber == "3rd"):
            speak_output = "The dish " + str(food_label[3]) + " contains " + str(dishCalories[3]) + " calories, " + str(
                dishCarbohydrates[3]) + " grams of carbohydrates, " + str(
                dishProteins[3]) + " grams of proteins and " + str(dishFats[3]) + " grams of fats."
        elif (dishnumber == "fourth" or dishnumber == "4th"):
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


# Option 6: Handle Vitamin Deficiency
class VitaminDeficiency(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("VitaminDeficiency")(handler_input)

    def handle(self, handler_input):
        speak_output = "How are you feeling today?"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 6: Handle Vitamin Deficiency
class VitaminDeficiencyUserInput(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("VitaminDeficiencyUserInput")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        feeling = slots["feeling"].value

        f = open("/tmp/profile.txt", "a")
        f.write("Feeling: " + str(feeling) + " . ")
        f.close()

        # Store user feeling in database
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        persistent_attributes["user_feeling"] = str(feeling)
        handler_input.attributes_manager.save_persistent_attributes()

        # Store the feeling of the user in a session attribute
        handler_input.attributes_manager.session_attributes["feeling"] = str(feeling)

        if (feeling == "like I have dry eyes" or feeling == "dry eyes"):
            speak_output = "Maybe you have vitamin A deficiency. Say 'benefits' if you want to know more about the benefits of vitamin A."
        elif (
                feeling == "tired" or feeling == "restless" or feeling == "like I cannot concentrate" or feeling == "cannot concentrate" or feeling == "sick"):
            speak_output = "Maybe you have vitamin B deficiency. Say 'benefits' if you want to know more about the benefits of vitamin B."
        elif (feeling == "headache"):
            speak_output = "Maybe you have vitamin C deficiency. Say 'benefits' if you want to know more about the benefits of vitamin C."
        elif (feeling == "back pain"):
            speak_output = "Maybe you have vitamin D deficiency. Say 'benefits' if you want to know more about the benefits of vitamin D."
        elif (
                feeling == "difficulties walking" or feeling == "muscle weakness" or feeling == "like I have circulatory problems"):
            speak_output = "Maybe you have vitamin E deficiency. Say 'benefits' if you want to know more about the benefits of vitamin E."
        elif (feeling == "bruises" or feeling == "my nose bleeds"):
            speak_output = "Maybe you have vitamin K deficiency. Say 'benefits' if you want to know more about the benefits of vitamin K."
        else:
            speak_output = "Sorry, I don't understand how you feel. Please retry."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 6: Handle Vitamin Deficiency
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


# Option 7: Autocomplete Food Ingredients
class AutocompleteFoodInfo(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AutocompleteFoodInfo")(handler_input)

    def handle(self, handler_input):
        speak_output = "Name a few letters, and I will try to find all food ingredients that contain those! For example: Autocomplete nut"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 7: Autocomplete Food Ingredients
class AutocompleteFoodUserInput(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AutocompleteFoodUserInput")(handler_input)

    def handle(self, handler_input):

        slots = handler_input.request_envelope.request.intent.slots
        substring = slots["substring"].value

        searchResults = []

        # Make an API call to get results for the specified substring
        create_foodsubstring_url = "https://api.edamam.com/auto-complete?app_id=cf568ffc&app_key=4ab5d97c9657f25c95983fd710a96627&q=" + str(
            substring)

        response_API = requests.get(create_foodsubstring_url)
        data = response_API.json()

        for i in range(1, 5):
            searchResults.append(data)

        for list in searchResults:
            for string in list:
                None

        if (str(list[0]) != "" and str(list[1]) != "" and str(list[2]) != "" and str(list[3]) != ""):
            speak_output = "I've found the following results: " + str(list[0]) + ", " + str(list[1]) + ", " + str(
                list[2]) + ", " + str(list[3]) + ", and " + str(
                list[4]) + ". You can try another ingredient or function now."
        else:
            speak_output = "Sorry, I couldn't find any ingredients for your specified letters. You can try it with other letters or call another function.?"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 8: Get Nutrient Information
class NutrientDetailsInfo(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NutrientDetailsInfo")(handler_input)

    def handle(self, handler_input):
        speak_output = "Ask me about a nutrient and I will check if I can tell you more about it! For example: Magnesium"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 8: Get Nutrient Information
class NutrientDetailsUserInput(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("NutrientDetailsUserInput")(handler_input)

    def handle(self, handler_input):

        slots = handler_input.request_envelope.request.intent.slots
        nutrient = slots["nutrient"].value

        # The .lower function checks if the string has been written in upper or lower case.
        # Without it, we would have written if (nutrient == "Proteins" or nutrient == "proteins"):
        if (nutrient == "proteins"):
            speak_output = "Proteins are necessary for tissue formation, cell reparation, and hormone and enzyme production. They are essential for building strong muscles and a healthy immune system. Try another nutrient or function now."
        elif (nutrient == "carbohydrates"):
            speak_output = "Carbohydrates are a ready source of energy for the body and provide structural constituents for the formation of cells. Try another nutrient or function now."
        elif (nutrient == "fat"):
            speak_output = "Fats provide stored energy for the body, functions as structural components of cells, and signaling molecules for proper cellular communication. They provide insulation to vital organs and works to maintain body temperature. Try another nutrient or function now."
        elif (nutrient == "vitamins"):
            speak_output = "Vitamins regulate body processes and promote normal body-system functions. Try another nutrient or function now."
        elif (nutrient == "minerals"):
            speak_output = "Minerals regulate body processes. They are necessary for proper cellular function, and comprise body tissue. Try another nutrient or function now."
        elif (nutrient == "water"):
            speak_output = "Water ransports essential nutrients to all body parts. It transports waste products for disposal, and aids with body temperature maintenance. You should drink it a lot! Try another nutrient or function now."
        elif (nutrient == "sodium"):
            speak_output = "Major functions of sodium are fluid balance, nerve transmission and muscle contraction. Try another nutrient or function now."
        elif (nutrient == "chloride"):
            speak_output = "Major functions of chloride are fluid balance and stomach acid production. Try another nutrient or function now."
        elif (nutrient == "potassium"):
            speak_output = "Major functions of potassium are fluid balance, nerve transmission, muscle contraction. Try another nutrient or function now."
        elif (nutrient == "calcium"):
            speak_output = "Major functions of calcium are bone and teeth health maintenance, nerve transmission, muscle contraction and blood clotting. Try another nutrient or function now."
        elif (nutrient == "phosphorus"):
            speak_output = "Major functions of phosphoures are bone and teeth health maintenance and acid-base balance. Try another nutrient or function now."
        elif (nutrient == "magnesium"):
            speak_output = "Major functions of magnesium are protein production, nerve transmission, muscle contraction. Try another nutrient or function now."
        elif (nutrient == "sulfur"):
            speak_output = "Sulfur is important for the production of protein. Try another nutrient or function now."
        elif (nutrient == "iron"):
            speak_output = "Iron carries oxygen and assists in energy production. Try another nutrient or function now."
        elif (nutrient == "zinc"):
            speak_output = "Major function of zinc are protein and DNA production, wound healing, growth and immune system functions. Try another nutrient or function now."
        elif (nutrient == "iodine"):
            speak_output = "Major functions of iodine are thyroid hormone production, growth and metabolism. Try another nutrient or function now."
        elif (nutrient == "selenium"):
            speak_output = "Selenium is an antioxidant. Try another nutrient or function now."
        elif (nutrient == "copper"):
            speak_output = "Copper is a coenzyme and used for iron metabolism. Try another nutrient or function now."
        elif (nutrient == "manganese"):
            speak_output = "Manganese is a coenzyme. Try another nutrient or function now."
        elif (nutrient == "fluoride"):
            speak_output = "Fluoride is important for bone and teeth health maintenance and tooth decay prevention. Try another nutrient or function now."
        elif (nutrient == "chromium"):
            speak_output = "Chromium assists insulin in glucose metabolism. Try another nutrient or function now."
        elif (nutrient == "molybendum"):
            speak_output = "Molybendum is a coenzyme. Try another nutrient or function now."
        else:
            speak_output = "Sorry, I couldn't find your nutrient. Try another one or use one of the options from earlier. "

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 9: Convert Nutrients Into Calories
class ConvertNutrientsInfo(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ConvertNutrientsInfo")(handler_input)

    def handle(self, handler_input):
        speak_output = "Using this option, you can calculate how many calories a certain amount of nutrients has. For example: Convert 100 grams of fat"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 9: Convert Nutrients Into Calories
class ConvertNutrientsUserInput(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ConvertNutrientsUserInput")(handler_input)

    def handle(self, handler_input):

        slots = handler_input.request_envelope.request.intent.slots
        nutrientweight = slots["nutrientweight"].value  # Weight in grams
        type = slots["type"].value  # carbs/fat/proteins

        calculateCaloriesCarbs = int(nutrientweight) * 4
        calculateCaloriesFats = int(nutrientweight) * 9
        calculateCaloriesProteins = int(nutrientweight) * 4

        # 1 gram of fat = 9 calories
        # 1 gram of carbohydrates = 4 calories
        # 1 gram of proteins = 4 calories

        if (type == "carbohydrates"):
            speak_output = str(nutrientweight) + " gram of " + str(type) + " amounts to " + str(
                calculateCaloriesCarbs) + " calories. You can try another nutrient or option now."
        elif (type == "fat" or type == "fats"):
            speak_output = str(nutrientweight) + " gram of " + str(type) + " amounts to " + str(
                calculateCaloriesFats) + " calories. You can try another nutrient or option now."
        elif (type == "protein" or type == "proteins"):
            speak_output = str(nutrientweight) + " gram of " + str(type) + " amounts to " + str(
                calculateCaloriesProteins) + " calories. You can try another nutrient or option now."
        else:
            speak_output = "Sorry, I couldn't calculate that. Try again using this format: Convert 300 grams of protein"

        return (
            handler_input.response_builder.speak(speak_output).ask(speak_output).response
        )


# Option 10: Food Fun Facts
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


# Option 11: Load Profile
class LoadProfile(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("LoadProfile")(handler_input)

    def handle(self, handler_input):
        persistent_attributes = handler_input.attributes_manager.persistent_attributes

        try:
            # Read user's name from the DB.
            user_name = persistent_attributes['user_name']
            speak_output = "I have loaded the profile of " + str(
                user_name) + ". You can calculate your BMI now directly."
            reprompt = "Test reprompt"
        except:
            speak_output = "Unfortunately, this did not work."

        # persistent_attributes = handler_input.attributes_manager.persistent_attributes
        # speak_output = "I have loaded the following profile. Name: " + persistent_attributes["user_name"] + " . Age: " + persistent_attributes["age"] + " ."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 11
class BMICalculatorProfileLoaded(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BMICalculatorProfileLoaded")(handler_input)

    def handle(self, handler_input):
        persistent_attributes = handler_input.attributes_manager.persistent_attributes

        try:
            # Read user's name from the DB.
            user_name = persistent_attributes['user_name']
            user_weight = persistent_attributes['user_weight']
            user_height = persistent_attributes['user_height']

            step1 = (float(user_height) * float(user_height)) / 10000  # (160*160)/10000 = 2.56
            step2 = (float(user_weight) / step1)  # 55 / 2.56 = 21.5

            speak_output = "The BMI of " + str(user_name) + " is: " + str(round(step2, 2))
        except:
            speak_output = "Unfortunately, this did not work."

        # persistent_attributes = handler_input.attributes_manager.persistent_attributes
        # speak_output = "I have loaded the following profile. Name: " + persistent_attributes["user_name"] + " . Age: " + persistent_attributes["age"] + " ."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 12
class DeleteProfile(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DeleteProfile")(handler_input)

    def handle(self, handler_input):
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        user_name = persistent_attributes['user_name']

        # Clear the contents of the text file
        f = open("/tmp/profile.txt", "a")
        f.truncate(0)
        f.close()

        speak_output = "I have deleted the session logs. Which profile would you like to delete? I have stored the profile(s) of " + str(user_name) + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# Option 12
class DeleteProfileUserInput(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DeleteProfileUserInput")(handler_input)

    def handle(self, handler_input):
        persistent_attributes = handler_input.attributes_manager.persistent_attributes

        slots = handler_input.request_envelope.request.intent.slots
        user = slots["user"].value

        try:
            # Delete all attributes from the dynamo database
            handler_input.attributes_manager.delete_persistent_attributes()
            speak_output = "I have deleted the data for " + str(user) + "."

        except:
            speak_output = "Unfortunately, I could not delete the data of " + user + " . Please retry by saying 'Delete username'."

        return (
            handler_input.response_builder.response
        )


# sb = SkillBuilder()
sb = CustomSkillBuilder(persistence_adapter=dynamodb_adapter)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(ProfileHandler())  # Option 1
sb.add_request_handler(NameHandler())  # Option 1
sb.add_request_handler(AgeHandler())  # Option 1
sb.add_request_handler(WeightHandler())  # Option 1
sb.add_request_handler(HeightHandler())  # Option 1
sb.add_request_handler(BMICalculator())  # Option 1
sb.add_request_handler(CaloriesCalculator())  # Option 1
sb.add_request_handler(LoseWeightHandler())  # Option 1
sb.add_request_handler(GainWeightHandler())  # Option 1
sb.add_request_handler(MaintainWeight())  # Option 1
sb.add_request_handler(FoodInfoHandler())  # Option 2
sb.add_request_handler(FoodRequestHandler())  # Option 2
sb.add_request_handler(SessionLogs())  # Option 3
sb.add_request_handler(FoodIntakeInfoHandler())  # Option 4
sb.add_request_handler(CalculateFoodIntake())  # Option 4
sb.add_request_handler(CalculateFoodIntakeSum())  # Option 4
sb.add_request_handler(DishSuggestionsInfoIntent())  # Option 5
sb.add_request_handler(DishSuggestionsUserInput())  # Option 5
sb.add_request_handler(DishDetails())  # Option 5
sb.add_request_handler(VitaminDeficiency())  # Option 6
sb.add_request_handler(VitaminDeficiencyUserInput())  # Option 6
sb.add_request_handler(VitaminBenefits())  # Option 6
sb.add_request_handler(AutocompleteFoodInfo())  # Option 7
sb.add_request_handler(AutocompleteFoodUserInput())  # Option 7
sb.add_request_handler(NutrientDetailsInfo())  # Option 8
sb.add_request_handler(NutrientDetailsUserInput())  # Option 8
sb.add_request_handler(ConvertNutrientsInfo())  # Option 9
sb.add_request_handler(ConvertNutrientsUserInput())  # Option 9
sb.add_request_handler(FoodFunFacts())  # Option 10
sb.add_request_handler(LoadProfile())  # Option 11
sb.add_request_handler(BMICalculatorProfileLoaded())  # Option 11
sb.add_request_handler(DeleteProfile())  # Option 12
sb.add_request_handler(DeleteProfileUserInput())  # Option 12


# IntentReflectorHandler should be the last one, so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()