from memory import activity
from tools import apps, files, reminders, shell, system, web


def make_tool(name: str, description: str, properties: dict = None, required: list = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
            },
        },
    }


TOOLS = [
    make_tool("open_app", "Open an application on the laptop (e.g. chrome, notepad, vscode, spotify, calculator).",
              {"name": {"type": "string"}}, ["name"]),
    make_tool("open_website", "Open a website URL in the default browser.",
              {"url": {"type": "string"}}, ["url"]),
    make_tool("web_search", "Search Google for a query in the browser.",
              {"query": {"type": "string"}}, ["query"]),
    make_tool("get_time", "Get the current date and time."),
    make_tool("find_files", "Find files by name in the user's Documents, Downloads and Desktop folders.",
              {"query": {"type": "string"}}, ["query"]),
    make_tool("open_file", "Open a file by its full path (only inside allowed folders).",
              {"path": {"type": "string"}}, ["path"]),
    make_tool("take_screenshot", "Take a screenshot of the screen and save it."),
    make_tool("battery_status", "Get battery percentage and charging state."),
    make_tool("set_volume", "Change system volume.",
              {"action": {"type": "string", "enum": ["up", "down", "mute"]},
               "steps": {"type": "integer", "description": "Number of steps, default 5"}},
              ["action"]),
    make_tool("set_brightness", "Set screen brightness from 0 to 100.",
              {"level": {"type": "integer"}}, ["level"]),
    make_tool("set_reminder", "Set a reminder. Convert the time to minutes from now.",
              {"text": {"type": "string"}, "minutes": {"type": "number"}}, ["text", "minutes"]),
    make_tool("list_reminders", "List pending reminders."),
    make_tool("run_shell", "Run a Windows shell command. Asks the user for confirmation. Use only if no other tool fits.",
              {"command": {"type": "string"}}, ["command"]),
]

HANDLERS = {
    "open_app": lambda a: apps.open_app(a["name"]),
    "open_website": lambda a: web.open_website(a["url"]),
    "web_search": lambda a: web.web_search(a["query"]),
    "get_time": lambda a: system.get_time(),
    "find_files": lambda a: files.find_files(a["query"]),
    "open_file": lambda a: files.open_file(a["path"]),
    "take_screenshot": lambda a: system.take_screenshot(),
    "battery_status": lambda a: system.battery_status(),
    "set_volume": lambda a: system.set_volume(a["action"], a.get("steps", 5)),
    "set_brightness": lambda a: system.set_brightness(a["level"]),
    "set_reminder": lambda a: reminders.set_reminder(a["text"], a["minutes"]),
    "list_reminders": lambda a: reminders.list_reminders(),
    "run_shell": lambda a: shell.run_shell(a["command"]),
}


def run(name: str, args: dict) -> str:
    """Tool chalata hai, errors pakadta hai, aur har call tool_log mein likhta hai."""
    handler = HANDLERS.get(name)
    if handler is None:
        return f"Unknown tool: {name}"
    try:
        result = str(handler(args))
    except KeyError as e:
        result = f"Missing argument: {e}"
    except Exception as e:
        result = f"Tool error: {e}"
    activity.log_tool(name, args, result)
    return result