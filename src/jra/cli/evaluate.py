"""CLI evaluate command implementation.

Evaluates a single Jira ticket against process guidelines.
"""

import json
import sys
from pathlib import Path
from typing import Union

import click

from jra.evaluators.compliance import ComplianceEvaluator
from jra.formatters.human_formatter import HumanFormatter
from jra.formatters.json_formatter import JSONFormatter
from jra.parsers.jira_parser import JiraParser
from jra.parsers.markdown_parser import MarkdownParser
from jra.utils.exceptions import EvaluationError, JiraParseError, GuidelineParseError
from jra.utils.logging import setup_logging
from jra.utils.timing import timed_operation, format_duration


logger = setup_logging()


@click.command()
@click.argument("ticket_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--guidelines",
    "-g",
    "guidelines_file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Process guidelines markdown file",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "human"], case_sensitive=False),
    default="human",
    help="Output format (default: human)",
)
@click.option(
    "--timing",
    "-t",
    "show_timing",
    is_flag=True,
    default=False,
    help="Show timing information",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@click.pass_context
def evaluate(
    ctx: click.Context,
    ticket_file: Path,
    guidelines_file: Path,
    output_format: str,
    show_timing: bool,
    debug: bool,
) -> None:
    """Evaluate a Jira ticket against process guidelines.

    TICKET_FILE is the path to the Jira ticket JSON file.

    \b
    Examples:
        jra evaluate ticket.json --guidelines team-guidelines.md
        jra evaluate ticket.json -g guidelines.md --format json
        jra evaluate ticket.json -g guidelines.md --timing
    """
    try:
        with timed_operation("Total evaluation") as timer:
            # Parse Jira ticket
            logger.info(f"Parsing Jira ticket from {ticket_file}")
            with timed_operation("Jira parsing") as jira_timer:
                try:
                    with open(ticket_file) as f:
                        ticket_data = json.load(f)

                    jira_parser = JiraParser()
                    issue = jira_parser.parse(ticket_data)

                    logger.debug(f"Parsed issue: {issue.key} ({issue.get_issue_type_name()})")

                except json.JSONDecodeError as e:
                    raise click.ClickException(f"Invalid JSON in ticket file: {e}")
                except JiraParseError as e:
                    raise click.ClickException(f"Failed to parse Jira ticket: {e.message}")

            # Parse guidelines
            logger.info(f"Parsing guidelines from {guidelines_file}")
            with timed_operation("Guidelines parsing") as guidelines_timer:
                try:
                    guidelines_content = guidelines_file.read_text(encoding="utf-8")

                    markdown_parser = MarkdownParser()
                    guidelines = markdown_parser.parse(guidelines_content)

                    logger.debug(
                        f"Parsed guidelines: {len(guidelines.required_fields)} required fields, "
                        f"{len(guidelines.field_validations)} validations"
                    )

                except GuidelineParseError as e:
                    raise click.ClickException(f"Failed to parse guidelines: {e.message}")

            # Evaluate
            logger.info("Evaluating compliance")
            with timed_operation("Compliance evaluation") as eval_timer:
                try:
                    evaluator = ComplianceEvaluator()
                    report = evaluator.evaluate(issue, guidelines)

                    logger.debug(
                        f"Evaluation complete: {report.compliance.total_violations} violations, "
                        f"score: {report.compliance.compliance_score}"
                    )

                except EvaluationError as e:
                    raise click.ClickException(f"Evaluation failed: {e.message}")

            # Format output
            logger.info(f"Formatting output as {output_format}")
            with timed_operation("Output formatting") as format_timer:
                formatter: Union[JSONFormatter, HumanFormatter]
                if output_format.lower() == "json":
                    formatter = JSONFormatter(indent=2)
                else:
                    formatter = HumanFormatter(use_color=sys.stdout.isatty())

                output = formatter.format(report)

        # Display output
        click.echo(output)

        # Show timing if requested
        if show_timing:
            click.echo("\n" + "=" * 70, err=True)
            click.echo("Timing Information:", err=True)
            click.echo(f"  Jira parsing:      {format_duration(jira_timer.elapsed)}", err=True)
            click.echo(
                f"  Guidelines parsing: {format_duration(guidelines_timer.elapsed)}", err=True
            )
            click.echo(f"  Evaluation:        {format_duration(eval_timer.elapsed)}", err=True)
            click.echo(f"  Formatting:        {format_duration(format_timer.elapsed)}", err=True)
            click.echo(f"  Total:             {format_duration(timer.elapsed)}", err=True)
            click.echo("=" * 70, err=True)

        # Exit with appropriate code
        if report.is_fail():
            sys.exit(2)  # Non-compliant

    except click.ClickException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during evaluation")
        raise click.ClickException(f"Unexpected error: {str(e)}")
