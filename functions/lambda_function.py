def lambda_handler(event, context):
    print(event)
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": { "Content-Type": "text/plain" },
        "body": "Hello from an authorized API!!"
    }
