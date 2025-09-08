
import time
def execute(duration: int = 5) -> str:
    """A slow tool for testing timeouts"""
    time.sleep(duration)
    return "Completed"


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
