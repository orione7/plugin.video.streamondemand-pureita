# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Alfa / Alfa-PureITA
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of Alfa / Alfa-PureITA 
#
# Alfa / Alfa-PureITA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alfa / Alfa-PureITA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Alfa / Alfa-PureITA.  If not, see <http://www.gnu.org/licenses/>.
#=====================================================================================================================================
# Cloudflare 
#=====================================================================================================================================

import re
import time
import urllib
import urlparse

from core import logger
from decimal import Decimal

#=====================================================================================================================================

class Cloudflare:
    def __init__(self, response):
        self.timeout = 5
        self.domain = urlparse.urlparse(response["url"])[1]
        self.protocol = urlparse.urlparse(response["url"])[0]
        self.js_data = {}
        self.header_data = {}

        if not "var s,t,o,p,b,r,e,a,k,i,n,g,f" in response["data"] or "chk_jschl" in response["url"]:
            return

        try:
            self.js_data["auth_url"] = \
            re.compile('<form id="challenge-form" action="([^"]+)" method="get">').findall(response["data"])[0]
            self.js_data["params"] = {}
            self.js_data["params"]["jschl_vc"] = \
            re.compile('<input type="hidden" name="jschl_vc" value="([^"]+)"/>').findall(response["data"])[0]
            self.js_data["params"]["pass"] = \
            re.compile('<input type="hidden" name="pass" value="([^"]+)"/>').findall(response["data"])[0]
            var, self.js_data["value"] = \
            re.compile('var s,t,o,p,b,r,e,a,k,i,n,g,f[^:]+"([^"]+)":([^\n]+)};', re.DOTALL).findall(response["data"])[0]
            self.js_data["op"] = re.compile(var + "([\+|\-|\*|\/])=([^;]+)", re.MULTILINE).findall(response["data"])
            self.js_data["wait"] = int(re.compile("\}, ([\d]+)\);", re.MULTILINE).findall(response["data"])[0]) / 1000
        except:
            logger.debug("Metodo #1 (javascript): NO disponible")
            self.js_data = {}

        if "refresh" in response["headers"]:
            try:
                self.header_data["wait"] = int(response["headers"]["refresh"].split(";")[0])
                self.header_data["auth_url"] = response["headers"]["refresh"].split("=")[1].split("?")[0]
                self.header_data["params"] = {}
                self.header_data["params"]["pass"] = response["headers"]["refresh"].split("=")[2]
            except:
                logger.debug("Metodo #2 (headers): NO disponible")
                self.header_data = {}
				
#=====================================================================================================================================

    @property
    def wait_time(self):
        if self.js_data.get("wait", 0):
            return self.js_data["wait"]
        else:
            return self.header_data.get("wait", 0)

#=====================================================================================================================================
			
    @property
    def is_cloudflare(self):
        return self.header_data.get("wait", 0) > 0 or self.js_data.get("wait", 0) > 0
		
#=====================================================================================================================================

    def get_url(self):
        if self.js_data.get("wait", 0):
            jschl_answer = self.decode(self.js_data["value"])

            for op, v in self.js_data["op"]:
                if op == '+':
                    jschl_answer = jschl_answer + self.decode(v)
                elif op == '-':
                    jschl_answer = jschl_answer - self.decode(v)
                elif op == '*':
                    jschl_answer = jschl_answer * self.decode(v)
                elif op == '/':
                    jschl_answer = jschl_answer / self.decode(v)

            self.js_data["params"]["jschl_answer"] = round(jschl_answer, 10) + len(self.domain)

            response = "%s://%s%s?%s" % (
            self.protocol, self.domain, self.js_data["auth_url"], urllib.urlencode(self.js_data["params"]))

            time.sleep(self.js_data["wait"])

            return response

        if self.header_data.get("wait", 0):
            response = "%s://%s%s?%s" % (
            self.protocol, self.domain, self.header_data["auth_url"], urllib.urlencode(self.header_data["params"]))

            time.sleep(self.header_data["wait"])

            return response

#=====================================================================================================================================
			
    def decode(self, data):
        data = re.sub("\!\+\[\]", "1", data)
        data = re.sub("\!\!\[\]", "1", data)
        data = re.sub("\[\]", "0", data)
        
        pos = data.find("/")
        numerador = data[:pos]
        denominador = data[pos+1:]
        
        aux = re.compile('\(([0-9\+]+)\)').findall(numerador)
        num1 = ""
        for n in aux:
            num1 += str(eval(n))

        aux = re.compile('\(([0-9\+]+)\)').findall(denominador)
        num2 = ""
        for n in aux:
            num2 += str(eval(n))

        return Decimal(Decimal(num1) / Decimal(num2)).quantize(Decimal('.0000000000000001'))


