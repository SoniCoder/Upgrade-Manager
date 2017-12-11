"""
Author: Hritik Soni

Description:

This module has implementation of the Mailer functionality.


"""
import globs
import os
import tempfile
import zipfile

# Module for helping with mailing
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send():
    """
    This function actually send the mail using information available in global vars
    """
    attachments = globs.ATTACHMENTS
    pswd = globs.PASSWORD
    file_data_set =[]
    for f in attachments:
        if globs.COMPRESS:
            zf = tempfile.TemporaryFile(prefix=os.path.basename(f).split('.')[0], suffix='.zip')
            zip = zipfile.ZipFile(zf, 'w', zipfile.ZIP_DEFLATED)
            zip.write(f, os.path.basename(f))
            zip.close()
            zf.seek(0)
            file_data_set.append(zf.read())
        else:
            file_data_set.append(open(f, 'rb').read())
    msg = MIMEMultipart()
    msg['Subject'] = globs.SUBJECT
    msg['From'] = globs.FROM
    msg['To'] = globs.TO
    text = MIMEText(globs.TEXT)
    msg.attach(text)
    for f_i in range(len(file_data_set)):
        name = os.path.basename(attachments[f_i])
        if globs.COMPRESS:
            name = name.split('.')[0] + ".zip"
        fl = MIMEApplication(file_data_set[f_i], name=name)
        msg.attach(fl)

    s = smtplib.SMTP(globs.SERVER, globs.PORT)
    if globs.USE_TLS:
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(globs.FROM, pswd)
    s.sendmail(globs.FROM, globs.TO, msg.as_string())
    s.quit()