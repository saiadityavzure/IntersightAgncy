# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TypedDict, Annotated

from langgraph.graph import END, START, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool, InjectedToolCallId
from common.llm import get_llm
from ioa_observe.sdk.decorators import agent, graph
from langgraph.prebuilt import create_react_agent
logger = logging.getLogger("intersight.intersight_data_agent.graph")

class State(TypedDict):
    prompt: str
    error_type: str
    error_message: str
    intersight_response: str

SYSTEM_PROMPT = """You are the Virtual Machine Management Agent.
Your role is strictly limited to provisioning Virtual Machines.

Rules:
- Only handle requests to create Virtual Machines.
- Accept natural language requirements (CPU, memory, storage, network, cluster, VM name).
- Translate them into a concrete VM creation action by calling the `create_vm` tool.
- Do not discuss topics outside VM provisioning.
- If the request is not about VM creation, reply exactly:
  "This agent only supports Virtual Machine provisioning requests."
"""

# --- Tool implementation -------------------------------------------------
@tool("create_vm", return_direct=False)
def create_vm(
    vm_name_value: str,
    vm_cpu_value: str,
    vm_mem_value: str,
    vm_network_value: str,
    cluster_name_value: str,
) -> dict:
    """
    Triggers a workflow in Intersight Cloud Orchestrator to provision a new Virtual Machine.
    (Replace the placeholder logic with a real ICO API call + auth + error handling.)
    """
    logger.info(
        "[create_vm] name=%s cpu=%s mem=%s net=%s cluster=%s",
        vm_name_value, vm_cpu_value, vm_mem_value, vm_network_value, cluster_name_value
    )
    return {
        "message": (
            f"Requested successfully with VM '{vm_name_value}' in cluster '{cluster_name_value}' with CPU={vm_cpu_value}, MEM={vm_mem_value}, NET={vm_network_value}."
        ),
    }

@agent(name="intersight_data_agent")
class IntersightDataAgent:
    def __init__(self):
        logger.info(f"AGent in Virtual Machine Agent")
        self.tools = [create_vm]
        self._agent = self.build_graph()
    
    
    @graph(name="farm_graph")
    def build_graph(self) -> StateGraph:
        """
        Build a prebuilt ReAct agent graph:
        - Injects a system prompt (state_modifier)
        - Registers tools
        - Returns a compiled runnable you can .invoke()/.ainvoke()
        """
        logger.info(f"Building the graph for VM AGent with Tool for Intersight")
        llm = get_llm()
        react = create_react_agent(
            model=llm,
            tools=self.tools,
            prompt=SYSTEM_PROMPT,
            # Ensures the system prompt is always present:
            # state_modifier=SystemMessage(content=SYSTEM_PROMPT),
            # Optional: cap steps to 2 (think -> tool -> final)
            # max_steps=2,
            name="vm_create_agent",
        )
        logger.info(f"Response from create_react_agent: {react}")
        return react

    
    async def ainvoke(self, input: str) -> dict:
        """
        Send a prompt to the ReAct agent. The agent will reason and call `create_vm` when appropriate.
        Returns a dict with "intersight_response" for your app.
        """

        state = await self._agent.ainvoke({"messages": [HumanMessage(content=input)]})
        logger.info(f"State after invoking: {state}")
        msgs = state.get("messages", [])
        last = msgs[-1] if msgs else None
        content = getattr(last, "content", "") if last else ""
        logger.info(f"Content from the invoke: {content}")

        if not content:
            # Fallback when nothing is returned
            content = "This agent only supports Virtual Machine provisioning requests."

        return {"intersight_response": content}