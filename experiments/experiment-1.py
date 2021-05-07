from kubernetes import client, config
import utils, yaml, time, logging, charts





config.load_kube_config()
deployment_api = client.AppsV1Api()
customobject_api = client.CustomObjectsApi()
services = ["frontend", "adservice", "checkoutservice", "recommendationservice", "cartservice", "shippingservice", "emailservice", "paymentservice", "currencyservice", "productcatalogservice"]
logging.basicConfig(format='%(asctime)s - [%(levelname)s]  %(message)s', datefmt='%d/%m/%Y %I:%M:%S', level=logging.INFO)

for service in services:
    with open('../yaml-files/Deployment/'+service+'.yaml') as f:
        dep = yaml.safe_load(f)
        utils.create_deployment(deployment_api, dep, cpu="300m")
with open('../yaml-files/Deployment/redis-cart.yaml') as f:
    dep = yaml.safe_load(f)
    utils.create_deployment(deployment_api, dep, cpu="300m")


logging.info("All services are deployed successfully with CPU allocation 300m - Wait for 120 seconds to for all pods "
             "to be running")
time.sleep(120)

rpss = [200]
cbs = [0 ,5, 10, 20, 50, 100, 150]
retrys = [1, 2, 5, 10]
retry_timeouts = ["1s", "2s", "3s", "5s", "10s"]

for cb in cbs:
    if cb:
        for service in services:
            utils.create_circuit_breaker(customobject_api, service, cb)
    for retry in retrys:
        if retry:
            for retry_timeout in retry_timeouts:
                for service in services:
                    utils.create_retry(customobject_api, service, retry, retry_timeout)
                start = str(int(time.time() * 1000))
                with open('../yaml-files/Deployment/loadgenerator.yaml') as f:
                    dep = yaml.safe_load(f)
                    for rps in rpss:
                        dep['spec']['template']['spec']['containers'][0]['env'][-1]['value'] = str(rps)
                        if rps == 200:
                            utils.create_deployment(deployment_api, dep, cpu="2000m")
                        else:
                            utils.patch_deployment(deployment_api, "loadgenerator", dep)
                        time.sleep(180)
                    end = int(time.time()*1000)
                    res_url = '<a href="http://130.239.41.56:3000/d/gSoJvZjMk/response-time?orgId=1&from='+str(start)+\
                              '&to='+str(end)+'" target="_blank">Response Time</a>'
                    req_url = '<a href="http://130.239.41.56:3000/d/O9Yl1U8Mz/requests-rate?orgId=1&from='+str(start)+\
                              '&to='+str(end)+'" target="_blank">Requests Rate</a>'
                    data = ("1", "1", str(cb), str(retry), str(retry_timeout), "300m", str(start), str(end), res_url,
                            req_url)
                    utils.insert_db(data)
                    time.sleep(120)

                utils.delete_deployment(deployment_api, "loadgenerator")
                for service in services:
                    utils.delete_retry(customobject_api, service)

    if cb:
        for service in services:
            utils.delete_circuit_breaker(customobject_api, service)

