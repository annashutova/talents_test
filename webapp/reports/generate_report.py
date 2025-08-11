from pathlib import Path

from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader


TEMPLATE_PATH = Path(__file__).parent.resolve()


def generate_personality_report(report_data: dict) -> bytes:
    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template('trait_report_template.html')

    rendered_html = template.render(report_data)

    return HTML(string=rendered_html).write_pdf()
