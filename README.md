# AWS Dynamic DNS

Use AWS DNS for a Dynamic IP DNS updater, complete with subdomains and live
modifiable zonefile.

## Usage

Configure Zonefile templates (see below), then run

```bash
    docker run \
        -e AWS_ACCESS_KEY_ID="YourAccessKey" \
        -e AWS_SECRET_ACCESS_KEY="YourSecretKey" \
        -v "$(pwd):/zonefiles \
        yoloClin/aws-dnydns
```

## Zonefile Templates

Zonefile templates end with the extenison .zonefile-template and
contain the string `{ip}` - this is replaced by the local IP Address.

Templates can be live-added but will refresh the next time the IP rotates or
the container is restarted.

Zonefile templates are otherwise legitimate zonefiles.

My zonefile looks like this:

```
$ORIGIN my_domain.lol.
$TTL 5m
my_domain.lol.  IN  A     {ip}
gitlab          IN  A     {ip}
foobar          IN  A     {ip}
```
