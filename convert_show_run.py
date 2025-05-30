# Cisco Sample Code License 1.1
# flopach 2025

# ================== IMPORTS ==================
from smolagents.agents import CodeAgent, ToolCallingAgent, ManagedAgent
from smolagents import tool, LiteLLMModel

# ================== TELEMETRY ==================
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

register()
SmolagentsInstrumentor().instrument()

# ================== TOOL CALLS ==================
@tool
def get_username_password_for_device(ip_address:str) -> str:
    """
    Returns the username and password separated by a comma for the given ip address or hostname.

    Args:
        ip_address: The IP address or hostname of the device

    Returns:
        str: A string with the username and password separated by a comma.
    """
    import json
    
    with open("../hosts.json", 'r') as file:
        devices = json.load(file)
        return f"{devices[ip_address]['username']},{devices[ip_address]['password']}"

@tool
def show_running_configuration(host:str,username:str,password:str,device_type:str = "cisco_ios",) -> str:
    """
    Returns the running configuration from the device with the given host, username, password, and device type.

    Args:
        host: The IP address or hostname of the device
        username: The username for the device
        password: The password for the device
        device_type: The device type for the device

    Returns:
        str: The running configuration of the device.
    """
    from netmiko import ConnectHandler

    device = {
        'ip': host,
        'username': username,
        'password': password,
        'device_type': device_type
    }

    connection = ConnectHandler(**device)

    running_config_output = connection.send_command('show running-config')

    return running_config_output

# ================== AGENTS + MODELS ==================

model = LiteLLMModel(model_id="ollama/qwen2.5",
                     num_ctx=8192)

device_agent = CodeAgent(tools=[get_username_password_for_device,
                         show_running_configuration],
                  model=model,
                  additional_authorized_imports=['ncclient', 'netmiko','requests','paramiko','io'],
                 )
# give the sandboxed Python interpreter access to read/write files outside (use with caution!)
device_agent.python_executor.additional_functions["open"] = open

# ================== TASKS ==================

# Routing Table Summary as Markdown
device_agent.run("""Export the running configuration on the Cisco device 10.10.20.48 to a txt file, but remove all the exclamation marks. You will at first need the username and password for the device.""")
