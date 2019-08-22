# AKTION

AKTION is a script that gathers the latest AWS Services and Actions, compares it to last weeks services and actions and sends the difference (the new ones) to your chosen email address. The aim of this is to help keep track of the new releases from AWS for policy management.

## Deployment:

Included is a CodePipeline defined in CloudFormation. This bundles up the Lambda and it's dependancies via CodeBuild, and uploads the resulting zip to S3 where it is then referenced in a CloudFormation deployment step for the Lambda itself. The pipeline updates itself based on the pipeline.yml included in the repo.

### First time setup:

1. Add you sending and receiving email addresses to AWS SES in your chosen region. Verify them by confirming the subscription email it sends.
2. Edit lines 67 and 68 of the `lambda.yml` file withh the arn's of the two verified emails.
3. Create an S3 bucket. On line 21 and 55 of `aktion.py` add your S3 bucket name.
4. On lines 97, 98, 99, 153, 154 and 155 add your email addresses and region where you will verify them in AWS SES.
5. Make a Secret in Secrets Manager called 'Github' and place two values in it:
    - PersonalAccessToken: A Personal Access Token from Github
    - WebhookSecret: A random string for adding access control to the CodePipeline webhook
6. Deploy the `pipeline.yml` via CloudFormation
7. For automatic pipeline execution on push events, configure the Webhook URL that is exported from the resulting stack in your Github repo's Webhook settings.
