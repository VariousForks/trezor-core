from common import *

from trezor.crypto import random
from trezor.pin import pin_to_int

from trezor import config

PINAPP = 0x00
PINKEY = 0x00


def random_entry():
    while True:
        appid, key = 1 + random.uniform(255), random.uniform(256)
        if appid != PINAPP or key != PINKEY:
            break
    return appid, key


class TestConfig(unittest.TestCase):

    def test_init(self):
        config.init()
        config.init()
        config.init()

    def test_wipe(self):
        config.init()
        config.wipe()
        self.assertEqual(config.unlock(pin_to_int(''), None), True)
        config.set(1, 1, b'hello')
        config.set(1, 2, b'world')
        v0 = config.get(1, 1)
        v1 = config.get(1, 2)
        self.assertEqual(v0, b'hello')
        self.assertEqual(v1, b'world')
        config.wipe()
        v0 = config.get(1, 1)
        v1 = config.get(1, 2)
        self.assertEqual(v0, bytes())
        self.assertEqual(v1, bytes())

    def test_lock(self):
        for _ in range(128):
            config.init()
            config.wipe()
            self.assertEqual(config.unlock(pin_to_int(''), None), True)
            appid, key = random_entry()
            value = random.bytes(16)
            config.set(appid, key, value)
            config.init()
            self.assertEqual(config.get(appid, key), bytes())
            with self.assertRaises(RuntimeError):
                config.set(appid, key, bytes())
        config.init()
        config.wipe()
        self.assertEqual(config.change_pin(pin_to_int(''), pin_to_int('000'), None), False)

    def test_change_pin(self):
        config.init()
        config.wipe()
        self.assertEqual(config.unlock(pin_to_int(''), None), True)
        with self.assertRaises(RuntimeError):
            config.set(PINAPP, PINKEY, b'value')
        self.assertEqual(config.change_pin(pin_to_int('000'), pin_to_int('666'), None), False)
        self.assertEqual(config.change_pin(pin_to_int(''), pin_to_int('000'), None), True)
        self.assertEqual(config.get(PINAPP, PINKEY), bytes())
        config.set(1, 1, b'value')
        config.init()
        self.assertEqual(config.unlock(pin_to_int('000'), None), True)
        config.change_pin(pin_to_int('000'), pin_to_int(''), None)
        config.init()
        self.assertEqual(config.unlock(pin_to_int('000'), None), False)
        self.assertEqual(config.unlock(pin_to_int(''), None), True)
        self.assertEqual(config.get(1, 1), b'value')

    def test_set_get(self):
        config.init()
        config.wipe()
        self.assertEqual(config.unlock(pin_to_int(''), None), True)
        for _ in range(32):
            appid, key = random_entry()
            value = random.bytes(128)
            config.set(appid, key, value)
            value2 = config.get(appid, key)
            self.assertEqual(value, value2)

    def test_compact(self):
        config.init()
        config.wipe()
        self.assertEqual(config.unlock(pin_to_int(''), None), True)
        appid, key = 1, 1
        for _ in range(259):
            value = random.bytes(259)
            config.set(appid, key, value)
        value2 = config.get(appid, key)
        self.assertEqual(value, value2)

    def test_get_default(self):
        config.init()
        config.wipe()
        self.assertEqual(config.unlock(pin_to_int(''), None), True)
        for _ in range(128):
            appid, key = random_entry()
            value = config.get(appid, key)
            self.assertEqual(value, bytes())


if __name__ == '__main__':
    unittest.main()
