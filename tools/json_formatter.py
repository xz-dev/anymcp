
import json

def execute(data: str, indent: int = 2) -> str:
    parsed = json.loads(data)
    return json.dumps(parsed, indent=indent)


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
