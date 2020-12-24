#!/usr/bin/env bash

# This script is only for recreating a local postgresql database (non docker)
# Note: This script must run it from root directory with `. ./scripts/reset_local_db.sh`

# Helper function: Exit with error
function exit_error() {
  ERROR "$1" 1>&2
}

if [[ -z $POSTGRES_DB ]]; then
  exit_error "POSTGRES_DB not set! Aborting."
fi

echo "Recreate Postgres database"
dropdb ${POSTGRES_DB}
createdb ${POSTGRES_DB}

# echo "Collecting static files"
python app/manage.py collectstatic --no-input -v 0

echo "Run migrations"
# python app/manage.py makemigrations main
python app/manage.py makemigrations
python app/manage.py migrate

# python app/manage.py createsuperuser
echo "Create default Django superuser admin/admin."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'gbournique@gmail.com', 'admin')" | python app/manage.py shell || true

