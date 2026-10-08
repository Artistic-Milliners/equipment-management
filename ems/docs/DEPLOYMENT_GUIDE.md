# EMS Production Deployment Guide (Docker on Linux)

Step-by-step plan for deploying the EMS Django application to a Linux server (Ubuntu/Debian) using `docker-compose.prod.yml`.

**Stack:** PostgreSQL 15 (`db`) → Django + Gunicorn (`web`) → Nginx reverse proxy (`nginx`), all on the private `ems_network`. Only Nginx is exposed to the outside (ports 80/443).

---

## Step 0 — Prerequisites (on your development machine)

The following files must be committed and pushed, or a fresh clone on the server will fail to build:

- `ems/Dockerfile`
- `ems/Dockerfile.nginx`
- `ems/nginx.conf`
- `ems/entrypoint.sh`
- `ems/docker-compose.prod.yml`
- `ems/.dockerignore`
- `ems/.gitignore`

```powershell
cd D:\Zohaib\webapps\ems
git add ems/Dockerfile ems/Dockerfile.nginx ems/nginx.conf ems/entrypoint.sh ems/docker-compose.prod.yml ems/.dockerignore ems/.gitignore
git add -u
git commit -m "Add production Docker setup"
git push origin <branch>
```

> `.env.prod` and `.env.dev` are git-ignored on purpose and are **never** pushed. `.env.prod` is created directly on the server in Step 4.

---

## Step 1 — Install Docker on the server

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
sudo systemctl enable --now docker
```

Log out and back in so the `docker` group change applies, then verify:

```bash
docker --version
docker compose version
```

---

## Step 2 — Configure the firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp      # only needed once HTTPS is configured
sudo ufw enable
```

> Docker bypasses ufw for any port a container publishes. In the production compose file only Nginx publishes ports (80/443); PostgreSQL and Gunicorn are reachable only inside the Docker network.

---

## Step 3 — Get the code onto the server

```bash
sudo mkdir -p /opt/ems && sudo chown $USER:$USER /opt/ems
cd /opt/ems
git clone -b <branch> https://github.com/Xzib/equipment-management.git .
cd ems                      # the Django project lives in this subfolder
```

If the repository is private, use a GitHub personal access token as the password, or add an SSH deploy key.

Create the `ssl` folder. `Dockerfile.nginx` copies it, and git does not keep empty folders:

```bash
mkdir -p ssl
```

---

## Step 4 — Create `.env.prod` on the server

```bash
nano .env.prod
```

```ini
ENV_STATE=prod
DEBUG=False
SECRET_KEY=<newly generated key>
JWT_SECRET_KEY=<a different newly generated key>

DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=ems
DB_USER=zohaib
DB_PASSWORD=<strong password>
DB_HOST=db
DB_PORT=5432

ALLOWED_HOSTS=172.25.25.173
API_BASE_URL=http://172.25.25.173
API_PORT=
TZ=Asia/Karachi
```

Generate each key separately (run twice):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Restrict access to the file:

```bash
chmod 600 .env.prod
```

Notes:

- **Server address:** if the server's IP is not `172.25.25.173`, update both `ALLOWED_HOSTS` and `API_BASE_URL`. Separate multiple hosts with spaces, e.g. `ALLOWED_HOSTS=172.25.25.173 ems.local`.
- **Existing database volume:** PostgreSQL only reads the password when the `postgres_data` volume is first created. If you are reusing an existing volume, `DB_PASSWORD` must match the original password, or change it first:
  ```bash
  docker exec -it ems_postgres psql -U zohaib -d ems -c "ALTER USER zohaib WITH PASSWORD 'new-password';"
  ```

---

## Step 5 — Build and start the containers

The production compose file **requires** `--env-file .env.prod` so the database container receives the same credentials as the web container. Add a shortcut alias:

```bash
echo "alias dc='docker compose --env-file /opt/ems/ems/.env.prod -f /opt/ems/ems/docker-compose.prod.yml'" >> ~/.bashrc
source ~/.bashrc
```

Build and start:

```bash
cd /opt/ems/ems
dc up -d --build
```

The first build takes a few minutes. On startup the web container waits for PostgreSQL, runs migrations and `collectstatic`, then starts Gunicorn.

---

## Step 6 — Verify the deployment

```bash
dc ps                       # all 3 services "Up"; db shows "(healthy)"
dc logs -f web              # look for "EMS Application is ready to start!" (Ctrl+C to exit)
curl -I http://172.25.25.173/   # expect 200 or 302, not 400 or 502
```

Use the server address, not `localhost`: Django rejects any hostname not listed in `ALLOWED_HOSTS` with `400 Bad Request`. To allow `localhost` as well, add it to `ALLOWED_HOSTS` (space-separated) and run `dc up -d`.

```bash
```

Then open `http://172.25.25.173/` from a computer on the same network.

---

## Step 7 — Load initial data (first deployment only)

Choose **one** option:

- **Option A — Start from fixtures:** an empty system seeded with the base data in `core/fixtures`. Follow 7.1–7.5 below.
- **Option B — Migrate the existing development database:** copies all complaints, spares, users, groups and permissions from the development machine. Follow [Step 7B](#step-7b--migrate-the-existing-development-database-option-b) and **skip 7.1–7.5**.

### 7.1 Create an admin account

```bash
dc exec web python manage.py createsuperuser
```

### 7.2 Create the Unit

All departments in `Department.json` belong to unit `AMX001`, so it must exist first. Replace the name and location with the real values:

```bash
dc exec web python manage.py shell -c "from core.models import Unit; Unit.objects.get_or_create(id='AMX001', defaults={'name':'AMX', 'location':'Karachi'})"
```

### 7.3 Load fixtures (order matters)

```bash
for f in Department Contractor Designation Manufacturer Equipment Machines Spares MachineSpares IssueList; do
  echo "Loading $f..." && dc exec -T web python manage.py loaddata $f.json || break
done
```

> `MachineSpares.json` holds the machine ↔ spare links and must load after both `Machines` and `Spares`.

### 7.4 Run setup and permission commands (order matters)

```bash
for c in setup_inventory_groups setup_tiered_permissions fix_spare_item_codes setup_approval_groups setup_inventory_access setup_inventory_permissions setup_management_permissions; do
  echo "Running $c..." && dc exec -T web python manage.py $c || break
done
```

### 7.5 Create user accounts

Log in at `http://172.25.25.173/admin/` and create employees, assigning each one a department and a group.

---

## Step 7B — Migrate the existing development database (Option B)

Moves the development data (local Windows PostgreSQL 16, database `ems` on `localhost:5432`) and uploaded images (`media/`) to the server.

Before you start:

- **Schema must match the code.** The migrations applied in the development database must be exactly the migration files in the deployed code. If they match, `migrate` has nothing to do when the container starts. Check with `python manage.py showmigrations` locally: every entry should be `[X]`.
- **Images are part of the data.** Database records point to files in `media/`. Copy both, or complaint and spare images will appear broken.
- **Version difference is fine.** Development runs PostgreSQL 16 and production runs 15. A plain SQL dump of the Django database restores into 15 without problems.
- **Do not load fixtures afterwards.** The development database already contains units, departments, groups and permissions; loading `core/fixtures` on top causes duplicate-key errors.

### 7B.1 Export on the development PC (PowerShell)

```powershell
cd D:\Zohaib\webapps\ems\ems
$env:PGPASSWORD = '<dev database password>'
& 'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe' -h localhost -U zohaib -d ems --no-owner --no-privileges -f ems_dev.sql
tar czf media.tar.gz -C media .
```

`--no-owner --no-privileges` makes every table belong to whichever user restores it on the server, so differing usernames don't cause problems.

### 7B.2 Copy both files to the server

```powershell
scp ems_dev.sql media.tar.gz ituser@172.25.25.173:/opt/ems/
```

### 7B.3 Empty the server database

The web container runs `migrate` on every start, so after Step 6 the server database already holds empty tables that would clash with the dump. Back it up, stop the app, and reset the schema:

```bash
cd /opt/ems/ems
docker exec ems_postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > /opt/ems/before_restore.sql.gz
dc stop web nginx
docker exec ems_postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"'
```

### 7B.4 Restore the database

```bash
docker exec -i ems_postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1' < /opt/ems/ems_dev.sql
```

The restore must finish without any `ERROR` line. `ON_ERROR_STOP` makes it stop at the first error instead of leaving a half-restored database.

### 7B.5 Start the app and restore uploaded images

```bash
dc up -d --build
docker cp /opt/ems/media.tar.gz ems_web:/tmp/media.tar.gz
docker exec -u root ems_web sh -c "tar xzf /tmp/media.tar.gz -C /app/media && chown -R django:django /app/media && rm /tmp/media.tar.gz"
docker exec ems_web sh -c "find /app/media -type f | wc -l"    # same file count as development media/
```

- **No extra image needed:** the archive is extracted inside the running `ems_web` container, which already has the media volume mounted. This works even when the server cannot reach Docker Hub.
- **Ownership is required:** the extracted files belong to root, but the app runs as the `django` user. Without the `chown`, new image uploads fail with a permission error.

### 7B.6 Verify

```bash
docker exec ems_postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "select count(*) from core_machineissue;"'   # same count as development
dc logs web | grep -i migrat          # expect "No migrations to apply"
```

Then open the site, log in with an existing account, and open a complaint that has images.

### 7B.7 Clean up and secure

- **Reset development passwords.** All accounts move over with their development passwords, which are often simple test ones:
  ```bash
  dc exec web python manage.py changepassword <username>
  ```
- **Expect one forced logout.** The production `SECRET_KEY` invalidates old sessions; users simply log in again.
- **Delete the dump files** on both machines. They contain all data, including password hashes:
  ```bash
  rm /opt/ems/ems_dev.sql /opt/ems/media.tar.gz
  ```
  ```powershell
  Remove-Item ems_dev.sql, media.tar.gz
  ```

If something goes wrong, the pre-restore backup can be restored with Step 9's restore command, using `/opt/ems/before_restore.sql.gz` after emptying the schema again (7B.3).

---

## Step 8 — Automatic start after reboot

No extra setup is needed: Docker is enabled at boot, and every service has `restart: unless-stopped`. To confirm, run `sudo reboot`, then `dc ps` once the server is back up.

---

## Step 9 — Backups

Create the backup script:

```bash
mkdir -p /opt/ems/backups
cat > /opt/ems/backup.sh <<'EOF'
#!/bin/bash
set -e
TS=$(date +%F_%H%M)
DIR=/opt/ems/backups
docker exec ems_postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > $DIR/db_$TS.sql.gz
docker exec ems_web tar czf - -C /app/media . > $DIR/media_$TS.tar.gz
find $DIR -type f -mtime +14 -delete     # keep 14 days
EOF
chmod +x /opt/ems/backup.sh
```

Schedule it daily at 2 am with `crontab -e`:

```
0 2 * * * /opt/ems/backup.sh >> /opt/ems/backups/backup.log 2>&1
```

Notes:

- **Volume name:** confirm the media volume name with `docker volume ls`. Compose prefixes volume names with the project folder name (`ems`).
- **Off-server copies:** copy backups to another machine regularly. A backup on the same disk will not survive that disk failing.

Restore the database from a backup:

```bash
gunzip -c /opt/ems/backups/db_<date>.sql.gz | docker exec -i ems_postgres sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'
```

---

## Step 10 — Deploying updates

```bash
cd /opt/ems && git pull
cd ems && dc up -d --build
dc logs -f web
```

Migrations and `collectstatic` run automatically each time the web container starts.

---

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `400 Bad Request` | The address you are using is not in `ALLOWED_HOSTS`. Add it to `.env.prod`, then run `dc up -d`. |
| `502 Bad Gateway` | The web container crashed or is still starting. Check `dc logs web`. |
| Page loads without CSS | Static files are missing. Run `dc exec web python manage.py collectstatic --noinput`, then `dc restart nginx`. |
| `password authentication failed` | `DB_PASSWORD` does not match the password the database was created with. Use `ALTER USER` (Step 4), or on a fresh install with no data, `dc down -v` (**deletes all data**). |
| `required variable DB_NAME is missing` | `docker compose` was run without `--env-file`. Use the `dc` alias. |
| Nginx build fails on `COPY ./ssl` | The `ssl/` folder does not exist. Run `mkdir ssl`. |
| `exec /app/entrypoint.sh: no such file` | Usually Windows line endings. The Dockerfile strips them, so rebuild with `dc build --no-cache web`. |

---

## Not yet configured: HTTPS

This setup serves plain HTTP. Because `172.25.25.173` is an internal address, Let's Encrypt cannot issue a certificate for it; a self-signed or company-issued certificate is needed. Enabling HTTPS requires:

1. Placing the certificate and key in `ssl/` (or mounting them as a volume).
2. Enabling the `listen 443 ssl` server block and HTTP → HTTPS redirect in `nginx.conf`.
3. Adding to `ems/settings.py`:
   ```python
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   CSRF_TRUSTED_ORIGINS = ['https://<your-host>']
   SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True
   ```
