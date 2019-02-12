import boto3
import datetime
from botocore.exceptions import ClientError

seconds = 86400
currentDT = int((datetime.datetime.now().timestamp())/seconds)
SENDER = "Do Not Reply <donotreply@youremail.com>"
RECIPIENT = "list@youremail.com"
AWS_REGION = "us-east-1"
CHARSET = "UTF-8"
BODY_TEXT = ("Domain is expiring. "
             "Please renew ASAP. "
             )
client = boto3.client('acm')
client_ses = boto3.client('ses', region_name=AWS_REGION)

def cert_details(cert_arn):
    response_cert_details = client.describe_certificate(
        CertificateArn=cert_arn
    )
    return response_cert_details

def email_send(cert_name, diff):
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client_ses.send_email(
            Destination={
                'ToAddresses': [RECIPIENT,],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': '{} is expiring in {} days. Please renew ASAP.'.format(cert_name, diff),
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': 'Domain certificate is expiring in {} days - {} - renew soon'.format(diff, cert_name),
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def lambda_handler(event, context):
    print('Loading function...')
    print('Getting Certificate list...')
    response_list_certs = client.list_certificates()
    cert_summary = response_list_certs['CertificateSummaryList']

    print('Checking Certificate expiration...')

    for cert in cert_summary:
        print('Certificate Name: ', '\n', cert['DomainName'])
        cert_arn = cert['CertificateArn']
        details = cert_details(cert_arn)
        cert_name = cert['DomainName']
        expiration = int(details['Certificate']['NotAfter'].timestamp()/seconds)
        diff = expiration - currentDT
        if diff < 90:
            print('** This certificate expires in:', diff, 'days. Please renew ASAP.')
            print('Sending email...')
            diff = str(diff)
            email_send(cert_name, diff)
        else:
            print(diff), '\n'
