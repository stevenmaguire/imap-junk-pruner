import argparse, imaplib, email, os, re

parser = argparse.ArgumentParser()

parser.add_argument("host")
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("-tf", "--target_folder", default='INBOX')
parser.add_argument("-bf", "--buffer_folder")

args = parser.parse_args()

target_folder = args.target_folder
if target_folder and " " in target_folder:
    target_folder = '"%s"' % target_folder

buffer_folder = args.buffer_folder
if buffer_folder and " " in buffer_folder:
    buffer_folder = '"%s"' % buffer_folder

mailbox = imaplib.IMAP4(args.host)
mailbox.login(args.username, args.password)

retcode, folders = mailbox.list()
normalized_folders = list(map(lambda b: b.decode().split(' "/" ')[1], folders))

if normalized_folders:
    print('Folders:')
    for folder in normalized_folders:
        print('\t' + folder)

if target_folder not in normalized_folders:
    print('Target folder %s does not exist; quitting' % target_folder)
    exit()

if buffer_folder and buffer_folder not in normalized_folders:
    print('Buffer folder %s does not exist; creating' % buffer_folder)
    mailbox.create(buffer_folder)

senders_file_path = 'accounts/%s.csv' % args.username
if os.path.exists(senders_file_path):
    file = open(senders_file_path, mode = 'r', encoding = 'utf-8-sig')
    senders = file.read().splitlines()
else:
    print('Senders list %s not found; quitting' % senders_file_path)
    exit()
if not senders:
    print('Senders list %s is empty; quitting' % senders_file_path)
    exit()

pattern_uid = re.compile(r'\d+ \(UID (?P<uid>\d+)\)')

def delete_message_by_uid(msg_uid):
    retcode, data = mailbox.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
    mailbox.expunge()
    print('\t' + '...deleted from target folder %s' % target_folder)

def handle_messages(messages, keyword):
    email_ids  = messages[0].split()

    for email_id in email_ids:

        retcode, uid = mailbox.fetch(email_id, "(UID)")
        msg_uid = parse_uid(uid[0].decode('utf-8'))

        retcode, message = mailbox.fetch(email_id, "(RFC822)")
        original = email.message_from_bytes(message[0][1])
        print(keyword, msg_uid, original['subject'], original['from'], original['date'])

        if buffer_folder:
            result = mailbox.uid('COPY', msg_uid, '%s' % buffer_folder)
            if result[0] == 'OK':
                print('\t' + '...copied to buffer folder %s' % buffer_folder)
                delete_message_by_uid(msg_uid)
            else:
                print('failed', result)
                break
        else:
            delete_message_by_uid(msg_uid)

def parse_uid(data):
    match = pattern_uid.match(data)
    return match.group('uid')

mailbox.select(target_folder)
for sender in senders:
    keyword = '(FROM "%s")' % sender
    (retcode, messages) = mailbox.sort('REVERSE DATE', 'UTF-8', keyword)
    if retcode == 'OK':
        handle_messages(messages, keyword)

mailbox.close()
exit()
