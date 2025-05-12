from os import getenv

from agno.playground import Playground

from agents.sage import get_sage
from agents.scholar import get_scholar
from teams.finance_researcher import get_finance_researcher_team
from teams.multi_language import get_multi_language_team
from workflows.blog_post_generator import get_blog_post_generator
from workflows.investment_report_generator import get_investment_report_generator
from workspace.dev_resources import dev_fastapi

######################################################
## Router for the Playground Interface
######################################################

# Agents
sage_agent = get_sage(debug_mode=True)
scholar_agent = get_scholar(debug_mode=True)

# Teams
finance_researcher_team = get_finance_researcher_team(debug_mode=True)
multi_language_team = get_multi_language_team(debug_mode=True)

# Workflows
blog_post_generator = get_blog_post_generator(debug_mode=True)
investment_report_generator = get_investment_report_generator(debug_mode=True)

# Create a playground instance
playground = Playground(
    agents=[sage_agent, scholar_agent],
    teams=[finance_researcher_team, multi_language_team],
    workflows=[blog_post_generator, investment_report_generator],
)

# Register the endpoint where playground routes are served with agno.com
if getenv("RUNTIME_ENV") == "dev":
    playground.create_endpoint(f"http://localhost:{dev_fastapi.host_port}")

playground_router = playground.get_async_router()
