import random, logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Order received from user 4821")
    errors = [
        "ERROR: Database connection timed out after 30s",
        "ERROR: Payment service returned HTTP 503",
        "ERROR: Failed to parse JSON body from client",
    ]
    for _ in range(random.randint(2, 4)):
        logger.error(random.choice(errors))
    return {"statusCode": 200}