# RDS_Scheduler_v2

# Flow

1. Amazon EventBridge Scheduler invoke's lambda with payload
2. In Lambda, First check Schduelr ON account with ssm parameter store
3. get TOKEN with assume role
4. check rds instance's tags SCHEDULER, SCH_TIME
5. if all conditions is true, then execute scheduler



# Step1. 
- set RDS instances tags
```
          Key : SCHEDULER, Value : ON || OFF -> scheduler tag
          Key : SCH_TIME, Value: WORKING -> check schedluer time tag
```
# Step2.
## SSM Parameter store

-  SCHEDULER_SVC
```value
{
        "ACCOUNT ID" : "OFF",
        "ACCOUNT2 ID"  : "ON"
}
```  
- SCHEDUELR_IAM_ROLE_ARN

```value
{
        "ACCOUNT ID" : "SCHEDULER_ROLE", <- permission is rds stop/start policy
        "ACCOUNT ID" : "SCHEDULER_ROLE"
 
}
```
- SCHEDULER_ROLE's policy
```
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "rds:StopDBInstance",
                "rds:StartDBInstance"
            ],
            "Resource": "<arn:aws:rds:ap-northeast-2:<account-id>:db:<db-identifier>"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "rds:Desc*",
                "rds:List*"
            ],
            "Resource": "*"
        }
    ]
}
```

# Step3.
## Create EventBridge Scheduler
- WORKING_START
```
Cron : 0 8 * * ? *
```
```
#payload
{ "SCH_TIME":"WORKING", "ACTION":"START" }
```
- WORKING_STOP
```
Cron : 0 18 * * ? *
```
```
#payload
{ "SCH_TIME":"WORKING", "ACTION":"STOP" }
```
