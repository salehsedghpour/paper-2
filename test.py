# from kubernetes import client, config
# import yaml
# from utils import patch_deployment
# config.load_kube_config()
#
# v1 = client.CoreV1Api()
# #ret = v1.list(watch=False)
# with open('yaml-files/Deployment/loadgenerator.yaml') as f:
#     dep = yaml.safe_load(f)
#     # deployment
#     k8s_beta = client.AppsV1Api()
#     # service
#     #k8s_beta = client.CoreV1Api()
#     # CB
#     #k8s_beta = client.CustomObjectsApi()
#     dep['spec']['template']['spec']['containers'][0]['env'][-1]['value'] = str(20)
#     patch_deployment(k8s_beta, "loadgenerator", dep)
#
#     #k8s_beta.deployment
#
#     #print()
#     #resp = k8s_beta(
#     #    body=dep, namespace="default")
#     #create_service(k8s_beta, dep)
#     #print("Deployment created. status='%s'" % str(resp.status))
#
# # k8s_beta = client.CustomObjectsApi()
# # delete_retry(k8s_beta, "frontend")
#
#

import psycopg2

try:
    connection = psycopg2.connect(user="postgres",
                                  password="Alirez@6617",
                                  host="130.239.41.56",
                                  port="5432",
                                  database="experiments")
    cursor = connection.cursor()

    postgres_insert_query = """ INSERT INTO experiments.experiment ( name, scenario, cb, retry, retry_time_out, cpu, start_time, end_time, 
    response_time_url, requests_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    record_to_insert = ("test", "test", "test", "test", "test","test", "test", "test", "test", "test")
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into mobile table")

except (Exception, psycopg2.Error) as error:
    print("Failed to insert record into mobile table", error)

finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")