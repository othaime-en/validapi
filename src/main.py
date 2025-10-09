import click
import sys
from pathlib import Path
from typing import Optional
import json
from validation_engine import ValidationEngine

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """API Response Validator - Validate APIs against OpenAPI specifications"""
    pass

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--base-url', '-u', help='Base URL for API (overrides spec)')
@click.option('--test-data', '-t', type=click.Path(exists=True), help='JSON file with test data')
@click.option('--endpoint', '-e', help='Test specific endpoint (format: METHOD /path)')
def validate(spec_file: str, base_url: Optional[str], test_data: Optional[str], endpoint: Optional[str]):
    """Validate API endpoints against OpenAPI specification"""
    try:
        engine = ValidationEngine(spec_file, base_url)
        
        test_data_dict = {}
        if test_data:
            with open(test_data, 'r') as f:
                test_data_dict = json.load(f)
        
        click.echo(f"[*] Starting API validation...")
        click.echo(f"[+] Spec file: {spec_file}")
        if base_url:
            click.echo(f"[+] Base URL: {base_url}")
        
        if endpoint:
            parts = endpoint.strip().split(' ', 1)
            if len(parts) != 2:
                click.echo("[ERROR] Endpoint format should be: METHOD /path (e.g., 'GET /users')", err=True)
                sys.exit(1)
            
            method, path = parts
            click.echo(f"[>] Testing endpoint: {method} {path}")
            endpoint_test_data = test_data_dict.get(path, {}).get(method.lower()) if test_data_dict else None
            result = engine.validate_endpoint(path, method, endpoint_test_data)
            results = [result]
        else:
            click.echo("[*] Testing all endpoints...")
            results = engine.validate_all_endpoints(test_data_dict)
        
        click.echo(f"[*] Total endpoints tested: {len(results)}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()