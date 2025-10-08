import click
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from validation_engine import ValidationEngine

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """API Response Validator - Validate APIs against OpenAPI specifications"""
    pass

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--base-url', '-u', help='Base URL for API (overrides spec)')
@click.option('--endpoint', '-e', help='Test specific endpoint (format: METHOD /path)')
def validate(spec_file: str, base_url: str, endpoint: str):
    """Validate API endpoints against OpenAPI specification"""
    try:
        engine = ValidationEngine(spec_file, base_url)
        
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
            result = engine.validate_endpoint(path, method)
            click.echo(f"[*] Result: {'Success' if result['success'] else 'Failed'}")
        
    except Exception as e:
        click.echo(f"[ERROR] Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()