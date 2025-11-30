"""Main CLI application entry point."""

import click

from jra import __version__
from jra.utils.logging import setup_logging


@click.group()
@click.version_option(version=__version__, prog_name="jra")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """Jira Review Agent - Evaluate Jira tickets against process guidelines.
    
    jra is a CLI tool that evaluates Jira issue tickets against your team's
    process guidelines, identifying violations and providing quality assessments.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(level=log_level)
    
    # Store debug flag in context
    ctx.obj["debug"] = debug


@cli.command()
def version() -> None:
    """Show version information."""
    click.echo(f"jra version {__version__}")


if __name__ == "__main__":
    cli()
