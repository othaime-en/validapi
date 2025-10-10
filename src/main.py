import click
import sys
from pathlib import Path
from typing import Optional
import json
from validation_engine import ValidationEngine
from reporters.html_reporter import HTMLReporter, JSONReporter
from parsers.openapi_parser import OpenAPIParser

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """API Response Validator - Validate APIs against OpenAPI specifications"""
    pass

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--base-url', '-u', help='Base URL for API (overrides spec)')
@click.option('--test-data', '-t', type=click.Path(exists=True), help='JSON file with test data')
@click.option('--output-format', '-f', type=click.Choice(['html', 'json', 'console']), 
              default='html', help='Output format for results')
@click.option('--output-dir', '-o', default='reports', help='Output directory for reports')
@click.option('--endpoint', '-e', help='Test specific endpoint (format: METHOD /path)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def validate(spec_file: str, base_url: Optional[str], test_data: Optional[str], 
            output_format: str, output_dir: str, endpoint: Optional[str], verbose: bool):
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
        
        summary = engine.get_summary()
        
        _display_console_results(results, summary, verbose)
        
        if output_format in ['html', 'json']:
            spec_info = {
                'spec_file': spec_file,
                'base_url': base_url or engine.base_url,
                'openapi_version': engine.parser.spec.get('openapi', 'unknown'),
                'title': engine.parser.spec.get('info', {}).get('title', 'Unknown API'),
                'version': engine.parser.spec.get('info', {}).get('version', 'unknown')
            }
            
            if output_format == 'html':
                reporter = HTMLReporter(output_dir)
                report_path = reporter.generate_report(results, summary, spec_info)
                click.echo(f"[+] HTML report generated: {report_path}")
            else:
                reporter = JSONReporter(output_dir)
                report_path = reporter.generate_report(results, summary, spec_info)
                click.echo(f"[+] JSON report generated: {report_path}")
        
        if summary['failed'] > 0:
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"[ERROR] Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def _display_console_results(results, summary, verbose):
    """Display results in console"""
    click.echo("\n" + "="*60)
    click.echo("[*] VALIDATION RESULTS")
    click.echo("="*60)
    
    click.echo(f"[*] Total endpoints tested: {summary['total']}")
    click.echo(f"[+] Passed: {summary['passed']}")
    click.echo(f"[!] Failed: {summary['failed']}")
    click.echo(f"[*] Success rate: {summary['success_rate']:.1f}%")
    if 'average_response_time' in summary:
        click.echo(f"[*] Average response time: {summary['average_response_time']*1000:.0f}ms")
    
    failed_results = [r for r in results if not r['success']]
    if failed_results:
        click.echo(f"\n[!] FAILED TESTS ({len(failed_results)}):")
        for result in failed_results:
            click.echo(f"   {result['method']} {result['path']}")
            if 'error' in result:
                click.echo(f"      Error: {result['error']}")
            elif verbose and 'validations' in result:
                for val_type, val_result in result['validations'].items():
                    if not val_result['valid']:
                        click.echo(f"      {val_type}: {val_result['message']}")
                        if val_result['errors']:
                            for error in val_result['errors'][:2]:
                                click.echo(f"        - {error['message']}")
    
    if verbose:
        click.echo(f"\n[+] PASSED TESTS ({summary['passed']}):")
        passed_results = [r for r in results if r['success']]
        for result in passed_results:
            response_time = f" ({result['response_time']*1000:.0f}ms)" if 'response_time' in result else ""
            click.echo(f"   {result['method']} {result['path']}{response_time}")

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
def analyze(spec_file: str):
    """Analyze OpenAPI specification and show endpoint summary"""
    try:
        parser = OpenAPIParser(spec_file)
        endpoints = parser.get_all_endpoints()
        
        click.echo(f"[+] Analyzing specification: {spec_file}")
        click.echo(f"[+] Base URL: {parser.base_url}")
        
        spec_info = parser.spec.get('info', {})
        click.echo(f"[+] API: {spec_info.get('title', 'Unknown')} v{spec_info.get('version', 'unknown')}")
        
        if spec_info.get('description'):
            click.echo(f"[*] Description: {spec_info['description']}")
        
        click.echo(f"\n[*] Found {len(endpoints)} endpoints:")
        
        by_tags = {}
        for endpoint in endpoints:
            tags = endpoint.get('tags', ['Untagged'])
            for tag in tags:
                if tag not in by_tags:
                    by_tags[tag] = []
                by_tags[tag].append(endpoint)
        
        for tag, tag_endpoints in by_tags.items():
            click.echo(f"\n[*] {tag} ({len(tag_endpoints)} endpoints):")
            for endpoint in tag_endpoints:
                click.echo(f"   {endpoint['method']} {endpoint['path']}")
                if endpoint.get('summary'):
                    click.echo(f"      {endpoint['summary']}")
        
        errors = parser.validate_spec()
        if errors:
            click.echo(f"\n[!] Specification issues:")
            for error in errors:
                click.echo(f"   - {error}")
        else:
            click.echo(f"\n[+] Specification is valid")
            
    except Exception as e:
        click.echo(f"[ERROR] Error analyzing specification: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()