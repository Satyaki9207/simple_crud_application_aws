import boto3
import json
import logging
from custom_encoder import CustomEncoder

logger=logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName="product-inventory"
dynamodb=boto3.resource("dynamodb")
table=dynamodb.Table(dynamodbTableName)

getMethod="GET"
postMethod="POST"
patchMethod="PATCH"
deleteMethod="DELETE"

healthPath="/health"
productPath="/product"
productsPath="/products"


def buildresponse(status,body=None):
    # response builder for statuscode 200
    response={
        "statusCode":status,
        "headers":{
            "Content-Type":"application/json",
            "Access-Control-Allow-Origin":"*"
        }
    }

    if body is not None:
        response["body"]=json.dumps(body,cls=CustomEncoder)

    return response

def getProduct(productId):
    # fetch a product by productId
    try:
        response=table.get_item(Key={'productId':productId})

        if "Item" in response:
            return buildresponse(200,response['Item'])
        else:
            return buildresponse(404,"Product not found")
    except:
        logger.exception("Perform custom error handling here")
    return response

def getProducts():
    # fetch all products
    try:
        response=table.scan()
        result=response['Item']

        while 'LastEvaluatedKey' in response:
            response=table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Item'])
        
        body={
            'products':result            
        }
        return buildresponse(200,body)
    except:
        logger.exception("Do custom error handling")
    
def saveProduct(requestBody):
    try:
        table.put_item(Item=requestBody)
        body={
            'Operation':'SAVE',
            'Message':'SUCCESS',
            'Item':requestBody
        }
        return buildresponse(200,body)
    except:
        logger.exception("Custom error handling")

def modifyProduct(productId,updateKey,updateValue):
    try:
        response=table.update_item(
            Key={'productId':productId},
            UpdateExpression='set %s = :value'%updateKey,
            ExpressionAttributeValues={
                ':value':updateValue
            },
            ReturnValues='UPDATED_NEW'
        )

        body={'Operation':'UPDATE',
              'Message':'SUCCESS',
              'UpdatedAttributes':response
              }
        return buildresponse(200,body)
    except:
        logger.exception("custom error handling")
    
def deleteProduct(productId):
    try:
        response=table.delete_item(
            Key={
                'productId':productId
            },
            ReturnValues='ALL_OLD'
        )
        body={
            'Operation':'DELETE',
            'Message':'SUCCESS',
            'deletedItems':response
        }
        return buildresponse(200,body)
    except:
        logger.exception("Custom error handling")


def lambda_handler(event,context):
    logger.info(event)
    httpMethod=event["httpMethod"]
    path=event["path"]

    if httpMethod==getMethod and path==healthPath:
        # health check
        response=buildresponse(200)

    elif httpMethod==getMethod and path==productPath:
        # get details of a product
        response=getProduct(event['queryStringParameters']['productId'])
    
    elif httpMethod==getMethod and path==productsPath:
        # show all products
        response=getProducts()

    elif httpMethod==postMethod and path==productPath:
        # insert new product in database
        response=saveProduct(json.loads(event["body"]))
    
    elif httpMethod==patchMethod and path==productPath:
        # modify an existing product
        requestBody=json.loads(event['body'])
        response=modifyProduct(requestBody['productId'],requestBody['updateKey'],requestBody['updateValue'])
    
    elif httpMethod==deleteMethod and path==productPath:
        requestBody=json.loads(event['body'])
        response=deleteProduct(requestBody['productId'])
    
    else:
        response=buildresponse(404,"Product not found")
    
    return response



    



    