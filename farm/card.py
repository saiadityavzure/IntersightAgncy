# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill)
from config.config import INTERSIGHT_AGENT_HOST, INTERSIGHT_AGENT_PORT

# AGENT_SKILL = AgentSkill(
#     id="estimate_flavor",
#     name="Estimate Flavor Profile",
#     description="Analyzes a natural language prompt and returns the expected flavor profile for a coffee-growing region and/or season.",
#     tags=["coffee", "flavor", "farm"],
#     examples=[
#         "What flavors can I expect from coffee in Huila during harvest?",
#         "Describe the taste of beans grown in Sidamo in the dry season",
#         "How does Yirgacheffe coffee taste?"
#     ]
# )

AGENT_SKILL = AgentSkill(
    id="estimate_intersight_profile",
    name="Estimate Intersight Profile",
    description="Analyzes a natural language prompt and returns the expected configuration or operational profile of Cisco Intersight resources such as server profiles, domain profiles, and policies.",
    tags=["intersight", "server", "profile", "policy", "configuration"],
    examples=[
        "What configuration is applied to the server profile template VZURE_ESXI?",
        "Describe the policies attached to the domain profile PROD_FABRIC_A.",
        "Which firmware version is linked to the UCSX-210C-M6 servers?",
        "Show me the VLAN and VSAN policies for environment PRD01179D02C1T01.",
        "What BIOS settings are applied in the profile Alpha_Server?"
    ]
)

AGENT_CARD = AgentCard(
    name='Intersight Data Agent',
    id='intersight-data-agent',
    description="An AI agent that estimates the configuration and operational profile of Cisco Intersight resources using their input attributes. Your role is to analyze metadata such as server type, firmware version, policy attachments, and environment context (e.g., domain profiles, VLAN/VSAN policies, BIOS/boot settings, or assigned templates). Based on these inputs, you must infer the most relevant Intersight configuration details and provide a structured summary of the server or profile state.",
    url=f'http://{INTERSIGHT_AGENT_HOST}:{INTERSIGHT_AGENT_PORT}/',
    version='1.0.0',
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[AGENT_SKILL],
    supportsAuthenticatedExtendedCard=False,
)
