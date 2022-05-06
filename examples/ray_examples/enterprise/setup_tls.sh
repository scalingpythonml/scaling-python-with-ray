# Generate some certificates, you will have to make these
# available on _all of your workers and clients_. This makes
# it not much better than shared secret.
# On k8s you can make it available as a secret or shared RO volume.

# Make the CA
openssl req -x509 -newkey rsa:4096 -nodes -days 365 -keyout ca-key.pem -out ca-cert.pem -subj "/C=CA/ST=Ontario/L=Ottawa/O=Magic/OU=Distributed/CN=*/emailAddress=professor@timbit.ca"

# Server's cert
openssl req -newkey rsa:4096 -nodes -keyout server-key.pem -out server-req.pem -subj "/C=CA/ST=Ontario/L=Ottawa/O=Magic/OU=Distributed/CN=*/emailAddress=boo@magic.com"

# Sign the server cert with the CA
openssl x509 -req -in server-req.pem -days 365 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem

export RAY_USE_TLS=1
export RAY_TLS_SERVER_CERT=./server-cert.pem
export RAY_TLS_SERVER_KEY=./server-key.pem
export RAY_TLS_CA_CERT=./ca-cert.pem
