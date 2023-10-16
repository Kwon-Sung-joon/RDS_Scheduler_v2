import boto3
import datetime
import json
import os
import time
import asyncio


'''
Create by sj kwon
2023-09-25
'''

def get_ssm_parameters_role(accountId):
    ssm_client = boto3.client('ssm');
    iam_role_arn=ssm_client.get_parameters(Names=['SCHEDUELR_IAM_ROLE_ARN'])['Parameters'];
    value=iam_role_arn[0]['Value']
    # using json.loads()
    # convert dictionary string to dictionary
    res = json.loads(value)
    print("IAM_ROLE_ARN : "+res[accountId])
    return res[accountId]
def get_ssm_parameters_svc():
    accountList=[]
    ssm_client = boto3.client('ssm');
    svc_name=ssm_client.get_parameters(Names=['SCHEDUELR_SVC'])['Parameters'];
    value=svc_name[0]['Value']
    # using json.loads()
    # convert dictionary string to dictionary
    res = json.loads(value)
    
    for i in res:
        if res[i] == "ON" :
            accountList.append(i) 
        else :
            continue
    
    return accountList
def getToken(accountId):
	SESSION_KEY={
    "aws_access_key_id":"",
        "aws_secret_access_key":"",
        "aws_session_token":""
	}

	sts_client=boto3.client('sts');
        #get session to target aws account.
	response = sts_client.assume_role(
    	RoleArn=get_ssm_parameters_role(accountId),
    	RoleSessionName="scheduler-session"
        )
        #set aws access config
	SESSION_KEY["aws_access_key_id"]=response['Credentials']['AccessKeyId']
	SESSION_KEY["aws_secret_access_key"]=response['Credentials']['SecretAccessKey']
	SESSION_KEY["aws_session_token"]=response['Credentials']['SessionToken']
    
	return SESSION_KEY;    

class Rds:
	def __init__(self,token):
		self.rds_client=boto3.client('rds',aws_access_key_id=token["aws_access_key_id"],
        aws_secret_access_key=token["aws_secret_access_key"],
        aws_session_token=token["aws_session_token"]
        );

	def get_rds_lists(self):
		sch_db_list={}
		response=self.rds_client.describe_db_instances()
		rds_instances=response.get("DBInstances")
		for i in response['DBInstances']:
			tags = self.rds_client.list_tags_for_resource(ResourceName=i['DBInstanceArn'])['TagList'];
			for tag in tags:
				if tag['Key'] == "SCHEDULER" and tag['Value'] == "ON":
					sch_db_list[i['DBInstanceIdentifier']]=""
				elif tag['Key'] == "SCH_TIME":
					sch_db_list[i['DBInstanceIdentifier']] = tag['Value']
				else:
					continue;
		print("##Schedule DB Lists###")			
		print(sch_db_list)		
		return sch_db_list

	def stop_rds(self,rds_identifier):
		response = self.rds_client.stop_db_instance(
	    		DBInstanceIdentifier=rds_identifier)
		print(response)
		print('###{0} STOPT###'.format(rds_identifier))
		
	def start_rds(self,rds_identifier):
		response = self.rds_client.start_db_instance(
    			DBInstanceIdentifier=rds_identifier)
		print(response)
		print('###{0} START###'.format(rds_identifier))


def lambda_handler(event, context):
	# TODO implement
	# 1. Scanning ALL RDS ...
	# 2. Get RDS Tags with SCHEDUELR
	# 3. if SCHEDUELR ON -> put rule stop or start rule
	sch_instnaces={}
	#accountList = ["AccountA","AccountB",...,]
	accountList=get_ssm_parameters_svc();
	for i in accountList:
		token = getToken(i);
		rds=Rds(token);
		#check schedule rds
		#sch_instnaces[i]  = {'stg-apigw': 'WORKING'}
		sch_instnaces[i]=rds.get_rds_lists()
		for instance in sch_instnaces[i]:
			if sch_instnaces[i][instance] == event['SCH_TIME'] and event['ACTION'] == "STOP":
				rds.stop_rds(instance)
			elif sch_instnaces[i][instance] == event['SCH_TIME'] and event['ACTION'] == "START" :
				rds.start_rds(instance);
