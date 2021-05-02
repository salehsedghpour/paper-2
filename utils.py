import logging, yaml
from kubernetes.client.rest import ApiException


logging.basicConfig(format='%(asctime)s - [%(levelname)s]  %(message)s', datefmt='%d/%m/%Y %I:%M:%S', level=logging.INFO)


def create_deployment(api_instance, deployment, cpu=None):
    """
    :param api_instance:
    :param deployment:
    :return:
    """
    try:
        if cpu:
            deployment['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu'] = cpu
            deployment['spec']['template']['spec']['containers'][0]['resources']['requests']['cpu'] = cpu
        resp = api_instance.create_namespaced_deployment(body=deployment, namespace="default")

        logging.info("Deployment %s is successfully created. " % str(deployment['metadata']['name']))
        return True
    except ApiException as e:
        logging.warning("Deployment creation of %s did not completed %s"  % (str(deployment['metadata']['name']), str(e)))
        return False


def delete_deployment(api_instance, deployment_name):
    """
    :param api_instance:
    :param deployment_name:
    :return:
    """
    try:
        resp = api_instance.delete_namespaced_deployment(name=deployment_name, namespace="default")

        logging.info("Deployment %s is successfully deleted. " % str(deployment_name))
        return True
    except ApiException as e:
        logging.warning("Deployment deletion of %s did not completed %s"  % (deployment_name, str(e)))
        return False


def create_service(api_instance, service):
    """
    :param api_instance:
    :param service:
    :return:
    """
    try:
        resp = api_instance.create_namespaced_service(body=service, namespace="default")
        logging.info("Service %s is successfully created. " % str(service['metadata']['name']))
        return True
    except ApiException as e:
        logging.warning("Service creation of %s did not completed %s"  % (str(service['metadata']['name']), str(e)))
        return False


def delete_service(api_instance, service_name):
    """
    :param api_instance:
    :param service_name:
    :return:
    """
    try:
        resp = api_instance.delete_namespaced_service(name=service_name, namespace="default")
        logging.info("Service %s is successfully deleted. " % str(service_name))
        return True
    except ApiException as e:
        logging.warning("Service deletion of %s did not completed %s"  % (str(service_name), str(e)))
        return False


def create_circuit_breaker(api_instance, service_name, max_requests):
    """
    :param api_instance:
    :param service_name:
    :param max_requests:
    :return:
    """
    try:
        cb = {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "DestinationRule",
            "metadata": {"name": service_name+"-cb"},
            "spec": {
                "host": service_name,
                "trafficPolicy":{
                    "connectionPool":{
                        "http": {"http2MaxRequests": max_requests}
                    }
                }
            }
        }
        api_instance.create_namespaced_custom_object(
            namespace="default",
            body=cb,
            group="networking.istio.io",
            version="v1alpha3",
            plural="destinationrules"
        )
        logging.info("Circuit breaker for service %s with value of %s is successfully created. " % (str(service_name), str(max_requests)))
        return True
    except ApiException as e:
        logging.warning("Circuit breaker creation for service %s is not completed. %s" % (str(service_name), str(e)))
        return False


def delete_circuit_breaker(api_instance, service_name):
    """
    :param api_instance:
    :param service_name:
    :return:
    """
    try:
        api_instance.delete_namespaced_custom_object(
            namespace="default",
            group="networking.istio.io",
            version="v1alpha3",
            plural="destinationrules",
            name=service_name+"-cb"
        )
        logging.info("Circuit breaker for service %s is successfully deleted. " % str(service_name))
        return True
    except ApiException as e:
        logging.warning(
            "Circuit breaker deletion for service %s is not completed. %s" % (str(service_name), str(e)))
        return False


def create_retry(api_instance, service_name, attempts, timeout):
    """
    :param api_instance:
    :param service_name:
    :param attempts:
    :param timeout:
    :return:
    """
    try:
        retry = {
          "apiVersion": "networking.istio.io/v1alpha3",
          "kind": "VirtualService",
          "metadata": {
            "name": service_name +"-retry"
          },
          "spec": {
            "hosts": [
              service_name+".default.svc.cluster.local"
            ],
            "http": [
              {
                "route": [
                  {
                    "destination": {
                      "host": service_name+".default.svc.cluster.local",
                    }
                  }
                ],
                "retries": {
                  "attempts": attempts,
                  "perTryTimeout": timeout
                }
              }
            ]
          }
        }
        api_instance.create_namespaced_custom_object(
            namespace="default",
            body=retry,
            group="networking.istio.io",
            version="v1alpha3",
            plural="virtualservices"
        )
        logging.info("Retry mechanism for service %s with value of %s is successfully created. " % (str(service_name), str(attempts)))
        return True
    except ApiException as e:
        logging.warning("Retry mechanism creation for service %s is not completed. %s" % (str(service_name), str(e)))
        return False