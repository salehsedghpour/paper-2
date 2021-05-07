import matplotlib.pyplot as plt
import requests, logging
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300

from configparser import ConfigParser, NoOptionError, NoSectionError, MissingSectionHeaderError, ParsingError
PROMETHEUS="http://130.239.41.56:9090/"
logging.basicConfig(format='%(asctime)s - [%(levelname)s]  %(message)s', datefmt='%d/%m/%Y %I:%M:%S', level=logging.INFO)

envoy_status_queries = [
    {
        "query":'sum(irate(istio_requests_total{destination_service="httpbin.default.svc.cluster.local",response_code="0",response_flags="DC"}[5m]))',
        "name": "failed"
    },
    {
        "query": 'irate(istio_requests_total{destination_service="httpbin.default.svc.cluster.local",response_code="200",destination_version="v1"}[5m])',
        "name": "success"
    },
    {
        "query":'irate(istio_requests_total{destination_service="httpbin.default.svc.cluster.local",response_code="503",response_flags="UO",destination_version="v1"}[5m])',
        "name": "cb"
    }
]


def response_time(data):
    fig, axs = plt.subplots(12, 3)
    fig.set_figheight(15)
    fig.set_figwidth(10)
    title = "CB: "+str(data['cb'])+ "- Retry: "+str(data['retry'])+ "- Scenario: "+str(data['scenario'] +"- CPU:" +str(data['cpu']))
    fig.suptitle(title, fontsize=16)
    # make empty charts
    axs[0, 0].axis('off')
    axs[1, 0].axis('off')
    axs[2, 0].axis('off')
    axs[3, 0].axis('off')
    axs[4, 0].axis('off')
    axs[7, 0].axis('off')
    axs[8, 0].axis('off')
    axs[9, 0].axis('off')
    axs[10, 0].axis('off')
    axs[11, 0].axis('off')

    axs[2, 1].axis('off')
    axs[3, 1].axis('off')
    axs[4, 1].axis('off')
    axs[7, 1].axis('off')
    axs[8, 1].axis('off')
    axs[9, 1].axis('off')

    charts_rt = {}
    charts_st = {}
    logging.info("Fetching the data from Promethues between %s and %s." % (str(data['start']), str(data['end'])))

    for service in data['services']:
        raw_data_response_time = requests.get(
            PROMETHEUS + 'api/v1/query_range?query=(histogram_quantile(0.95, sum(irate(istio_request_duration_milliseconds_bucket{reporter="destination",destination_service="'+service+'.default.svc.cluster.local"}[1m])) by (le)))&start=' + str(
                data['start']) + '&end=' + str(data["end"]) + '&step=1')
        raw_data_status_200 = requests.get(
            PROMETHEUS + 'api/v1/query_range?query=irate(istio_requests_total{destination_service="'+service+'.default.svc.cluster.local",response_code="200"}[5m])&start=' + str(
                data['start']) + '&end=' + str(data["end"]) + '&step=1')
        raw_data_status_500 = requests.get(
            PROMETHEUS + 'api/v1/query_range?query=sum(irate(istio_requests_total{destination_service="'+service+'.default.svc.cluster.local",response_code="0",response_flags="DC"}[5m]))&start=' + str(
                data['start']) + '&end=' + str(data["end"]) + '&step=1')
        raw_data_status_cb = requests.get(
            PROMETHEUS + 'api/v1/query_range?query=irate(istio_requests_total{destination_service="'+service+'.default.svc.cluster.local",response_code="503",response_flags="UO"}[5m])&start=' + str(
                data['start']) + '&end=' + str(data["end"]) + '&step=1')
        logging.info("%s response times and status codes are successfully fetched from Prometheus. " % str(service))
        charts_rt[service] = []
        charts_st[service] = {
            "success": [],
            "failed": [],
            "cb": []
        }
        for item in raw_data_response_time.json()['data']['result'][0]['values']:
            if item[1] != 'NaN':
                if float(item[1]) < 0:
                    print("manfi")
                charts_rt[service].append(float(item[1]))
        try:
            for item in raw_data_status_200.json()['data']['result'][0]['values']:
                if item[1] != 'NaN':
                    if float(item[1]) < 0:
                        print("manfi")
                    charts_st[service]['success'].append(float(item[1]))
        except:
            charts_st[service]['success'] = len(charts_st[service]['success'])*[0]
        try:
            for item in raw_data_status_500.json()['data']['result'][0]['values']:
                if item[1] != 'NaN':
                    if float(item[1]) < 0:
                        print("manfi")
                    charts_st[service]['failed'].append(float(item[1]))
        except:
            charts_st[service]['failed'] = []
        try:
            for item in raw_data_status_cb.json()['data']['result'][0]['values']:
                if item[1] != 'NaN':
                    if float(item[1]) < 0:
                        print("manfi")
                    charts_st[service]['cb'].append(float(item[1]))
        except:
            charts_st[service]['cb'] = len(charts_st[service]['success'])*[0]
    # Front end
    axs[5, 0].plot(charts_rt['frontend'], label="95th-RT")
    # axs[5, 0].legend(bbox_to_anchor=(.7, 1.7), loc='upper left', fontsize="x-small")
    axs[5, 0].set_title("Frontend")
    axs[5, 0].set_ylabel("Latency")
    axs[6, 0].plot(charts_st['frontend']['success'], label="successful")
    axs[6, 0].plot(charts_st['frontend']['failed'], label="failed")
    axs[6, 0].plot(charts_st['frontend']['cb'], label="Circuit Broken")
    axs[6, 0].legend(loc='lower center', ncol=3, frameon=False, fontsize="x-small")
    axs[6, 0].set_xlabel("Time (s)")
    axs[6, 0].set_ylabel("RPS")

    # ad service
    axs[0, 1].plot(charts_rt['adservice'], label="95th-RT")
    #axs[0, 1].legend(loc="best", fontsize="x-small")
    axs[0, 1].set_title("Ad-Service")
    axs[0, 1].set_ylabel("Latency")
    axs[1, 1].plot(charts_st['adservice']['success'], label="successful")
    axs[1, 1].plot(charts_st['adservice']['failed'], label="failed")
    axs[1, 1].plot(charts_st['adservice']['cb'], label="Circuit Broken")
    #axs[1, 1].legend(loc="best", fontsize="x-small")
    axs[1, 1].set_xlabel("Time (s)")
    axs[1, 1].set_ylabel("RPS")

    # Checkout
    axs[5, 1].plot(charts_rt['checkoutservice'], label="95th-RT")
    #axs[5, 0].legend(loc="best", fontsize="x-small")
    axs[5, 1].set_title("Checkout Service")
    axs[5, 1].set_ylabel("Latency")
    axs[6, 1].plot(charts_st['checkoutservice']['success'], label="successful")
    axs[6, 1].plot(charts_st['checkoutservice']['failed'], label="failed")
    axs[6, 1].plot(charts_st['checkoutservice']['cb'], label="Circuit Broken")
    #axs[6, 0].legend(loc="best", fontsize="x-small")
    axs[6, 1].set_xlabel("Time (s)")
    axs[6, 1].set_ylabel("RPS")

    # Recommendation Service
    axs[10, 1].plot(charts_rt['recommendationservice'], label="95th-RT")
    # axs[5, 0].legend(loc="best", fontsize="x-small")
    axs[10, 1].set_title("Recommendation Service")
    axs[10, 1].set_ylabel("Latency")
    axs[11, 1].plot(charts_st['recommendationservice']['success'], label="successful")
    axs[11, 1].plot(charts_st['recommendationservice']['failed'], label="failed")
    axs[11, 1].plot(charts_st['recommendationservice']['cb'], label="Circuit Broken")
    # axs[6, 0].legend(loc="best", fontsize="x-small")
    axs[11, 1].set_xlabel("Time (s)")
    axs[11, 1].set_ylabel("RPS")

    # cart service
    axs[0, 2].plot(charts_rt['cartservice'], label="95th-RT")
    # axs[0, 1].legend(loc="best", fontsize="x-small")
    axs[0, 2].set_title("Cart Service")
    axs[0, 2].set_ylabel("Latency")
    axs[1, 2].plot(charts_st['cartservice']['success'], label="successful")
    axs[1, 2].plot(charts_st['cartservice']['failed'], label="failed")
    axs[1, 2].plot(charts_st['cartservice']['cb'], label="Circuit Broken")
    # axs[1, 1].legend(loc="best", fontsize="x-small")
    axs[1, 2].set_xlabel("Time (s)")
    axs[1, 2].set_ylabel("RPS")

    # shipping service
    axs[2, 2].plot(charts_rt['shippingservice'], label="95th-RT")
    # axs[0, 1].legend(loc="best", fontsize="x-small")
    axs[2, 2].set_title("Shipping Service")
    axs[2, 2].set_ylabel("Latency")
    axs[3, 2].plot(charts_st['shippingservice']['success'], label="successful")
    axs[3, 2].plot(charts_st['shippingservice']['failed'], label="failed")
    axs[3, 2].plot(charts_st['shippingservice']['cb'], label="Circuit Broken")
    # axs[1, 1].legend(loc="best", fontsize="x-small")
    axs[3, 2].set_xlabel("Time (s)")
    axs[3, 2].set_ylabel("RPS")

    # Email service
    axs[4, 2].plot(charts_rt['emailservice'], label="95th-RT")
    # axs[0, 1].legend(loc="best", fontsize="x-small")
    axs[4, 2].set_title("Email Service")
    axs[4, 2].set_ylabel("Latency")
    axs[5, 2].plot(charts_st['emailservice']['success'], label="successful")
    axs[5, 2].plot(charts_st['emailservice']['failed'], label="failed")
    axs[5, 2].plot(charts_st['emailservice']['cb'], label="Circuit Broken")
    # axs[1, 1].legend(loc="best", fontsize="x-small")
    axs[5, 2].set_xlabel("Time (s)")
    axs[5, 2].set_ylabel("RPS")

    # Payment service
    axs[6, 2].plot(charts_rt['paymentservice'], label="95th-RT")
    # axs[0, 1].legend(loc="best", fontsize="x-small")
    axs[6, 2].set_title("Payment Service")
    axs[6, 2].set_ylabel("Latency")
    axs[7, 2].plot(charts_st['paymentservice']['success'], label="successful")
    axs[7, 2].plot(charts_st['paymentservice']['failed'], label="failed")
    axs[7, 2].plot(charts_st['paymentservice']['cb'], label="Circuit Broken")
    # axs[1, 1].legend(loc="best", fontsize="x-small")
    axs[7, 2].set_xlabel("Time (s)")
    axs[7, 2].set_ylabel("RPS")

    # Currency service
    axs[8, 2].plot(charts_rt['currencyservice'], label="95th-RT")
    # axs[0, 1].legend(loc="best", fontsize="x-small")
    axs[8, 2].set_title("Currency Service")
    axs[8, 2].set_ylabel("Latency")
    axs[9, 2].plot(charts_st['currencyservice']['success'], label="successful")
    axs[9, 2].plot(charts_st['currencyservice']['failed'], label="failed")
    axs[9, 2].plot(charts_st['currencyservice']['cb'], label="Circuit Broken")
    # axs[1, 1].legend(loc="best", fontsize="x-small")
    axs[9, 2].set_xlabel("Time (s)")
    axs[9, 2].set_ylabel("RPS")

    # product catalog service
    axs[10, 2].plot(charts_rt['productcatalogservice'], label="95th-RT")
    # axs[0, 1].legend(loc="best", fontsize="x-small")
    axs[10, 2].set_title("Product Catalog Service")
    axs[10, 2].set_ylabel("Latency")
    axs[11, 2].plot(charts_st['productcatalogservice']['success'], label="successful")
    axs[11, 2].plot(charts_st['productcatalogservice']['failed'], label="failed")
    axs[11, 2].plot(charts_st['productcatalogservice']['cb'], label="Circuit Broken")
    # axs[1, 1].legend(loc="best", fontsize="x-small")
    axs[11, 2].set_xlabel("Time (s)")
    axs[11, 2].set_ylabel("RPS")

    # lines = [
    #     plt.Line2D((.7, 1), (.17, .17), color="k", linewidth=3),
    #     plt.Line2D((.7, 1), (.335, .335), color="k", linewidth=3),
    #     plt.Line2D((.7, 1), (.5, .5), color="k", linewidth=3),
    #     plt.Line2D((.7, 1), (.665, .665), color="k", linewidth=3),
    #     plt.Line2D((.7, 1), (.83, .83), color="k", linewidth=3)
    #
    # ]
    # #for line in lines:
    #     #fig.add_artist(line)
    title = "CB-"+str(data['cb'])+ "_Retry-"+str(data['retry'])+ "+R-timeout-"+str(data['retry_to'])+"_Scenario-"+str(data['scenario']) +"_CPU-" +str(data['cpu'])+'.png'
    plt.savefig("../results/"+title)
    logging.info("%s is successfully created and saved." % str(title))

