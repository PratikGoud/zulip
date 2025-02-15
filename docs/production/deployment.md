# Deployment options

The default Zulip installation instructions will install a complete
Zulip server, with all of the services it needs, on a single machine.

For production deployment, however, it's common to want to do
something more complicated. This page documents the options for doing so.

## Installing Zulip from Git

To install a development version of Zulip from Git, just clone the Git
repository from GitHub:

```bash
# First, install Git if you don't have it installed already
sudo apt install git
git clone https://github.com/zulip/zulip.git zulip-server-git
```

and then
[continue the normal installation instructions](install.md#step-2-install-zulip).
You can also [upgrade Zulip from Git](upgrade.md#upgrading-from-a-git-repository).

The most common use case for this is upgrading to `main` to get a
feature that hasn't made it into an official release yet (often
support for a new base OS release). See [upgrading to
main][upgrade-to-main] for notes on how `main` works and the
support story for it, and [upgrading to future
releases][upgrade-to-future-release] for notes on upgrading Zulip
afterwards.

In particular, we are always very glad to investigate problems with
installing Zulip from `main`; they are rare and help us ensure that
our next major release has a reliable install experience.

[upgrade-to-main]: modify.md#upgrading-to-main
[upgrade-to-future-release]: modify.md#upgrading-to-future-releases

## Zulip in Docker

Zulip has an officially supported, experimental
[docker image](https://github.com/zulip/docker-zulip). Please note
that Zulip's [normal installer](install.md) has been
extremely reliable for years, whereas the Docker image is new and has
rough edges, so we recommend the normal installer unless you have a
specific reason to prefer Docker.

## Zulip installer details

The [Zulip installer](install.md) does the following:

- Creates the `zulip` user, which the various Zulip servers will run as.
- Creates `/home/zulip/deployments/`, which the Zulip code for this
  deployment (and future deployments when you upgrade) goes into. At the
  very end of the install process, the script moves the Zulip code tree
  it's running from (which you unpacked from a tarball above) to a
  directory there, and makes `/home/zulip/deployments/current` as a
  symbolic link to it.
- Installs Zulip's various dependencies.
- Configures the various third-party services Zulip uses, including
  PostgreSQL, RabbitMQ, Memcached and Redis.
- Initializes Zulip's database.

### Advanced installer options

The Zulip installer supports the following advanced installer options
as well as those mentioned in the
[install](install.md#installer-options) documentation:

- `--postgresql-version`: Sets the version of PostgreSQL that will be
  installed. We currently support PostgreSQL 12, 13, 14, 15, and 16, with 16
  being the default.

- `--postgresql-database-name=exampledbname`: With this option, you
  can customize the default database name. If you do not set this. The
  default database name will be `zulip`. This setting can only be set
  on the first install.

- `--postgresql-database-user=exampledbuser`: With this option, you
  can customize the default database user. If you do not set this. The
  default database user will be `zulip`. This setting can only be set
  on the first install.

- `--postgresql-missing-dictionaries`: Set
  `postgresql.missing_dictionaries` ([docs][missing-dicts]) in the
  Zulip settings, which omits some configuration needed for full-text
  indexing. This should be used with [cloud managed databases like
  RDS](#using-zulip-with-amazon-rds-as-the-database). This option
  conflicts with `--no-overwrite-settings`.

- `--no-init-db`: This option instructs the installer to not do any
  database initialization. This should be used when you already have a
  Zulip database.

- `--no-overwrite-settings`: This option preserves existing
  `/etc/zulip` configuration files.

[missing-dicts]: system-configuration.md#missing_dictionaries

## Installing on an existing server

Zulip's installation process assumes it is the only application
running on the server; though installing alongside other applications
is not recommended, we do have [some notes on the
process](install-existing-server.md).

## Deployment hooks

Zulip's upgrades have a hook system which allows for arbitrary
user-configured actions to run before and after an upgrade; see the
[upgrading documentation](upgrade.md#deployment-hooks) for details on
how to write your own.

### Zulip message deploy hook

Zulip can use its deploy hooks to send a message immediately before and after
conducting an upgrade. To configure this:

1. Add `, zulip::hooks::zulip_notify` to the `puppet_classes` line in
   `/etc/zulip/zulip.conf`
1. Add a `[zulip_notify]` section to `/etc/zulip/zulip.conf`:
   ```ini
   [zulip_notify]
   bot_email = your-bot@zulip.example.com
   server = zulip.example.com
   stream = deployments
   ```
1. Add the [api key](https://zulip.com/api/api-keys#get-a-bots-api-key) for the
   bot user in `/etc/zulip/zulip-secrets.conf` as `zulip_release_api_key`:
   ```ini
   # Replace with your own bot's token, found in the Zulip UI
   zulip_release_api_key = abcd1234E6DK0F7pNSqaMSuzd8C5i7Eu
   ```
1. As root, run `/home/zulip/deployments/current/scripts/zulip-puppet-apply`.

### Sentry deploy hook

Zulip can use its deploy hooks to create [Sentry
releases][sentry-release], which can help associate Sentry [error
logging][sentry-error] with specific releases. If you are deploying
Zulip from Git, it can be aware of which Zulip commits are associated
with the release, and help identify which commits might be relevant to
an error.

To do so:

1. Enable [Sentry error logging][sentry-error].
2. Add a new [internal Sentry integration][sentry-internal] named
   "Release annotator".
3. Grant the internal integration the [permissions][sentry-perms] of
   "Admin" on "Release".
4. Add `, zulip::hooks::sentry` to the `puppet_classes` line in `/etc/zulip/zulip.conf`
5. Add a `[sentry]` section to `/etc/zulip/zulip.conf`:
   ```ini
   [sentry]
   organization = your-organization-name
   project = your-project-name
   ```
6. Add the [authentication token][sentry-tokens] for your internal Sentry integration
   to your `/etc/zulip/zulip-secrets.conf`:
   ```ini
   # Replace with your own token, found in Sentry
   sentry_release_auth_token = 6c12f890c1c864666e64ee9c959c4552b3de473a076815e7669f53793fa16afc
   ```
7. As root, run `/home/zulip/deployments/current/scripts/zulip-puppet-apply`.

If you are deploying Zulip from Git, you will also need to:

1. In your Zulip project, add the [GitHub integration][sentry-github].
2. Configure the `zulip/zulip` GitHub project for your Sentry project.
   You should do this even if you are deploying a private fork of
   Zulip.
3. Additionally grant the internal integration "Read & Write" on
   "Organization"; this is necessary to associate the commits with the
   release.

[sentry-release]: https://docs.sentry.io/product/releases/
[sentry-error]: ../subsystems/logging.md#sentry-error-logging
[sentry-github]: https://docs.sentry.io/product/integrations/source-code-mgmt/github/
[sentry-internal]: https://docs.sentry.io/product/integrations/integration-platform/internal-integration/
[sentry-perms]: https://docs.sentry.io/product/integrations/integration-platform/#permissions
[sentry-tokens]: https://docs.sentry.io/product/integrations/integration-platform/internal-integration#auth-tokens

## Running Zulip's service dependencies on different machines

Zulip has full support for each top-level service living on its own
machine.

You can configure remote servers for PostgreSQL, RabbitMQ, Redis,
in `/etc/zulip/settings.py`; just search for the service name in that
file and you'll find inline documentation in comments for how to
configure it.

Since some of these services require some configuration on the node
itself (e.g. installing our PostgreSQL extensions), we have designed
the Puppet configuration that Zulip uses for installing and upgrading
configuration to be completely modular.

For example, to install a Zulip Redis server on a machine, you can run
the following after unpacking a Zulip production release tarball:

```bash
env PUPPET_CLASSES=zulip::profile::redis ./scripts/setup/install
```

All puppet modules under `zulip::profile` are allowed to be configured
stand-alone on a host. You can see most likely manifests you might
want to choose in the list of includes in [the main manifest for the
default all-in-one Zulip server][standalone.pp], though it's also
possible to subclass some of the lower-level manifests defined in that
directory if you want to customize. A good example of doing this is
in the [kandra Puppet configuration][zulipchat-puppet] that we use
as part of managing chat.zulip.org and zulip.com.

### Using Zulip with Amazon RDS as the database

You can use DBaaS services like Amazon RDS for the Zulip database.
The experience is slightly degraded, in that most DBaaS provides don't
include useful dictionary files in their installations and don't
provide a way to provide them yourself, resulting in a degraded
[full-text search](../subsystems/full-text-search.md) experience
around issues dictionary files are relevant (e.g. stemming).

You also need to pass some extra options to the Zulip installer in
order to avoid it throwing an error when Zulip attempts to configure
the database's dictionary files for full-text search; the details are
below.

#### Step 1: Set up Zulip

Follow the [standard instructions](install.md), with one
change. When running the installer, pass the `--no-init-db`
flag, e.g.:

```bash
sudo -s  # If not already root
./zulip-server-*/scripts/setup/install --certbot \
    --email=YOUR_EMAIL --hostname=YOUR_HOSTNAME \
    --no-init-db --postgresql-missing-dictionaries
```

The script also installs and starts PostgreSQL on the server by
default. We don't need it, so run the following command to
stop and disable the local PostgreSQL server.

```bash
sudo service postgresql stop
sudo update-rc.d postgresql disable
```

This complication will be removed in a future version.

#### Step 2: Create the PostgreSQL database

Access an administrative `psql` shell on your PostgreSQL database, and
run the commands in `scripts/setup/create-db.sql` to:

- Create a database called `zulip`.
- Create a user called `zulip`.
- Now log in with the `zulip` user to create a schema called
  `zulip` in the `zulip` database. You might have to grant `create`
  privileges first for the `zulip` user to do this.

Depending on how authentication works for your PostgreSQL installation,
you may also need to set a password for the Zulip user, generate a
client certificate, or similar; consult the documentation for your
database provider for the available options.

#### Step 3: Configure Zulip to use the PostgreSQL database

In `/etc/zulip/settings.py` on your Zulip server, configure the
following settings with details for how to connect to your PostgreSQL
server. Your database provider should provide these details.

- `REMOTE_POSTGRES_HOST`: Name or IP address of the PostgreSQL server.
- `REMOTE_POSTGRES_PORT`: Port on the PostgreSQL server.
- `REMOTE_POSTGRES_SSLMODE`: SSL Mode used to connect to the server.

If you're using password authentication, you should specify the
password of the `zulip` user in /etc/zulip/zulip-secrets.conf as
follows:

```ini
postgres_password = abcd1234
```

Now complete the installation by running the following commands.

```bash
# Ask Zulip installer to initialize the PostgreSQL database.
su zulip -c '/home/zulip/deployments/current/scripts/setup/initialize-database'

# And then generate a realm creation link:
su zulip -c '/home/zulip/deployments/current/manage.py generate_realm_creation_link'
```

## Using an alternate port

If you'd like your Zulip server to use an HTTPS port other than 443, you can
configure that as follows:

1. Edit `EXTERNAL_HOST` in `/etc/zulip/settings.py`, which controls how
   the Zulip server reports its own URL, and restart the Zulip server
   with `/home/zulip/deployments/current/scripts/restart-server`.
1. Add the following block to `/etc/zulip/zulip.conf`:

   ```ini
   [application_server]
   nginx_listen_port = 12345
   ```

1. As root, run
   `/home/zulip/deployments/current/scripts/zulip-puppet-apply`. This
   will convert Zulip's main `nginx` configuration file to use your new
   port.

We also have documentation for a Zulip server [using HTTP][using-http] for use
behind reverse proxies.

[using-http]: reverse-proxies.md#configuring-zulip-to-allow-http

## Customizing the outgoing HTTP proxy

To protect against [SSRF][ssrf], Zulip 4.8 and above default to
routing all outgoing HTTP and HTTPS traffic through
[Smokescreen][smokescreen], an HTTP `CONNECT` proxy; this includes
outgoing webhooks, website previews, and mobile push notifications.
By default, the Camo image proxy will be automatically configured to
use a custom outgoing proxy, but does not use Smokescreen by default
because Camo includes similar logic to deny access to private
subnets. You can [override][proxy.enable_for_camo] this default
configuration if desired.

To use a custom outgoing proxy:

1. Add the following block to `/etc/zulip/zulip.conf`, substituting in
   your proxy's hostname/IP and port:

   ```ini
   [http_proxy]
   host = 127.0.0.1
   port = 4750
   ```

1. As root, run
   `/home/zulip/deployments/current/scripts/zulip-puppet-apply`. This
   will reconfigure and restart Zulip.

If you have a deployment with multiple frontend servers, or wish to
install Smokescreen on a separate host, you can apply the
`zulip::profile::smokescreen` Puppet class on that host, and follow
the above steps, setting the `[http_proxy]` block to point to that
host.

If you wish to disable the outgoing proxy entirely, follow the above
steps, configuring an empty `host` value.

Optionally, you can also configure the [Smokescreen ACL
list][smokescreen-acls]. By default, Smokescreen denies access to all
[non-public IP
addresses](https://en.wikipedia.org/wiki/Private_network), including
127.0.0.1, but allows traffic to all public Internet hosts.

In Zulip 4.7 and older, to enable SSRF protection via Smokescreen, you
will need to explicitly add the `zulip::profile::smokescreen` Puppet
class, and configure the `[http_proxy]` block as above.

[proxy.enable_for_camo]: system-configuration.md#enable_for_camo
[smokescreen]: https://github.com/stripe/smokescreen
[smokescreen-acls]: https://github.com/stripe/smokescreen#acls
[ssrf]: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery

### S3 file storage requests and outgoing proxies

By default, the [S3 file storage backend][s3] bypasses the Smokescreen
proxy, because when running on EC2 it may require metadata from the
IMDS metadata endpoint, which resides on the internal IP address
169.254.169.254 and would thus be blocked by Smokescreen.

If your S3-compatible storage backend requires use of Smokescreen or
some other proxy, you can override this default by setting
`S3_SKIP_PROXY = False` in `/etc/zulip/settings.py`.

[s3]: upload-backends.md#s3-backend-configuration

## PostgreSQL warm standby

Zulip's configuration allows for [warm standby database
replicas][warm-standby] as a disaster recovery solution; see the
linked PostgreSQL documentation for details on this type of
deployment. Zulip's configuration builds on top of `wal-g`, our
[streaming database backup solution][wal-g], and thus requires that it
be configured for the primary and all secondary warm standby replicas.

In addition to having `wal-g` backups configured, warm standby
replicas should configure the hostname of their primary replica, and
username to use for replication, in `/etc/zulip/zulip.conf`:

```ini
[postgresql]
replication_user = replicator
replication_primary = hostname-of-primary.example.com
```

The `postgres` user on the replica will need to be able to
authenticate as the `replication_user` user, which may require further
configuration of `pg_hba.conf` and client certificates on the replica.
If you are using password authentication, you can set a
`postgresql_replication_password` secret in
`/etc/zulip/zulip-secrets.conf`.

[warm-standby]: https://www.postgresql.org/docs/current/warm-standby.html
[wal-g]: export-and-import.md#database-only-backup-tools
