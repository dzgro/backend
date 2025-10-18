The deploy poetry project uses a Builder.py in Template Builder dir to dynamically build AWS SAM Template for the region and using env in .env file.
It also creates certificates and cognito login templates (which AWS SAM is incapable of).
There are 4 stages. We only create S3 Buckets for local while all other resources for other environements.
The Starter Mappping file contains resources and their integrations.

Problem with this deployment is that, we create 4 buckets for each bucket name, 3 sqs queues, 3 apis, 3 functions, 3 apis whihc are getting tough to manage.
We did not have knowledge of lambda aliases and api stage variables before.
Now that we do, we want to simplify our deployment and number of resources being created in AWS.

1. We will still create 4 buckets per env.
2. we will create 4 queues per env. (earlier we were not creating for local). only diff is that local queues will not trigger lambda.
3. we will create 1 lambda and define aliases for env other than local and auto publish to dev.
4. we will create 1 api for /api/{proxy+} integrations that points to lambda as per stage variable.
5. we will create 1 api for /webhook/{proxy+} integrations that points to lambda as per stage variable.
6. in place of restapi , we will now use httpapi.
7. we will still create 3 cognitos for each env except for local.

Now, this project will create a common sam template for all environments for a region that is specified and deploy it.
The deploy project should be used as reference while this new project can optimise it in its own way.
There are helper function in Builder.py for name generations as per env for lambda , queues, buckets etc. some of them will be useless (like lambda, which is common now).
Dont Change name generations unless very critical.
