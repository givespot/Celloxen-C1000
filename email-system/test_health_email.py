import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

configs = [
    {
        "name": "health@celloxen.com - UK Server STARTTLS",
        "server": "smtp.ionos.co.uk",
        "port": 587,
        "username": "health@celloxen.com",
        "password": "Kuwait1000$$"
    },
    {
        "name": "health@celloxen.com - COM Server STARTTLS",
        "server": "smtp.ionos.com",
        "port": 587,
        "username": "health@celloxen.com",
        "password": "Kuwait1000$$"
    },
    {
        "name": "health@celloxen.com - UK Server SSL",
        "server": "smtp.ionos.co.uk",
        "port": 465,
        "username": "health@celloxen.com",
        "password": "Kuwait1000$$",
        "use_ssl": True
    }
]

for config in configs:
    print(f"\n{'='*60}")
    print(f"Testing: {config['name']}")
    print(f"Server: {config['server']}:{config['port']}")
    print(f"{'='*60}")
    
    try:
        if config.get('use_ssl'):
            print("Using SSL...")
            server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=10)
        else:
            print("Connecting...")
            server = smtplib.SMTP(config['server'], config['port'], timeout=10)
            print("Starting TLS...")
            server.starttls()
        
        print("Attempting login...")
        server.login(config['username'], config['password'])
        print("✅ LOGIN SUCCESSFUL!")
        
        # Try sending test email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Celloxen SMTP Test - SUCCESS!'
        msg['From'] = 'Celloxen Health <health@celloxen.com>'
        msg['To'] = 'health@celloxen.com'
        
        html = """
        <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #28a745;">✅ SMTP Configuration Working!</h2>
            <p>This email confirms that the SMTP configuration is correct.</p>
            <hr>
            <p><strong>Configuration:</strong></p>
            <ul>
                <li>Server: """ + config['server'] + """</li>
                <li>Port: """ + str(config['port']) + """</li>
                <li>Account: health@celloxen.com</li>
            </ul>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        print("Sending test email...")
        server.send_message(msg)
        print("✅ EMAIL SENT SUCCESSFULLY!")
        server.quit()
        
        print(f"\n🎉🎉🎉 SUCCESS! Working configuration found:")
        print(f"   Server: {config['server']}")
        print(f"   Port: {config['port']}")
        print(f"   Username: health@celloxen.com")
        print(f"   SSL: {config.get('use_ssl', False)}")
        print(f"\n📧 Check health@celloxen.com inbox!")
        
        # Save working config
        with open('/var/www/celloxen-portal/email-system/working_config.txt', 'w') as f:
            f.write(f"SMTP_SERVER={config['server']}\n")
            f.write(f"SMTP_PORT={config['port']}\n")
            f.write(f"SMTP_SSL={config.get('use_ssl', False)}\n")
            f.write(f"SMTP_USERNAME=health@celloxen.com\n")
            f.write(f"SMTP_PASSWORD=Kuwait1000$$\n")
        print("\n✅ Configuration saved to working_config.txt")
        
        break
        
    except Exception as e:
        print(f"❌ FAILED: {e}")

print("\n" + "="*60)
