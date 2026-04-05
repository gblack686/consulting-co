"""
Voiceflow Scoping Agent SDK - Python Implementation
Integrates Voiceflow agents with Google Meet for technical project scoping
"""

import asyncio
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import httpx


@dataclass
class ScopingData:
    """Collected scoping information"""
    project_name: Optional[str] = None
    client: Optional[str] = None
    timeline: Optional[str] = None
    budget: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    integrations: Optional[List[str]] = None
    mvp_features: Optional[List[str]] = None
    nice_to_have_features: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    success_metrics: Optional[List[str]] = None
    team_size: Optional[str] = None
    existing_infrastructure: Optional[str] = None
    technical_debt: Optional[str] = None
    third_party_dependencies: Optional[str] = None
    launch_date: Optional[str] = None
    post_launch_support: Optional[str] = None
    stakeholder_signoff: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        required_fields = [
            'project_name', 'client', 'timeline', 'budget',
            'tech_stack', 'mvp_features', 'success_metrics', 'launch_date'
        ]
        return all(getattr(self, field) is not None for field in required_fields)


@dataclass
class VoiceflowState:
    """Voiceflow session state"""
    variables: Dict[str, Any]
    stack: List[Any] = field(default_factory=list)


@dataclass
class DialogResponse:
    """Response from Dialog Manager API"""
    state: VoiceflowState
    trace: List[Dict[str, Any]]


class VoiceflowScoper:
    """
    Manages conversations with Voiceflow scoping agents
    """

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        base_url: str = "https://general-runtime.voiceflow.com"
    ):
        """
        Initialize Voiceflow Scoper

        Args:
            api_key: Voiceflow API key
            agent_id: Voiceflow agent ID
            base_url: Voiceflow API base URL
        """
        if not api_key or not agent_id:
            raise ValueError("API Key and Agent ID are required")

        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = base_url
        self.session_data: Dict[str, VoiceflowState] = {}

    async def initialize_session(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DialogResponse:
        """
        Initialize a new scoping session

        Args:
            user_id: Unique identifier for the user
            metadata: Optional metadata (meeting ID, participant name, etc.)

        Returns:
            DialogResponse from agent initialization
        """
        payload = {"action": {"type": "launch"}}
        if metadata:
            payload["metadata"] = metadata

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/state/user/{user_id}/interact",
                    json=payload,
                    headers={"Authorization": self.api_key},
                    params={"projectID": self.agent_id}
                )
                response.raise_for_status()

                data = response.json()
                self.session_data[user_id] = VoiceflowState(
                    variables=data.get("state", {}).get("variables", {}),
                    stack=data.get("state", {}).get("stack", [])
                )

                return DialogResponse(
                    state=self.session_data[user_id],
                    trace=data.get("trace", [])
                )
            except httpx.HTTPError as e:
                raise RuntimeError(f"Failed to initialize session for user {user_id}: {e}")

    async def send_message(
        self,
        user_id: str,
        user_message: str
    ) -> DialogResponse:
        """
        Send a message to the scoping agent

        Args:
            user_id: Session user ID
            user_message: User's message or answer

        Returns:
            DialogResponse from agent
        """
        payload = {
            "action": {
                "type": "text",
                "payload": user_message
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/state/user/{user_id}/interact",
                    json=payload,
                    headers={"Authorization": self.api_key},
                    params={"projectID": self.agent_id}
                )
                response.raise_for_status()

                data = response.json()
                self.session_data[user_id] = VoiceflowState(
                    variables=data.get("state", {}).get("variables", {}),
                    stack=data.get("state", {}).get("stack", [])
                )

                return DialogResponse(
                    state=self.session_data[user_id],
                    trace=data.get("trace", [])
                )
            except httpx.HTTPError as e:
                raise RuntimeError(f"Failed to send message for user {user_id}: {e}")

    async def get_scoping_data(self, user_id: str) -> ScopingData:
        """
        Get current scoping data collected so far

        Args:
            user_id: Session user ID

        Returns:
            ScopingData object with collected information
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/state/user/{user_id}",
                    headers={"Authorization": self.api_key},
                    params={"projectID": self.agent_id}
                )
                response.raise_for_status()

                data = response.json()
                state = data.get("state", {})
                variables = state.get("variables", {})

                self.session_data[user_id] = VoiceflowState(
                    variables=variables,
                    stack=state.get("stack", [])
                )

                return self._extract_scoping_data(variables)
            except httpx.HTTPError as e:
                raise RuntimeError(f"Failed to get scoping data for user {user_id}: {e}")

    async def is_complete(self, user_id: str) -> bool:
        """
        Check if scoping conversation is complete

        Args:
            user_id: Session user ID

        Returns:
            True if all required data is collected
        """
        try:
            data = await self.get_scoping_data(user_id)
            return data.is_complete()
        except Exception as e:
            print(f"Failed to check completion for user {user_id}: {e}")
            return False

    def get_session_state(self, user_id: str) -> Optional[VoiceflowState]:
        """
        Get agent state for session

        Args:
            user_id: Session user ID

        Returns:
            VoiceflowState if session exists
        """
        return self.session_data.get(user_id)

    def clear_session(self, user_id: str) -> None:
        """
        Clear session data (e.g., on meeting end)

        Args:
            user_id: Session user ID
        """
        self.session_data.pop(user_id, None)

    def _extract_scoping_data(self, variables: Dict[str, Any]) -> ScopingData:
        """Extract and normalize scoping data from Voiceflow variables"""
        mapping = {
            "project_name": "project_name",
            "client_name": "client",
            "timeline": "timeline",
            "budget": "budget",
            "tech_stack": "tech_stack",
            "integrations": "integrations",
            "mvp_features": "mvp_features",
            "nice_to_have_features": "nice_to_have_features",
            "constraints": "constraints",
            "success_metrics": "success_metrics",
            "team_size": "team_size",
            "existing_infrastructure": "existing_infrastructure",
            "technical_debt": "technical_debt",
            "third_party_dependencies": "third_party_dependencies",
            "launch_date": "launch_date",
            "post_launch_support": "post_launch_support",
            "stakeholder_signoff": "stakeholder_signoff"
        }

        data = {}
        for voiceflow_key, data_key in mapping.items():
            if voiceflow_key in variables:
                data[data_key] = variables[voiceflow_key]

        return ScopingData(**data)


class GoogleMeetScopingIntegration:
    """Manages Voiceflow agent integration with Google Meet"""

    def __init__(self, scoper: VoiceflowScoper, meeting_id: str):
        """
        Initialize Google Meet integration

        Args:
            scoper: VoiceflowScoper instance
            meeting_id: Google Meet meeting ID
        """
        self.scoper = scoper
        self.meeting_id = meeting_id
        self.participants: Dict[str, Dict[str, Any]] = {}

    async def register_participant(
        self,
        participant_id: str,
        participant_name: str
    ) -> None:
        """
        Register a participant in the meeting

        Args:
            participant_id: Google Meet participant ID
            participant_name: Display name
        """
        self.participants[participant_id] = {
            "name": participant_name,
            "join_time": datetime.now()
        }

        await self.scoper.initialize_session(
            participant_id,
            {
                "meeting_id": self.meeting_id,
                "participant_name": participant_name,
                "join_time": datetime.now().isoformat()
            }
        )

    async def unregister_participant(self, participant_id: str) -> Optional[ScopingData]:
        """
        Unregister participant and collect final scoping data

        Args:
            participant_id: Google Meet participant ID

        Returns:
            ScopingData if available
        """
        try:
            data = await self.scoper.get_scoping_data(participant_id)
            self.participants.pop(participant_id, None)
            self.scoper.clear_session(participant_id)
            return data
        except Exception as e:
            print(f"Error unregistering participant {participant_id}: {e}")
            return None

    async def process_user_input(
        self,
        participant_id: str,
        user_input: str
    ) -> DialogResponse:
        """
        Process user input during meeting

        Args:
            participant_id: Google Meet participant ID
            user_input: User's message/answer

        Returns:
            DialogResponse from agent
        """
        return await self.scoper.send_message(participant_id, user_input)

    async def get_participant_scoping_data(self, participant_id: str) -> ScopingData:
        """
        Get scoping results for a participant

        Args:
            participant_id: Google Meet participant ID

        Returns:
            ScopingData for participant
        """
        return await self.scoper.get_scoping_data(participant_id)

    async def check_meeting_completion(self) -> Dict[str, Any]:
        """Check if all participants have completed scoping"""
        results = []
        for participant_id in self.participants.keys():
            is_complete = await self.scoper.is_complete(participant_id)
            results.append((participant_id, is_complete))

        completed = [p for p, c in results if c]
        pending = [p for p, c in results if not c]

        return {
            "complete": len(pending) == 0 and len(completed) > 0,
            "completed": completed,
            "pending": pending
        }

    async def export_meeting_results(self) -> Dict[str, Any]:
        """Export meeting scoping results"""
        results = []

        for participant_id, participant_info in self.participants.items():
            try:
                scoping_data = await self.scoper.get_scoping_data(participant_id)
                results.append({
                    "id": participant_id,
                    "name": participant_info["name"],
                    "scoping_data": scoping_data.to_dict()
                })
            except Exception as e:
                print(f"Failed to export data for participant {participant_id}: {e}")

        return {
            "meeting_id": self.meeting_id,
            "timestamp": datetime.now().isoformat(),
            "participants": results
        }

    def get_participants(self) -> List[Dict[str, Any]]:
        """Get list of registered participants"""
        return [
            {
                "id": pid,
                "name": info["name"],
                "join_time": info["join_time"]
            }
            for pid, info in self.participants.items()
        ]


class ScopingDocumentGenerator:
    """Creates structured documents from collected scoping data"""

    @staticmethod
    def generate_markdown(data: ScopingData) -> str:
        """Generate markdown scoping document"""
        template = f"""# Technical Scoping Document

## Project Information
- **Project Name**: {data.project_name or "N/A"}
- **Client**: {data.client or "N/A"}
- **Timeline**: {data.timeline or "N/A"}
- **Budget**: {data.budget or "N/A"}

## Technical Requirements
- **Technology Stack**: {", ".join(data.tech_stack) if data.tech_stack else "N/A"}
- **Integrations**: {", ".join(data.integrations) if data.integrations else "N/A"}

## Scope

### MVP Features
{chr(10).join(f"- {f}" for f in data.mvp_features) if data.mvp_features else "- N/A"}

### Nice-to-Have Features
{chr(10).join(f"- {f}" for f in data.nice_to_have_features) if data.nice_to_have_features else "- N/A"}

## Constraints & Dependencies
{chr(10).join(f"- {c}" for c in data.constraints) if data.constraints else "- N/A"}

## Success Metrics
{chr(10).join(f"- {m}" for m in data.success_metrics) if data.success_metrics else "- N/A"}

---
Generated: {datetime.now().isoformat()}
"""
        return template

    @staticmethod
    def generate_json(data: ScopingData) -> str:
        """Generate JSON scoping report"""
        report = {
            "project_name": data.project_name,
            "client": data.client,
            "timeline": data.timeline,
            "budget": data.budget,
            "technical": {
                "stack": data.tech_stack,
                "integrations": data.integrations
            },
            "scope": {
                "mvp_features": data.mvp_features,
                "nice_to_have_features": data.nice_to_have_features
            },
            "constraints": data.constraints,
            "success_metrics": data.success_metrics,
            "generated_at": datetime.now().isoformat()
        }
        return json.dumps(report, indent=2)


# Example usage
async def main():
    """Example: Run scoping session"""
    scoper = VoiceflowScoper(
        api_key=os.getenv("VOICEFLOW_API_KEY", ""),
        agent_id=os.getenv("VOICEFLOW_AGENT_ID", "")
    )

    # Initialize session
    await scoper.initialize_session("participant_123")

    # Send message
    response = await scoper.send_message("participant_123", "My project")

    # Get scoping data
    data = await scoper.get_scoping_data("participant_123")
    print(f"Scoping Data: {data.to_dict()}")

    # Generate document
    document = ScopingDocumentGenerator.generate_markdown(data)
    print(document)


if __name__ == "__main__":
    asyncio.run(main())
