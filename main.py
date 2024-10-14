import subprocess
import telnetlib
import time


def get_mx_record(domain):
    result = subprocess.run(
        ["nslookup", "-type=mx", domain], capture_output=True, text=True
    )
    output = result.stdout.strip().split("\n")
    mx_records = [line.split()[-1] for line in output if "mail exchanger" in line]
    if mx_records:
        return mx_records[0]
    return None


def is_real_email(email, domain):
    mx_record = get_mx_record(domain)
    if not mx_record:
        return False

    try:
        # Connect to the mail server
        telnet = telnetlib.Telnet(mx_record, 25)
        telnet.read_until(b"220")

        # Send HELO command
        telnet.write(b"HELO google.com\r\n")
        telnet.read_until(b"250")

        # Send MAIL FROM command
        telnet.write(b"MAIL FROM:<matiasfuentesdev@gmail.com>\r\n")
        telnet.read_until(b"250")

        # Send RCPT TO command and measure the delay
        start_time = time.time()
        telnet.write(f"RCPT TO:<{email}>\r\n".encode())
        telnet.read_until(b"250").decode()
        end_time = time.time()

        # Calculate the delay
        delay = (end_time - start_time) * 1000  # Convert to milliseconds

        # Close the connection
        telnet.write(b"QUIT\r\n")
        telnet.close()

        # Check if the delay is 300ms or higher
        if delay >= 300:
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False


def generate_email_variations(first_name, last_name, domain):
    variations = [
        f"{first_name}{last_name}@{domain}",
        f"{first_name}{last_name[0]}@{domain}",
        f"{last_name}{first_name}@{domain}",
        f"{last_name[0]}{first_name}@{domain}",
        f"{last_name}{first_name[0]}@{domain}",
        f"{first_name[0]}{last_name}@{domain}",
    ]
    return variations


def check_emails(names, domain):
    valid_emails = []
    for name in names:
        first_name, last_name = name.split()
        email_variations = generate_email_variations(
            first_name.lower(), last_name.lower(), domain
        )
        for email in email_variations:
            if is_real_email(email, domain):
                valid_emails.append(email)
    return valid_emails


def write_emails_to_file(emails, filename):
    with open(filename, "w") as file:
        file.write(", ".join(emails))


# Example usage
domain = "google.com"
names = ["John Doe", "Jane Smith"]
valid_emails = check_emails(names, domain)
write_emails_to_file(valid_emails, "valid_emails.txt")
