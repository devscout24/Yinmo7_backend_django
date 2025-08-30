#!/bin/bash
# Usage: ./deploy.sh project_name domain django_app

PROJECT=$1
DOMAIN=$2
DJANGO_APP=$3

BASE_DIR="/var/www/$PROJECT"
VENV="$BASE_DIR/env"
APP_DIR="$BASE_DIR/app"

if [ -z "$PROJECT" ] || [ -z "$DOMAIN" ] || [ -z "$DJANGO_APP" ]; then
  echo "❌ Usage: ./deploy.sh project_name domain django_app"
  exit 1
fi

echo "🚀 Deploying $PROJECT ($DOMAIN)..."

# 1. Install system packages
sudo apt update
sudo apt install -y python3-venv python3-pip nginx git

# 2. Setup directories
sudo mkdir -p $BASE_DIR/{static,media}
sudo chown -R $USER:$USER $BASE_DIR

# 3. Setup virtual environment
if [ ! -d "$VENV" ]; then
  python3 -m venv $VENV
fi
source $VENV/bin/activate

# 4. Install requirements
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi
pip install gunicorn

# 5. Copy project files
rsync -av --exclude 'deploy/' ./ $APP_DIR/

# 6. Run migrations & collectstatic
cd $APP_DIR
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 7. Setup Gunicorn systemd
sed "s/{{project}}/$PROJECT/g; s/{{django_app}}/$DJANGO_APP/g" $(dirname $0)/gunicorn.service.template | sudo tee /etc/systemd/system/$PROJECT.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable $PROJECT
sudo systemctl restart $PROJECT

# 8. Setup Nginx
sed "s/{{project}}/$PROJECT/g; s/{{domain}}/$DOMAIN/g" $(dirname $0)/nginx.conf.template | sudo tee /etc/nginx/sites-available/$PROJECT > /dev/null
sudo ln -sf /etc/nginx/sites-available/$PROJECT /etc/nginx/sites-enabled/

sudo nginx -t && sudo systemctl reload nginx

echo "✅ Deployment completed for $PROJECT"
echo "🌍 Visit: http://$DOMAIN"
