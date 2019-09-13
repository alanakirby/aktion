# AKTION

AKTION is a script that gathers the latest AWS Services and Actions, compares it to last weeks services and actions and sends the difference (the new ones) to your chosen email address. The aim of this is to help keep track of the new releases from AWS for policy management.

## Deployment:

Included is a CodePipeline defined in CloudFormation. This bundles up the Lambda and it's dependencies via CodeBuild, and uploads the resulting zip to S3 where it is then referenced in a CloudFormation deployment step for the Lambda itself. The pipeline updates itself based on the pipeline.yml included in the repo.

### First time setup:

1. Add you sending and receiving email addresses to AWS SES in your chosen region. Verify them by confirming the subscription email it sends.
2. Make a Secret in Secrets Manager called 'Github' and place two values in it:
    - PersonalAccessToken: A Personal Access Token from Github
    - WebhookSecret: A random string for adding access control to the CodePipeline webhook
3. Deploy the `pipeline.yml` via CloudFormation
4. For automatic pipeline execution on push events, configure the Webhook URL that is exported from the resulting stack in your Github repo's Webhook settings.
