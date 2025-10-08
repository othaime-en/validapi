import click

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """API Response Validator - Validate APIs against OpenAPI specifications"""
    pass

@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
def validate(spec_file: str):
    """Validate API endpoints against OpenAPI specification"""
    click.echo(f"[*] Starting API validation for {spec_file}")

if __name__ == '__main__':
    cli()