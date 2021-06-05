import smtplib
###
def randomstring(request):
    import secrets
    import string

    N = 7
    res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(N))

    return str(res)

###
def mail(receiver,body):
    import smtplib
    try:
        s = smtplib.SMTP('mail.fortunecloudindia.com', 587)
        s.starttls()
        s.login("aniket.pawar@cravitaindia.com", "Aniket@123")
        s.sendmail("aniket.pawar@cravitaindia.com", receiver, body)
        s.quit()
        return "success"
    except:
        return "failed"

###
def mailletter(receiver,body):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    try:
        s = smtplib.SMTP('mail.fortunecloudindia.com', 587)
        s.starttls()
        s.login("aniket.pawar@cravitaindia.com", "Aniket@123")


        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = "aniket.pawar@cravitaindia.com"
        message['To'] = receiver
        message['Subject'] = 'Fortune Cloud LMS'

        message.attach(MIMEText(body, 'plain'))

        pdfname = 'Offer Letter.pdf'

        # open the file in bynary
        binary_pdf = open(pdfname, 'rb')

        payload = MIMEBase('application', 'octate-stream', Name=pdfname)
        payload = MIMEBase('application', 'pdf', Name=pdfname)
        payload.set_payload((binary_pdf).read())

        # enconding the binary into base64
        encoders.encode_base64(payload)

        # add header with pdf name
        payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
        message.attach(payload)

        text = message.as_string()
        s.sendmail("aniket.pawar@cravitaindia.com", receiver, text)
        s.quit()

        print("success")
        return "success"
    except:
        print("failed")
        return "failed"



