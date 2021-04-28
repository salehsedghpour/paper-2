import logging, yaml
from kubernetes.client.rest import ApiException


logging.basicConfig(format='%(asctime)s - [%(levelname)s]  %(message)s', datefmt='%d/%m/%Y %I:%M:%S', level=logging.INFO)


def create_deployment(api_instance, deployment):
    """
    :param api_instance:
    :param deployment:
    :return:
    """
    try:
        resp = api_instance.create_namespaced_deployment(body=deployment, namespace="default")

        logging.info("Deployment %s is successfully created. " % str(deployment['metadata']['name']))
        return True
    except ApiException as e:
        logging.warning("Deployment creation of %s did not completed %s"  % (str(deployment['metadata']['name']), str(e)))
        return False


def delete_deployment(api_instance, deployment_name):
    """
    :param api_instance:
    :param deployment:
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
