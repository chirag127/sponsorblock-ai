"""This module contains the FreeProxy class."""
from concurrent.futures import ThreadPoolExecutor
import random

import lxml.html as lh
import requests

from ftr import get_location
from reques import get_url, get_url_with_retry


class FreeProxyException(Exception):
    """Exception class with message as a required parameter"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class FreeProxy:
    """
    FreeProxy class scrapes proxies from <https://www.sslproxies.org/>
    and checks if proxy is working. There is possibility to filter proxies
    by country and acceptable timeout. You can also randomize list
    of proxies from where script would get first working proxy.
    """

    def __init__(
        self,
        country_id=None,
        timeout=0.5,
        rand=False,
        anonym=False,
        elite=False,
        google=None,
        https=False,
    ):
        """
        :param country_id: list of country codes
        :param timeout: acceptable timeout
        :param rand: randomize list of proxies
        :param anonym: anonymous proxy
        :param elite: elite proxy
        :param google: google proxy
        :param https: https proxy
        """
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = "https" if https else "http"

    def get_proxy_list(self):
        """Returns a list of proxies that match the specified parameters."""
        try:
            page = get_url_with_retry("https://www.sslproxies.org")

            if page.ok:

                doc = lh.fromstring(page.content)

                tr_elements = doc.xpath('//*[@id="list"]//tr')
                return [
                    f"{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}"
                    for i in range(1, len(tr_elements))
                    if self.__criteria(tr_elements[i])
                ]

            raise FreeProxyException("Failed to get list of proxies")
        except Exception as error:  # pylint: disable=broad-except
            print(error)
            return []

    def get_proxy_list_from_hidemy(self):
        """Returns a list of proxies that match the specified parameters."""
        try:
            return self._extracted_from_get_proxy_list_from_hidemy_4()
        except Exception as error:  # pylint: disable=broad-except
            return self._extracted_from_get_proxy_list_from_geonode_6(error)

    # TODO Rename this here and in `get_proxy_list_from_hidemy`
    def _extracted_from_get_proxy_list_from_hidemy_4(self):
        timeout = 1000 * self.timeout
        _type = "s" if self.schema == "https" else "hs"

        url = f"https://hidemy.name/en/proxy-list/?maxtime={timeout}&type={_type}"

        page = get_url_with_retry(url)
        doc = lh.fromstring(page.content)

        # above is the html of the table of the hidemy website

        tr_elements = doc.xpath('//div[@class="table_block"]//tr')

        return [
            f"{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}"
            for i in range(1, len(tr_elements))
        ]

    def get_proxy_list_from_geonode(self):
        """Returns a list of proxies that match the specified parameters."""
        try:
            protocols = "https" if self.schema == "https" else "http"

            url = (
                "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1"
                + f"&sort_by=lastChecked&sort_type=desc&speed=fast&protocols={protocols}"
            )

            response = get_url(url)

            if response.ok:
                return [
                    f"{proxy['ip']}:{proxy['port']}"
                    for proxy in response.json()["data"]
                ]

            print("Failed to get list of proxies")
            print(response.json())
            return []

        except Exception as error:  # pylint: disable=broad-except
            return self._extracted_from_get_proxy_list_from_geonode_6(error)

    def _extracted_from_get_proxy_list_from_geonode_6(self, error):
        print("Failed to get list of proxies")
        print(error)
        return []

    def __criteria(self, row_elements):
        """Returns True if proxy matches the specified parameters."""
        country_criteria = (
            row_elements[2].text_content() in self.country_id
            if self.country_id
            else True
        )

        elite_criteria = (
            "elite" in row_elements[4].text_content() if self.elite else True
        )

        anonym_criteria = (
            True
            if (not self.anonym) or self.elite
            else row_elements[4].text_content() == "anonymous"
        )

        switch = {"yes": True, "no": False}
        google_criteria = (
            True
            if self.google is None
            else self.google == switch.get(row_elements[5].text_content())
        )
        return (
            country_criteria and elite_criteria and anonym_criteria and google_criteria
        )

    def get(self):
        """Returns a proxy that matches the specified parameters."""
        proxy_list = self.get_proxy_list()

        proxy_list_from_hidemy = self.get_proxy_list_from_hidemy()

        proxy_list = (
            proxy_list_from_hidemy + proxy_list + self.get_proxy_list_from_geonode()
        )

        if self.random:
            random.shuffle(proxy_list)

        working_proxies = self.get_working_proxies(proxy_list)

        working_proxies = self.get_working_proxies(working_proxies)

        if working_proxies:
            return working_proxies

        if self.country_id is not None:
            self.country_id = None
            return self.get()
        raise FreeProxyException("There are no working proxies at this time.")

    def get_working_proxies(self, working_proxies):
        with ThreadPoolExecutor(max_workers=40) as executor:
            results = executor.map(self.check_if_proxy_is_working, working_proxies)

        working_proxies = [proxy for proxy in results if proxy is not None]

        print(len(working_proxies), "working proxies")
        return working_proxies

    def check_if_proxy_is_working(self, proxy_to_test):
        """Returns proxy if it is working."""
        try:
            response = requests.get(
                """https://sponsor.ajay.app/api/skipSegments/2a77""",
                proxies={"http": proxy_to_test, "https": proxy_to_test},
                timeout=self.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                    + "537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
                },
            )

            if response.ok:
                return proxy_to_test
        except requests.exceptions.RequestException:
            return None


if __name__ == "__main__":
    proxy_addresses = FreeProxy(
        timeout=1,
        https=True,
    ).get()

    print(proxy_addresses)

    get_location(proxy_addresses)
