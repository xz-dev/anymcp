
__tool_name__ = "Weather Fetcher"
__description__ = "Fetches weather information"
__version__ = "1.0.0"

def execute(city: str, units: str = "metric") -> dict:
    return {"city": city, "temperature": 20, "units": units}


if __name__ == "__main__":
    import json
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('params', nargs='?', default='{}')
    args = parser.parse_args()
    
    params = json.loads(args.params)
    result = execute(**params) if params else execute()
    
    if isinstance(result, (dict, list)):
        print(json.dumps(result))
    else:
        print(result)
