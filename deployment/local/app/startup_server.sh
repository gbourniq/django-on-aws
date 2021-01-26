#!/bin/bash

cd /home/portfoliouser/app

if [[ ! -z $STATICFILES_BUCKET ]]; then
    echo "STATICFILES_BUCKET is set, assuming AWS deployment"
    echo "Enable public access for Django collectstatic"
    aws s3api put-public-access-block \
        --bucket $STATICFILES_BUCKET \
        --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" || true
fi

echo "Collecting static files"
python manage.py collectstatic --no-input -v 0

if [[ ! -z $STATICFILES_BUCKET ]]; then
    echo "Disable public access for Django collectstatic"
    aws s3api put-public-access-block \
        --bucket $STATICFILES_BUCKET \
        --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" || true
fi

echo "Running migrations"
python manage.py makemigrations main
python manage.py migrate

# echo "Django superuser must be create manually with python manage.py createsuperuser"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'gbournique@gmail.com', 'admin')" | python manage.py shell 2>/dev/null || true

echo "Starting webserver"
gunicorn portfolio.wsgi:application --bind 0.0.0.0:8080 
