"""Fetch today's market data."""

from django.core.management.base import BaseCommand, CommandError
from report.models import Position


class Command(BaseCommand):
    """Command to execute."""

    help = "Fetch market data for today"

    def handle(self, *args, **options):
        """Handle the command call."""
        try:
            Position.update_all()
            self.stdout.write(
                self.style.SUCCESS('Successfully fetched market data.')
            )
        except Exception as exc:
            raise CommandError(f'Error fetching market data:\n{exc}')
