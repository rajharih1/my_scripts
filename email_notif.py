import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Replace sender@example.com with your "From" address.
# This address must be verified.
SENDER = 'app@company.com'
SENDERNAME = 'DevOps Platform Update'

# Replace recipient@example.com with a "To" address. If your account
# is still in the sandbox, this address must be verified.
RECIPIENT = 'f1.l1@company.com','f2.l2@company.com'

# Replace smtp_username with your Amazon SES SMTP user name.
USERNAME_SMTP = "dsdsdasswew"

# Replace smtp_password with your Amazon SES SMTP password.
PASSWORD_SMTP = "wpqoepwodps0dckdlckdlc"

# (Optional) the name of a configuration set to use for this message.
# If you comment out this line, you also need to remove or comment out
# the "X-SES-CONFIGURATION-SET:" header below.
CONFIGURATION_SET = "ConfigSet"

# If you're using Amazon SES in an AWS Region other than US West (Oregon),
# replace email-smtp.us-west-2.amazonaws.com with the Amazon SES SMTP
# endpoint in the appropriate region.
HOST = "email-smtp.us-west-2.amazonaws.com"
PORT = 587

# The subject line of the email.
SUBJECT = '[NOTIFICATION] Windows & Linux Server Maintenance | 16th and 17th January 2018 3:30 am to 8:30 am UTC'

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("""""")

# The HTML body of the email.
BODY_HTML = """<html>
<p><span style="font-size: 12pt; font-family: calibri, sans-serif;">Hi All,</span></p>
<p><span style="font-size: 12pt; font-family: calibri, sans-serif;">&nbsp;We would like to provide an update on the maintenance notifications you have received this week from DevOps platform.&nbsp;</span></p>
<p style="margin-right: 6.0pt; line-height: 115%; background: white;"><span style="font-size: 12pt; font-family: calibri, sans-serif;"><strong><u><span style="color: #1f497d;">Schedule:</span></u></strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </span></p>
<p style="margin-right: 6.0pt; line-height: 115%; background: white;"><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">15<sup>th</sup> January 2018(Monday)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3:30 (UTC) - 8:30 (UTC)</span></p>
<p style="margin-right: 6.0pt; line-height: 115%; background: white;"><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">16<sup>th</sup> January 2018 (Tuesday)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3:30 (UTC) - 8:30 (UTC)</span></p>
<p style="margin-right: 6.0pt; line-height: 115%; background: white;"><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">17<sup>th</sup> January 2018 (Wednesday)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3:30 (UTC) - 8:30 (UTC)</span></p>
<p style="margin-right: 6.0pt; line-height: 13.5pt;"><span style="font-size: 12pt; font-family: calibri, sans-serif;"><strong><u><span style="color: #1f497d;">Event:</span></u></strong></span></p>
<p style="margin-right: 6.0pt; line-height: 13.5pt;"><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Maintenance activity done on the DevOps Platform : &nbsp;</span></p>
<ul>
<li><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Applied latest security patches on Linux machines.</span></li>
<li><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Applied latest security patches on Windows machines.</span></li>
<li><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Upgraded McAfee ePO to latest version</span></li>
<li><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Pushed McAfee agents, Antivirus and Malware protection on all Windows machines</span></li>
<li><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Fix for Meltdown and Spectre Vulnerability</span></li>
<li><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Implemented Windows Server Update Services for Windows Automated patch management</span></li>
</ul>
<p><span style="color: #1f497d; font-size: 12pt; font-family: calibri, sans-serif;">Please let us know if you have any questions.&nbsp;</span></p>
<p style="line-height: 115%;"><span style="font-size: 12pt; font-family: calibri, sans-serif;">Thanks,</span></p>
<p style="line-height: 115%;"><span style="font-size: 12pt; font-family: calibri, sans-serif;"><strong>DevOps Platform Team</strong></span></p>
</html>"""

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = SUBJECT
msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
msg['To'] = ','.join(RECIPIENT)
# Comment or delete the next line if you are not using a configuration set
#msg.add_header('X-SES-CONFIGURATION-SET', CONFIGURATION_SET)

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(BODY_TEXT, 'plain')
part2 = MIMEText(BODY_HTML, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Try to send the message.
try:
    server = smtplib.SMTP(HOST, PORT)
    server.ehlo()
    server.starttls()
    # stmplib docs recommend calling ehlo() before & after starttls()
    server.ehlo()
    server.login(USERNAME_SMTP, PASSWORD_SMTP)
    server.sendmail(SENDER, RECIPIENT, msg.as_string())
    server.close()
# Display an error message if something goes wrong.
except Exception as e:
    print("Error: ", e)
else:
    print("Email sent!")