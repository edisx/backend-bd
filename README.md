# create .env like .env.example

# add your ca_bundle.crt, certificate.crt and private.key to dockerfiles

# sudo docker build -t backend .

# sudo docker run -d -p 80:80 -p 443:443 --env-file .env backend