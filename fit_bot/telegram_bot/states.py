from enum import Enum
from telebot.handler_backends import State, StatesGroup


class States(Enum):
    START = "start"
    STATE_1 = "state_1"
    STATE_2 = "state_2"
    ASK_GENDER = 'ask_gender'
    ASK_AGE = 'ask_age'
    ASK_HEIGHT = 'ask_height'
    ASK_WEIGHT = 'ask_weight'
    ASK_ACTIVITY = 'ask_activity'
    FINISHED = 'finished'
    ASK_INITIALS = 'ask_initials'
    CONTINUE_INITIALS = 'continue_initials'
    ASK_PLACE = 'ask_place'
    ASK_GOAL = 'ask_goal'
    ASK_EXPERIENCE = 'ask_experience'
    WRITE_CALORIES = 'write_calories'
    ADD_REMOVE_CALORIES = 'add_remove_calories'
    MAILING = 'mailing'
    CHOOSING_MAILING_CATEGORY = 'choosing_mailing_category'
    ENTER_TEXT_FOR_MAILING = 'enter_text_for_mailing'
    UPLOAD_VIDEO = 'upload_video'
    CHOOSE_PRODUCT = 'choose_product'
    ASK_PRODUCT_NAME = 'ask_product_name'
    ADD_GRAMS = 'add_grams'
    PRODUCT_ACTIONS = 'product_actions'
    ADD_PRODUCT = 'add_product'
    CHANGE_PRODUCT = 'change_product'
    CHANGE_GRAMS = 'change_grams'


class PurchaseStates(StatesGroup):
    initial = State()
    added_initials = State()
    choose_bank = State()


class TestStates(StatesGroup):
    initial = State()
    start_test = State()
    ask_name = State()
    choose_gender = State()
    enter_height = State()
    enter_weight = State()
    enter_age = State()
    ask_activity = State()
    ask_goal = State()


class CourseInteraction(StatesGroup):
    initial = State()
    enter_own_KBJU = State()
    enter_new_product = State()
    choose_product = State()
    continue_choosing_product = State()
    enter_grams = State()
    choose_amount = State()
    enter_meal_name = State()
    continue_meal_name = State()
    enter_meal_calories = State()
    enter_meal_protein = State()
    redacting = State()
    delete_product = State()


class AdminStates(StatesGroup):
    initial = State()
    mailing = State()
    choosing_mailing_category = State()
    upload_video = State()
    enter_mailing_text = State()
    upload_photo = State()


class AfterPurchaseStates(StatesGroup):
    initial = State()


class GeopositionStates(StatesGroup):
    initial = State()
