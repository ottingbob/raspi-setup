NODE_SERVER="192.168.1.256"
# To get the TOKEN_VALUE you need to get the token from the server node
# at the location /var/lib/rancher/k3s/server/token
TOKEN_VALUE=""
NODE_NAME="my-k3s-agent"

sudo k3s agent --server https://$NODE_SERVER:6443 --token $TOKEN_VALUE --with-node-id $NODE_NAME --node-name $NODE_NAME
