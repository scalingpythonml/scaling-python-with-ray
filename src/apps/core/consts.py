from enum import Enum


class OnboardingStepsEnum(Enum):
    SIGN_UP = 1
    DETAILS = 2
    ADD_DEVICE = 3
    PICK_PLAN = 4
    PAYMENT = 5
    ACTIVATION = 6


class ProfileStepsEnum(Enum):
    DASHBOARD = 1
    BILLING = 2
    SETTINGS = 3