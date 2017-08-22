User Service using Django, rabbit-mq and docker

To run:

docker build -t user_service .
docker run -d --name mathurt_user_service -p 127.0.0.1:8000:8000 -p 127.0.0.1:5673:5672 -p 127.0.0.1:15673:15672 --rm -i -t user_service
docker exec -it mathurt_user_service bash 


rabbitmq-start &

#------------------
To run tests
python3.6 manage.py test tests
#------------------

cd /user_consumer_service/
python3.6 consumer.py &

#------------------
Can be executed from docker container or from the client machine
Issues with docker on local machine can sometimes prevent port forwarding and it can be run from inside the container
#------------------



POST CURL:
curl -X POST   http://127.0.0.1:8000/v1/users/   -H 'cache-control: no-cache'   -H 'content-type: application/json'   -H 'postman-token: 7c199d37-511b-4b2f-94b9-6ba8c9b444a2'   -d '{
  "email": "joey@friends.com",
  "phone_number": "2521235535",
  "full_name": "Joey Tribbiani",
  "password": "Chandler",
  "metadata": "male, age 32, actor, philanthropist, plays guitar, college-educated. Played character in Days of our lives"
  }'

GET URL:
curl -X GET --header 'Accept: application/json' --header 'X-CSRFToken: Cqrjj2ewZMqiCEKYk4Gl5JT04njE9mx7OD4DBhWkmpW00ir4JBGeHKng6yDXdEdf' 'http://127.0.0.1:8000/v1/users'

GET URL with Parameter:
curl -X GET --header 'Accept: application/json' --header 'X-CSRFToken: Cqrjj2ewZMqiCEKYk4Gl5JT04njE9mx7OD4DBhWkmpW00ir4JBGeHKng6yDXdEdf' 'http://127.0.0.1:8000/v1/users?query=age%2032'
