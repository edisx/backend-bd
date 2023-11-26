1. sudo apt-get update && sudo apt-get upgrade -y
1. sudo apt install docker.io

1. clone project

1. create .env like .env.example add your ec2 ip
1. make sure your route53 is pointing to your ec2 ip

1. add your ca_bundle.crt, certificate.crt and private.key to /dockerfiles

1. sudo docker build -t backend .
1. sudo docker run -d -p 80:80 -p 443:443 --env-file .env backend