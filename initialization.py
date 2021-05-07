from kubernetes import client, config
import yaml

config.load_kube_config()


from os import walk

f = []
for (dirpath, dirnames, filenames) in walk("yaml-files"):
    print(dirpath)
    break



data={
    "services": ["frontend", "adservice", "checkoutservice", "recommendationservice", "cartservice", "shippingservice", "emailservice", "paymentservice", "currencyservice", "productcatalogservice"],
    "start": 1619783313,
    "end": 1619783513,
    "cb": 'default',
    "scenario": '1',
    "retry": "default",
    "cpu": 0.2
}
response_time(data)