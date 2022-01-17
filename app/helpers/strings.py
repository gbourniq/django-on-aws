"""API messages"""

SIGNUP_MSG = "New account created: {account_name}. Please check your emails."
LOGOUT = "Logged out successfully!"
LOGIN = "You are now logged in as {username}"
REDIRECT_AFTER_LOGIN = "Redirecting user back to {secure_page}"
INVALID_LOGIN = "Invalid username or password."

NO_ITEM_IN_CATEGORY = "Oops.. Category {category} does not contain any item!"
MSG_404 = "Oops.. There's nothing here."
MSG_500 = "Internal Server Error (500)"

INVALID_FORM = "Email form is invalid."
CONTACTUS_FORM = "Success! Thank you for your message."

SNS_SERVICE_RESPONSE = "SNS service response: {response}"
SNS_TOPIC_NOT_CONFIGURED_USER_FRIENDLY = "Oops, your email could not be sent."
SNS_TOPIC_NOT_CONFIGURED = (
    "ContactForm email not forward to Slack because the SNS_TOPIC_ARN "
    "environment variable is not configured."
)
