"""Handles sending email, platform dependent."""

import smtplib
import string

class SSMTP(object):
    """Reads from /etc/ssmtp/ssmtp.conf."""
    #| TODO: The status.py script fails if the password for email notifications
    #|       is wrong.
    def __init__(self):
        conf = open('/etc/ssmtp/ssmtp.conf', 'r+')
        for line in conf.read().split('\n'):
            fields = line.split('=')
            if fields[0] == "root":
                self.root = fields[1]
            elif fields[0] == "mailhub":
                mailhub = fields[1].split(':')
                self.server = mailhub[0]
                self.port = int(mailhub[1])
            elif fields[0] == "rewriteDomain":
                self.domain = fields[1]
            elif fields[0] == "AuthUser":
                self.user = fields[1]
            elif fields[0] == "AuthPass":
                self.password = fields[1]
            #elif 


class Email(object):
    def __init__(self):
        ssmtpConfig = SSMTP()
        self.user = ssmtpConfig.user
        self.password = ssmtpConfig.password
        self.host = ssmtpConfig.server
        self.port = ssmtpConfig.port
        self.server = smtplib.SMTP()

    def send(self, subject, to, message):
        body = string.join((
                    "From: %s" % self.user,
                    "To: %s" % to,
                    "Subject: %s" % subject,
                    "",
                    message
                    ), "\r\n")
        self.server.connect(self.host, self.port)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.user, self.password)
        self.server.sendmail(self.user, [to], body)
        self.server.quit()
