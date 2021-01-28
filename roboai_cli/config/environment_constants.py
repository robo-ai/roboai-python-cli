CURRENT_ENVIRONMENT = "CURRENT_ENV"
ENVIRONMENTS = "ENVIRONMENTS"
API_KEY_SETTING = "API_KEY"
API_AUTH_TOKEN_SETTING = "API_AUTH_TOKEN"
API_ENDPOINT_SETTING = "API_ENDPOINT"
PACKAGE_NAME = "robo-ai"

DEFAULT_SETTINGS = {
    CURRENT_ENVIRONMENT: "",
    "production": {
        API_KEY_SETTING: "",
        API_AUTH_TOKEN_SETTING: "",
        API_ENDPOINT_SETTING: {
            "url": "https://robo-core-production.eu-de.mybluemix.net",
            "username": "m2m",
            "password": "adJl777lIxMuF4iA8Ai9",
        },
    },
}
