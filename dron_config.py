import json

CONFIG_PATH = "config.json"

def _save_config(ip_address, port,
                 config_path=CONFIG_PATH):
    """
    Сохраняет IP-адрес и порт в файле конфигурации.

    Параметры:
    - ip_address: str, IP-адрес сервера.
    - port: int, порт сервера.
    """
    with open(config_path, "w") as f:
        config = {"ip_address": ip_address, "port": port}
        json.dump(config, f)

def _load_config(config_path=CONFIG_PATH):
    """
    Загружает IP-адрес и порт из файла конфигурации.

    Возвращает:
    - tuple, содержащий IP-адрес и порт сервера.
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            ip_address = str(config.get("ip_address"))
            port = config.get("port")
            if ip_address and port:
                return ip_address, int(port)
            else:
                return None, None
    except (FileNotFoundError, json.JSONDecodeError):
        return None, None


class DroneConfig:
    def __init__(self, 
                 config_path=CONFIG_PATH) -> None:
        self._config_path = config_path
    
    @property
    def ip(self)->str:
        ip, _ = _load_config(self._config_path)
        return (ip or '192.168.10.1')
    
    @ip.setter
    def ip(self, ip:str)->None:
        if not isinstance(ip, str):
            raise TypeError(ip)
        port = self.port
        _save_config(ip, port, self._config_path)
    
    @property
    def port(self)->int:
        _, port = _load_config(self._config_path)
        return port or 8889

    @port.setter
    def port(self, val:int):
        port = int(val)
        ip = self.ip
        _save_config(ip, port, self._config_path)


    