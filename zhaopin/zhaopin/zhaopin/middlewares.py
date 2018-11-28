from scrapy import signals
from .utils.userAgents import agents
import base64
import random
from uuid import uuid4
# 代理服务器
proxyServer = "http://http-dyn.abuyun.com:9020"

# 代理隧道验证信息
proxyUser = ""
proxyPass = ""
# for Python3
proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")

class ProxyMiddleWare(object):
    def process_request(self, request, spider):
        request.meta["proxy"] = proxyServer
        request.headers['Referer'] = "https://www.lagou.com/jobs/list_"
        # request.headers['Cookie'] = "JSESSIONID={}+user_trace_token={}".format(uuid4(),uuid4())
        request.headers["Proxy-Authorization"] = proxyAuth

    def process_exception(self, request, exception, spider):
        # 出现异常时（超时）使用代理
        print("\n出现异常，正在使用代理重试....\n")
        request.meta["proxy"] = proxyServer
        request.headers["Proxy-Authorization"] = proxyAuth
        return request


class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers['User-Agent'] = agent


class CheckProxy(object):
    def process_response(self, request, response, spider):
        print(request.meta['proxy'])
        print(request.headers['User-Agent'])
        return response
