from enum import Enum
from typing import AsyncGenerator, List, Optional

from agno.team import Team
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from teams.operator import TeamType, get_available_teams, get_team
from utils.log import logger

######################################################
## Router for the Agent Interface
######################################################

teams_router = APIRouter(prefix="/teams", tags=["Teams"])


class Model(str, Enum):
    gpt_4o = "gpt-4o"
    o3_mini = "o3-mini"


@teams_router.get("", response_model=List[str])
async def list_teams():
    """
    Returns a list of all available team IDs.

    Returns:
        List[str]: List of team identifiers
    """
    return get_available_teams()


async def chat_response_streamer(team: Team, message: str) -> AsyncGenerator:
    """
    Stream team responses chunk by chunk.

    Args:
        team: The team instance to interact with
        message: User message to process

    Yields:
        Text chunks from the team response
    """
    run_response = await team.arun(message, stream=True)
    async for chunk in run_response:
        # chunk.content only contains the text response from the Agent.
        # For advanced use cases, we should yield the entire chunk
        # that contains the tool calls and intermediate steps.
        yield chunk.content


class RunRequest(BaseModel):
    """Request model for an running an team"""

    message: str
    stream: bool = True
    model: Model = Model.gpt_4o
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@teams_router.post("/{team_id}/runs", status_code=status.HTTP_200_OK)
async def run_team(team_id: TeamType, body: RunRequest):
    """
    Sends a message to a specific team and returns the response.

    Args:
        team_id: The ID of the team to interact with
        body: Request parameters including the message

    Returns:
        Either a streaming response or the complete team response
    """
    logger.debug(f"RunRequest: {body}")

    try:
        team: Team = get_team(
            model_id=body.model.value,
            team_id=team_id,
            user_id=body.user_id,
            session_id=body.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team not found: {str(e)}")

    if body.stream:
        return StreamingResponse(
            chat_response_streamer(team, body.message),
            media_type="text/event-stream",
        )
    else:
        response = await team.arun(body.message, stream=False)
        # response.content only contains the text response from the Agent.
        # For advanced use cases, we should yield the entire response
        # that contains the tool calls and intermediate steps.
        return response.content
