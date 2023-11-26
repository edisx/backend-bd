# create .env like .env.example

# add your project name in gunicorn.conf

# maybe change domain in django.conf

# sudo docker build -t backend .

# sudo docker run -d -p 80:80 -p --env-file .env backend