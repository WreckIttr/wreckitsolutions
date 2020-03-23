import json
import boto3
from botocore.client import Config
import StringIO
import zipfile

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:050915168657:deployPortfolioTopic')
    
    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        
        portfolio_bucket = s3.Bucket('portfolio.wreckitsolutions.com')
        build_bucket = s3.Bucket('portfoliobuild.wreckitsolutions.com')
        
        portfoliobuild_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfoliobuild_zip)
        
        with zipfile.ZipFile(portfoliobuild_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        
        print "Job "
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfully")    
    except:
        topic.publish(Subject="Portfolio Deployment Failed", Message="The Portfolio was not deployed successfully.")
        raise
    
    return 'Hello Wreckit, your portfolio lambda function worked!'