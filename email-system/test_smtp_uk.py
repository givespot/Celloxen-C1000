import smtplib
from email.mime.text import MIMEText

configs = [
    {
        "name": "Config 1: UK Server with full email",
        "server": "smtp.ionos.co.uk",
        "port": 587,
        "username": "noreply@celloxen.com",
        "password": "Kuwait1000$$"
    },
    {
        "name": "Config 2: COM Server with full email",
        "server": "smtp.ionos.com",
        "port": 587,
        "username": "noreply@celloxen.com",
        "password": "Kuwait1000$$"
    },
    {
        "name": "Config 3: UK Server, port 465 SSL",
        "server": "smtp.ionos.co.uk",
        "port": 465,
        "username": "noreply@celloxen.com",
        "password": "Kuwait1000$$",
        "use_ssl": True
    }
]

for config in configs:
    print(f"\n{'='*60}")
    print(f"Testing: {config['name']}")
    print(f"Server: {config['server']}:{config['port']}")
    print(f"Username: {config['username']}")
    print(f"{'='*60}")
    
    try:
        if config.get('use_ssl'):
            print("Using SSL...")
            server = smtplib.SMTP_SSL(config['server'], config['port'])
        else:
            print("Using STARTTLS...")
            server = smtplib.SMTP(config['server'], config['port'])
            server.starttls()
        
        print("Attempting login...")
        server.login(config['username'], config['password'])
        print("✅ LOGIN SUCCESSFUL!")
        
        # Try sending test email
        msg = MIMEText("Test from Celloxen", 'plain')
        msg['Subject'] = 'SMTP Test'
        msg['From'] = config['username']
        msg['To'] = 'health@celloxen.com'
        
        server.send_message(msg)
        print("✅ EMAIL SENT!")
        server.quit()
        
        print(f"\n🎉 SUCCESS! Use this configuration:")
        print(f"   Server: {config['server']}")
        print(f"   Port: {config['port']}")
        print(f"   SSL: {config.get('use_ssl', False)}")
        break
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        
print("\n" + "="*60)
