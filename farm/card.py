# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill)
from config.config import VM_AGENT_HOST, VM_AGENT_PORT


AGENT_SKILL = AgentSkill(
    id="create_virtual_machine",
    name="Create Virtual Machine",
    description="Handles provisioning operations of Virtual Machines. Takes natural language input describing VM requirements such as CPU, memory, storage, and network, and translates them into a concrete VM creation action.",
    tags=["virtual-machine", "vm", "create"],
    examples=[
        "Create a virtual machine with 4 CPUs, 16GB memory, and 200GB storage.",
        "Provision a new VM called 'Test-VM' with 2 CPUs and 8GB RAM.",
        "Spin up a VM for Ubuntu with 2 cores, 4GB RAM, and default network settings.",
        "Deploy a Windows VM with 8GB RAM and 100GB disk.",
        "Create a VM in cluster Alpha with 6 CPUs, 32GB memory, and 500GB storage."
    ]
)

AGENT_CARD = AgentCard(
    name='Virtual Machine Management Agent',
    id='virtual-machine-agent',
    description="An AI agent that manages Virtual Machines. It supports tasks such as only provisioning VMs based on user input. It interprets natural language descriptions of VM requirements and uses the Create Virtual Machine tool to execute the request.",
    url=f'http://{VM_AGENT_HOST}:{VM_AGENT_PORT}/',
    version='1.0.0',
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[AGENT_SKILL],
    supportsAuthenticatedExtendedCard=False,
)


# AGENT_SKILL = AgentSkill(
#     id="estimate_intersight_profile",
#     name="Estimate Intersight Profile",
#     description="Analyzes a natural language prompt and returns the expected configuration or operational profile of Cisco Intersight resources such as server profiles, domain profiles, and policies.",
#     tags=["intersight", "server", "profile", "policy", "configuration"],
#     examples=[
#         "What configuration is applied to the server profile template VZURE_ESXI?",
#         "Describe the policies attached to the domain profile PROD_FABRIC_A.",
#         "Which firmware version is linked to the UCSX-210C-M6 servers?",
#         "Show me the VLAN and VSAN policies for environment PRD01179D02C1T01.",
#         "What BIOS settings are applied in the profile Alpha_Server?"
#     ]
# )
# AGENT_CARD = AgentCard(
#     name='Intersight Data Agent',
#     id='intersight-data-agent',
#     description="An AI agent that estimates the configuration and operational profile of Cisco Intersight resources using their input attributes. Your role is to analyze metadata such as server type, firmware version, policy attachments, and environment context (e.g., domain profiles, VLAN/VSAN policies, BIOS/boot settings, or assigned templates). Based on these inputs, you must infer the most relevant Intersight configuration details and provide a structured summary of the server or profile state.",
#     url=f'http://{INTERSIGHT_AGENT_HOST}:{INTERSIGHT_AGENT_PORT}/',
#     version='1.0.0',
#     defaultInputModes=["text"],
#     defaultOutputModes=["text"],
#     capabilities=AgentCapabilities(streaming=True),
#     skills=[AGENT_SKILL],
#     supportsAuthenticatedExtendedCard=False,
# )
