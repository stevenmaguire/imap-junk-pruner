## IMAP Junk Pruner

Let's help keep our inboxes free from junk.

### Up and running

Create a senders keyword list in `accounts` directory. Name the file `{email address}.csv`. Senders can be keywords, email addresses, domains - anything that you can use to search your inbox to find emails when prefixed with FROM.

```
# accounts/junk.hater@example.com.csv
newsletter@example.com
example.com
Politician Name
```

Run the tool.

```
$ python3 main.py {host} {email address} {password}
```

Available options:

| Option      | Parameters | Default | Example |
| ----------- | ----------- | ----------- | ----------- |
| Target Folder | `-tf` or `--target_folder`| `INBOX` | `-tf=INBOX/My\ Folder` |
| Buffer Folder | `-bf` or `--buffer_folder`| `None` | `-bf=INBOX/Bulk\ Delete` |

When executed, the tool will loop over the list of sender keywords, locate all matching messages, then delete them from the `target_folder`.

If a `buffer_folder` is specified, the messages will be copied to the `buffer_folder` before deleting from the `target_folder`. This is useful if you want to quarantine and review the candidate deletions.

### Tip

Unsubscribing from senders while you accumulate your sender keywords will help reduce the amount of future emails - hopefully.
