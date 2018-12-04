# describe_certs

### Lambda function using Boto3 and Python 3.6

Determines if certificates within AWS Certificate Manager are up to date. Alerts Users via email if certificate expires within 90 days.

*** Uses SES instead of SNS for formatting purposes. This can obviously be simplified with SNS. However, when using client certs for subdomains, I have found a better HTML formatted email can get more views.
