"""
I didn't read the task properly until the end and thought we'd be comparing several thousands
of files....... so this is largely unnecessary, but committing for now.
"""
import os

try:
    os.mkdir("emails")
except FileExistsError:
    print("email directory exists, continuing.")

with open("fradulent_emails.txt", "r", errors="ignore") as f:
    content = f.read()

emails = content.split(
    "From r"
)  # By just looking at the textfile this seems reasonable

for index, email in enumerate(emails[1:]):
    with open(f"emails/email-{index}.txt", "w") as f:
        try:
            # We removed the header which ends with an empty line before the email begins
            email = email.split("\n\n", 1)[1]
            f.write(email)
        except IndexError:
            pass
