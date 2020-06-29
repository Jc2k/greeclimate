import logging

import greeclimate.network_helper as nethelper


class GreeClimate:
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger('gree_climate')
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        """ FOR NOW - We'll remove this a bit later on """
        fh = logging.FileHandler('gree_climate.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    async def search_devices(self):
        """ Sends a discovery broadcast packet on each network interface to
            locate Gree units on the network
        """
        self._logger.info("Starting Gree device discovery process")

        devices = await nethelper.search_devices()
        for d in devices:
            self._logger.info("Found %s", str(d))

        return devices
